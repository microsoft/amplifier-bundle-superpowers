"""Tests for Fix 5: Mode content cleanup after infrastructure changes."""

import re
from pathlib import Path

import yaml

MODES_DIR = Path(__file__).parent.parent / "modes"

MODE_FILES = [
    "brainstorm.md",
    "write-plan.md",
    "execute-plan.md",
    "debug.md",
    "verify.md",
    "finish.md",
]


def read_mode(filename: str) -> str:
    return (MODES_DIR / filename).read_text(encoding="utf-8")


def parse_frontmatter(content: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match, "Missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


class TestVerifyAspirationNote:
    def test_verify_no_false_exemption_claim(self) -> None:
        content = read_mode("verify.md")
        assert "infrastructure_tools" in content or "infrastructure tools" in content


class TestSafeToolsCleanup:
    def test_no_todo_in_safe_tools(self) -> None:
        for filename in MODE_FILES:
            content = read_mode(filename)
            fm = parse_frontmatter(content)
            safe = fm.get("mode", {}).get("tools", {}).get("safe", [])
            assert "todo" not in safe, f"{filename}: 'todo' should not be in safe_tools"
