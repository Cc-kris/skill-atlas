import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_html import render
from classifier import classify
from host_adapters import ADAPTERS, detect_host
from metadata import extract_metadata, parse_frontmatter
from scanner import scan


def make_skill(root: Path, name: str, text: str = "") -> Path:
    path = root / name
    path.mkdir(parents=True)
    file = path / "SKILL.md"
    file.write_text(text or f"---\nname: {name}\ndescription: {name} tooling\ntriggers: [scan, map]\n---\n# {name}\nDetails.", encoding="utf-8")
    return file


class AtlasTests(unittest.TestCase):
    def test_frontmatter_normal_and_fallback(self):
        data, warnings, body = parse_frontmatter("---\nname: demo\ndescription: Hello\n---\n# Heading")
        self.assertEqual(data["name"], "demo")
        self.assertFalse(warnings)
        self.assertIn("Heading", body)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = make_skill(root, "fallback", "# Fallback\n\nA useful local skill.")
            record = extract_metadata(file, "generic", root)
            self.assertEqual(record.name, "fallback")
            self.assertEqual(record.status, "warning")
            self.assertTrue(record.summary)

    def test_triggers_only_use_explicit_declarations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = make_skill(
                root,
                "trigger-source",
                """---
name: trigger-source
description: Trigger extraction test
---
# Usage
Run `$trigger-source` from `scripts/build.py` and inspect `/tmp/output`.
Triggers: alpha, beta
When to Use: migration, audit
""",
            )
            record = extract_metadata(file, "generic", root)
            self.assertEqual(record.triggers, ["alpha", "beta", "migration", "audit"])
            self.assertNotIn("$trigger-source", record.triggers)
            self.assertNotIn("scripts/build.py", record.triggers)
            self.assertNotIn("/tmp/output", record.triggers)

    def test_triggers_read_explicit_use_when_block(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = make_skill(root, "block", """---
name: block
description: test
---
<Use_When>
- User requests a complete delivery
- User says $block
</Use_When>
`not-a-trigger`
""")
            record = extract_metadata(file, "generic", root)
            self.assertEqual(record.triggers, ["User requests a complete delivery", "User says $block"])

    def test_triggers_read_routing_language_from_description(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = make_skill(root, "description-routing", """---
name: description-routing
description: Build UI from references; also use for image to UI, UI screenshot to code, and mobile prototype.
---
# Details
""")
            record = extract_metadata(file, "generic", root)
            self.assertEqual(record.triggers, ["image to UI", "UI screenshot to code", "mobile prototype"])

    def test_triggers_fall_back_to_unmodified_description_sentence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = make_skill(root, "description-fallback", """---
name: description-fallback
description: Source-backed release validation for deployment work. This sentence must not become part of the trigger.
---
# Details
`scripts/release.py` and $release are implementation examples.
""")
            record = extract_metadata(file, "generic", root)
            self.assertEqual(record.triggers, ["Source-backed release validation for deployment work."])
            self.assertNotIn("scripts/release.py", record.triggers)
            self.assertNotIn("$release", record.triggers)

    def test_scanner_excludes_sensitive_dirs_and_keeps_bad_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "good")
            make_skill(root / "auth", "secret")
            bad = root / "bad"
            bad.mkdir()
            (bad / "SKILL.md").write_bytes(b"\xff\xfe")
            result = scan(ADAPTERS["generic"], [root])
            names = {skill.name for skill in result.skills}
            self.assertIn("good", names)
            self.assertNotIn("secret", names)
            self.assertIn("bad", names)

    def test_classifier_splits_over_ten_and_is_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills = []
            for index in range(12):
                file = make_skill(root, f"design-{index}", f"---\nname: design-{index}\ndescription: design interface toolkit\n---\n# Interface")
                skills.append(extract_metadata(file, "generic", root))
            classify(skills)
            self.assertGreaterEqual(len({skill.category for skill in skills}), 1)
            self.assertTrue(all(skill.category for skill in skills))
            first = [(skill.id, skill.category, skill.level) for skill in skills]
            classify(skills)
            self.assertEqual(first, [(skill.id, skill.category, skill.level) for skill in skills])

    def test_host_detection_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_codex = os.environ.get("CODEX_HOME")
            old_claude = os.environ.get("CLAUDE_CODE_HOME")
            try:
                os.environ["CODEX_HOME"] = str(root / "missing")
                os.environ["CLAUDE_CODE_HOME"] = str(root / "missing2")
                with self.assertRaisesRegex(ValueError, "explicitly"):
                    detect_host()
            finally:
                if old_codex is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old_codex
                if old_claude is None:
                    os.environ.pop("CLAUDE_CODE_HOME", None)
                else:
                    os.environ["CLAUDE_CODE_HOME"] = old_claude

    def test_explicit_host_reads_only_its_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "codex-only")
            adapter, roots = detect_host("codex", str(root))
            result = scan(adapter, roots)
            self.assertEqual(adapter.host_name, "codex")
            self.assertEqual([skill.name for skill in result.skills], ["codex-only"])

    def test_codex_home_env_resolves_skills_child(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            make_skill(home / "skills", "from-home")
            old = os.environ.get("CODEX_HOME")
            try:
                os.environ["CODEX_HOME"] = str(home)
                adapter, roots = detect_host("codex")
                self.assertEqual(roots, [(home / "skills").resolve()])
                self.assertEqual([skill.name for skill in scan(adapter, roots).skills], ["from-home"])
            finally:
                if old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old

    def test_html_is_self_contained_and_has_controls(self):
        snapshot = {"host": "generic", "roots": [], "skills": [], "warnings": []}
        page = render(snapshot)
        self.assertNotIn("__ATLAS_JSON__", page)
        self.assertIn("交互式技能脑图", page)
        self.assertIn("搜索技能", page)
        self.assertNotIn("https://", page)


if __name__ == "__main__":
    unittest.main()
