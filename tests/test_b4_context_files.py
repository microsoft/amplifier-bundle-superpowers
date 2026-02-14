"""Verification tests for B4: Context files and skills.

Tests that:
1. using-superpowers-amplifier.md exists with required content, no Claude Code refs
2. code-review-reception skill exists with required content, no Claude Code refs
3. parallel-agent-dispatch skill exists with required content, uses delegate() not Task()
4. superpowers-methodology.yaml includes required context files
"""

import os
import re

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
CONTEXT_DIR = os.path.join(REPO_ROOT, "context")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
BEHAVIOR_FILE = os.path.join(REPO_ROOT, "behaviors", "superpowers-methodology.yaml")

CLAUDE_CODE_FORBIDDEN = [
    "Skill tool",  # Claude Code's Skill tool
    "TodoWrite",  # Claude Code's TodoWrite
    "CLAUDE.md",  # Claude Code config
]


def read_context(filename: str) -> str:
    path = os.path.join(CONTEXT_DIR, filename)
    assert os.path.isfile(path), f"File does not exist: {path}"
    with open(path) as f:
        return f.read()


def read_skill(skill_name: str) -> str:
    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    assert os.path.isfile(path), f"Skill file does not exist: {path}"
    with open(path) as f:
        return f.read()


# --- using-superpowers-amplifier.md ---


class TestUsingSuperPowersAmplifier:
    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_context("using-superpowers-amplifier.md")

    def test_has_the_rule(self):
        assert "The Rule" in self.content

    def test_has_load_skill_reference(self):
        assert "load_skill()" in self.content

    def test_has_mode_reference(self):
        # References mode tool or /mode commands
        assert "mode" in self.content.lower()

    def test_has_skill_priority_rules(self):
        assert (
            "Process skills first" in self.content
            or "Process skills FIRST" in self.content
        )

    def test_has_red_flags_table(self):
        # Must have at least 12 rationalization rows in a table
        table_rows = re.findall(r"^\|[^|]+\|[^|]+\|$", self.content, re.MULTILINE)
        # Subtract header and separator rows
        data_rows = [r for r in table_rows if not r.startswith("|-")]
        # Header row + 12 data rows minimum
        assert len(data_rows) >= 13, (
            f"Expected 13+ table rows (1 header + 12 data), got {len(data_rows)}"
        )

    def test_has_delegate_reference(self):
        assert "delegate()" in self.content

    def test_no_claude_code_references(self):
        for forbidden in CLAUDE_CODE_FORBIDDEN:
            assert forbidden not in self.content, (
                f"Found forbidden Claude Code reference: {forbidden}"
            )


# --- code-review-reception skill ---


class TestCodeReviewReception:
    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_skill("code-review-reception")

    def test_has_forbidden_responses(self):
        assert "You're absolutely right!" in self.content

    def test_has_required_response_pattern(self):
        assert "Restate" in self.content or "restate" in self.content

    def test_has_clarifying_questions(self):
        assert (
            "clarifying question" in self.content.lower()
            or "Ask clarifying" in self.content
        )

    def test_has_push_back(self):
        assert "push back" in self.content.lower() or "Push back" in self.content

    def test_has_just_start_working(self):
        assert (
            "start working" in self.content.lower()
            or "just act" in self.content.lower()
            or "Just start" in self.content
        )

    def test_has_yagni_check(self):
        assert "YAGNI" in self.content

    def test_has_grep_for_usage(self):
        assert "grep" in self.content.lower()

    def test_no_claude_code_references(self):
        for forbidden in CLAUDE_CODE_FORBIDDEN:
            assert forbidden not in self.content, (
                f"Found forbidden Claude Code reference: {forbidden}"
            )


# --- parallel-agent-dispatch skill ---


class TestParallelDispatch:
    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_skill("parallel-agent-dispatch")

    def test_has_decision_framework(self):
        # Should have when-to-use guidance
        assert "When to" in self.content or "when to" in self.content

    def test_has_delegate_syntax(self):
        assert "delegate(" in self.content

    def test_no_task_syntax(self):
        # Should NOT use Task() syntax from Claude Code
        assert "Task(" not in self.content, (
            "Found Task() syntax — should use delegate() instead"
        )

    def test_has_context_depth_none(self):
        assert (
            'context_depth="none"' in self.content
            or "context_depth='none'" in self.content
            or 'context_depth: "none"' in self.content
        )

    def test_has_parallelize_vs_serialize(self):
        assert "parallel" in self.content.lower()
        assert "serial" in self.content.lower() or "sequential" in self.content.lower()


# --- superpowers-methodology.yaml wiring ---


class TestBehaviorYamlWiring:
    @pytest.fixture(autouse=True)
    def load_content(self):
        assert os.path.isfile(BEHAVIOR_FILE), f"Behavior file missing: {BEHAVIOR_FILE}"
        with open(BEHAVIOR_FILE) as f:
            self.content = f.read()

    def test_includes_using_superpowers_amplifier(self):
        assert "superpowers:context/using-superpowers-amplifier.md" in self.content

    def test_includes_modes_instructions(self):
        assert "modes:context/modes-instructions.md" in self.content

    def test_does_not_include_deleted_context_files(self):
        assert "code-review-reception.md" not in self.content
        assert "parallel-dispatch.md" not in self.content
