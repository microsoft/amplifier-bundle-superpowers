"""Verification tests for B3: Wire tool-mode into Superpowers Bundle.

Tests that:
1. bundle.md has tool-mode in a tools: section with gate_policy: "warn"
2. bundle.md hooks-mode config uses @superpowers:modes in search_paths
3. context/instructions.md mentions the mode tool
4. At least 3 mode files reference the mode tool in their transitions
5. All YAML frontmatter in bundle.md is valid
"""

import os
import re

import yaml
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
BUNDLE_MD = os.path.join(REPO_ROOT, "bundle.md")
INSTRUCTIONS_MD = os.path.join(REPO_ROOT, "context", "instructions.md")
MODES_DIR = os.path.join(REPO_ROOT, "modes")


def read_file(path: str) -> str:
    assert os.path.isfile(path), f"File does not exist: {path}"
    with open(path) as f:
        return f.read()


def extract_yaml_blocks(content: str) -> list[str]:
    """Extract YAML frontmatter blocks from markdown bundle files.

    bundle.md uses labeled YAML blocks (e.g. 'hooks:', 'tools:', 'skills:')
    at the top level, not fenced code blocks.
    """
    blocks = []
    current_block_lines = []
    in_yaml = False

    for line in content.splitlines():
        # Detect start of a YAML block: a top-level key like 'bundle:', 'hooks:', 'tools:', 'skills:', 'includes:'
        if re.match(r"^[a-z_]+:\s*$", line) or re.match(r"^[a-z_]+:\s*\S", line):
            if in_yaml and current_block_lines:
                blocks.append("\n".join(current_block_lines))
            current_block_lines = [line]
            in_yaml = True
        elif in_yaml:
            # YAML blocks continue with indented lines or blank lines
            if line.startswith("  ") or line.startswith("\t") or line.strip() == "":
                current_block_lines.append(line)
            elif line.startswith("- "):
                current_block_lines.append(line)
            else:
                # Non-indented, non-YAML line ends the block
                if current_block_lines:
                    blocks.append("\n".join(current_block_lines))
                current_block_lines = []
                in_yaml = False

    if in_yaml and current_block_lines:
        blocks.append("\n".join(current_block_lines))

    return blocks


class TestBundleToolMode:
    """Tests for tool-mode wiring in bundle.md."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_file(BUNDLE_MD)

    def test_has_tools_section(self):
        """bundle.md must have a top-level tools: section."""
        assert re.search(r"^tools:", self.content, re.MULTILINE), (
            "Expected top-level 'tools:' section in bundle.md"
        )

    def test_has_tool_mode_module(self):
        """tools: section must reference tool-mode module."""
        assert "module: tool-mode" in self.content, (
            "Expected 'module: tool-mode' in bundle.md tools section"
        )

    def test_tool_mode_has_gate_policy_warn(self):
        """tool-mode config must include gate_policy: 'warn'."""
        assert re.search(r'gate_policy:\s*["\']?warn["\']?', self.content), (
            "Expected gate_policy: 'warn' in tool-mode config"
        )

    def test_tool_mode_has_source(self):
        """tool-mode must have a source pointing to amplifier-bundle-modes."""
        assert "amplifier-bundle-modes" in self.content, (
            "Expected amplifier-bundle-modes source reference for tool-mode"
        )
        assert "modules/tool-mode" in self.content, (
            "Expected modules/tool-mode subdirectory in source"
        )


class TestBundleHooksModeSearchPaths:
    """Tests for hooks-mode search_paths update."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_file(BUNDLE_MD)

    def test_search_paths_uses_at_superpowers_syntax(self):
        """hooks-mode search_paths must use @superpowers:modes syntax."""
        assert (
            '"@superpowers:modes"' in self.content
            or "'@superpowers:modes'" in self.content
        ), "Expected '@superpowers:modes' in hooks-mode search_paths"

    def test_search_paths_no_bare_modes(self):
        """hooks-mode search_paths should not use bare 'modes' path."""
        # Find the hooks-mode config section and check it doesn't use bare 'modes'
        hooks_match = re.search(
            r"hooks:.*?(?=^[a-z]|\Z)", self.content, re.MULTILINE | re.DOTALL
        )
        assert hooks_match, "Expected hooks: section in bundle.md"
        hooks_section = hooks_match.group()
        # The search_paths should not have a bare '- modes' line
        assert not re.search(r"^\s+- modes\s*$", hooks_section, re.MULTILINE), (
            "Expected search_paths to use '@superpowers:modes', not bare 'modes'"
        )


class TestInstructionsModeToolNote:
    """Tests for mode tool note in instructions.md."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_file(INSTRUCTIONS_MD)

    def test_mentions_mode_tool(self):
        """instructions.md must mention the mode tool."""
        assert "mode tool" in self.content.lower() or "`mode`" in self.content, (
            "Expected mention of mode tool in instructions.md"
        )

    def test_mentions_mode_tool_set_operation(self):
        """instructions.md or superpowers-reference skill must show mode() call syntax."""
        # After context trimming, mode() syntax moved to superpowers-reference skill.
        # instructions.md still references the mode tool conceptually.
        skill_path = os.path.join(
            REPO_ROOT, "skills", "superpowers-reference", "SKILL.md"
        )
        skill_content = ""
        if os.path.isfile(skill_path):
            with open(skill_path) as f:
                skill_content = f.read()
        assert "mode(" in self.content or "mode(" in skill_content, (
            "Expected mode() call syntax in instructions.md or superpowers-reference skill"
        )

    def test_mentions_gate_policy_behavior(self):
        """instructions.md or superpowers-reference skill should mention gate/blocking behavior."""
        # After context trimming, detailed mode tool docs moved to superpowers-reference skill.
        skill_path = os.path.join(
            REPO_ROOT, "skills", "superpowers-reference", "SKILL.md"
        )
        skill_content = ""
        if os.path.isfile(skill_path):
            with open(skill_path) as f:
                skill_content = f.read()
        combined = (self.content + skill_content).lower()
        assert (
            "blocked" in combined or "reminder" in combined or "confirm" in combined
        ), "Expected mention of gate/blocking/confirm behavior for mode tool"


class TestModeFilesTransitions:
    """Tests that mode files reference the mode tool in transitions."""

    MODE_FILES = [
        "brainstorm.md",
        "write-plan.md",
        "execute-plan.md",
        "debug.md",
        "verify.md",
        "finish.md",
    ]

    def _read_mode(self, filename: str) -> str:
        return read_file(os.path.join(MODES_DIR, filename))

    def _get_transitions_section(self, content: str) -> str:
        """Extract the Transitions section from a mode file."""
        match = re.search(r"## Transitions\b.*", content, re.DOTALL)
        assert match, "Expected '## Transitions' section in mode file"
        return match.group()

    def test_at_least_3_mode_files_reference_mode_tool(self):
        """At least 3 mode files must mention the mode tool in transitions."""
        count = 0
        for filename in self.MODE_FILES:
            content = self._read_mode(filename)
            transitions = self._get_transitions_section(content)
            if (
                "`mode` tool" in transitions
                or "mode tool" in transitions
                or "mode(" in transitions
            ):
                count += 1
        assert count >= 3, (
            f"Expected at least 3 mode files to reference mode tool in transitions, found {count}"
        )

    def test_brainstorm_transitions_mention_mode_tool(self):
        """brainstorm.md transitions should reference mode tool (explicit call or mention)."""
        content = self._read_mode("brainstorm.md")
        transitions = self._get_transitions_section(content)
        assert "`mode` tool" in transitions or "mode tool" in transitions or "mode(" in transitions, (
            "Expected brainstorm.md transitions to reference the mode tool"
        )

    def test_execute_plan_transitions_mention_mode_tool(self):
        """execute-plan.md transitions should reference mode tool (explicit call or mention)."""
        content = self._read_mode("execute-plan.md")
        transitions = self._get_transitions_section(content)
        assert "`mode` tool" in transitions or "mode tool" in transitions or "mode(" in transitions, (
            "Expected execute-plan.md transitions to reference the mode tool"
        )

    def test_verify_transitions_mention_mode_tool(self):
        """verify.md transitions should reference mode tool (explicit call or mention)."""
        content = self._read_mode("verify.md")
        transitions = self._get_transitions_section(content)
        assert "`mode` tool" in transitions or "mode tool" in transitions or "mode(" in transitions, (
            "Expected verify.md transitions to reference the mode tool"
        )


class TestYamlValidity:
    """Test that YAML blocks in bundle.md are valid."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        self.content = read_file(BUNDLE_MD)

    def test_yaml_blocks_parse(self):
        """All YAML blocks in bundle.md should parse without error."""
        blocks = extract_yaml_blocks(self.content)
        assert len(blocks) >= 3, (
            f"Expected at least 3 YAML blocks (bundle, hooks, tools, skills), found {len(blocks)}"
        )
        for i, block in enumerate(blocks):
            try:
                yaml.safe_load(block)
            except yaml.YAMLError as e:
                pytest.fail(f"YAML block {i} failed to parse:\n{block}\n\nError: {e}")
