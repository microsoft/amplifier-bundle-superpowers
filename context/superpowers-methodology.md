# Superpowers Development Methodology

## The Iron Laws

### 1. No Production Code Without a Failing Test First

Write code before the test? **Delete it. Start over.**

No exceptions:
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

### 2. No Implementation Without a Design First

Before any creative work - creating features, building components, adding functionality:
1. Explore the idea through questions
2. Present 2-3 approaches with trade-offs
3. Validate design in sections (200-300 words each)
4. Document the validated design

### 3. No Completion Without Verification

"It works" requires proof:
- Tests pass (watched them fail first)
- Manual verification of behavior
- Edge cases covered
- No regressions

## Red-Green-Refactor Cycle

```
RED: Write failing test
  ↓ Verify it fails for the right reason
GREEN: Write minimal code to pass
  ↓ Verify all tests pass
REFACTOR: Clean up
  ↓ Stay green
REPEAT
```

## Common Rationalizations (And Why They're Wrong)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is debt. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "TDD will slow me down" | TDD faster than debugging. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

## Red Flags - STOP and Start Over

If you catch yourself:
- Writing code before test
- Test passes immediately (didn't watch it fail)
- Rationalizing "just this once"
- Saying "I already manually tested it"
- Thinking "it's about spirit not ritual"
- Saying "this is different because..."
- Keeping code as "reference" while writing tests
- Saying "tests after achieve the same purpose"

**All of these mean: Delete code. Start over with TDD.**

## Bite-Sized Task Granularity

Each task should be 2-5 minutes:
- "Write the failing test" - one step
- "Run it to make sure it fails" - one step
- "Implement the minimal code" - one step
- "Run tests and verify pass" - one step
- "Commit" - one step

## Two-Stage Review Pattern

After each task:

**Stage 1: Spec Compliance Review**
- Does implementation match the spec exactly?
- Nothing missing from requirements?
- Nothing extra that wasn't requested?

**Stage 2: Code Quality Review**
- Clean code principles followed?
- Proper error handling?
- Test coverage adequate?
- No obvious issues?

Both stages must pass before moving to next task.

## Subagent Advantages

Using fresh subagents per task provides:
- **Clean context** - No pollution from previous work
- **Focused attention** - Single task, single responsibility
- **Quality gates** - Review checkpoints catch issues early
- **Parallel safety** - Subagents don't interfere with each other

## Integration Points

| When | Skill/Agent |
|------|-------------|
| Starting new feature | brainstorming → writing-plans |
| Implementing plan | subagent-driven-development |
| Debugging issues | systematic-debugging |
| Before declaring done | verification-before-completion |
| Creating isolated workspace | using-git-worktrees |
