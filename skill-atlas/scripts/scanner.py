"""Discover and normalize skills without executing their contents."""

from __future__ import annotations

import json
from pathlib import Path

from atlas_model import ScanResult, SkillRecord
from host_adapters import EXCLUDED_DIRS, HostAdapter
from metadata import extract_metadata


def discover_skill_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for directory in sorted((item for item in root.rglob("*") if item.is_dir()), key=lambda item: item.as_posix()):
        if any(part.lower() in EXCLUDED_DIRS for part in directory.relative_to(root).parts):
            continue
        skill_file = directory / "SKILL.md"
        if skill_file.is_file() and not skill_file.is_symlink():
            found.append(skill_file)
    return found


def _skill_json(path: Path) -> dict[str, object]:
    candidate = path.parent / "skill.json"
    if not candidate.is_file() or candidate.is_symlink():
        return {}
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def scan(adapter: HostAdapter, roots: list[Path]) -> ScanResult:
    records: list[SkillRecord] = []
    warnings: list[dict[str, str]] = []
    seen_real_paths: set[Path] = set()
    for root in roots:
        for path in discover_skill_files(root):
            real_path = path.resolve()
            if real_path in seen_real_paths:
                continue
            seen_real_paths.add(real_path)
            is_project = ".agents" in path.parts and "skills" in path.parts and path.parts[path.parts.index(".agents") + 1] == "skills"
            record = extract_metadata(path, adapter.host_name, root, "project" if is_project else "user")
            metadata = _skill_json(path)
            if metadata.get("description") and not record.description:
                record.description = str(metadata["description"])
            if isinstance(metadata.get("triggers"), list) and not record.triggers:
                record.triggers = [str(value) for value in metadata["triggers"]]
            records.append(record)
    records.sort(key=lambda item: (item.name.casefold(), item.host, item.path.casefold()))
    return ScanResult(host=adapter.host_name, roots=[str(root) for root in roots], skills=records, warnings=warnings)
