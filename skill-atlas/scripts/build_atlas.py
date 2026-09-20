#!/usr/bin/env python3
"""CLI entrypoint for scanning a host and building an offline atlas."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    cache_path = output.with_suffix('.enrichment.json')
    if not args.no_ai_label:
        from ai_enrich import enrich_many
        try:
            cache = json.loads(cache_path.read_text()) if not args.refresh else {}
        except (OSError, ValueError):
            cache = {}
        keys = {s.id: hashlib.sha256(('v3:'+adapter.host_name+s.source_text).encode()).hexdigest() for s in result.skills}
        enriched = {s.id: cache[keys[s.id]] for s in result.skills if keys[s.id] in cache}
        items = [{"id": s.id, "name": s.name, "description": s.description, "source": s.source_text[:16000]} for s in result.skills if s.id not in enriched]
        batches = [items[start:start+8] for start in range(0,len(items),8)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(enrich_many,b,host=adapter.host_name):b for b in batches}
            for future in as_completed(futures):
                batch = future.result()
                for item in futures[future]:
                    data = batch.get(item['id'], {})
                    if valid_enrichment(data):
                        enriched[item['id']] = data
                        cache[keys[item['id']]] = data
                cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
                print(f'中文总结已就绪：{len(enriched)}/{len(result.skills)}',file=sys.stderr,flush=True)
        missing = [s.name for s in result.skills if s.id not in enriched]
        if missing:
            raise ValueError('中文总结未完成，已保存成功缓存，原有HTML保持不变；重新运行可续传：'+', '.join(missing))
        for skill in result.skills:
            data = enriched.get(skill.id) or {}
            if data:
                generated = str(data.get("summary_cn") or "").strip()
                if generated:
                    skill.summary = generated
                    # The model improves prose only. Classification remains a
                    # deterministic, inspectable local pass so one run cannot
                    # invent a new top-level theme.
        classify(result.skills)
    snapshot = result.to_dict()
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
    parser.add_argument("--no-ai-label", action="store_true", help="仅扫描并使用本地分类；不保证中文总结")
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


def valid_enrichment(data: dict) -> bool:
    if not isinstance(data,dict):
        return False
    text = data.get('summary_cn','')
    if not isinstance(text,str) or len(re.findall(r'[\u4e00-\u9fff]',text)) < 65:
        return False
    for key in ('category','subcategory'):
        value=data.get(key,'')
        if not isinstance(value,str) or not re.search(r'[\u4e00-\u9fff]',value) or len(value)>18 or any(t in value for t in ('其他','综合工具','通用工具','工具能力','自动主题','/')):
            return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
