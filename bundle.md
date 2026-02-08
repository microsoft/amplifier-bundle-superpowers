---
bundle:
  name: superpowers
  version: 1.0.0
  description: Agentic skills framework and software development methodology - TDD, subagent-driven development, systematic debugging

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: superpowers:behaviors/superpowers-methodology.yaml

# Mode hook to discover superpowers modes (brainstorm, write-plan, execute-plan, debug, verify, finish)
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - modes

# Skills from original obra/superpowers (fetched and cached automatically)
skills:
  sources:
    - git+https://github.com/obra/superpowers@main#subdirectory=skills
---

# Superpowers Development Methodology

You have access to the Superpowers development methodology - a comprehensive framework for building software with AI assistance.

@superpowers:context/philosophy.md
@superpowers:context/instructions.md

---

## Core Principles

1. **Design Before Code** - Always brainstorm and create a spec before implementation
2. **Test-Driven Development** - Write the test first, watch it fail, write minimal code
3. **Subagent-Driven Development** - Fresh agent per task with two-stage review
4. **Verification Before Completion** - Prove it works, don't just claim it

## The Superpowers Workflow

```
/brainstorm  ->  Design Document
      |
/write-plan  ->  Implementation Plan (bite-sized tasks)
      |
/execute-plan  ->  Subagent-Driven Development
      |               Per Task:
      |               1. Implementer agent (implements + tests + commits)
      |               2. Spec reviewer agent (validates against spec)
      |               3. Code quality reviewer agent (ensures quality)
      |
/verify  ->  Evidence-based verification (tests, behavior, edge cases)
      |
/finish  ->  Branch completion (merge / PR / keep / discard)
```

**Two tracks to the same destination:**

| Track | How | Best For |
|-------|-----|----------|
| **Interactive modes** | `/brainstorm` → `/write-plan` → `/execute-plan` → `/verify` → `/finish` | Hands-on sessions where you want control at each step |
| **Recipe automation** | `superpowers-full-development-cycle.yaml` | End-to-end automation with approval gates between stages |

Both tracks use the same agents, the same TDD process, and the same review pipeline. Modes give you the steering wheel; recipes give you cruise control.

**Off-ramp at any time:** `/debug` when something breaks. It rejoins the main flow at `/verify` after the fix.

## Available Commands

| Command | Purpose | Next Step |
|---------|---------|-----------|
| `/brainstorm` | Refine idea into a solid design through collaborative dialogue | `/write-plan` |
| `/write-plan` | Create detailed implementation plan with bite-sized TDD tasks | `/execute-plan` |
| `/execute-plan` | Orchestrate implementation via subagent pipeline with two-stage review | `/verify` |
| `/debug` | Systematic 4-phase debugging: reproduce, hypothesize, test, fix | `/verify` |
| `/verify` | Collect fresh evidence that everything works - no claims without proof | `/finish` or `/debug` |
| `/finish` | Verify tests, summarize work, present merge/PR/keep/discard options | Session complete |

## Available Agents

| Agent | Purpose |
|-------|---------| 
| `superpowers:implementer` | Implements tasks following TDD |
| `superpowers:spec-reviewer` | Reviews code against spec compliance |
| `superpowers:code-quality-reviewer` | Reviews code quality and best practices |
| `superpowers:brainstormer` | Facilitates design refinement |
| `superpowers:plan-writer` | Creates detailed implementation plans |

## Available Recipes

| Recipe | Purpose |
|--------|---------| 
| `superpowers:recipes/brainstorming.yaml` | Refine ideas into designs (staged, approval gate) |
| `superpowers:recipes/writing-plans.yaml` | Create TDD implementation plans (staged, approval gate) |
| `superpowers:recipes/subagent-driven-development.yaml` | Fresh agent per task with foreach + two-stage review |
| `superpowers:recipes/executing-plans.yaml` | Batch execution with human checkpoints |
| `superpowers:recipes/git-worktree-setup.yaml` | Isolated worktree with project setup |
| `superpowers:recipes/finish-branch.yaml` | Branch completion (merge/PR/keep/discard) |
| `superpowers:recipes/superpowers-full-development-cycle.yaml` | End-to-end: idea to merged code |

## Skills Library

The full Superpowers skills library is available via the skills tool:

- **test-driven-development** - RED-GREEN-REFACTOR cycle
- **systematic-debugging** - 4-phase root cause analysis
- **brainstorming** - Design refinement process
- **writing-plans** - Implementation plan creation
- **subagent-driven-development** - Task execution with reviews
- **verification-before-completion** - Prove it works
- And more...

Use `load_skill(search="superpowers")` to discover available skills.

---

@foundation:context/shared/common-system-base.md
