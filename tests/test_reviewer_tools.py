"""Test that reviewer agents have tool-bash, python_check, and verification instructions."""

from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / "agents"
SPEC_REVIEWER = AGENTS_DIR / "spec-reviewer.md"
CODE_QUALITY_REVIEWER = AGENTS_DIR / "code-quality-reviewer.md"


def _read_frontmatter_tools(filepath: Path) -> str:
    """Extract the tools section from YAML frontmatter."""
    content = filepath.read_text()
    # Frontmatter is between the first and second '---' lines
    parts = content.split("---")
    if len(parts) < 3:
        return ""
    return parts[1]  # The YAML frontmatter content


def _read_body(filepath: Path) -> str:
    """Extract the markdown body (after frontmatter)."""
    content = filepath.read_text()
    parts = content.split("---")
    if len(parts) < 3:
        return content
    return "---".join(parts[2:])  # Everything after frontmatter


class TestSpecReviewerTools:
    def test_has_tool_bash_in_frontmatter(self):
        """spec-reviewer.md must have tool-bash in its tools list."""
        frontmatter = _read_frontmatter_tools(SPEC_REVIEWER)
        assert "tool-bash" in frontmatter, (
            "tool-bash not found in spec-reviewer.md frontmatter tools list"
        )

    def test_has_python_check_in_frontmatter(self):
        """spec-reviewer.md must have tool-python-check in its tools list."""
        frontmatter = _read_frontmatter_tools(SPEC_REVIEWER)
        assert "tool-python-check" in frontmatter, (
            "tool-python-check not found in spec-reviewer.md frontmatter tools list"
        )

    def test_has_verification_instructions(self):
        """spec-reviewer.md must instruct reviewer to run the test suite."""
        body = _read_body(SPEC_REVIEWER)
        assert "Run the project's test suite" in body, (
            "Verification instructions not found in spec-reviewer.md body"
        )

    def test_has_independent_verification_instruction(self):
        """spec-reviewer.md must say not to trust implementer's claims."""
        body = _read_body(SPEC_REVIEWER)
        assert (
            "Do NOT trust the implementer" in body
            or "Do NOT trust the implementer's claim" in body
        ), "Independent verification instruction not found in spec-reviewer.md body"


class TestCodeQualityReviewerTools:
    def test_has_tool_bash_in_frontmatter(self):
        """code-quality-reviewer.md must have tool-bash in its tools list."""
        frontmatter = _read_frontmatter_tools(CODE_QUALITY_REVIEWER)
        assert "tool-bash" in frontmatter, (
            "tool-bash not found in code-quality-reviewer.md frontmatter tools list"
        )

    def test_has_python_check_in_frontmatter(self):
        """code-quality-reviewer.md must have tool-python-check in its tools list."""
        frontmatter = _read_frontmatter_tools(CODE_QUALITY_REVIEWER)
        assert "tool-python-check" in frontmatter, (
            "tool-python-check not found in code-quality-reviewer.md frontmatter tools list"
        )

    def test_has_verification_instructions(self):
        """code-quality-reviewer.md must instruct reviewer to run the test suite."""
        body = _read_body(CODE_QUALITY_REVIEWER)
        assert "Run the project's test suite" in body, (
            "Verification instructions not found in code-quality-reviewer.md body"
        )

    def test_has_independent_verification_instruction(self):
        """code-quality-reviewer.md must say not to trust implementer's claims."""
        body = _read_body(CODE_QUALITY_REVIEWER)
        assert (
            "Do NOT trust the implementer" in body
            or "Do NOT trust the implementer's claim" in body
        ), (
            "Independent verification instruction not found in code-quality-reviewer.md body"
        )
