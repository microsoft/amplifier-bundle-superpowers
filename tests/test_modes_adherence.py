"""Tests for modes adherence — validates frontmatter config, guidance content, and agent inclusions."""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent

MODES_DIR = REPO_ROOT / "modes"
AGENTS_DIR = REPO_ROOT / "agents"

MODE_FILES = [
    "brainstorm.md",
    "write-plan.md",
    "execute-plan.md",
    "debug.md",
    "verify.md",
    "finish.md",
]

NON_FINISH_MODES = [
    "brainstorm.md",
    "write-plan.md",
    "execute-plan.md",
    "debug.md",
    "verify.md",
]

AGENT_FILES = [
    "brainstormer.md",
    "plan-writer.md",
    "implementer.md",
    "spec-reviewer.md",
    "code-quality-reviewer.md",
]

EXECUTION_AGENTS = [
    "implementer.md",
    "spec-reviewer.md",
    "code-quality-reviewer.md",
]

# Expected transition map from design
TRANSITION_MAP = {
    "brainstorm": {
        "allowed_transitions": ["write-plan", "debug"],
        "allow_clear": False,
    },
    "write-plan": {
        "allowed_transitions": ["execute-plan", "brainstorm", "debug"],
        "allow_clear": False,
    },
    "execute-plan": {
        "allowed_transitions": ["verify", "debug", "brainstorm", "write-plan"],
        "allow_clear": False,
    },
    "debug": {
        "allowed_transitions": ["verify", "brainstorm", "execute-plan"],
        "allow_clear": False,
    },
    "verify": {
        "allowed_transitions": ["finish", "debug", "execute-plan", "brainstorm", "write-plan"],
        "allow_clear": False,
    },
    "finish": {
        "allowed_transitions": ["execute-plan", "brainstorm"],
        "allow_clear": True,
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_mode(filename: str) -> str:
    path = MODES_DIR / filename
    assert path.exists(), f"Mode file not found: {path}"
    return path.read_text(encoding="utf-8")


def _read_agent(filename: str) -> str:
    path = AGENTS_DIR / filename
    assert path.exists(), f"Agent file not found: {path}"
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(content: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match, "Missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


def _transitions_section(content: str) -> str:
    """Extract everything from '## Transitions' to the next top-level '## ' heading (or EOF)."""
    match = re.search(r"^## Transitions\s*\n(.*?)(?=^## |\Z)", content, re.DOTALL | re.MULTILINE)
    return match.group(1) if match else ""


# ---------------------------------------------------------------------------
# 1. TestModeTransitionMap
# ---------------------------------------------------------------------------


class TestModeTransitionMap:
    def test_allowed_transitions_match(self) -> None:
        """Each mode file's allowed_transitions matches the expected transition map."""
        for filename in MODE_FILES:
            content = _read_mode(filename)
            fm = _parse_frontmatter(content)
            mode_name = fm["mode"]["name"]
            expected = TRANSITION_MAP[mode_name]["allowed_transitions"]
            actual = fm["mode"]["allowed_transitions"]
            assert sorted(actual) == sorted(expected), (
                f"{filename}: allowed_transitions {actual!r} != expected {expected!r}"
            )

    def test_allow_clear_matches(self) -> None:
        """Each mode file's allow_clear matches the expected transition map."""
        for filename in MODE_FILES:
            content = _read_mode(filename)
            fm = _parse_frontmatter(content)
            mode_name = fm["mode"]["name"]
            expected = TRANSITION_MAP[mode_name]["allow_clear"]
            actual = fm["mode"]["allow_clear"]
            assert actual == expected, (
                f"{filename}: allow_clear={actual!r}, expected {expected!r}"
            )

    def test_only_finish_allows_clear(self) -> None:
        """All non-finish modes have allow_clear: false; finish has allow_clear: true."""
        for filename in NON_FINISH_MODES:
            content = _read_mode(filename)
            fm = _parse_frontmatter(content)
            actual = fm["mode"]["allow_clear"]
            assert actual is False, f"{filename}: expected allow_clear=false, got {actual!r}"

        finish_content = _read_mode("finish.md")
        finish_fm = _parse_frontmatter(finish_content)
        assert finish_fm["mode"]["allow_clear"] is True, (
            "finish.md: expected allow_clear=true"
        )


# ---------------------------------------------------------------------------
# 2. TestDoNotProhibitions
# ---------------------------------------------------------------------------


class TestDoNotProhibitions:
    def test_non_finish_modes_prohibit_push_merge_pr(self) -> None:
        """All 5 non-finish modes contain 'git push' AND 'git merge' AND 'gh pr create'."""
        for filename in NON_FINISH_MODES:
            content = _read_mode(filename)
            assert "git push" in content, f"{filename}: missing 'git push'"
            assert "git merge" in content, f"{filename}: missing 'git merge'"
            assert "gh pr create" in content, f"{filename}: missing 'gh pr create'"

    def test_finish_does_not_prohibit_push(self) -> None:
        """finish.md does NOT contain 'belong exclusively to /finish'."""
        content = _read_mode("finish.md")
        assert "belong exclusively to /finish" not in content, (
            "finish.md: should NOT contain 'belong exclusively to /finish' "
            "(that prohibition text belongs in non-finish modes only)"
        )


# ---------------------------------------------------------------------------
# 3. TestContradictionFixes
# ---------------------------------------------------------------------------


class TestContradictionFixes:
    def test_execute_plan_no_mode_off(self) -> None:
        """execute-plan.md does NOT contain '/mode off'."""
        content = _read_mode("execute-plan.md")
        assert "/mode off" not in content, (
            "execute-plan.md: should NOT contain '/mode off'"
        )

    def test_execute_plan_transitions_to_verify(self) -> None:
        """execute-plan.md contains '/verify'."""
        content = _read_mode("execute-plan.md")
        assert "/verify" in content, (
            "execute-plan.md: should contain '/verify' as a transition target"
        )

    def test_brainstorm_no_mode_clear_escape(self) -> None:
        """brainstorm.md does NOT contain \"mode(operation='clear')\"."""
        content = _read_mode("brainstorm.md")
        assert "mode(operation='clear')" not in content, (
            "brainstorm.md: should NOT contain \"mode(operation='clear')\" "
            "(clear is only allowed from finish mode)"
        )

    def test_brainstorm_exploration_stays_in_mode(self) -> None:
        """brainstorm.md Transitions section contains 'stay in brainstorm'."""
        content = _read_mode("brainstorm.md")
        transitions = _transitions_section(content)
        assert "stay in brainstorm" in transitions, (
            "brainstorm.md Transitions section: should contain 'stay in brainstorm' "
            "for the code exploration dynamic transition"
        )


# ---------------------------------------------------------------------------
# 4. TestTransitionProseConsistency
# ---------------------------------------------------------------------------


class TestTransitionProseConsistency:
    def test_no_invalid_transition_references(self) -> None:
        """For each mode, verify all name='X' in Transitions section are valid targets.

        Also verifies mode(operation='clear') only appears if allow_clear is true.
        """
        for filename in MODE_FILES:
            content = _read_mode(filename)
            fm = _parse_frontmatter(content)
            mode_name = fm["mode"]["name"]
            allowed = fm["mode"]["allowed_transitions"]
            allow_clear = fm["mode"]["allow_clear"]

            transitions_prose = _transitions_section(content)

            # Find all name='X' or name="X" references in the Transitions section
            referenced = re.findall(r"""name=['"]([\w-]+)['"]""", transitions_prose)

            for target in referenced:
                assert target in allowed, (
                    f"{filename} ({mode_name}): Transitions section references "
                    f"name='{target}' but it is NOT in allowed_transitions={allowed}"
                )

            # If allow_clear is false, mode(operation='clear') must not appear in transitions
            if not allow_clear:
                assert "mode(operation='clear')" not in transitions_prose, (
                    f"{filename} ({mode_name}): allow_clear=false but Transitions section "
                    "contains mode(operation='clear')"
                )


# ---------------------------------------------------------------------------
# 5. TestAgentInclusions
# ---------------------------------------------------------------------------


class TestAgentInclusions:
    def test_all_agents_include_common_agent_base(self) -> None:
        """All 5 agents contain '@foundation:context/shared/common-agent-base.md'."""
        for filename in AGENT_FILES:
            content = _read_agent(filename)
            assert "@foundation:context/shared/common-agent-base.md" in content, (
                f"{filename}: missing '@foundation:context/shared/common-agent-base.md'"
            )

    def test_all_agents_include_superpowers_philosophy(self) -> None:
        """All 5 agents contain '@superpowers:context/philosophy.md'."""
        for filename in AGENT_FILES:
            content = _read_agent(filename)
            assert "@superpowers:context/philosophy.md" in content, (
                f"{filename}: missing '@superpowers:context/philosophy.md'"
            )

    def test_execution_agents_have_scope_boundary(self) -> None:
        """implementer, spec-reviewer, code-quality-reviewer contain '## Scope Boundary'
        AND 'git push' AND 'gh pr create'.
        """
        for filename in EXECUTION_AGENTS:
            content = _read_agent(filename)
            assert "## Scope Boundary" in content, (
                f"{filename}: missing '## Scope Boundary' section"
            )
            assert "git push" in content, f"{filename}: Scope Boundary missing 'git push'"
            assert "gh pr create" in content, (
                f"{filename}: Scope Boundary missing 'gh pr create'"
            )

    def test_non_execution_agents_no_scope_boundary(self) -> None:
        """brainstormer and plan-writer do NOT contain '## Scope Boundary'."""
        non_execution = ["brainstormer.md", "plan-writer.md"]
        for filename in non_execution:
            content = _read_agent(filename)
            assert "## Scope Boundary" not in content, (
                f"{filename}: should NOT contain '## Scope Boundary' "
                "(non-execution agents don't need this)"
            )
