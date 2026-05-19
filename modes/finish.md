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
      - delegate
      - recipes
      - LSP
      - python_check
      - load_skill
    warn:
      - write_file
      - edit_file
  
  default_action: block
  allowed_transitions: [execute-plan, brainstorm]
  allow_clear: true
---

FINISH MODE: Complete development work with structured options.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

## Repository conventions discovery (mandatory on mode entry)

Before finalizing anything (merge, push, PR), look for these files in the target repository and apply their contents:

1. `AGENTS.md` — repo root first, then walk up from the current working directory. Defines repo-specific completion gates, required smoke/integration evidence, and what "ready to merge" means in this repo.
2. `.github/PULL_REQUEST_TEMPLATE.md` — the checklist the repo expects every PR body to honor.

If either file exists:
- Read it before presenting options to the user.
- Treat its gates as preconditions for Options 1 (MERGE) and 2 (PR) — not optional add-ons.
- When repo conventions conflict with your defaults, the repo wins.

If neither exists, fall back to generic finish discipline (the steps below).

See `foundation:docs/PER_REPO_CONVENTIONS.md` for the principle.

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

### Step 1.5: Optional Holistic Code Review

**When to use:** After all tests pass, optionally request a holistic review of the complete implementation on this branch before presenting merge options.

**Skip if:**
- Holistic review was already done in `/verify` mode
- Per-task pipeline reviews may suffice for smaller changes

```python
delegate(
    agent='superpowers:code-reviewer',
    instruction='Review the complete implementation on this branch against the design and plan, focusing on cross-task integration, architectural coherence, and production readiness.',
    context_depth='recent',
    model_role='critique'
)
```

If the review surfaces significant issues, consider switching to execute-plan mode to address them before completing.

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

**Pre-merge gate (mandatory if `AGENTS.md` is present):**
Re-read `AGENTS.md` and confirm every gate it requires for merge (smoke test on fresh environment, live-run evidence, integration scenario, etc.) is satisfied. If any gate is unmet, surface the gap to the user and STOP until it is addressed.

```bash
git checkout <base-branch>
git pull
git merge --ff-only <feature-branch>
# If fast-forward merge fails (branch has diverged):
#   "Fast-forward merge not possible — branch has diverged from <base-branch>."
#   Offer: (a) Create a PR instead (Option 2)
#          (b) Regular merge: git merge <feature-branch>
#          (c) Rebase first: git rebase <base-branch> from feature branch
#   Wait for user choice before proceeding.
#
# If merge conflicts occur (from regular merge):
#   Show conflicting files: git diff --name-only --diff-filter=U
#   Offer: resolve manually, abort (git merge --abort), or switch to PR (Option 2)
#   Do NOT force-resolve conflicts without user guidance.
#
# Verify tests on merged result
<test command>
# If tests pass
git branch -d <feature-branch>
git push origin --delete <feature-branch> 2>/dev/null  # Clean up remote if pushed
```

Then: Check if in worktree and clean up if applicable.

#### Option 2: PR

**Pre-PR template gate (mandatory if `.github/PULL_REQUEST_TEMPLATE.md` exists):**

```bash
# Read the repo's template and use it as the PR body scaffold
test -f .github/PULL_REQUEST_TEMPLATE.md && cat .github/PULL_REQUEST_TEMPLATE.md
```

Before approving the PR creation:
1. Read `.github/PULL_REQUEST_TEMPLATE.md` end-to-end.
2. Build the PR body from the template — do not substitute the generic "## Summary / ## Test Plan" stub below if the repo ships its own template.
3. For every checkbox in the template, confirm the evidence exists. If any item is not addressed, surface the unchecked items to the user and STOP until they are addressed or the user explicitly waives them.

```bash
git push -u origin <feature-branch>
# If a PR template exists, the body MUST be derived from it (with checklist items honored).
# The block below is the fallback ONLY when no template is present.
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
git push origin --delete <feature-branch> 2>/dev/null  # Clean up remote if pushed
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

## Announcement

When entering this mode, announce:
"I'm entering finish mode. I'll verify the branch is ready, summarize the work, and present your completion options."

## Transitions

**Done when:** Branch merged/PR created/kept/discarded

**Golden path:** Session complete
- Tell user: "Branch completed via [chosen option]. Great work!"
- Use `mode(operation='clear')` to exit modes.

**Dynamic transitions:**
- If tests failing → use `mode(operation='set', name='execute-plan')` because failing tests need to go through the implementation pipeline for fixes
- If user wants more work on this project → use `mode(operation='set', name='brainstorm')` because new work needs the design process
- If user wants to add more work on the current plan → use `mode(operation='set', name='execute-plan')` because additional tasks go through the execution pipeline
- Session truly complete → use `mode(operation='clear')` to exit the development workflow

**Skill connection:** If you load a workflow skill (brainstorming, writing-plans, etc.),
the skill tells you WHAT to do. This mode enforces HOW. They complement each other.

---

@superpowers:context/philosophy.md
