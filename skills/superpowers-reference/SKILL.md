---
name: superpowers-reference
description: "Complete reference tables for Superpowers modes, agents, recipes, and anti-patterns"
---

## Reference: The Superpowers Pipeline

The full development workflow:

```
/brainstorm  ->  Design document (user validates each section)
     |
/write-plan  ->  Implementation plan (bite-sized TDD tasks)
     |
/execute-plan  ->  Subagent-driven development (implement -> spec-review -> quality-review per task)
     |
/verify  ->  Fresh evidence that everything works
     |
/finish  ->  Merge / PR / Keep / Discard
```

At any point, if bugs arise: `/debug` (4-phase systematic debugging).

**Priority order when multiple modes could apply:**
1. Process modes first (`/brainstorm`, `/debug`) -- determine HOW to approach the task
2. Implementation modes second (`/write-plan`, `/execute-plan`) -- guide execution
3. Completion modes last (`/verify`, `/finish`) -- close out work

## Reference: Mode Tool

The `mode` tool allows programmatic mode transitions. Use `mode(operation="set", name="write-plan")` to request a mode change. The first request will be blocked with a reminder — call again to confirm. This is useful when agents need to request transitions during automated workflows.

## Reference: Modes

| Mode | Shortcut | Purpose | Who Does The Work |
|------|----------|---------|-------------------|
| Brainstorm | `/brainstorm` | Design refinement through collaborative dialogue | You (main agent) |
| Write Plan | `/write-plan` | Create detailed implementation plan with TDD tasks | You (main agent) |
| Execute Plan | `/execute-plan` | Subagent-driven development with three-agent pipeline | Subagents (you orchestrate) |
| Debug | `/debug` | 4-phase systematic debugging | You (main agent) |
| Verify | `/verify` | Evidence-based completion verification | You (main agent) |
| Finish | `/finish` | Complete branch -- verify, merge/PR/keep/discard | You (main agent) |

## Reference: Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `superpowers:brainstormer` | Design refinement specialist | MANDATORY — after brainstorm conversation, delegate document creation |
| `superpowers:plan-writer` | Detailed plan creation | MANDATORY — after write-plan conversation, delegate plan creation |
| `superpowers:implementer` | Implements tasks following strict TDD | MANDATORY -- every task in `/execute-plan` |
| `superpowers:spec-reviewer` | Reviews implementation against spec | MANDATORY -- every task in `/execute-plan`, after implementer |
| `superpowers:code-quality-reviewer` | Reviews code quality and best practices | MANDATORY -- every task in `/execute-plan`, after spec-reviewer |

**Delegation rules:**
- **Brainstorm and Write-Plan: YOU own the conversation.** When it's time to write the artifact, delegate to the brainstormer/plan-writer agent. The back-and-forth with the user is what makes these phases effective. The agent writes the document after you've validated everything.
- **Execute-Plan: YOU delegate everything.** You are the orchestrator. Every task goes through the three-agent pipeline (implementer -> spec-reviewer -> code-quality-reviewer). You never write code in this mode.
- **Debug, Verify, Finish: YOU do the work directly.** You may delegate to `foundation:bug-hunter` for multi-file investigation in debug mode, but you own the process.

**Why fresh subagents per task:**
- **Clean context** — No pollution from previous work
- **Focused attention** — Single task, single responsibility
- **Quality gates** — Review checkpoints catch issues early
- **Parallel safety** — Subagents don't interfere with each other

## Reference: Recipes

Execute these workflows using the recipes tool:

| Recipe | Purpose | When to Use |
|--------|---------|-------------|
| `superpowers:recipes/superpowers-full-development-cycle.yaml` | End-to-end: idea to merged code | Complete feature development |
| `superpowers:recipes/brainstorming.yaml` | Refine ideas into designs | Starting a new feature |
| `superpowers:recipes/writing-plans.yaml` | Create detailed implementation plans | After design is approved |
| `superpowers:recipes/executing-plans.yaml` | Execute plans in batches | For batch execution with checkpoints |
| `superpowers:recipes/subagent-driven-development.yaml` | Fresh agent per task + reviews | For same-session execution with foreach |
| `superpowers:recipes/git-worktree-setup.yaml` | Create isolated workspace | Before implementation |
| `superpowers:recipes/finish-branch.yaml` | Complete development branch | After implementation done |

## Reference: Anti-Rationalization Table

| Your Excuse | Why It's Wrong | What You MUST Do |
|-------------|---------------|------------------|
| "This is a simple/trivial change" | Simple changes cause production outages. They still need tests and review. | Follow the appropriate mode's process. |
| "I can do this faster myself" | Speed is not the goal. Tested, reviewed, quality code is the goal. | In `/execute-plan`: delegate. In `/brainstorm`: follow the process. |
| "The user seems to want a quick response" | The user chose the Superpowers methodology. They want quality. | Give them the full process for the active mode. |
| "I'll write the test after" | That's not TDD. Test FIRST defines what you need, not confirms what you wrote. | RED-GREEN-REFACTOR. Always. |
| "This doesn't need a review" | Everything in `/execute-plan` needs review. Both reviews. | Delegate to spec-reviewer, then code-quality-reviewer. |
| "I need to debug this myself" | Use `/debug` mode and follow the 4-phase framework. | Activate debug mode. Phase 1 before any fixes. |
| "I already know what to build" | Then the brainstorming questions will be fast. That's not a reason to skip design. | Follow `/brainstorm` process. Assumptions kill designs. |
| "The plan is obvious" | If it's obvious, writing exact code will be fast. Vague plans produce bad implementations. | Follow `/write-plan` process. Every task needs complete code. |
| "Should work now" | Run the verification. "Should" is not evidence. | Use `/verify`. Run the command. Read the output. THEN claim. |
| "Just one more fix attempt" | 3+ failed fixes = architectural problem. Stop fixing symptoms. | Question the architecture. Discuss with user. |
| "No mode applies here" | If there's even a 1% chance, suggest it. Let the user decide. | State which mode might apply and why. |

## Reference: Key Rules

1. **Standing Order First** -- Check which mode applies before starting any work. Suggest it even if you're only 1% sure.
2. **Own Design Conversations, Delegate Artifacts** -- You brainstorm and write plans through conversation. When it's time to produce the document, delegate to the brainstormer/plan-writer agent.
3. **Delegate in Execution** -- Every task in `/execute-plan` goes through the three-agent pipeline. No exceptions.
4. **TDD Always** -- No production code without failing test first.
5. **Verify Everything** -- Evidence before claims, fresh commands before assertions.
6. **Systematic Debugging** -- Root cause before fixes, 4 phases in order.
7. **Human Checkpoints** -- Validate designs section by section, approval gates at critical points.
8. **Two-Stage Review** -- Spec compliance first, then code quality -- for EVERY task in execution.

## Reference: Skills

Load these for reference using the skills tool:

| Skill | Purpose |
|-------|---------|
| `test-driven-development` | TDD methodology and rules |
| `systematic-debugging` | 4-phase debugging framework |
| `verification-before-completion` | Verification checklist |

## Philosophy Reference

For deep understanding of the principles, see:
- `superpowers:context/philosophy.md` -- Core principles, anti-patterns, and the two-stage review pattern
