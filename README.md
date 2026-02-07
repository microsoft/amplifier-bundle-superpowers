# amplifier-bundle-superpowers

Amplifier bundle for [Superpowers](https://github.com/obra/superpowers), the excellent agentic skills framework and software development methodology created by [Jesse Vincent](https://github.com/obra).

## About Superpowers

[Superpowers](https://github.com/obra/superpowers) is a battle-tested development methodology that transforms how AI coding agents work. Rather than letting agents jump straight to writing code, Superpowers enforces a disciplined workflow: design first, plan carefully, implement with TDD, and review rigorously. The result is agents that can work autonomously for hours without deviating from your plan.

The project has earned significant community adoption (43k+ stars) for good reason - it works. The core skills (brainstorming, test-driven development, subagent-driven development, systematic debugging, and more) represent hard-won lessons about what makes AI-assisted development reliable.

This bundle brings full Superpowers support to [Amplifier](https://github.com/microsoft/amplifier), including the original skills library, Amplifier-native agents for the key workflow roles, workflow modes, and a recipe for the subagent-driven development pattern.

## What This Bundle Provides

- **The complete Superpowers skills library** - All 14 original skills, loaded via Amplifier's skills system
- **5 specialized agents** - Amplifier-native agents for brainstorming, planning, implementation, and two-stage review
- **3 workflow modes** - `/brainstorm`, `/write-plan`, `/execute-plan` as Amplifier mode shortcuts
- **Subagent-driven development recipe** - The core execution workflow as a declarative Amplifier recipe
- **Composable behavior** - Include just the methodology in your own bundles

## Quick Start

```bash
# Add the bundle
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-superpowers@main --name superpowers

# Activate it
amplifier bundle use superpowers

# Start a session
amplifier
```

## The Workflow

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
Finished → PR or Merge
```

## Modes

The bundle provides three workflow modes:

| Mode | Shortcut | Purpose |
|------|----------|---------|
| `brainstorm` | `/brainstorm` | Design refinement - explore approaches and trade-offs |
| `write-plan` | `/write-plan` | Create detailed implementation plan with TDD tasks |
| `execute-plan` | `/execute-plan` | Execute plan with subagent-driven development |

Use `/modes` to list all available modes, `/mode off` to exit a mode.

## Agents

| Agent | Purpose |
|-------|---------|
| `superpowers:brainstormer` | Facilitates design refinement through dialogue |
| `superpowers:plan-writer` | Creates detailed implementation plans |
| `superpowers:implementer` | Implements tasks following strict TDD |
| `superpowers:spec-reviewer` | Reviews code against spec compliance |
| `superpowers:code-quality-reviewer` | Reviews code quality and best practices |

## Skills Library

The original [Superpowers skills](https://github.com/obra/superpowers) are included and available via the skills tool:

- **test-driven-development** - RED-GREEN-REFACTOR cycle
- **systematic-debugging** - 4-phase root cause analysis
- **brainstorming** - Design refinement process
- **writing-plans** - Implementation plan creation
- **subagent-driven-development** - Task execution with reviews
- **verification-before-completion** - Prove it works

Use `load_skill(search="superpowers")` to discover all available skills.

## Composing Just the Methodology

If you want to add the Superpowers agents and methodology to your own bundle without replacing your entire configuration, include just the behavior:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-superpowers@main#subdirectory=behaviors/superpowers-methodology.yaml
```

This gives you the 5 agents and methodology context without changing your providers, tools, or other configuration.

## Bundle Structure

```
amplifier-bundle-superpowers/
├── bundle.md                              # Root bundle (thin pattern)
├── behaviors/
│   └── superpowers-methodology.yaml       # Composable behavior
├── agents/
│   ├── brainstormer.md                    # Design refinement
│   ├── plan-writer.md                     # Implementation planning
│   ├── implementer.md                     # TDD implementation
│   ├── spec-reviewer.md                   # Spec compliance review
│   └── code-quality-reviewer.md           # Code quality review
├── modes/
│   ├── brainstorm.md                      # /brainstorm mode
│   ├── write-plan.md                      # /write-plan mode
│   └── execute-plan.md                    # /execute-plan mode
├── context/
│   └── superpowers-methodology.md         # Core methodology
└── recipes/
    └── subagent-driven-development.yaml   # Workflow recipe
```

## Acknowledgments

This bundle exists because of the outstanding work by [Jesse Vincent](https://github.com/obra) and the contributors to [Superpowers](https://github.com/obra/superpowers). The methodology, skills, and workflow patterns in this bundle originate from that project. We built this bundle to bring Superpowers support to Amplifier users because we believe it represents some of the best thinking on how to make AI-assisted software development disciplined and reliable.

The original Superpowers project is included as a submodule and its skills are loaded directly - this bundle adds Amplifier-native agents, modes, and recipes on top of that foundation.

Superpowers is licensed under the [MIT License](https://github.com/obra/superpowers/blob/main/LICENSE).

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

---

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
