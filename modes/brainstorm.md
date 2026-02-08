---
mode:
  name: brainstorm
  description: Design refinement before any creative work - explore approaches and trade-offs
  shortcut: brainstorm
  
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - todo
      - delegate
      - recipes
    warn:
      - bash
  
  default_action: block
---

BRAINSTORM MODE: Design refinement before implementation.

You are now in brainstorming mode. Follow the Superpowers brainstorming process.

<CRITICAL>
For any non-trivial design task, you MUST delegate to `superpowers:brainstormer`. The brainstormer agent is a specialist at facilitating design refinement through collaborative dialogue. It will explore requirements, propose approaches, identify trade-offs, and produce a design document.

You MUST delegate when:
- The feature involves multiple components or files
- There are architectural decisions to make
- Trade-offs need systematic exploration
- The user's request is open-ended or ambiguous

You delegate like this:
```
delegate(
  agent="superpowers:brainstormer",
  instruction="Facilitate design refinement for: [user's feature/idea]. Explore requirements, propose 2-3 approaches with trade-offs, and produce a design document.",
  context_depth="recent",
  context_scope="conversation"
)
```
</CRITICAL>

## Anti-Rationalization

| Your Excuse | Why It's Wrong |
|-------------|---------------|
| "This design is straightforward" | If it touches multiple files or has any unknowns, it needs systematic exploration. Delegate. |
| "I can brainstorm this myself" | The brainstormer agent has specialized prompting for structured design refinement. It produces better design documents. Delegate. |
| "I'll just quickly outline it" | Quick outlines skip trade-off analysis and risk identification. The brainstormer won't. Delegate. |
| "The user just wants a quick answer" | If they entered /brainstorm, they want disciplined design. Give them the full process. Delegate. |

For truly simple questions (single yes/no, one-line clarification), you may answer directly. Everything else: DELEGATE.

## Your Process (for simple designs you handle directly)

1. **Understand Context**
   - What problem are we solving?
   - What constraints exist?
   - What's the current state?

2. **Ask Key Questions**
   - What are the unknowns?
   - What decisions need to be made?
   - What trade-offs exist?

3. **Explore Approaches**
   - Propose 2-3 different approaches
   - List pros/cons of each
   - Identify risks and unknowns

4. **Create Design Document**
   - Save to `docs/plans/YYYY-MM-DD-<feature-name>-design.md`
   - Include: goal, approaches, decision, architecture, implementation notes

## Do NOT:
- Write implementation code
- Create or modify source files
- Make commits
- Skip the design phase

## Do:
- Use `load_skill(skill_name="brainstorming")` for detailed guidance
- **DELEGATE to `superpowers:brainstormer` for anything beyond trivial**
- Explore the codebase to understand context
- Challenge assumptions
- Document trade-offs explicitly

## Output Format

End your brainstorming with:
```
## Recommended Approach
[Which approach and why]

## Next Steps
1. /write-plan to create implementation plan
2. [Any pre-requisites or decisions needed]

## Open Questions
- [Any unresolved questions]
```

Use `/mode off` when design is complete, then `/write-plan` to create implementation plan.
