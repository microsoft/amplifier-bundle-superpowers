"""Tests for the load-plan step prompt in subagent-driven-development.yaml.

History:
- v4.0.2: Bug C observed — LLMs wrap structured output in preamble + code fences.
- v4.0.3: Workaround added — CRITICAL OUTPUT FORMAT block explicitly forbade preamble
  and code fences in the load-plan prompt.
- v4.0.4: Workaround removed — the upstream recipe engine bug is fixed (PR #25,
  amplifier-module-loop-streaming, commit 54e6f4c).  The root cause was
  _extract_text_from_content using hasattr(block, "text") which let
  ThinkingContent blocks leak into the response string, corrupting the
  downstream parse_json extraction.  With the fix in place the prompt no
  longer needs to carry duct tape about output format.

These tests verify:
1. The CRITICAL OUTPUT FORMAT workaround is ABSENT (regression guard — ensures
   the duct tape stays off now that the root cause is fixed upstream).
2. The validate-plan step catches the real-world malformed output patterns that
   the un-fixed prompt allowed through (behavioral — simulates Bug C).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

RECIPES_DIR = Path(__file__).parent.parent / "recipes"
SUBAGENT_RECIPE = RECIPES_DIR / "subagent-driven-development.yaml"

# ─────────────────────────────────────────────────────────────────────────────
# Helpers shared with test_validate_plan.py (duplicated intentionally to keep
# each test file self-contained and independently runnable).
# ─────────────────────────────────────────────────────────────────────────────


def load_recipe() -> dict:
    return yaml.safe_load(SUBAGENT_RECIPE.read_text())


def get_task_execution_steps() -> list:
    recipe = load_recipe()
    for stage in recipe["stages"]:
        if stage["name"] == "task-execution":
            return stage["steps"]
    raise AssertionError("task-execution stage not found in recipe")


def get_step_by_id(steps: list, step_id: str) -> dict | None:
    for step in steps:
        if step.get("id") == step_id:
            return step
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Validation script — mirrors the Python logic embedded in the validate-plan
# bash step's heredoc.  Kept in sync so these behavioral tests reflect what
# actually runs inside the recipe.
# ─────────────────────────────────────────────────────────────────────────────
VALIDATION_SCRIPT = """\
import json, sys, os

raw = os.environ.get("PLAN_DATA", "null")
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"ERROR: plan_data is not valid JSON: {e}", file=sys.stderr)
    print(f"Raw plan_data (first 500 chars): {raw[:500]}", file=sys.stderr)
    sys.exit(1)

if not isinstance(data, dict) or "tasks" not in data:
    print("ERROR: plan_data must be a dict with a 'tasks' key", file=sys.stderr)
    print(f"  type: {type(data).__name__}", file=sys.stderr)
    if isinstance(data, dict):
        print(f"  keys: {list(data.keys())}", file=sys.stderr)
    print(f"  value (first 500 chars): {json.dumps(data)[:500]}", file=sys.stderr)
    sys.exit(1)

tasks = data["tasks"]
if not isinstance(tasks, list):
    print(f"ERROR: plan_data.tasks must be a list, got {type(tasks).__name__}", file=sys.stderr)
    sys.exit(1)

if len(tasks) == 0:
    print("ERROR: plan_data.tasks is empty - no tasks found in plan", file=sys.stderr)
    sys.exit(1)

REQUIRED = {"task_id", "description", "spec", "acceptance_criteria", "files"}
for i, task in enumerate(tasks):
    if not isinstance(task, dict):
        print(f"ERROR: plan_data.tasks[{i}] is {type(task).__name__}, not a dict", file=sys.stderr)
        print(f"  value: {repr(task)}", file=sys.stderr)
        print(f"  full tasks: {json.dumps(tasks)}", file=sys.stderr)
        sys.exit(1)
    missing = REQUIRED - set(task.keys())
    if missing:
        tid = task.get("task_id", "UNKNOWN")
        print(f"ERROR: plan_data.tasks[{i}] (task_id={tid!r}) missing keys: {sorted(missing)}", file=sys.stderr)
        print(f"  keys found: {sorted(task.keys())}", file=sys.stderr)
        print(f"  task: {json.dumps(task)}", file=sys.stderr)
        sys.exit(1)

print(f"plan_data validated: {len(tasks)} task(s) ready for execution")
"""


def run_validation_with_raw_string(raw_plan_data: str) -> subprocess.CompletedProcess:
    """Run the validation script with a raw string injected as PLAN_DATA.

    This lets us test exactly what happens when parse_json: true produces a
    corrupted value (e.g. it attempted JSON extraction from a preamble+fence
    response and got a garbled result).
    """
    env = os.environ.copy()
    env["PLAN_DATA"] = raw_plan_data
    return subprocess.run(
        [sys.executable, "-"],
        input=VALIDATION_SCRIPT.encode(),
        env=env,
        capture_output=True,
        timeout=10,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Regression guard — the CRITICAL OUTPUT FORMAT workaround must NOT be
# present in the load-plan prompt.
#
# The workaround was added in v4.0.3 to compensate for a recipe engine bug
# where thinking-block content leaked into parse_json input.  That bug is fixed
# upstream (PR #25, amplifier-module-loop-streaming, commit 54e6f4c).
# These tests guard against the workaround being re-introduced.
# ─────────────────────────────────────────────────────────────────────────────


class TestCriticalOutputFormatWorkaroundIsAbsent:
    """Regression guard: the CRITICAL OUTPUT FORMAT workaround must NOT appear
    in the load-plan prompt.

    The workaround block was added in v4.0.3 (commit 60b0c07) to compensate for
    a bug in amplifier-module-loop-streaming where thinking-block content leaked
    into the response string via hasattr(block, 'text') type confusion between
    content_models.ThinkingContent and message_models.ThinkingBlock.  That bug
    is fixed upstream (PR #25, commit 54e6f4c).

    Duct tape that stays becomes architecture.  These tests ensure it stays
    removed now that the root cause is fixed.
    """

    def _get_load_plan_prompt(self) -> str:
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "load-plan")
        assert step is not None, "load-plan step not found in task-execution stage"
        prompt = step.get("prompt")
        assert prompt is not None, "load-plan step has no 'prompt' field"
        return prompt

    def test_prompt_does_not_contain_critical_output_format_header(self):
        """The 'CRITICAL OUTPUT FORMAT' workaround block must be absent from the load-plan prompt.

        This was the duct tape added in v4.0.3 to work around thinking-block
        leakage in the recipe engine.  With the upstream fix in place the
        workaround is unnecessary and must stay removed.
        """
        prompt = self._get_load_plan_prompt()
        assert "CRITICAL OUTPUT FORMAT" not in prompt, (
            "load-plan prompt still contains 'CRITICAL OUTPUT FORMAT' — this is the "
            "v4.0.3 workaround that was removed in v4.0.4.  The upstream recipe "
            "engine bug (thinking-block leakage via hasattr(block, 'text')) is fixed "
            "(PR #25 amplifier-module-loop-streaming, commit 54e6f4c).  "
            "Remove the full CRITICAL OUTPUT FORMAT block from the load-plan prompt."
        )

    def test_prompt_does_not_contain_preamble_ban(self):
        """The explicit 'Do NOT start with preamble' instruction must be absent.

        This line was part of the CRITICAL OUTPUT FORMAT workaround block.  With
        the upstream fix the recipe engine correctly filters thinking blocks before
        parse_json runs, so the symptom-level instruction is no longer needed.
        """
        prompt = self._get_load_plan_prompt()
        assert "Do NOT start with preamble" not in prompt, (
            "load-plan prompt contains 'Do NOT start with preamble' — this is part "
            "of the v4.0.3 workaround removed in v4.0.4.  Remove the full "
            "CRITICAL OUTPUT FORMAT block from the load-plan prompt."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Behavioral tests — validate-plan catches Bug C's failure patterns.
#
# These simulate what happened during the DTU run:
#   - LLM returned preamble + ``json fence + JSON content + closing fence
#   - parse_json: true couldn't parse the full string as JSON
#   - Its fallback produced a string or a dict with tasks as a list of strings
#   - The foreach crashed with "Cannot access 'task_id' on str, not a dict"
#
# We cannot unit-test LLM output directly, but we CAN test that the
# validate-plan step (Bug B's fix) correctly intercepts the malformed values
# that Bug C's unfixed prompt would have allowed through.
# ─────────────────────────────────────────────────────────────────────────────


# What the DTU run actually observed coming out of the plan-writer agent:
PREAMBLE_AND_FENCE_RESPONSE = """\
I've read the plan. It contains 2 simple tasks, both independent. Here's the extracted structured result:

```json
{
  "tasks": [
    {
      "task_id": "task-1-hello",
      "description": "Print hello world",
      "spec": "A script that prints hello world",
      "acceptance_criteria": "Script outputs hello world",
      "files": ["hello.py"],
      "dependencies": []
    },
    {
      "task_id": "task-2-goodbye",
      "description": "Print goodbye world",
      "spec": "A script that prints goodbye world",
      "acceptance_criteria": "Script outputs goodbye world",
      "files": ["goodbye.py"],
      "dependencies": []
    }
  ],
  "total_tasks": 2
}
```
"""


class TestValidatePlanCatchesBugCOutputPatterns:
    """validate-plan must catch the malformed output patterns produced by Bug C.

    These tests document the precise failure mode observed in the DTU run and
    confirm that validate-plan (Bug B's fix) catches it before foreach runs,
    giving a clear error instead of the opaque 'Cannot access task_id on str'.
    """

    def test_raw_preamble_fence_response_is_not_valid_json(self):
        """The exact LLM output observed in the DTU run must NOT be valid JSON.

        This confirms the root cause: parse_json: true receives a string that
        cannot be decoded as-is, so it falls back to some form of string/partial
        extraction that corrupts plan_data.tasks.
        """
        try:
            json.loads(PREAMBLE_AND_FENCE_RESPONSE)
            assert False, (
                "PREAMBLE_AND_FENCE_RESPONSE was parsed as valid JSON — it should "
                "NOT be.  The test fixture is wrong; it must contain preamble text "
                "before the JSON that makes json.loads() raise JSONDecodeError."
            )
        except json.JSONDecodeError:
            pass  # Expected — the preamble makes it invalid JSON

    def test_validate_plan_catches_tasks_as_raw_strings(self):
        """validate-plan must reject plan_data where tasks are strings.

        This is the corrupted state that Bug C's unfixed prompt produced:
        parse_json: true couldn't parse the full preamble+fence response, so
        its fallback produced something like {"tasks": ["task-1-hello", ...]},
        treating each task JSON object as a raw string.
        """
        # Simulate the corrupted plan_data that parse_json fallback produced
        corrupted_plan_data = json.dumps({
            "tasks": [
                "task-1-hello",
                "task-2-goodbye",
            ],
            "total_tasks": 2,
        })
        result = run_validation_with_raw_string(corrupted_plan_data)
        assert result.returncode != 0, (
            "validate-plan must fail (non-zero exit) when tasks are strings.  "
            "This is the exact corruption Bug C caused: parse_json: true couldn't "
            "parse the preamble+fence response and fell back to extracting task "
            "names as strings.  validate-plan is the safety net."
        )

    def test_validate_plan_error_identifies_string_type(self):
        """The error message must say tasks[0] is a str, not a dict."""
        corrupted_plan_data = json.dumps({
            "tasks": ["task-1-hello", "task-2-goodbye"],
            "total_tasks": 2,
        })
        result = run_validation_with_raw_string(corrupted_plan_data)
        stderr = result.stderr.decode()
        assert "str" in stderr.lower() or "dict" in stderr.lower(), (
            f"Error must identify the type mismatch (str vs dict).  Got: {stderr!r}"
        )
        assert "tasks[0]" in stderr, (
            f"Error must identify the malformed index (tasks[0]).  Got: {stderr!r}"
        )

    def test_validate_plan_catches_entire_response_as_string(self):
        """validate-plan must reject plan_data that is a single string (full LLM response).

        Worst-case fallback: parse_json: true stores the entire raw response
        string as plan_data (not even a dict).  validate-plan catches this
        before it reaches foreach.
        """
        # Worst case: plan_data IS the raw LLM response string
        result = run_validation_with_raw_string(
            json.dumps(PREAMBLE_AND_FENCE_RESPONSE)
        )
        assert result.returncode != 0, (
            "validate-plan must fail when plan_data is a string (the full LLM "
            "response), not a dict.  This is the most extreme fallback of "
            "parse_json: true storing the raw string in plan_data."
        )

    def test_validate_plan_catches_plan_data_missing_tasks_key(self):
        """validate-plan must reject a plan_data dict that has no 'tasks' key.

        Another corruption pattern: parse_json: true extracts a partial object
        from inside the code fence but loses the outer structure, producing
        something like the first task object directly (no 'tasks' wrapper).
        """
        # Simulate partial extraction: got the first task object, lost the wrapper
        result = run_validation_with_raw_string(json.dumps({
            "task_id": "task-1-hello",
            "description": "Print hello world",
            "spec": "A script",
            "acceptance_criteria": "Works",
            "files": ["hello.py"],
        }))
        assert result.returncode != 0, (
            "validate-plan must fail when plan_data is missing the 'tasks' key.  "
            "This can happen when parse_json: true extracts a single task object "
            "from inside a code fence instead of the outer wrapper object."
        )
        stderr = result.stderr.decode()
        assert "tasks" in stderr.lower(), (
            f"Error must mention the expected 'tasks' key.  Got: {stderr!r}"
        )

    def test_well_formed_plan_data_still_passes(self):
        """Sanity check: correctly formed plan_data must still pass validate-plan.

        The fix must not break the happy path.  If the load-plan prompt works
        as intended (after Bug C is fixed), validate-plan must let it through.
        """
        good_plan_data = json.dumps({
            "tasks": [
                {
                    "task_id": "task-1-hello",
                    "description": "Print hello world",
                    "spec": "A script that prints hello world to stdout",
                    "acceptance_criteria": "Running python hello.py outputs 'hello world'",
                    "files": ["hello.py", "tests/test_hello.py"],
                    "dependencies": [],
                }
            ],
            "total_tasks": 1,
        })
        result = run_validation_with_raw_string(good_plan_data)
        assert result.returncode == 0, (
            f"validate-plan must pass for well-formed plan_data (the happy path).  "
            f"exit={result.returncode}, stderr={result.stderr.decode()!r}"
        )
        stdout = result.stdout.decode()
        assert "validated" in stdout.lower() or "ready" in stdout.lower(), (
            f"Success message must confirm validation passed.  Got: {stdout!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Version guard — confirms the version was bumped to 4.0.4.
# ─────────────────────────────────────────────────────────────────────────────


class TestRecipeVersion:
    """Recipe version must be bumped to 4.0.4 with this fix."""

    def test_version_is_4_0_4(self):
        """Recipe version must be '4.0.4' (workaround removal bump from 4.0.3)."""
        recipe = load_recipe()
        version = recipe.get("version")
        assert version == "4.0.4", (
            f"Recipe version must be '4.0.4' after removing the CRITICAL OUTPUT FORMAT "
            f"workaround, got {version!r}.  Bump the version field from 4.0.3 to 4.0.4."
        )
