---
name: integration-testing-discipline
description: "4 principles for E2E testing discipline — observe first, fix in batches, expect long durations, check container state directly. NO FIXES DURING OBSERVATION RUNS."
---

# Integration Testing Discipline

## The Core Principle

```
OBSERVE FIRST. FIX IN BATCHES. NEVER FIX DURING ACTIVE E2E RUNS.
```

When running integration tests or E2E validation, your job is to CAPTURE ALL failures first, then fix them systematically. Making code changes during a running test invalidates that test run.

## The Four Principles

### Principle 1: Don't Fix During Observation Runs

**DO:** Let the E2E run complete (or fail with a real error), capture ALL failure points, then fix everything as a coordinated batch.

**DON'T:** See one failure, fix it immediately, and continue the same E2E run.

**Why:** Code changes during E2E runs invalidate the running test. You lose the ability to trust that run's results.

**Example:**
```
❌ WRONG:
1. E2E run finds validation error
2. Fix validation immediately  
3. Continue same E2E run
4. Find auth error
5. Fix auth immediately
6. Continue same E2E run
→ Result: Can't trust this run's success

✅ RIGHT:
1. E2E run finds validation error — RECORD IT
2. E2E run finds auth error — RECORD IT  
3. E2E run completes — STOP OBSERVING
4. Fix validation AND auth as a batch
5. Start fresh E2E run to validate fixes
→ Result: Clean validation of coordinated fixes
```

### Principle 2: Long-Running Processes Are Normal

**DO:** Check for actual error signals: non-zero exit codes, error messages in logs, process death, hung processes.

**DON'T:** Declare "stuck" or "failed" based on wall clock time alone.

**Expected Durations:**
- Container setup: 60-90 seconds
- Simple spec (1 endpoint): ~13 minutes  
- Medium spec (4 CRUD endpoints): ~25 minutes
- Complex spec (8+ endpoints): ~40 minutes
- Each convergence iteration: 5-8 minutes

**Example:**
```
❌ WRONG:
"Process has been running 20 minutes with no output — it's stuck"

✅ RIGHT:
"Process has been running 20 minutes. Checking:
- Exit code: still running (0)
- Error logs: none
- New files: tracker.json updated 30s ago
- Container: process alive, making progress
→ Status: WORKING, not stuck"
```

### Principle 3: Check Container State Directly

**DO:** Use `docker exec` to check the container's internal state directly when monitoring seems inconsistent.

**DON'T:** Trust API status or monitor reports when they contradict expected behavior.

**Why:** Monitor APIs may lag behind container reality. Always verify directly.

**Example:**
```
❌ WRONG:
"API shows no progress for 10 minutes — declaring failure"

✅ RIGHT:
"API shows no progress. Checking container directly:
$ docker exec container-name ls -la /workspace/
$ docker exec container-name cat tracker.json  
$ docker exec container-name ps aux
→ Found: New files created 2 min ago, process active
→ Status: API lag, not failure"
```

### Principle 4: One Run, All Errors

**DO:** Let each run discover its full set of failures, then address them in dependency order.

**DON'T:** Fix errors one-by-one across multiple runs when you could batch them.

**Why:** Many failures have dependency relationships. Fixing in random order creates thrashing.

**Example:**
```
❌ WRONG:
Run 1: Find validation error → fix → new run
Run 2: Find auth error → fix → new run  
Run 3: Find storage error → fix → new run
→ Result: 3 full E2E cycles for related issues

✅ RIGHT:
Run 1: Find validation + auth + storage errors → RECORD ALL
Fix: Address validation first (dependency), then auth, then storage
Run 2: Validate all fixes together
→ Result: 1 observation run + 1 validation run
```

## When to Apply

Use this discipline for ANY integration testing scenario:

- E2E recipe validation
- Multi-service integration tests
- Container-based testing workflows  
- Cross-repo change validation
- Production deployment validation

Use ESPECIALLY when under time pressure — the temptation to "quick fix" during observation runs is highest when deadlines loom, but disciplined observation is fastest.

## Red Flags — Return to Observation Mode

If you catch yourself thinking:
- "Just fix this one thing and continue the run"
- "Quick patch while the E2E is running"  
- "I'll fix this now and the rest later"
- "This failure is blocking — fix immediately"
- "We're so close, just one more fix"

ALL of these mean: STOP fixing. Return to pure observation mode.

## Impact

- Disciplined approach: 1 observation run + 1 validation run = ~50 minutes total
- Fix-during-run approach: 6+ interrupted runs = 3+ hours total  
- Success rate: 95% vs 60%
- Stress level: Manageable vs high