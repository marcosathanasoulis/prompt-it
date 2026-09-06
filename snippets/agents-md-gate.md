# The "Prompt it?" gate — for `~/.codex/AGENTS.md`

The installed skill performs the research and writes the brief. This loader
block makes Codex offer the workflow before substantial new tasks while leaving
questions, lookups, follow-ups, and small edits alone.

Append this to `~/.codex/AGENTS.md` (create the file if it does not exist):

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

Put the block in a repository-level `AGENTS.md` instead when the gate should
apply only to that repository.
