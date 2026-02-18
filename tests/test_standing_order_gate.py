"""Test that the standing order includes a step 0 check for active modes."""

from pathlib import Path

INSTRUCTIONS = Path(__file__).parent.parent / "context" / "instructions.md"


def read_instructions() -> str:
    return INSTRUCTIONS.read_text(encoding="utf-8")


class TestStandingOrderGate:
    """Fix 4: Standing order must check if a mode is already active."""

    def test_has_step_zero(self) -> None:
        content = read_instructions()
        assert "<STANDING-ORDER>" in content
        start = content.index("<STANDING-ORDER>")
        end = content.index("</STANDING-ORDER>")
        standing_order = content[start:end]
        assert "0." in standing_order, "STANDING-ORDER must have a step 0"

    def test_step_zero_mentions_mode_active(self) -> None:
        content = read_instructions()
        start = content.index("<STANDING-ORDER>")
        end = content.index("</STANDING-ORDER>")
        standing_order = content[start:end]
        assert "MODE ACTIVE" in standing_order

    def test_step_zero_says_do_not_reactivate(self) -> None:
        content = read_instructions()
        start = content.index("<STANDING-ORDER>")
        end = content.index("</STANDING-ORDER>")
        standing_order = content[start:end].lower()
        assert "re-activate" in standing_order or "already active" in standing_order

    def test_original_steps_still_present(self) -> None:
        content = read_instructions()
        start = content.index("<STANDING-ORDER>")
        end = content.index("</STANDING-ORDER>")
        standing_order = content[start:end]
        for step in ["1.", "2.", "3.", "4."]:
            assert step in standing_order, f"Step {step} must still be present"
