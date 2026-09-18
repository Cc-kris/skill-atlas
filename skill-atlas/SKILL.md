---
name: skill-atlas
description: "Inventory the skills installed for the current Codex, Claude Code, WorkBuddy, or OpenCode host and generate a searchable offline HTML atlas. Use when a user asks to scan, classify, map, or refresh their current skills."
---

# Skill Atlas

Use the bundled local scanner to create an atlas of the active host's skills. The scanner is read-only with respect to discovered skills: it reads `SKILL.md`, optional `skill.json`, and safe metadata only; it never executes a discovered skill or reads credential/history directories.

## Run

From this skill directory, run:

```bash
python3 scripts/build_atlas.py --output ./atlas.html
```

The command writes a self-contained HTML file and a sibling `atlas.json` snapshot. Open the HTML directly in a browser; no server or network is needed.

Use `--host codex|claude-code|workbuddy|opencode` when automatic host detection is ambiguous. Use `--root PATH --host generic` for an explicitly supplied skill directory. `--include-project` adds a project-local `.agents/skills` directory. `--open` opens the generated file with the platform default browser when supported.

The output is deterministic for the same input files. Warnings for malformed or incomplete skills are visible in the snapshot and UI while valid skills continue to render. Classification is local and dynamic: labels come from the discovered names, descriptions, triggers, and headings; categories containing more than ten skills are recursively split to a maximum depth of three when the data supports it.

For the data contract and host path policy, read [references/output-schema.json](references/output-schema.json) and [references/host-profiles.yaml](references/host-profiles.yaml). The implementation is intentionally dependency-free so the generated page remains offline-capable.
