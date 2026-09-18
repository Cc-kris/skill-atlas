"""Host detection and narrowly scoped skill-root adapters."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


EXCLUDED_DIRS = {"auth", "credentials", "history", "cache", "backup", "backups", ".git", "node_modules"}


@dataclass(frozen=True)
class HostAdapter:
    host_name: str
    root_env: str | None
    default_roots: tuple[str, ...]
    env_points_to_home: bool = False

    def discover_roots(self, explicit_root: str | None = None, include_project: bool = False) -> list[Path]:
        if explicit_root:
            roots = [Path(explicit_root).expanduser()]
        else:
            configured = os.environ.get(self.root_env or "") if self.root_env else None
            if configured:
                configured_path = Path(configured).expanduser()
                roots = [configured_path / "skills"] if self.env_points_to_home else [configured_path]
            else:
                roots = [Path(item).expanduser() for item in self.default_roots]
        if include_project:
            roots.append(Path.cwd() / ".agents" / "skills")
        result: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            resolved = root.resolve()
            if resolved in seen or not resolved.is_dir():
                continue
            seen.add(resolved)
            result.append(resolved)
        return result

    def relative_path(self, path: Path, root: Path) -> str:
        return path.resolve().relative_to(root.resolve()).as_posix()


def _home(name: str) -> str:
    return str(Path.home() / name)


ADAPTERS: dict[str, HostAdapter] = {
    "codex": HostAdapter("codex", "CODEX_HOME", (str(Path.home() / ".codex" / "skills"),), True),
    "claude-code": HostAdapter("claude-code", "CLAUDE_CODE_HOME", (str(Path.home() / ".claude" / "skills"),)),
    "workbuddy": HostAdapter("workbuddy", "WORKBUDDY_SKILLS_DIR", (str(Path.home() / ".workbuddy" / "skills"),)),
    "opencode": HostAdapter(
        "opencode",
        "OPENCODE_SKILLS_DIR",
        (str(Path.home() / ".config" / "opencode" / "skills"), str(Path.home() / ".opencode" / "skills")),
    ),
    "generic": HostAdapter("generic", "SKILL_ATLAS_ROOT", ()),
}


def detect_host(explicit_host: str | None = None, explicit_root: str | None = None) -> tuple[HostAdapter, list[Path]]:
    if explicit_host:
        key = explicit_host.lower()
        if key not in ADAPTERS:
            raise ValueError(f"Unsupported host: {explicit_host}")
        adapter = ADAPTERS[key]
        roots = adapter.discover_roots(explicit_root)
        if not roots:
            raise ValueError(f"No skill root found for host {key}; provide --root or create its allowlisted directory")
        return adapter, roots

    candidates: list[tuple[HostAdapter, list[Path]]] = []
    for adapter in ADAPTERS.values():
        if adapter.host_name == "generic":
            continue
        roots = adapter.discover_roots()
        if roots:
            candidates.append((adapter, roots))
    if len(candidates) != 1:
        names = ", ".join(adapter.host_name for adapter, _ in candidates) or "none"
        raise ValueError(f"Unable to identify one host (detected: {names}); pass --host explicitly")
    adapter, roots = candidates[0]
    return adapter, roots
