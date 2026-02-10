# Superpowers Bundle Usage Guide

A practical guide to using the Superpowers development methodology with Amplifier. This covers everything from installation to running full autonomous development cycles.

## Table of Contents

- [Getting Started](#getting-started)
- [The Superpowers Workflow](#the-superpowers-workflow)
- [Modes Guide](#modes-guide)
- [Agents Guide](#agents-guide)
- [Recipes Guide](#recipes-guide)
- [The Full Development Cycle](#the-full-development-cycle)
- [Composing Into Your Own Bundle](#composing-into-your-own-bundle)
- [Tips & Best Practices](#tips--best-practices)
- [Quick Reference](#quick-reference)

---

## Getting Started

### Recommended: Behavior Install (works with any bundle)

The best way to use Superpowers is to install the behavior at your app level. This layers the methodology on top of whatever bundle you already have active - no need to switch:

```bash
# Add the superpowers methodology to your app settings
amplifier bundle add --app git+https://github.com/microsoft/amplifier-bundle-superpowers@main#subdirectory=behaviors/superpowers-methodology.yaml
```

Or add it directly to `~/.amplifier/settings.yaml`:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-superpowers@main#subdirectory=behaviors/superpowers-methodology.yaml
```

This gives you all 5 specialist agents and the methodology context, composed on top of your existing bundle's providers, tools, and configuration.

### Alternative: Full Bundle Install

If you want the complete standalone experience with modes, recipes, and skills:

```bash
# Add the full bundle from GitHub
amplifier bundle add --app git+https://github.com/microsoft/amplifier-bundle-superpowers@main
```

### Verify It's Working

Start a session and check that the components loaded:

```bash
amplifier
```

Once inside a session, verify:

```
# If using the full bundle, check modes are available
/modes

# Check skills loaded (full bundle only)
load_skill(list=True)

# Check a specific skill
load_skill(search="superpowers")
```

With the behavior install, you'll have the 5 agents available. With the full bundle, you'll also see three modes (`/brainstorm`, `/write-plan`, `/execute-plan`) and the skills library.

### What You Get

**Behavior install** (recommended):

| Component | Count | What It Is |
|-----------|-------|------------|
| **Agents** | 5 | Specialized sub-agents for each workflow role |
| **Methodology** | 1 | Core Superpowers philosophy and anti-rationalization context |

**Full bundle** (adds on top of behavior):

| Component | Count | What It Is |
|-----------|-------|------------|
| **Modes** | 3 | Workflow shortcuts that constrain tool access |
| **Recipes** | 7 | Declarative multi-step workflows with approval gates |
| **Skills** | 14+ | The original Superpowers skills library from [obra/superpowers](https://github.com/obra/superpowers) |

---

## The Superpowers Workflow

Superpowers enforces a disciplined pipeline: **design first, plan carefully, implement with TDD, review rigorously**. The result is agents that can work autonomously without deviating from your intent.

### The Pipeline

```
/brainstorm  -->  Design Document (human approves)
                       |
/write-plan  -->  Implementation Plan (human approves)
                       |
      git worktree  -->  Isolated workspace
                       |
/execute-plan  -->  Per-task implementation:
                       |   1. Implementer agent (TDD)
                       |   2. Spec reviewer agent
                       |   3. Code quality reviewer agent
                       |
               Finished Branch --> Merge / PR / Keep
```

### Why This Order Matters

1. **Design before code** - Prevents building the wrong thing. Brainstorming surfaces trade-offs, constraints, and alternatives *before* any code is written.

2. **Plan before implementation** - Plans are written for "an enthusiastic junior engineer with poor taste, no judgment, no project context, and an aversion to testing." If the plan is clear enough for that person, a fresh agent can execute it perfectly.

3. **Fresh agent per task** - Each task gets a new agent with zero context from previous tasks. This prevents context pollution where mistakes compound across tasks.

4. **Two-stage review** - Spec compliance first (did you build what was asked?), then code quality (did you build it well?). Order matters because there's no point reviewing code quality on something that doesn't meet the spec.

### When to Use the Full Pipeline vs. Parts

| Situation | Approach |
|-----------|----------|
| New feature from scratch | Full pipeline: brainstorm → plan → execute |
| Clear spec already exists | Skip brainstorming: plan → execute |
| Quick bug fix with known cause | Just use `/execute-plan` with a small plan |
| Exploring an idea | Just `/brainstorm` - stop when you have clarity |
| Adding to existing feature | `/write-plan` with existing design context → execute |

---

## Modes Guide

Modes change how the agent behaves by constraining which tools it can use and injecting workflow-specific instructions. Think of them as "mindsets" - each one focuses the agent on a specific phase.

### `/brainstorm` - Design Refinement

**Purpose:** Explore ideas, evaluate trade-offs, and produce a design document.

**What's different in this mode:**
- Write/edit file tools are blocked (no implementation)
- Bash requires confirmation (prevents accidental changes)
- Agent focuses on asking questions and exploring alternatives

**How to use it:**

```
/brainstorm

I want to add rate limiting to our API endpoints.
```

The agent will:
1. Survey your codebase to understand the current architecture
2. Ask clarifying questions **one at a time** (preferring multiple choice)
3. Propose 2-3 approaches with trade-offs
4. Present the design in digestible sections, asking for validation after each
5. Save the approved design to `docs/plans/YYYY-MM-DD-<topic>-design.md`

**When you're done:**

```
/mode off
```

### `/write-plan` - Implementation Planning

**Purpose:** Break a design into bite-sized TDD tasks that a fresh agent can execute.

**Prerequisites:** A design document from `/brainstorm` (or an equivalent spec).

**What's different in this mode:**
- Write/edit are allowed (to save the plan)
- Agent focuses on creating granular, copy-pasteable tasks

**How to use it:**

```
/write-plan

Create an implementation plan from docs/plans/2026-02-07-rate-limiting-design.md
```

The agent will:
1. Read and analyze the design document
2. Break it into tasks of 2-5 minutes each
3. Each task follows: write test → verify fail → implement → verify pass → commit
4. Include exact file paths, complete code blocks, and runnable commands
5. Save the plan to `docs/plans/YYYY-MM-DD-<feature>-implementation.md`

**When you're done:**

```
/mode off
```

### `/execute-plan` - Subagent-Driven Development

**Purpose:** Execute the plan by dispatching fresh agents per task with two-stage review.

**Prerequisites:** An implementation plan from `/write-plan`.

**What's different in this mode:**
- All tools are available (full implementation power)
- Agent acts as an **orchestrator**, dispatching sub-agents
- The pattern is: implementer → spec reviewer → code quality reviewer per task

**How to use it:**

```
/execute-plan

Execute the plan at docs/plans/2026-02-07-rate-limiting-implementation.md
```

The agent will:
1. Load the plan and create a todo list
2. For each task, delegate to `superpowers:implementer` with `context_depth="none"` (fresh start)
3. After implementation, delegate to `superpowers:spec-reviewer` to validate against the spec
4. After spec approval, delegate to `superpowers:code-quality-reviewer` for quality checks
5. Handle any reviewer feedback before moving to the next task

**When you're done:**

```
/mode off
```

### Transitioning Between Modes

The natural flow is:

```
/brainstorm  →  (design complete)  →  /mode off
/write-plan  →  (plan complete)    →  /mode off
/execute-plan →  (tasks complete)  →  /mode off
```

Always exit a mode with `/mode off` before entering the next one. Each mode sets up different tool constraints and behavioral instructions - overlapping them can cause confusion.

**Tip:** You don't need to use modes at all if you prefer recipes. Modes give you interactive, conversational control. Recipes give you automated pipelines with approval gates. See [Modes vs. Recipes](#when-to-use-modes-vs-recipes) for guidance.

---

## Agents Guide

The bundle provides 5 specialized agents. Each has a specific role in the workflow and is designed to be delegated to from a parent session.

### `superpowers:brainstormer`

**Role:** Facilitates design refinement through collaborative dialogue.

**When to use:** Starting any new feature, exploring a rough idea, or when you need to understand trade-offs before committing to an approach.

**Key behaviors:**
- Asks questions one at a time, preferring multiple choice
- Proposes 2-3 approaches with trade-offs
- Presents design in 200-300 word sections with validation after each
- Saves design documents to `docs/plans/`
- Applies YAGNI ruthlessly

**Example delegation:**

```python
delegate(
    agent="superpowers:brainstormer",
    instruction="Explore design options for adding WebSocket support to our REST API. The project is a Python FastAPI app in /home/user/myproject/.",
    context_depth="none"
)
```

### `superpowers:plan-writer`

**Role:** Creates detailed implementation plans with bite-sized TDD tasks.

**When to use:** After a design is approved and you need an actionable plan for implementation.

**Key behaviors:**
- Assumes the implementer has zero context and questionable judgment
- Creates tasks of 2-5 minutes each
- Each task follows the TDD cycle: test → fail → implement → pass → commit
- Includes exact file paths, complete code blocks, and runnable commands
- No placeholders or vague instructions

**Example delegation:**

```python
delegate(
    agent="superpowers:plan-writer",
    instruction="Create an implementation plan from the design at docs/plans/2026-02-07-websocket-design.md. Break it into tasks following TDD.",
    context_depth="none"
)
```

### `superpowers:implementer`

**Role:** Implements a single task following strict TDD.

**When to use:** Executing one task from a plan. Always give this agent a fresh context (`context_depth="none"`) so it doesn't carry over assumptions from previous tasks.

**Key behaviors:**
- Follows RED-GREEN-REFACTOR strictly (test first, watch it fail, minimal code to pass)
- Will delete code written before tests - no exceptions
- Asks questions rather than guessing on ambiguous specs
- Commits atomically after each task
- Performs self-review checklist before signaling completion

**Example delegation:**

```python
delegate(
    agent="superpowers:implementer",
    instruction="""Implement Task 3: Add email validation.

    Files:
    - Create: src/validators/email.py
    - Test: tests/validators/test_email.py

    Step 1: Write test for valid email format
    Step 2: Run test, verify it fails
    Step 3: Implement validate_email() function
    Step 4: Run test, verify it passes
    Step 5: Commit with message 'feat: add email validation'""",
    context_depth="none"
)
```

### `superpowers:spec-reviewer`

**Role:** Validates that implementation matches the specification exactly.

**When to use:** After an implementer completes a task. This is Stage 1 of the two-stage review.

**Key behaviors:**
- Checks that every spec requirement is implemented
- Flags anything implemented that wasn't in the spec
- Does NOT check code style or quality (that's the quality reviewer's job)
- Verdict is binary: APPROVED or NEEDS CHANGES
- "The spec is the contract" - doesn't accept "but this is better" arguments

**Example delegation:**

```python
delegate(
    agent="superpowers:spec-reviewer",
    instruction="""Review Task 3 implementation against spec.

    Spec requirements:
    1. validate_email() accepts a string, returns bool
    2. Must check for @ symbol and valid domain
    3. Must reject empty strings

    Check the implementation in src/validators/email.py and tests/validators/test_email.py.""",
    context_scope="agents"  # Can see implementer's output
)
```

### `superpowers:code-quality-reviewer`

**Role:** Reviews code quality after spec compliance is confirmed.

**When to use:** After the spec reviewer approves. This is Stage 2 of the two-stage review.

**Key behaviors:**
- Only reviews AFTER spec compliance is confirmed
- Checks: clarity, error handling, test quality, design, security, maintainability
- Issues ranked: Critical (must fix) > Important (should fix) > Suggestion (nice to have)
- Every criticism comes with a suggested fix
- Acknowledges good work before listing issues

**Example delegation:**

```python
delegate(
    agent="superpowers:code-quality-reviewer",
    instruction="Review Task 3 (email validation) for code quality. Spec compliance was already approved. Focus on error handling, test quality, and maintainability.",
    context_scope="agents"  # Can see previous agents' output
)
```

---

## Recipes Guide

Recipes are declarative YAML workflows that run multi-step pipelines with approval gates. They're more automated than modes - you kick them off, approve at checkpoints, and they handle the rest.

### How to Run a Recipe

**From inside an Amplifier session:**

```
Execute superpowers:recipes/brainstorming.yaml with topic="rate limiting for API"
```

**From the command line:**

```bash
amplifier run "execute superpowers:recipes/brainstorming.yaml with topic='rate limiting for API'"
```

### Managing Recipe Sessions

Recipes with approval gates pause and wait for human input. Here's how to manage them:

```bash
# List all pending approvals
amplifier run "list pending approvals"

# Approve a stage
amplifier run "approve recipe session <session-id> stage <stage-name>"

# Deny a stage (stops the recipe)
amplifier run "deny recipe session <session-id> stage <stage-name> reason='needs more detail'"

# Resume after approval
amplifier run "resume recipe session <session-id>"

# List active recipe sessions
amplifier run "list recipe sessions"
```

### Recipe 1: Brainstorming

**File:** `superpowers:recipes/brainstorming.yaml`

**What it does:** Turns rough ideas into fully-formed designs through a 6-step process with an approval gate after the design is presented.

**Stages:**
1. **discovery-and-design** - Understands context, explores requirements, proposes approaches, presents design
2. *Approval gate* - Human validates the design
3. **finalization** - Saves the design document, offers handoff to planning

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `topic` | No | `""` | The feature/idea being designed |
| `project_path` | No | `"."` | Path to the project |

**Examples:**

```bash
# With a topic
amplifier run "execute superpowers:recipes/brainstorming.yaml with topic='user authentication with OAuth'"

# Let it discover from conversation
amplifier run "execute superpowers:recipes/brainstorming.yaml"

# Specific project path
amplifier run "execute superpowers:recipes/brainstorming.yaml with topic='caching layer' project_path='/home/user/myapp'"
```

**Output:** Design document saved to `docs/plans/YYYY-MM-DD-<topic>-design.md`

---

### Recipe 2: Writing Plans

**File:** `superpowers:recipes/writing-plans.yaml`

**What it does:** Takes a design document and produces a detailed implementation plan with TDD tasks.

**Stages:**
1. **planning** - Loads design, analyzes requirements, creates plan with TDD tasks
2. *Approval gate* - Human validates the plan
3. **finalization** - Saves the plan, offers execution options

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `design_path` | Yes | `""` | Path to the design document |
| `feature_name` | No | `""` | Extracted from design if not provided |

**Examples:**

```bash
# From a design document
amplifier run "execute superpowers:recipes/writing-plans.yaml with design_path='docs/plans/2026-02-07-auth-design.md'"

# With explicit feature name
amplifier run "execute superpowers:recipes/writing-plans.yaml with design_path='docs/plans/auth-design.md' feature_name='user-authentication'"
```

**Output:** Implementation plan saved to `docs/plans/YYYY-MM-DD-<feature>-plan.md`

---

### Recipe 3: Subagent-Driven Development

**File:** `superpowers:recipes/subagent-driven-development.yaml`

**What it does:** The core execution engine. Dispatches a fresh implementer agent per task, runs two-stage review (spec compliance then code quality), with `foreach` loops over all tasks.

**Stages:**
1. **task-execution** - Loads plan, validates tasks, implements each (foreach), spec reviews each (foreach), quality reviews each (foreach), summarizes
2. *Approval gate* - Human reviews the final comprehensive code review
3. **finish** - Verifies all tests, presents merge options

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `plan_path` | Yes | `""` | Path to the implementation plan |

**Examples:**

```bash
# Execute a plan
amplifier run "execute superpowers:recipes/subagent-driven-development.yaml with plan_path='docs/plans/2026-02-07-auth-plan.md'"
```

**Key features:**
- Fresh agent per task (no context pollution)
- `foreach` loops iterate automatically over all tasks
- Review agents iterate until approved (fix-and-recheck loop)
- Final comprehensive review looks at the implementation holistically

---

### Recipe 4: Executing Plans (Batched)

**File:** `superpowers:recipes/executing-plans.yaml`

**What it does:** Alternative to subagent-driven development. Executes tasks in configurable batches with human checkpoints between each batch.

**Stages:**
1. **plan-review** - Loads plan, performs critical review → *Approval gate*
2. **batch-execution** - Identifies next batch, executes tasks
3. **batch-report** - Generates report, checks remaining → *Approval gate*
4. **feedback-and-next** - Applies feedback, determines next steps
5. **finish** - Verifies completion, presents merge options → *Approval gate*

**Important:** This recipe processes ONE BATCH per execution. Re-run it to process subsequent batches.

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `plan_path` | Yes | `""` | Path to the plan file |
| `batch_size` | No | `3` | Number of tasks per batch |

**Examples:**

```bash
# Default batch size (3 tasks)
amplifier run "execute superpowers:recipes/executing-plans.yaml with plan_path='docs/plans/auth-plan.md'"

# Larger batches
amplifier run "execute superpowers:recipes/executing-plans.yaml with plan_path='docs/plans/auth-plan.md' batch_size=5"

# Re-run for next batch
amplifier run "execute superpowers:recipes/executing-plans.yaml with plan_path='docs/plans/auth-plan.md'"
```

**When to choose this over subagent-driven development:**
- Large plans where you want periodic check-ins
- When you want tighter control over progress
- When you might need to adjust the plan between batches

---

### Recipe 5: Git Worktree Setup

**File:** `superpowers:recipes/git-worktree-setup.yaml`

**What it does:** Creates an isolated git worktree for feature development with automatic project setup and baseline test verification.

**Stages:**
1. **discovery** - Checks for existing worktree directories, determines location, verifies gitignore
2. **worktree-creation** - Creates worktree with `git worktree add`
3. **project-setup** - Auto-detects project type, runs setup commands (npm install, pip install, etc.)
4. **baseline-verification** - Runs tests to verify clean baseline → *Approval gate* (if tests fail, you decide whether to proceed)
5. **completion** - Generates summary with quick-start commands

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `branch_name` | Yes | `""` | Branch name (e.g., `feature/my-feature`) |
| `feature_name` | No | `""` | Descriptive name |
| `worktree_location` | No | `""` | Override default location |

**Examples:**

```bash
# Basic worktree setup
amplifier run "execute superpowers:recipes/git-worktree-setup.yaml with branch_name='feature/rate-limiting'"

# With feature description
amplifier run "execute superpowers:recipes/git-worktree-setup.yaml with branch_name='fix/login-bug' feature_name='Fix login timeout bug'"

# Custom location
amplifier run "execute superpowers:recipes/git-worktree-setup.yaml with branch_name='feature/api' worktree_location='~/worktrees/myproject'"
```

---

### Recipe 6: Finish Branch

**File:** `superpowers:recipes/finish-branch.yaml`

**What it does:** Completes a development branch - runs tests, summarizes changes, and lets you choose how to finish: merge, PR, keep, or discard.

**Stages:**
1. **verify-and-summarize** - Detects branch info, runs tests, summarizes changes
2. **option-selection** - Presents four options → *Approval gate* (you choose)
3. **execute-choice** - Executes your chosen action (merge/PR/keep/discard)
4. **cleanup** - Removes worktree if appropriate, generates final summary

**Options:**

| Option | What It Does | When to Use |
|--------|-------------|-------------|
| **MERGE** | Fast-forward merge to main, delete branch, remove worktree | Ready-to-ship changes (requires passing tests) |
| **PR** | Push branch, create pull request with summary | Changes needing team review |
| **KEEP** | Leave everything as-is | Work in progress |
| **DISCARD** | Delete branch and worktree (destructive) | Abandoned experiments |

**Context variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `branch_name` | No | Auto-detected | The branch to finish |
| `worktree_path` | No | Auto-detected | Path to the worktree |

**Examples:**

```bash
# Auto-detect current branch
amplifier run "execute superpowers:recipes/finish-branch.yaml"

# Specific branch
amplifier run "execute superpowers:recipes/finish-branch.yaml with branch_name='feature/rate-limiting'"
```

**At the approval gate:** Type your choice (MERGE, PR, KEEP, or DISCARD) in the chat, then approve.

---

### Recipe 7: Full Development Cycle (Meta-Recipe)

**File:** `superpowers:recipes/superpowers-full-development-cycle.yaml`

**What it does:** End-to-end autonomous development from idea to merged code. Composes all the individual recipes into a single pipeline.

See the next section for full details.

---

## The Full Development Cycle

The meta-recipe chains the entire Superpowers workflow into a single execution with three approval gates.

### Pipeline

```
Stage 1: DESIGN (approval gate 1)
    - Survey project context
    - Explore requirements
    - Create design document
    - Save to docs/plans/

Stage 2: PLANNING (approval gate 2)
    - Load approved design
    - Create implementation plan with TDD tasks
    - Save to docs/plans/

Stage 3: IMPLEMENTATION (approval gate 3)
    - Create git worktree
    - Execute plan with TDD
    - Debug failures if needed
    - Verify against spec

Stage 4: FINISH
    - Execute chosen action (merge/PR/keep)
    - Clean up
    - Final summary
```

### Running It

```bash
# Basic - just a feature name
amplifier run "execute superpowers:recipes/superpowers-full-development-cycle.yaml with feature_name='user-authentication'"

# With initial description to guide brainstorming
amplifier run "execute superpowers:recipes/superpowers-full-development-cycle.yaml with feature_name='rate-limiting' topic='Add per-user rate limiting to all API endpoints using a sliding window algorithm'"

# Specific project
amplifier run "execute superpowers:recipes/superpowers-full-development-cycle.yaml with feature_name='caching' topic='Redis caching layer' project_path='/home/user/myapi'"
```

### Context Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `feature_name` | Yes | `""` | Name for branch and files (e.g., `user-authentication`) |
| `topic` | No | `""` | Initial idea description for brainstorming |
| `project_path` | No | `"."` | Project directory |

### Approval Gates

The recipe pauses three times for human input:

1. **After design** - Review the design document. Approve to proceed to planning, deny to revise.
2. **After plan** - Review the implementation plan. Approve to proceed to implementation, deny to revise.
3. **After implementation** - Review the completed work. Approve with message:
   - `"merge"` - Merge to main and clean up
   - `"pr"` - Create a pull request
   - `"keep"` - Keep branch for later

### Artifacts Created

After completion, you'll find:
- `docs/plans/YYYY-MM-DD-<feature>-design.md` - The design document
- `docs/plans/YYYY-MM-DD-<feature>-plan.md` - The implementation plan
- A git branch with all implementation commits
- Worktree (if kept) at `worktrees/<feature-slug>`

---

## Composing Into Your Own Bundle

The behavior install described in [Getting Started](#getting-started) is the recommended approach for most users - it works at the app level with any bundle.

For bundle authors who want to include the methodology directly in their bundle configuration:

### Include the Behavior

In your `bundle.md` or bundle YAML:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-superpowers@main#subdirectory=behaviors/superpowers-methodology.yaml
```

This gives you:
- All 5 agents (`superpowers:brainstormer`, `superpowers:plan-writer`, `superpowers:implementer`, `superpowers:spec-reviewer`, `superpowers:code-quality-reviewer`)
- The philosophy and instructions context
- No changes to your providers, tools, or other configuration

### Include Specific Agents

If you only want certain agents, reference them individually in your bundle's agent configuration. The agents are in the `agents/` directory of the superpowers bundle.

### Include Just the Skills

If you only want the original Superpowers skills library (without agents or modes), add the skills source:

```yaml
skills:
  sources:
    - git+https://github.com/obra/superpowers@main#subdirectory=skills
```

Then use them in your sessions with `load_skill(skill_name="test-driven-development")`.

### Include Modes

To get the workflow modes, add the hooks-mode module:

```yaml
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - modes
```

And include the mode files from the superpowers bundle.

---

## Tips & Best Practices

### When to Use Modes vs. Recipes

| Use **Modes** when... | Use **Recipes** when... |
|----------------------|----------------------|
| You want interactive, conversational control | You want automated pipelines |
| You're exploring and might change direction | You have a clear path forward |
| You want to guide the process step by step | You want to kick it off and approve at gates |
| You're pairing with the agent | You want maximum autonomy between checkpoints |
| It's a small, focused task | It's a multi-step workflow |

**The hybrid approach:** Use `/brainstorm` interactively (you want to guide the design conversation), then use the `writing-plans.yaml` recipe (planning is more mechanical), then use `subagent-driven-development.yaml` (execution should be autonomous).

### How to Write Effective Brainstorming Prompts

**Good prompts give context and constraints:**

```
I want to add caching to our API. We're running FastAPI with PostgreSQL.
The main bottleneck is the /users endpoint which gets 10k requests/minute.
We need sub-100ms response times. Budget is limited so prefer in-memory over Redis.
```

**Less effective:**

```
Add caching.
```

**Tips for brainstorming:**
- State the **problem**, not just the solution you imagine
- Mention **constraints** (tech stack, performance requirements, team size)
- Share **context** (what you've tried, what you're worried about)
- Be honest about **unknowns** ("I'm not sure if we need WebSockets or SSE")

### Common Pitfalls and How to Avoid Them

**Pitfall 1: Skipping brainstorming for "simple" features**

Even small features benefit from 5 minutes of design thinking. The brainstormer will often surface edge cases you hadn't considered.

*Fix:* At minimum, ask the brainstormer to propose 2-3 approaches even for small features. You might be surprised.

**Pitfall 2: Plans with tasks that are too large**

If a task takes more than 5 minutes, the implementer agent is more likely to make mistakes or deviate from the spec.

*Fix:* Break large tasks into smaller ones. "Implement the user service" should be 3-5 tasks: create model, add validation, implement CRUD operations, add error handling, wire up routes.

**Pitfall 3: Not giving the implementer a fresh context**

If you delegate to the implementer with `context_depth="all"`, it carries assumptions from previous tasks, which can cause it to "improve" things that aren't in its current spec.

*Fix:* Always use `context_depth="none"` for implementer agents. Include everything they need in the instruction itself.

**Pitfall 4: Running spec review and quality review in the wrong order**

Quality reviewing code that doesn't meet the spec wastes time. You'll need to redo the quality review after spec fixes anyway.

*Fix:* Always run spec review first. Only run quality review after spec is approved.

**Pitfall 5: Approving a plan you haven't read**

The approval gates exist for a reason. Rubber-stamping a plan means bugs in the plan become bugs in the code.

*Fix:* At minimum, check that file paths look right, task sizes are reasonable, and the TDD flow is complete (test → fail → implement → pass → commit for each task).

### Working with the Two-Stage Review Pattern

The two-stage review is the heart of Superpowers quality assurance:

**Stage 1: Spec Compliance** (`superpowers:spec-reviewer`)
- Asks: "Does the implementation match the spec?"
- Checks: Everything in spec is implemented, nothing extra, behavior matches exactly
- Does NOT check: Code style, naming, error handling quality, performance

**Stage 2: Code Quality** (`superpowers:code-quality-reviewer`)
- Asks: "Is the implementation well-built?"
- Checks: Clean code, error handling, test quality, design, security, maintainability
- Does NOT check: Whether the right thing was built (that's Stage 1's job)
- Only runs after Stage 1 approves

**When reviews find issues:** The subagent-driven-development recipe includes fix-and-recheck loops. Reviewers fix issues themselves and re-review until approved. In manual mode, you'll need to address feedback and re-run the review.

### When to Override TDD (and When Never To)

**Never skip TDD for:**
- Business logic
- Data transformations
- Validation rules
- API endpoints
- Anything with conditional behavior

**Reasonable to relax TDD for:**
- Pure configuration files (YAML, JSON)
- Static content (HTML templates, copy)
- One-line wiring code (imports, route registration)
- Generated code (migrations, scaffolding)

Even in relaxed cases, **integration tests should still exist** to verify the wiring works. The implementer agent will follow TDD strictly by default - if you want to relax it, you need to explicitly say so in the task spec.

### Maximizing Autonomous Operation

To get the most autonomous behavior (agent works for hours without intervention):

1. **Use the meta-recipe** - The full development cycle recipe chains everything together
2. **Provide a detailed topic** - More context in the initial prompt = fewer questions
3. **Pre-create a design document** - Skip brainstorming if you already know what you want
4. **Use subagent-driven development** over batched execution - It handles the full task loop automatically
5. **Trust the approval gates** - They're your safety net. Let the agent work freely between them.

---

## Quick Reference

### Commands

| Command | Purpose |
|---------|---------|
| `/brainstorm` | Enter design refinement mode |
| `/write-plan` | Enter implementation planning mode |
| `/execute-plan` | Enter subagent-driven execution mode |
| `/modes` | List all available modes |
| `/mode off` | Exit current mode |

### Agents

| Agent | Purpose | Context Setting |
|-------|---------|----------------|
| `superpowers:brainstormer` | Design refinement | `context_depth="none"` |
| `superpowers:plan-writer` | Implementation planning | `context_depth="none"` |
| `superpowers:implementer` | TDD implementation | `context_depth="none"` (always fresh) |
| `superpowers:spec-reviewer` | Spec compliance review | `context_scope="agents"` |
| `superpowers:code-quality-reviewer` | Code quality review | `context_scope="agents"` |

### Recipes

| Recipe | CLI Example |
|--------|-------------|
| **Brainstorming** | `amplifier run "execute superpowers:recipes/brainstorming.yaml with topic='my feature'"` |
| **Writing Plans** | `amplifier run "execute superpowers:recipes/writing-plans.yaml with design_path='docs/plans/design.md'"` |
| **Subagent Dev** | `amplifier run "execute superpowers:recipes/subagent-driven-development.yaml with plan_path='docs/plans/plan.md'"` |
| **Executing Plans** | `amplifier run "execute superpowers:recipes/executing-plans.yaml with plan_path='docs/plans/plan.md' batch_size=3"` |
| **Git Worktree** | `amplifier run "execute superpowers:recipes/git-worktree-setup.yaml with branch_name='feature/x'"` |
| **Finish Branch** | `amplifier run "execute superpowers:recipes/finish-branch.yaml"` |
| **Full Cycle** | `amplifier run "execute superpowers:recipes/superpowers-full-development-cycle.yaml with feature_name='my-feature'"` |

### Skills

| Skill | Load Command |
|-------|-------------|
| All available | `load_skill(list=True)` |
| Search | `load_skill(search="superpowers")` |
| TDD | `load_skill(skill_name="test-driven-development")` |
| Debugging | `load_skill(skill_name="systematic-debugging")` |
| Brainstorming | `load_skill(skill_name="brainstorming")` |
| Planning | `load_skill(skill_name="writing-plans")` |
| Subagent Dev | `load_skill(skill_name="subagent-driven-development")` |
| Verification | `load_skill(skill_name="verification-before-completion")` |

### The Two-Stage Review Flow

```
Implementation Complete
         |
         v
  Spec Compliance Review  ──FAIL──> Fix, re-review
         |
       PASS
         |
         v
  Code Quality Review  ──FAIL──> Fix, re-review
         |
       PASS
         |
         v
    Next Task (or Done)
```

### Key Principles (Cheat Sheet)

1. **Design before code** - Always brainstorm first
2. **TDD always** - No production code without a failing test
3. **Fresh agent per task** - `context_depth="none"` for implementers
4. **Spec first, quality second** - Two-stage review in order
5. **Evidence over claims** - Prove it works, don't just say it does
6. **YAGNI** - Don't build what you don't need yet
7. **Human checkpoints** - Approval gates at every critical point

---

## Acknowledgments

The Superpowers methodology was created by [Jesse Vincent](https://github.com/obra) and the contributors to [Superpowers](https://github.com/obra/superpowers). This bundle brings that methodology to the Amplifier ecosystem with native agents, modes, and recipes.

The original skills library is fetched directly from GitHub at runtime - this bundle adds the Amplifier integration layer on top of that foundation.
