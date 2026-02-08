---
mode:
  name: write-plan
  description: Create detailed implementation plan with bite-sized TDD tasks
  shortcut: write-plan
  
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - todo
      - delegate
      - recipes
      - write_file
    warn:
      - bash
  
  default_action: block
---

WRITE-PLAN MODE: Create detailed implementation plan.

You are now in plan-writing mode. Follow the Superpowers plan-writing process.

<CRITICAL>
For any plan with more than 2-3 tasks, you MUST delegate to `superpowers:plan-writer`. The plan-writer agent is a specialist at creating detailed, bite-sized task lists from design specs. It creates plans assuming zero context and questionable taste — meaning the plans are detailed enough for ANY agent to execute without needing to ask questions.

You MUST delegate when:
- The design document describes more than a trivial change
- Multiple files or components are involved
- The implementation has dependencies between tasks
- You need to break work into TDD-structured steps

You delegate like this:
```
delegate(
  agent="superpowers:plan-writer",
  instruction="Create a detailed implementation plan from the design at [path]. Break into bite-sized TDD tasks with exact file paths, complete code, and expected test output.",
  context_depth="recent",
  context_scope="conversation"
)
```
</CRITICAL>

## Anti-Rationalization

| Your Excuse | Why It's Wrong |
|-------------|---------------|
| "I can write this plan myself" | The plan-writer agent creates plans with zero-context assumptions — detailed enough for a fresh agent to execute. Your plans will have implicit context that breaks execution. Delegate. |
| "The design is simple enough" | Simple designs still need exact file paths, complete code, and expected test output per task. The plan-writer ensures this. Delegate. |
| "I'll just list the tasks quickly" | Quick task lists lack TDD structure, exact commands, and expected output. That's not a Superpowers plan. Delegate. |
| "I already know the implementation" | Knowing the implementation is not the same as writing a plan that a fresh agent can execute with zero context. Delegate. |

For truly trivial plans (1-2 tasks in a single file), you may write directly. Everything else: DELEGATE.

## Prerequisites

A design document should exist from `/brainstorm`. If not, ask the user to brainstorm first.

## Your Process (for trivial plans you handle directly)

1. **Review the Design**
   - Load the design document
   - Understand the chosen approach
   - Identify all components to build

2. **Break Into Tasks**
   - Each task: 2-5 minutes of work
   - Each task: ONE action (not "write tests and implementation")
   - Each task: Exact file paths
   - Each task: Complete code (copy-pasteable)

3. **Apply TDD Structure**
   Per task:
   - Step 1: Write failing test
   - Step 2: Run test, verify failure
   - Step 3: Write minimal implementation
   - Step 4: Run test, verify pass
   - Step 5: Commit

4. **Save the Plan**
   - Save to `docs/plans/YYYY-MM-DD-<feature-name>-implementation.md`

## Task Format

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**
\`\`\`python
[Complete test code]
\`\`\`

**Step 2: Run test to verify failure**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "[error message]"

**Step 3: Write minimal implementation**
\`\`\`python
[Complete implementation code]
\`\`\`

**Step 4: Run test to verify pass**
Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**
\`\`\`bash
git add [files]
git commit -m "feat: [description]"
\`\`\`
```

## Do NOT:
- Create vague tasks ("set up the module")
- Combine multiple actions into one step
- Skip the TDD cycle
- Write implementation code (that's for execute-plan)

## Do:
- Use `load_skill(skill_name="writing-plans")` for detailed guidance
- **DELEGATE to `superpowers:plan-writer` for anything beyond trivial**
- Be extremely specific about file paths
- Include exact commands with expected output

## Output

End with:
```
Plan saved to `docs/plans/YYYY-MM-DD-<feature>-implementation.md`

Ready to execute? Use `/execute-plan` to begin subagent-driven development.
Or for automated execution: Execute superpowers:recipes/subagent-driven-development.yaml
```

Use `/mode off` when plan is complete, then `/execute-plan` to begin implementation.
