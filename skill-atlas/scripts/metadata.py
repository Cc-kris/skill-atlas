"""Safe, dependency-free metadata extraction for SKILL.md files."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from atlas_model import SkillRecord



FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,2}\s+(.+?)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}|[\u4e00-\u9fff]{2,}")


def _scalar(value: str) -> Any:
    raw = value.strip()
    if not raw:
        return ""
    if raw.startswith("[") and raw.endswith("]"):
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (ValueError, SyntaxError, json.JSONDecodeError):
                continue
        return [item.strip(" '\"") for item in raw[1:-1].split(",") if item.strip()]
    return raw.strip(" '\"")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], list[str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, ["frontmatter missing; fallback metadata used"], text
    data: dict[str, Any] = {}
    warnings: list[str] = []
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line_number = index + 1
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[:1].isspace():
            index += 1
            continue
        if ":" not in line:
            warnings.append(f"frontmatter line {line_number} is not key/value")
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            warnings.append(f"frontmatter line {line_number} has empty key")
            index += 1
            continue
        raw = value.strip()
        if raw in {">", ">-", "|", "|-"}:
            folded: list[str] = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index][:1].isspace()):
                if lines[index].strip():
                    folded.append(lines[index].strip())
                index += 1
            data[key] = (" " if raw.startswith(">") else "\n").join(folded).strip()
            continue
        if raw == "":
            values: list[str] = []
            cursor = index + 1
            while cursor < len(lines) and (not lines[cursor].strip() or lines[cursor][:1].isspace()):
                item = lines[cursor].strip()
                if item.startswith("-"):
                    values.append(item[1:].strip(" '\""))
                cursor += 1
            data[key] = values if values else ""
            index = cursor
            continue
        data[key] = _scalar(raw)
        index += 1
    return data, warnings, text[match.end() :]


def _first_paragraph(body: str) -> str:
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("```"):
            if lines:
                break
            continue
        if stripped.startswith("#") or stripped.startswith(">") or stripped.startswith("-"):
            continue
        lines.append(stripped)
    return re.sub(r"\s+", " ", " ".join(lines))[:280]


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [part.strip() for part in re.split(r"[,;]", str(value)) if part.strip()]
    return []


def _declared_triggers(body: str) -> list[str]:
    """Read only explicitly labelled invocation sections from a skill source."""
    values: list[str] = []
    inline = re.findall(r"(?im)^\s*(?:trigger(?:s)?|触发词|适用场景|when to use)\s*[:：]\s*(.+)$", body)
    values.extend(item for line in inline for item in _as_list(line))
    tagged = re.findall(r"(?is)<(?:use_when|when_to_use|triggers?)>\s*(.*?)\s*</(?:use_when|when_to_use|triggers?)>", body)
    for block in tagged:
        values.extend(re.findall(r"(?m)^\s*[-*]\s+(.+?)\s*$", block))
    headings = re.findall(r"(?im)^#{1,3}\s*(?:when to use|triggers?|触发词|适用场景)\s*$\n(.*?)(?=^#{1,3}\s|\Z)", body)
    for block in headings:
        values.extend(re.findall(r"(?m)^\s*[-*]\s+(.+?)\s*$", block))
    return [re.sub(r"\s+", " ", value).strip() for value in values if value.strip()]


def _description_triggers(description: str) -> list[str]:
    """Extract invocation language explicitly declared in frontmatter prose."""
    if not description:
        return []
    values: list[str] = []
    # Skill descriptions commonly use these exact routing contracts. Keep the
    # source wording and split only list-like clauses; never infer from nouns.
    patterns = (
        (r"(?is)\b(?:also\s+use\s+for|also\s+trigger\s+for)\s+(.+?)(?=\.\s*(?:[A-Z]|[\u4e00-\u9fff])|$)", True),
        (r"(?is)\buse\s+when\s+(.+?)(?=\.\s*(?:[A-Z]|[\u4e00-\u9fff])|$)", False),
        (r"(?is)(?<!also\s)\buse\s+for\s+(.+?)(?=\.\s*(?:[A-Z]|[\u4e00-\u9fff])|$)", False),
        (r"(?is)(当[^。；;]+(?:时使用|时调用|时启用))", False),
        (r"(?is)(适用于[^。；;]+)", False),
    )
    for pattern, is_list in patterns:
        for match in re.finditer(pattern, description):
            clause = match.group(1) if match.lastindex else match.group(0)
            parts = re.split(r"\s*,\s*|\s+and\s+|\s*、\s*|\s*；\s*|\s*;\s*", clause) if is_list else [clause]
            values.extend(re.sub(r"^(?:and|or)\s+", "", part.strip(" .，。；;")) for part in parts if part.strip(" .，。；;"))
    if not values:
        # A frontmatter description is authored as the skill's routing
        # contract. Preserve its first sentence as a source-backed scenario
        # when the author did not use a standard trigger label.
        first = re.split(r"(?<=[。！？!?])\s*|(?<=\.)\s+(?=[A-Z])", description, maxsplit=1)[0].strip()
        if first:
            values.append(first)
    return values


def extract_metadata(path: Path, host: str, root: Path, scope: str = "user") -> SkillRecord:
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
        warnings.append("file was not valid UTF-8; replacement characters used")
    except OSError as exc:
        return SkillRecord(
            id=f"{host}:{path.name}", name=path.parent.name, display_name=path.parent.name.replace("-", " ").title(),
            host=host, scope=scope, path=str(path), status="invalid", warnings=[f"read failed: {type(exc).__name__}"],
        )
    frontmatter, fm_warnings, body = parse_frontmatter(text)
    warnings.extend(fm_warnings)
    headings = [match.group(1).strip() for line in body.splitlines() if (match := HEADING_RE.match(line))]
    name = str(frontmatter.get("name") or path.parent.name).strip()
    description = str(frontmatter.get("description") or "").strip()
    triggers = _as_list(frontmatter.get("triggers", frontmatter.get("trigger")))
    if not triggers:
        # Keep the source contract honest: only an explicitly labelled field is
        # a trigger declaration. Ordinary prose, commands, paths, and examples
        # are intentionally ignored.
        triggers = _declared_triggers(body)
    if not triggers:
        triggers = _description_triggers(description)
    triggers = list(dict.fromkeys(triggers))[:10]
    if not description:
        description = _first_paragraph(body)
    # Frontmatter is the routing contract and usually contains the clearest
    # purpose/when-to-use statement; prefer it over a terse implementation note.
    summary = description or _first_paragraph(body)
    if not name:
        name = path.parent.name or "unnamed-skill"
        warnings.append("name missing; directory name used")
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        relative = path.name
    root_text = str(root.resolve())
    shown_root = "~" + root_text[len(str(Path.home())) :] if root_text.startswith(str(Path.home())) else root.name
    shown_path = f"{shown_root.rstrip('/')}/{relative}"
    status = "warning" if warnings else "valid"
    return SkillRecord(
        id=f"{host}:{relative}", name=name, display_name=name.replace("-", " ").replace("_", " ").title(),
        host=host, scope=scope, path=shown_path, description=description, triggers=triggers,
        summary=summary, headings=headings[:12], status=status, warnings=warnings, source_text=text,
    )
