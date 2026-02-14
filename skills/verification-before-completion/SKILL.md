---
name: verification-before-completion
description: "The Gate Function for verification — no completion claims without fresh evidence. Apply before ANY positive statement about work state."
---

# Verification Before Completion

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

"Fresh" means: run in THIS session. Prior runs don't count.
"Evidence" means: actual command output, not reasoning or confidence.

Violating the letter of this rule is violating the spirit of this rule.

## The Gate Function

Apply before ANY claim of status or satisfaction:

1. **IDENTIFY:** What command proves this claim?
2. **RUN:** Execute the FULL command (fresh, complete)
3. **READ:** Full output, check exit code, count failures
4. **VERIFY:** Does output confirm the claim?
   - If NO → state actual status with evidence
   - If YES → state claim WITH evidence
5. **ONLY THEN:** Make the claim

Skip any step = lying, not verifying.

## Claims → Required Evidence

| Claim | Required Evidence | NOT Sufficient |
|-------|-------------------|----------------|
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

ALL of these mean: STOP. Run the verification. Then speak.

## Why This Matters

This skill exists because of real failures:
- Undefined functions shipped — would crash in production
- Missing requirements shipped — incomplete features delivered
- Time wasted on false completion → redirect → rework
- Trust broken: "I don't believe you"

Unverified claims are not optimism. They are dishonesty. The Gate Function is the fix.

## When To Apply

ALWAYS before:
- ANY variation of success/completion claims
- ANY expression of satisfaction about work state
- Committing, PR creation, task completion
- Moving to the next task
- ANY communication suggesting completion or correctness

## Correct vs Incorrect Patterns

**Tests:**
- ✅ `[Run pytest -v] [See: 34/34 pass] "All tests pass"`
- ❌ `"Should pass now" / "Looks correct"`

**Bug fix:**
- ✅ `[Reproduce original bug] [See: fixed behavior] "Bug is resolved"`
- ❌ `"Code changed, should be fixed"`

**Agent delegation:**
- ✅ `Agent reports success → Check VCS diff → Run tests → Report actual state`
- ❌ `Trust agent report`

**Requirements:**
- ✅ `Re-read plan → Create checklist → Verify each item → Report gaps or completion`
- ❌ `"Tests pass, requirements are met"`
