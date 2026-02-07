# Superpowers Philosophy

## Core Principles

### 1. Test-Driven Development is Non-Negotiable

Write the test first. Watch it fail. Write minimal code to pass.

If you didn't watch the test fail, you don't know if it tests the right thing. Code written before tests must be deleted - no exceptions, no "keeping as reference."

### 2. Systematic Over Ad-Hoc

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

Always find the root cause before attempting fixes. Follow the four-phase debugging process: investigate, analyze patterns, form hypotheses, then implement.

### 3. Evidence Over Claims

"It should work" is not verification. "I tested it manually" is not proof.

Every fix must be demonstrated with evidence: tests passing, manual verification documented, side effects checked.

### 4. Complexity Reduction as Primary Goal

Simplicity is not just nice to have - it's the goal. Every abstraction must justify its existence.

YAGNI (You Aren't Gonna Need It) ruthlessly. DRY (Don't Repeat Yourself) pragmatically. Start minimal, grow only as needed.

### 5. Structured Planning Before Implementation

Never jump into code. First understand what you're building through collaborative design. Then create a detailed plan with bite-sized tasks. Then execute systematically.

The plan should be clear enough for "an enthusiastic junior engineer with poor taste, no judgment, no project context, and an aversion to testing" to follow.

### 6. Isolation for Safety

Use git worktrees to isolate feature work. Never work directly on main. Verify clean test baseline before starting. Clean up when done.

### 7. Human Checkpoints at Critical Points

Autonomous work is powerful, but human judgment is essential at key moments:
- After design completion (before saving)
- After plan creation (before execution)
- Between execution batches
- Before merging/PR creation

## The Superpowers Workflow

```
1. BRAINSTORM -> Refine idea into design (human approves)
2. PLAN -> Break design into tasks (human approves)
3. WORKTREE -> Create isolated workspace
4. EXECUTE -> Implement with TDD + reviews
5. FINISH -> Verify, merge/PR, cleanup
```

Each step uses the appropriate recipe with built-in quality gates.

## The Two-Stage Review Pattern

After each task implementation, two separate review passes ensure quality:

**Stage 1: Spec Compliance Review** (superpowers:spec-reviewer)
- Does implementation match the spec exactly?
- Nothing missing from requirements?
- Nothing extra that wasn't requested?

**Stage 2: Code Quality Review** (superpowers:code-quality-reviewer)
- Clean code principles followed?
- Proper error handling?
- Test coverage adequate?
- No obvious issues?

Both stages must pass before moving to next task. Order matters - spec compliance first, quality second.

## Anti-Patterns to Avoid

- **Jumping to code** without understanding requirements
- **Skipping tests** for "simple" changes
- **Multiple fixes at once** instead of isolated changes
- **Ignoring test failures** or marking them as "expected"
- **Working on main** instead of feature branches
- **Claiming success** without verification evidence
- **Rationalizing shortcuts** ("just this once", "too simple to test")

## Philosophy in Practice

When you catch yourself thinking any of these, STOP:

| Thought | Action |
|---------|--------|
| "This is too simple to need a test" | Write the test anyway |
| "I'll add tests later" | Write them now or delete the code |
| "Quick fix, then investigate" | Investigate first |
| "It should work now" | Verify with evidence |
| "Just one more try" (after 2 failures) | Question the architecture |
| "I know what the problem is" | Prove it with evidence |

## The Goal

Superpowers isn't about following rules for their own sake. It's about:

1. **Higher quality** - Fewer bugs, more reliable software
2. **Faster delivery** - Less debugging, less rework
3. **Sustainable pace** - No firefighting, no technical debt spiral
4. **Confidence** - Know the code works because you proved it

The discipline enables the speed, not the other way around.
