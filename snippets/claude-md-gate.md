# The "Prompt it?" gate — for `~/.claude/CLAUDE.md`

The skill produces the plan. **This** is what makes Claude *offer* it, so you are never
surprised by a planning document you did not want. Install both, or people will blame
the skill for being pushy.

Append this to `~/.claude/CLAUDE.md` (create the file if it does not exist):

```markdown
## Working mode: offer to prompt it first

Before a substantial new task, ask exactly `Prompt it?` and wait.

- Yes (or a direct “prompt it” request): use the installed `prompt-it` edition.
  Follow its research boundaries, write the evidence-backed brief and staffing,
  then stop for execution approval.
- In the engineer edition, native read-only helpers follow runtime rules;
  external research requires explicit bounded authority (reuse existing
  authorization). The read-only edition retains its own rules.
- No: proceed normally.
- Skip this gate for questions, status checks, lookups, conversational replies,
  follow-ups already underway, and one-line edits.
```

You can put this in a project-level `CLAUDE.md` instead if you only want the gate in
one repository.
