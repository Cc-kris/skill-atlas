"""Shared data structures and small serialization helpers for Skill Atlas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SkillRecord:
    id: str
    name: str
    display_name: str
    host: str
    scope: str
    path: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    summary: str = ""
    headings: list[str] = field(default_factory=list)
    category: str = "Other"
    parent_category: str = ""
    level: int = 1
    status: str = "valid"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    host: str
    roots: list[str]
    skills: list[SkillRecord]
    warnings: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": "1.0",
            "host": self.host,
            "roots": self.roots,
            "skills": [skill.to_dict() for skill in self.skills],
            "warnings": self.warnings,
        }
