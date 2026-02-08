---
mode:
  name: finish
  description: Complete development work - verify tests, present merge/PR/keep/discard options, clean up
  shortcut: finish
  
  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - todo
      - delegate
      - recipes
      - LSP
      - python_check
    warn:
      - write_file
      - edit_file
  
  default_action: block
---

FINISH MODE: Complete development work with structured options.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

## The Process

### Step 1: Verify Tests

Before presenting any options, verify tests pass:

```bash
# Run project's test suite (detect which applies)
pytest / npm test / cargo test / go test ./...
```

**If tests fail:**
```
Tests failing (N failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
Use /debug to investigate failures.
```

STOP. Do not proceed to Step 2 until tests pass.

**If tests pass:** Continue to Step 2.

### Step 2: Summarize the Work

Show what was accomplished:
```bash
# Show commits on this branch
git log --oneline main..HEAD

# Show changed files
git diff --stat main
```

Present a brief summary of what was built/changed.

### Step 3: Determine Base Branch

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main — is that correct?"

### Step 4: Present Exactly 4 Options

Present these options concisely. Don't add lengthy explanations.

```
Implementation complete. All tests pass. What would you like to do?

1. MERGE — Merge back to <base-branch> locally
2. PR — Push and create a Pull Request
3. KEEP — Keep the branch as-is (handle later)
4. DISCARD — Discard this work

Which option?
```

### Step 5: Execute Choice

#### Option 1: MERGE

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# Verify tests on merged result
<test command>
# If tests pass
git branch -d <feature-branch>
```

Then: Check if in worktree and clean up if applicable.

#### Option 2: PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- [2-3 bullets of what changed]

## Test Plan
- [ ] [verification steps]
EOF
)"
```

Report the PR URL.

#### Option 3: KEEP

Report: "Keeping branch `<name>`. Worktree preserved at `<path>`."

Do NOT clean up anything.

#### Option 4: DISCARD

**Confirm first — require typed confirmation:**
```
This will permanently delete:
- Branch: <name>
- All commits: <commit-list>
- Worktree at <path> (if applicable)

Type 'discard' to confirm.
```

Wait for exact confirmation. If not confirmed, do nothing.

If confirmed:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Clean up worktree if applicable.

### Step 6: Worktree Cleanup

For Options 1, 2, and 4 — check if in worktree:
```bash
git worktree list
```

If in a worktree, remove it:
```bash
git worktree remove <worktree-path>
```

For Option 3 — keep worktree.

## Recipe Alternative

For structured execution with approval gates, recommend the finish-branch recipe:

```
Execute superpowers:recipes/finish-branch.yaml
```

The recipe handles test verification, option presentation, and cleanup automatically.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. MERGE | ✓ | - | - | ✓ |
| 2. PR | - | ✓ | ✓ | - |
| 3. KEEP | - | - | ✓ | - |
| 4. DISCARD | - | - | - | ✓ (force) |

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on the merged result
- Delete work without typed confirmation
- Force-push without explicit user request

**Always:**
- Verify tests BEFORE offering options
- Present exactly 4 options
- Get typed confirmation for DISCARD
- Show what was accomplished before asking
