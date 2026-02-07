---
bundle:
  name: superpowers
  version: 1.0.0
  description: Agentic skills framework and software development methodology - TDD, subagent-driven development, systematic debugging

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: superpowers:behaviors/superpowers-methodology.yaml

# Mode hook to discover superpowers modes (brainstorm, write-plan, execute-plan)
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - modes

# Skills from original obra/superpowers (included as submodule)
skills:
  dirs:
    - superpowers:skills
---

# Superpowers Development Methodology

You have access to the Superpowers development methodology - a comprehensive framework for building software with AI assistance.

@superpowers:context/superpowers-methodology.md

---

## Core Principles

1. **Design Before Code** - Always brainstorm and create a spec before implementation
2. **Test-Driven Development** - Write the test first, watch it fail, write minimal code
3. **Subagent-Driven Development** - Fresh agent per task with two-stage review
4. **Verification Before Completion** - Prove it works, don't just claim it

## The Superpowers Workflow

```
/brainstorm → Design Document
     ↓
/write-plan → Implementation Plan (bite-sized tasks)
     ↓
/execute-plan → Subagent-Driven Development
     ↓
     Per Task:
     1. Implementer agent (implements + tests + commits)
     2. Spec reviewer agent (validates against spec)
     3. Code quality reviewer agent (ensures quality)
     ↓
Finished Branch → PR or Merge
```

## Available Commands

| Command | Purpose |
|---------|---------|
| `/brainstorm` | Start design refinement before any creative work |
| `/write-plan` | Create detailed implementation plan from spec |
| `/execute-plan` | Execute plan using subagent-driven development |

## Available Agents

| Agent | Purpose |
|-------|---------|
| `superpowers:implementer` | Implements tasks following TDD |
| `superpowers:spec-reviewer` | Reviews code against spec compliance |
| `superpowers:code-quality-reviewer` | Reviews code quality and best practices |
| `superpowers:brainstormer` | Facilitates design refinement |
| `superpowers:plan-writer` | Creates detailed implementation plans |

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
