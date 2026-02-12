"""Test that README.md documents all 6 workflow modes consistently."""

from pathlib import Path

README = Path(__file__).parent.parent / "README.md"


def read_readme():
    return README.read_text()


def test_feature_count_says_6_modes():
    """The 'What This Bundle Provides' section should say '6 workflow modes'."""
    content = read_readme()
    assert "6 workflow modes" in content, (
        "Expected '6 workflow modes' in What This Bundle Provides section"
    )


def test_modes_section_says_six():
    """The Modes section heading text should say 'six workflow modes'."""
    content = read_readme()
    assert "six workflow modes" in content.lower(), (
        "Expected 'six workflow modes' in Modes section description"
    )


def test_modes_table_has_all_6_modes():
    """The modes table should list all 6 modes."""
    content = read_readme()
    required_modes = [
        "brainstorm",
        "write-plan",
        "execute-plan",
        "debug",
        "verify",
        "finish",
    ]
    # Look for each mode in table rows (lines starting with |)
    table_lines = [line for line in content.splitlines() if line.startswith("|")]
    table_text = "\n".join(table_lines)
    for mode in required_modes:
        assert f"`{mode}`" in table_text, f"Mode '{mode}' not found in modes table"


def test_bundle_structure_shows_all_6_mode_files():
    """The bundle structure diagram should show all 6 mode files."""
    content = read_readme()
    required_files = [
        "brainstorm.md",
        "write-plan.md",
        "execute-plan.md",
        "debug.md",
        "verify.md",
        "finish.md",
    ]
    # Find the bundle structure section
    structure_start = content.find("## Bundle Structure")
    assert structure_start != -1, "Bundle Structure section not found"
    structure_section = content[structure_start:]

    for f in required_files:
        assert f in structure_section, (
            f"Mode file '{f}' not found in Bundle Structure diagram"
        )
