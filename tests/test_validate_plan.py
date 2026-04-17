"""Tests for the validate-plan step in subagent-driven-development.yaml.

TDD: The structural tests below (TestValidatePlanStepExistsInRecipe) are written
BEFORE the validate-plan step exists — they should FAIL until the step is added.

The behavioral tests (TestValidatePlanBashLogic) test the validation logic directly
via subprocess. They demonstrate:
  - Malformed input (tasks as strings, missing keys, empty list) → exits non-zero
    with a clear, specific error message naming the problem.
  - Well-formed input → exits 0 with a success message.

Real-world failure this prevents:
  plan-writer returned tasks as a list of strings instead of dicts.
  The foreach on plan_data.tasks immediately crashed with the opaque:
    "Cannot access 'task_id' on {{current_task}} - it's a str, not a dict."
  With validate-plan, the same malformed output now produces:
    "ERROR: plan_data.tasks[0] is str, not a dict"
  ...before the foreach ever runs.
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
# Validation script — must match the Python logic embedded in the
# validate-plan bash step's heredoc.
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

# A well-formed task object (all required fields present)
VALID_TASK = {
    "task_id": "task-1",
    "description": "Implement the feature",
    "spec": "The feature should do X, Y, Z per the requirements.",
    "acceptance_criteria": "All tests pass; feature works end-to-end.",
    "files": ["src/feature.py", "tests/test_feature.py"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
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


def run_validation(plan_data: dict) -> subprocess.CompletedProcess:
    """Run the validation script with plan_data injected via PLAN_DATA env var.

    This mirrors how the bash step works: the recipe engine JSON-serialises
    plan_data into the PLAN_DATA environment variable, and the Python script
    reads and validates it.
    """
    env = os.environ.copy()
    env["PLAN_DATA"] = json.dumps(plan_data)
    return subprocess.run(
        [sys.executable, "-"],
        input=VALIDATION_SCRIPT.encode(),
        env=env,
        capture_output=True,
        timeout=10,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Structural tests — these FAIL before validate-plan step is added (RED phase)
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatePlanStepExistsInRecipe:
    """The recipe must have a validate-plan step after load-plan."""

    def test_validate_plan_step_exists(self):
        """validate-plan step must be present in the task-execution stage."""
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "validate-plan")
        assert step is not None, (
            "validate-plan step not found in task-execution stage. "
            "Add a bash validation step after load-plan to catch malformed plan_data "
            "before the foreach iterates. Without it, malformed tasks produce the opaque "
            "error: \"Cannot access 'task_id' on {{current_task}} - it's a str, not a dict.\""
        )

    def test_validate_plan_is_bash_type(self):
        """validate-plan must be a bash step (deterministic, no LLM needed)."""
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "validate-plan")
        assert step is not None, "validate-plan step not found"
        assert step.get("type") == "bash", (
            f"validate-plan must be type='bash', got type={step.get('type')!r}"
        )

    def test_validate_plan_comes_after_load_plan(self):
        """validate-plan must appear AFTER load-plan (validates what load-plan produced)."""
        steps = get_task_execution_steps()
        ids = [s.get("id") for s in steps]
        assert "load-plan" in ids, "load-plan step not found in recipe"
        assert "validate-plan" in ids, "validate-plan step not found in recipe"
        assert ids.index("load-plan") < ids.index("validate-plan"), (
            "validate-plan must come AFTER load-plan — it validates what load-plan produced"
        )

    def test_validate_plan_comes_before_per_task_pipeline(self):
        """validate-plan must appear BEFORE per-task-pipeline (blocks malformed input early)."""
        steps = get_task_execution_steps()
        ids = [s.get("id") for s in steps]
        assert "validate-plan" in ids, "validate-plan step not found in recipe"
        assert "per-task-pipeline" in ids, "per-task-pipeline step not found in recipe"
        assert ids.index("validate-plan") < ids.index("per-task-pipeline"), (
            "validate-plan must come BEFORE per-task-pipeline "
            "— it must block malformed data BEFORE the foreach runs"
        )

    def test_validate_plan_uses_plan_data_env_var(self):
        """validate-plan must receive plan_data via PLAN_DATA environment variable."""
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "validate-plan")
        assert step is not None, "validate-plan step not found"
        env = step.get("env") or {}
        assert "PLAN_DATA" in env, (
            "validate-plan step must have PLAN_DATA in its env field to receive plan_data. "
            "The recipe engine JSON-serialises {{plan_data}} into this env var."
        )
        assert "plan_data" in env["PLAN_DATA"], (
            f"validate-plan PLAN_DATA env value must reference {{{{plan_data}}}}, "
            f"got {env['PLAN_DATA']!r}"
        )

    def test_validate_plan_has_short_timeout(self):
        """validate-plan is pure Python validation — must have a short timeout (≤60s)."""
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "validate-plan")
        assert step is not None, "validate-plan step not found"
        timeout = step.get("timeout")
        assert timeout is not None, "validate-plan must have an explicit timeout"
        assert timeout <= 60, (
            f"validate-plan timeout should be ≤60s (fast in-process validation), "
            f"got {timeout}s"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Behavioral tests — run the validation Python logic directly via subprocess.
# These demonstrate the error messages users will see.
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatePlanBashLogicMalformedInput:
    """Malformed plan_data must produce non-zero exit and a clear, specific error."""

    def test_tasks_as_strings_exits_nonzero(self):
        """Real-world failure: plan-writer returns tasks as strings, not dicts.

        Current (broken) behaviour without validate-plan:
            foreach crashes immediately with opaque error
            "Cannot access 'task_id' on current_task - it's a str, not a dict."

        Expected (fixed) behaviour with validate-plan:
            exits 1 with clear message naming the problem before foreach runs.
        """
        result = run_validation(
            {
                "tasks": [
                    "task 1: implement foo",
                    "task 2: implement bar",
                ],
                "total_tasks": 2,
            }
        )
        assert result.returncode != 0, (
            "Validation MUST fail (non-zero exit) when tasks are strings, not dicts. "
            f"Got exit code 0. stderr: {result.stderr.decode()!r}"
        )

    def test_tasks_as_strings_error_names_index_and_type(self):
        """Error must identify WHICH task is wrong and WHAT is wrong with it."""
        result = run_validation(
            {
                "tasks": ["task 1: implement foo", "task 2: implement bar"],
                "total_tasks": 2,
            }
        )
        stderr = result.stderr.decode()
        assert "ERROR" in stderr, f"Error output must contain 'ERROR'. Got: {stderr!r}"
        assert "tasks[0]" in stderr, (
            f"Error must identify the malformed task by index (tasks[0]). Got: {stderr!r}"
        )
        # Must mention the type mismatch
        assert "str" in stderr.lower() or "dict" in stderr.lower(), (
            f"Error must mention the type mismatch (str vs dict). Got: {stderr!r}"
        )

    def test_missing_required_keys_exits_nonzero(self):
        """A task missing required keys must fail validation."""
        result = run_validation(
            {
                "tasks": [{"task_id": "t1", "description": "only two keys here"}],
                "total_tasks": 1,
            }
        )
        assert result.returncode != 0, (
            "Validation must fail when a task is missing required keys. "
            f"Got exit code 0. stderr: {result.stderr.decode()!r}"
        )

    def test_missing_required_keys_error_names_task_and_missing_fields(self):
        """Error for missing keys must name the task_id and the missing field names."""
        result = run_validation(
            {
                "tasks": [{"task_id": "task-alpha", "description": "only description"}],
                "total_tasks": 1,
            }
        )
        stderr = result.stderr.decode()
        assert "ERROR" in stderr
        # Must identify which task
        assert "task-alpha" in stderr, (
            f"Error must name the task_id 'task-alpha'. Got: {stderr!r}"
        )
        # Must name at least one of the missing required keys
        missing_mentioned = any(k in stderr for k in ["spec", "acceptance_criteria", "files"])
        assert missing_mentioned, (
            f"Error must name at least one missing required key "
            f"(spec, acceptance_criteria, files). Got: {stderr!r}"
        )

    def test_empty_tasks_list_exits_nonzero(self):
        """An empty tasks list must fail validation — there's nothing to execute."""
        result = run_validation({"tasks": [], "total_tasks": 0})
        assert result.returncode != 0, (
            "Validation must fail when tasks list is empty."
        )

    def test_empty_tasks_list_error_is_clear(self):
        """Error for empty tasks must say the list is empty."""
        result = run_validation({"tasks": [], "total_tasks": 0})
        stderr = result.stderr.decode()
        assert "empty" in stderr.lower() or "no tasks" in stderr.lower(), (
            f"Error for empty tasks must say 'empty' or 'no tasks'. Got: {stderr!r}"
        )

    def test_tasks_not_a_list_exits_nonzero(self):
        """Validation must fail if tasks is a dict instead of a list."""
        result = run_validation(
            {"tasks": {"task_id": "t1", "description": "wrong shape"}, "total_tasks": 1}
        )
        assert result.returncode != 0, (
            "Validation must fail if tasks is a dict, not a list."
        )

    def test_no_tasks_key_exits_nonzero(self):
        """Validation must fail if plan_data has no 'tasks' key at all."""
        result = run_validation({"items": [], "count": 0})
        assert result.returncode != 0, (
            "Validation must fail if plan_data has no 'tasks' key."
        )

    def test_no_tasks_key_error_mentions_tasks(self):
        """Error for missing tasks key must tell the user what key is expected."""
        result = run_validation({"items": [], "count": 0})
        stderr = result.stderr.decode()
        assert "tasks" in stderr.lower(), (
            f"Error must mention the expected 'tasks' key. Got: {stderr!r}"
        )


class TestValidatePlanBashLogicValidInput:
    """Well-formed plan_data must pass validation with exit code 0."""

    def test_single_valid_task_exits_zero(self):
        """A single valid task must pass validation."""
        result = run_validation({"tasks": [VALID_TASK], "total_tasks": 1})
        assert result.returncode == 0, (
            f"Valid task should pass validation. "
            f"Exit: {result.returncode}, stderr: {result.stderr.decode()!r}"
        )

    def test_multiple_valid_tasks_exits_zero(self):
        """Multiple valid tasks must all pass validation."""
        tasks = [{**VALID_TASK, "task_id": f"task-{i}"} for i in range(3)]
        result = run_validation({"tasks": tasks, "total_tasks": 3})
        assert result.returncode == 0, (
            f"Multiple valid tasks should pass validation. "
            f"Exit: {result.returncode}, stderr: {result.stderr.decode()!r}"
        )

    def test_valid_task_success_message_includes_count(self):
        """Success output must tell the user how many tasks are ready."""
        result = run_validation({"tasks": [VALID_TASK], "total_tasks": 1})
        stdout = result.stdout.decode()
        assert "1" in stdout, (
            f"Success message must include the task count. Got: {stdout!r}"
        )
        # Should be a positive confirmation, not an error
        assert "validated" in stdout.lower() or "ready" in stdout.lower(), (
            f"Success message must confirm validation passed. Got: {stdout!r}"
        )

    def test_valid_task_with_empty_files_list_exits_zero(self):
        """Tasks with files=[] (empty list) should still pass — files key is present."""
        task = {**VALID_TASK, "files": []}
        result = run_validation({"tasks": [task], "total_tasks": 1})
        assert result.returncode == 0, (
            f"Task with empty files list should pass (key is present). "
            f"Exit: {result.returncode}, stderr: {result.stderr.decode()!r}"
        )

    def test_valid_task_with_extra_fields_exits_zero(self):
        """Tasks with extra fields beyond the required set should also pass."""
        task = {**VALID_TASK, "dependencies": ["task-0"], "priority": "high"}
        result = run_validation({"tasks": [task], "total_tasks": 1})
        assert result.returncode == 0, (
            f"Task with extra fields should pass validation (extra fields are OK). "
            f"Exit: {result.returncode}, stderr: {result.stderr.decode()!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Regression tests: the recipe command itself must actually invoke Python.
# These run the ACTUAL bash command extracted from the YAML file (not the
# Python script in isolation), which is the only way to catch the
# $AMPLIFIER_PYTHON silent-no-op bug and verify the python3 fix holds.
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatePlanRecipeCommandInvokesRealPython:
    """The ACTUAL bash command in the recipe must invoke Python, not silently pass.

    Root cause being tested: commit 68a40b6 used $AMPLIFIER_PYTHON to start the
    interpreter.  In a typical DTU/CI environment AMPLIFIER_PYTHON is unset, so
    the shell expanded the command to:

        - << 'PYEOF'
        ... python code ...
        PYEOF

    That is a bash no-op (`-` as a command reads stdin and discards it).  Exit
    code: 0.  Stdout: empty.  The heredoc was swallowed, Python never ran,
    and malformed plan_data sailed straight through into the foreach, which
    then exploded with the opaque "Cannot access 'task_id' on str" error.

    The fix is to use `python3` literally.  These tests run the command string
    from the YAML file directly under bash to confirm the fix holds end-to-end.
    """

    @staticmethod
    def _get_recipe_command() -> str:
        """Extract the bash command string from the validate-plan step."""
        steps = get_task_execution_steps()
        step = get_step_by_id(steps, "validate-plan")
        assert step is not None, "validate-plan step not found in recipe"
        command = step.get("command")
        assert command is not None, "validate-plan step has no 'command' field"
        return command

    @staticmethod
    def _run_recipe_command(plan_data: dict) -> "subprocess.CompletedProcess[bytes]":
        """Run the recipe command via bash with PLAN_DATA set and AMPLIFIER_PYTHON absent.

        Mirrors the DTU/CI environment where AMPLIFIER_PYTHON is not in PATH.
        """
        command = TestValidatePlanRecipeCommandInvokesRealPython._get_recipe_command()
        env = os.environ.copy()
        env["PLAN_DATA"] = json.dumps(plan_data)
        # Simulate an environment where AMPLIFIER_PYTHON is not set (DTU, CI, most dev boxes).
        env.pop("AMPLIFIER_PYTHON", None)
        return subprocess.run(
            ["bash", "-c", command],
            env=env,
            capture_output=True,
            timeout=15,
        )

    def test_recipe_command_starts_with_python3(self):
        """The first non-whitespace interpreter token in the command must be 'python3'.

        Guards against re-introducing a variable reference like $AMPLIFIER_PYTHON
        that would silently expand to nothing in environments where the var is unset.
        """
        command = self._get_recipe_command()
        first_line = command.strip().splitlines()[0].strip()
        assert first_line.startswith("python3 "), (
            f"validate-plan command must start with 'python3 ', got: {first_line!r}.  "
            "Using a variable like $AMPLIFIER_PYTHON silently becomes a no-op when the "
            "variable is unset, bypassing all validation."
        )

    def test_recipe_command_exits_zero_for_valid_input(self):
        """Running the full recipe bash command with valid input must exit 0.

        If Python is not invoked (the $AMPLIFIER_PYTHON no-op bug), bash exits 0
        but produces no stdout.  We check BOTH the exit code AND the output.
        """
        result = self._run_recipe_command({"tasks": [VALID_TASK], "total_tasks": 1})
        assert result.returncode == 0, (
            f"Recipe command failed for valid input.  "
            f"exit={result.returncode}, "
            f"stdout={result.stdout.decode()!r}, "
            f"stderr={result.stderr.decode()!r}.  "
            "Check that 'python3' is the interpreter — not a variable that may be unset."
        )

    def test_recipe_command_produces_python_output_for_valid_input(self):
        """The recipe command must write a success message to stdout.

        A silent exit 0 with no stdout is the fingerprint of the $AMPLIFIER_PYTHON
        no-op bug — the heredoc was swallowed without any Python running.
        """
        result = self._run_recipe_command({"tasks": [VALID_TASK], "total_tasks": 1})
        stdout = result.stdout.decode().strip()
        assert stdout, (
            f"Recipe command produced no stdout for valid input.  "
            f"exit={result.returncode}, stderr={result.stderr.decode()!r}.  "
            "Empty stdout means Python never ran — the command is a no-op.  "
            "The first line of the command must be 'python3 -', not '$AMPLIFIER_PYTHON -'."
        )
        assert "validated" in stdout.lower() or "ready" in stdout.lower(), (
            f"stdout doesn't look like Python validation output: {stdout!r}"
        )

    def test_recipe_command_exits_nonzero_for_tasks_as_strings(self):
        """The recipe command must exit non-zero when tasks are strings, not dicts.

        This is the exact real-world failure case from the DTU run.  If the command
        is a no-op, it exits 0 even for malformed input — masking the problem.
        Python must catch the type mismatch and exit 1.
        """
        malformed = {
            "tasks": ["task 1: implement foo", "task 2: implement bar"],
            "total_tasks": 2,
        }
        result = self._run_recipe_command(malformed)
        assert result.returncode != 0, (
            f"Recipe command must exit non-zero for tasks-as-strings input.  "
            f"Got exit code 0.  "
            f"stdout={result.stdout.decode()!r}, stderr={result.stderr.decode()!r}.  "
            "Exit 0 with malformed input means Python is NOT running — this is the "
            "$AMPLIFIER_PYTHON silent no-op bug.  Fix: use 'python3' literally."
        )
        stderr = result.stderr.decode()
        assert "str" in stderr.lower() or "dict" in stderr.lower() or "ERROR" in stderr, (
            f"stderr must mention the type mismatch.  Got: {stderr!r}"
        )

    def test_recipe_command_exits_nonzero_for_missing_required_keys(self):
        """The recipe command must exit non-zero when a task is missing required keys."""
        incomplete_task = {"task_id": "t1", "description": "only two keys"}
        result = self._run_recipe_command({"tasks": [incomplete_task], "total_tasks": 1})
        assert result.returncode != 0, (
            f"Recipe command must exit non-zero for task missing required keys.  "
            f"exit={result.returncode}, stderr={result.stderr.decode()!r}"
        )
