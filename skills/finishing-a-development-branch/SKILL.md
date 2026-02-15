---
name: finishing-a-development-branch
description: "Complete development work — verify tests, present merge/PR/keep/discard options, clean up. The terminal step of every development workflow."
---

# Finishing a Development Branch

## Core Principle

```
Verify tests → Present options → Execute choice → Clean up
```

This is the terminal step of every development workflow. Use when implementation is complete, all tasks are done, and you need to decide how to integrate the work.

## The Test Gate

Before ANY option is presented, the project's test suite MUST pass:

```bash
pytest / npm test / cargo test / go test ./...
```

**If tests fail → STOP.** Show failures. Cannot proceed with merge/PR until tests pass. No workarounds.

**If tests pass → continue** to presenting options.

## The 4 Options

Present exactly these options — concise, no embellishment:

```
1. MERGE — Merge back to <base-branch> locally
2. PR — Push and create a Pull Request
3. KEEP — Keep the branch as-is (handle later)
4. DISCARD — Discard this work
```

### Option 1: MERGE

```bash
git checkout <base-branch>
git pull
git merge --ff-only <feature-branch>
# If fast-forward fails: suggest PR instead or regular merge
# Re-verify tests on merged result
<test command>
git branch -d <feature-branch>
git push origin --delete <feature-branch> 2>/dev/null
```

**Safety:** Tests run AGAIN after merge. Branch uses `-d` (safe delete — refuses if unmerged).

### Option 2: PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "<summary + test plan>"
```

**Keep worktree** — may need it for PR review cycles.

### Option 3: KEEP

Report location. Do NOT clean up anything. Both branch and worktree preserved.

### Option 4: DISCARD

**Requires typed confirmation** — show everything that will be deleted (branch, commits, worktree), wait for the exact word "discard":

```bash
git checkout <base-branch>
git branch -D <feature-branch>
git push origin --delete <feature-branch> 2>/dev/null
```

Uses `-D` (force delete) because the branch won't be merged.

## Worktree Cleanup

| Option | Branch | Worktree | Remote |
|--------|--------|----------|--------|
| MERGE | Deleted (`-d`) | Removed | Deleted |
| PR | Kept (pushed) | Kept | Kept |
| KEEP | Kept (local) | Kept | — |
| DISCARD | Force-deleted (`-D`) | Removed | Deleted |

## Safety Checks

1. **Tests must pass** before ANY option is presented (hard gate)
2. **MERGE re-runs tests** on the merged result (post-merge verification)
3. **DISCARD requires typed confirmation** — user must type literal "discard"
4. **No force-push** without explicit user request
5. **Merge conflicts** → show files, offer: resolve manually, abort, or switch to PR

## When to Apply

- After `/verify` passes — the golden path is verify → finish
- After all tasks complete in `/execute-plan`
- After debugging is resolved via `/debug` → `/verify` → `/finish`
- Any time work is ready to integrate
