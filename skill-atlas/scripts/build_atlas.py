#!/usr/bin/env python3
"""CLI entrypoint for scanning a host and building an offline atlas."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_html import write_html
from classifier import classify
from host_adapters import detect_host
from scanner import scan


def build(args: argparse.Namespace) -> tuple[Path, Path, dict]:
    adapter, roots = detect_host(args.host, args.root)
    if args.include_project:
        roots = adapter.discover_roots(args.root, include_project=True)
    result = scan(adapter, roots)
    classify(result.skills)
    if not args.no_ai_label:
        from ai_enrich import enrich_many
        items = [{"id": s.id, "name": s.name, "description": s.description, "headings": s.headings, "source": s.summary} for s in result.skills]
        enriched = enrich_many(items, host=adapter.host_name)
        for skill in result.skills:
            data = enriched.get(skill.id)
            if data:
                skill.summary = str(data.get("summary_cn") or "").strip()
                source_triggers = data.get("triggers")
                if isinstance(source_triggers, list) and source_triggers:
                    skill.triggers = [str(x).strip() for x in source_triggers if str(x).strip()][:10]
    snapshot = result.to_dict()
    output = Path(args.output).expanduser().resolve()
    json_path = output.with_suffix(".json")
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_html(snapshot, output)
    if args.open:
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(output)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os.name == "nt":
                os.startfile(str(output))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(output)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
    return output, json_path, snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local offline Skill Atlas")
    parser.add_argument("--host", choices=["codex", "claude-code", "workbuddy", "opencode", "generic"])
    parser.add_argument("--root", help="Explicit skill root, required for generic host")
    parser.add_argument("--output", default="./skill-atlas.html")
    parser.add_argument("--include-project", action="store_true")
    parser.add_argument("--no-ai-label", action="store_true", help="Reserved compatibility flag; local classifier is always used")
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="Rebuild even if output exists")
    args = parser.parse_args()
    try:
        output, json_path, snapshot = build(args)
    except ValueError as exc:
        print(f"skill-atlas: {exc}", file=sys.stderr)
        return 2
    print(f"host={snapshot['host']} skills={len(snapshot['skills'])} warnings={len(snapshot['warnings']) + sum(bool(s['warnings']) for s in snapshot['skills'])}")
    print(f"html={output}\njson={json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
