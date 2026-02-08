---
mode:
  name: verify
  description: Evidence-based completion verification - no claims without fresh proof
  shortcut: verify
  
  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - LSP
      - python_check
      - todo
    warn:
      - write_file
      - edit_file
  
  default_action: block
---

VERIFY MODE: Evidence before claims. Always.

Claiming work is complete without verification is dishonesty, not efficiency.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command IN THIS SESSION, you cannot claim it passes. Previous runs don't count. "Should pass" doesn't count. Confidence doesn't count.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## The Three Checks

Every verification MUST cover all three:

### Check 1: Tests Pass

Run the FULL test suite. Not a subset. Not "the relevant tests." The full suite.

```bash
# Run complete test suite
pytest / npm test / cargo test / go test ./...
```

Evidence required: exact output showing pass count and zero failures.

```
✅ "All 47 tests pass" [with output showing 47 passed, 0 failed]
❌ "Tests should pass" / "Tests were passing earlier"
```

### Check 2: Behavior Verified

The specific behavior that was built/fixed must be verified independently:

- For new features: demonstrate the feature works with a concrete example
- For bug fixes: reproduce the original bug scenario and show it's fixed
- For refactoring: show behavior is unchanged

```
✅ Run the specific scenario, show output, confirm correct behavior
❌ "The code looks correct" / "The tests cover this"
```

### Check 3: Edge Cases and Regressions

Check that nothing else broke:

- Run linter/type checker if available
- Check for obvious regressions in related functionality
- Verify error handling works (bad input, missing data, etc.)

```
✅ "Pyright: 0 errors. Ruff: 0 issues. Edge case test with empty input returns expected error."
❌ "I don't think anything else is affected"
```

## Common Verification Requirements

| Claim | Requires | NOT Sufficient |
|-------|----------|----------------|
| "Tests pass" | Test command output: 0 failures | Previous run, "should pass" |
| "Linter clean" | Linter output: 0 errors | Partial check, extrapolation |
| "Build succeeds" | Build command: exit 0 | "Linter passed" (linter ≠ build) |
| "Bug fixed" | Original symptom: gone (demonstrated) | "Code changed, assumed fixed" |
| "Regression test works" | Red-green cycle verified | Test passes once |
| "Agent completed task" | VCS diff shows correct changes | Agent reports "success" |
| "Requirements met" | Line-by-line checklist with evidence | "Tests passing" |

## Red Flags — STOP Immediately

If you catch yourself:
- Using "should," "probably," "seems to," "likely"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit/push/PR without verification
- Trusting an agent's success report without checking
- Relying on partial verification ("I checked the main path")
- Thinking "just this once"
- Tired and wanting the work to be over
- Using ANY wording implying success without having run the command

**ALL of these mean: STOP. Run the verification. Then speak.**

## Anti-Rationalization Table

| Your Excuse | Reality |
|-------------|---------|
| "Should work now" | RUN the verification. |
| "I'm confident" | Confidence ≠ evidence. |
| "Just this once" | No exceptions. |
| "Linter passed" | Linter ≠ compiler ≠ tests ≠ behavior. |
| "Agent said success" | Verify independently. Agents lie. |
| "I'm tired" | Exhaustion ≠ excuse. |
| "Partial check is enough" | Partial proves nothing about the rest. |
| "Different words so rule doesn't apply" | Spirit over letter. Always. |
| "Tests pass so requirements are met" | Tests verify behavior. Requirements verify completeness. Both needed. |
| "I just ran it a minute ago" | State changes. Run it again. Fresh evidence only. |

## Verification Report Format

When verification is complete, present results as:

```
## Verification Report

### Tests
- Command: `pytest -v`
- Result: 47 passed, 0 failed, 0 errors
- Evidence: [key output lines]

### Behavior
- Scenario: [what was tested]
- Result: [what happened]
- Expected: [what should happen]
- Status: ✅ VERIFIED / ❌ FAILED

### Edge Cases & Regressions
- Linter: [result]
- Type checker: [result]  
- Edge case tested: [description and result]

### Verdict: VERIFIED / NOT VERIFIED
[If NOT VERIFIED: what remains to be done]
```

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

## Announcement

When entering this mode, announce:
"I'm entering verify mode. I'll collect fresh evidence that everything works: tests, behavior, edge cases. No claims without proof."

## Transitions

**Done when:** All verification evidence collected

**Golden path (pass):** `/finish`
- Tell user: "Verification complete - all checks pass. Use `/finish` to merge, create PR, or complete the branch."

**Golden path (fail):** `/debug`
- Tell user: "Verification found issues: [list]. Use `/debug` to investigate."

**Dynamic transitions:**
- If missing tests discovered → suggest adding tests in `/execute-plan` because tests should go through the implementation pipeline
- If missing feature discovered → suggest `/brainstorm` or `/write-plan` because new work needs design and planning

**Skill connection:** If you load a workflow skill (brainstorming, writing-plans, etc.),
the skill tells you WHAT to do. This mode enforces HOW. They complement each other.
