"""Optional local-terminal enrichment for Chinese summaries and source triggers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any


def enrich_many(items: list[dict[str, Any]], host: str = "codex") -> dict[str, dict[str, Any]]:
    prompt = "你是技能目录整理器。只根据每个 Skill 自己提供的资料回答，不要臆造能力。输出严格 JSON 对象，键必须是输入 id，值为 summary_cn（自然中文、60字以内）和 triggers（资料中明确出现的触发词、适用场景或命令词，没有则为空数组）。输入：\n" + json.dumps(items, ensure_ascii=False)
    command = {"codex": ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-"], "claude-code": ["claude", "-p", "--output-format", "json", "--tools", "", "--no-session-persistence"]}.get(host)
    if not command:
        return {}
    try:
        result = subprocess.run(
            command,
            input=prompt,
            capture_output=True, text=True, timeout=300, check=True,
            env={**os.environ, "NO_COLOR": "1"},
        )
        text = result.stdout.strip()
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None
        data = json.loads(text[start:end + 1])
        return data if isinstance(data, dict) else {}
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None


def enrich(name: str, description: str, summary: str, headings: list[str]) -> dict[str, Any] | None:
    result = enrich_many([{"id": name, "name": name, "description": description, "summary": summary, "headings": headings}])
    return result.get(name) if result else None
