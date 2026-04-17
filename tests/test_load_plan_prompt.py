"""Tests for the load-plan step prompt in subagent-driven-development.yaml.

Bug C (fixed in v4.0.3): LLMs wrap structured output in preamble + code fences.

Observed failure pattern from DTU run with v4.0.2 (Opus model):

    I've read the plan. It contains 2 simple tasks, both independent.
    Here's the extracted structured result:

    ```json
    {
      "tasks": [
        {
          "task_id": "task-1-hello",
          ...

parse_json: true cannot handle this — it fails on the preamble, producing
corrupted plan_data where tasks ends up as a list of strings instead of
dicts. The foreach then crashes with:
    "Cannot access 'task_id' on {{current_task}} - it's a str, not a dict"

The fix: add CRITICAL OUTPUT FORMAT instructions to the load-plan prompt
explicitly forbidding preamble and code fences.

These tests verify:
1. The prompt contains the required anti-preamble instructions (structural).
2. The validate-plan step catches the real-world malformed output patterns
   that the un-fixed prompt allowed through (behavioral — simulates Bug C).
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
# Part 1: Structural tests — the prompt MUST contain the anti-preamble block.
# These fail before the fix is applied (RED phase), pass after (GREEN phase).
# ─────────────────────────────────────────────────────────────────────────────


class TestLoadPlanPromptContainsCriticalFormatInstructions:
    """The load-plan prompt must include explicit anti-preamble instructions.

    Root cause of Bug C: models naturally add conversational preamble and
    wrap JSON in markdown code fences unless explicitly told not to.  Without
    these instructions even Opus produces output that parse_json: true cannot
    handle cleanly, resulting in tasks being deserialized as strings.
    """

    def _get_load_plan_prompt(self) -> str:
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "load-plan")
        assert step is not None, "load-plan step not found in task-execution stage"
        prompt = step.get("prompt")
        assert prompt is not None, "load-plan step has no 'prompt' field"
        return prompt

    def test_prompt_contains_critical_output_format_header(self):
        """Prompt must include the 'CRITICAL OUTPUT FORMAT' section header."""
        prompt = self._get_load_plan_prompt()
        assert "CRITICAL OUTPUT FORMAT" in prompt, (
            "load-plan prompt is missing the 'CRITICAL OUTPUT FORMAT' section.  "
            "Without it, LLMs (even Opus) add conversational preamble and code "
            "fences that parse_json: true cannot handle.  "
            "Add the anti-preamble block at the end of the load-plan prompt."
        )

    def test_prompt_forbids_preamble(self):
        """Prompt must explicitly forbid conversational preamble before the JSON."""
        prompt = self._get_load_plan_prompt()
        # Must mention preamble restriction in some form
        has_preamble_ban = (
            "Do NOT start with preamble" in prompt
            or "no preamble" in prompt.lower()
            or "without preamble" in prompt.lower()
        )
        assert has_preamble_ban, (
            "load-plan prompt must explicitly forbid preamble.  "
            "Observed Bug C: Opus responded with 'I've read the plan. "
            "Here's the extracted structured result:' before the JSON, "
            "which broke parse_json: true."
        )

    def test_prompt_forbids_code_fences(self):
        """Prompt must explicitly forbid markdown code fences around the JSON."""
        prompt = self._get_load_plan_prompt()
        has_fence_ban = (
            "```json" in prompt
            or "code fences" in prompt.lower()
            or "no ```" in prompt
            or "markdown" in prompt.lower()
        )
        assert has_fence_ban, (
            "load-plan prompt must explicitly forbid markdown code fences.  "
            "Observed Bug C: Opus wrapped the JSON in ```json ... ``` fences, "
            "which broke parse_json: true."
        )

    def test_prompt_requires_first_char_is_brace(self):
        """Prompt must state the response must start with '{' (not preamble text)."""
        prompt = self._get_load_plan_prompt()
        has_brace_requirement = (
            "first character" in prompt.lower() and "{" in prompt
        ) or (
            "must be `{`" in prompt
            or "must be '{'" in prompt
            or "starts with {" in prompt.lower()
            or "start with {" in prompt.lower()
        )
        assert has_brace_requirement, (
            "load-plan prompt must require the response to start with '{'.  "
            "This makes the output constraint concrete and machine-checkable."
        )

    def test_prompt_requires_json_loads_parseable(self):
        """Prompt must state output must be parseable by json.loads() without modification."""
        prompt = self._get_load_plan_prompt()
        assert "json.loads()" in prompt or "json.loads" in prompt, (
            "load-plan prompt must state the response must be parseable by "
            "json.loads() with no modifications.  This directly ties the "
            "prompt requirement to the mechanism that will fail if violated."
        )

    def test_prompt_provides_error_fallback(self):
        """Prompt must provide a fallback error JSON for when pure output isn't possible."""
        prompt = self._get_load_plan_prompt()
        # The fallback: {"error": "reason for failure"}
        has_error_fallback = (
            '"error"' in prompt and "reason for failure" in prompt
        ) or (
            '{"error":' in prompt
        )
        assert has_error_fallback, (
            "load-plan prompt must include a fallback error JSON response.  "
            "If the model truly cannot produce pure JSON it should signal failure "
            "with {\"error\": \"reason for failure\"} rather than returning "
            "unparseable mixed content."
        )

    def test_prompt_format_block_is_at_end(self):
        """The CRITICAL OUTPUT FORMAT block must appear after the content instructions.

        Placing it at the end gives it maximum recency weight — LLMs tend to
        follow the most recent instruction most faithfully.
        """
        prompt = self._get_load_plan_prompt()
        important_idx = prompt.find("IMPORTANT: Preserve ALL spec details")
        critical_idx = prompt.find("CRITICAL OUTPUT FORMAT")
        assert important_idx != -1, (
            "IMPORTANT: Preserve ALL spec details not found in prompt"
        )
        assert critical_idx != -1, (
            "CRITICAL OUTPUT FORMAT section not found in prompt"
        )
        assert important_idx < critical_idx, (
            "CRITICAL OUTPUT FORMAT block must come AFTER the content instructions "
            "(after 'IMPORTANT: Preserve ALL spec details...').  "
            "Recency matters — put the format constraint last so it's freshest."
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
# Part 3: Version guard — confirms the version was bumped to 4.0.3.
# ─────────────────────────────────────────────────────────────────────────────


class TestRecipeVersion:
    """Recipe version must be bumped to 4.0.3 with this fix."""

    def test_version_is_4_0_3(self):
        """Recipe version must be '4.0.3' (Bug C fix bump from 4.0.2)."""
        recipe = load_recipe()
        version = recipe.get("version")
        assert version == "4.0.3", (
            f"Recipe version must be '4.0.3' after the Bug C fix, got {version!r}.  "
            "Bump the version field from 4.0.2 to 4.0.3."
        )
