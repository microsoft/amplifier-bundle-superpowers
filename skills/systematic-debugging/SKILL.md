---
name: systematic-debugging
description: "4-phase systematic debugging — root cause before fixes, evidence before claims. NO FIXES WITHOUT INVESTIGATION FIRST."
---

# Systematic Debugging

## The Iron Law

```
NEVER guess. NEVER apply shotgun fixes. NEVER skip phases.
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.
```

If you haven't completed Phase 1, you CANNOT propose fixes. If you catch yourself about to suggest a fix before investigating, STOP.

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Reproduce and Investigate

BEFORE attempting ANY fix:

1. **Read Error Messages Carefully** — Don't skip past errors or warnings. Read stack traces COMPLETELY. Note line numbers, file paths, error codes. They often contain the exact solution.
2. **Reproduce Consistently** — Can you trigger it reliably? What are the exact steps? If not reproducible → gather more data, don't guess.
3. **Check Recent Changes** — `git diff`, `git log --oneline -10`, recent commits. New dependencies, config changes, environmental differences.
4. **Gather Evidence in Multi-Component Systems** — Log what data enters/exits each component boundary. Verify environment/config propagation. Run once to gather evidence, THEN analyze.
5. **Trace Data Flow** — Where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not at symptom. See Root-Cause Tracing technique.

### Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in the same codebase.
2. **Compare Against References** — Read reference implementations COMPLETELY, don't skim.
3. **Identify Differences** — List every difference between working and broken, however small. Don't assume "that can't matter."
4. **Understand Dependencies** — What other components, settings, config, environment does this need?

### Phase 3: Hypothesis and Test

1. **Form a Single Hypothesis** — State clearly: "I think X is the root cause because Y." Write it down. Be specific, not vague.
2. **Design a Minimal Test** — What is the SMALLEST change that would confirm or deny this hypothesis? One variable at a time.
3. **Verify Before Continuing** — Did the evidence confirm the hypothesis? → Phase 4. Didn't confirm? → Form NEW hypothesis, return to Phase 1 with new information. DON'T add more fixes on top.
4. **When You Don't Know** — Say "I don't understand X." Don't pretend to know. Ask for help or research more.

### Phase 4: Fix

Root cause confirmed. Now fix it.

1. **Create Failing Test Case** — Write a test that reproduces the bug. Verify it fails. This IS your regression test.
2. **Implement Single Fix** — ONE change. No "while I'm here" improvements. No bundled refactoring.
3. **Verify Fix** — Test passes? No other tests broken? Issue actually resolved?
4. **If Fix Doesn't Work After 3 Attempts** — STOP. Question the architecture. Each fix reveals new problem = wrong architecture, not wrong fix. Discuss with human partner before attempting more fixes.

## Red Flags — STOP and Return to Phase 1

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals new problem in different place

ALL of these mean: STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Companion Techniques

For specific debugging situations:

- **Root-Cause Tracing** — Trace backward through the call chain until you find the original trigger, then fix at the source. NEVER fix just where the error appears.
- **Defense-in-Depth** — After finding root cause, add validation at EVERY layer data passes through (entry point, business logic, environment guards, debug instrumentation). Make the bug structurally impossible.
- **Condition-Based Waiting** — Replace arbitrary timeouts (`setTimeout`, `sleep`) with condition polling (`waitFor`). Wait for the actual condition you care about, not a guess about how long it takes.

## When to Apply

Use for ANY technical issue:
- Test failures
- Bugs (production or development)
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

Use ESPECIALLY when under time pressure — emergencies make guessing tempting, but systematic debugging is faster.

## Impact

- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common
