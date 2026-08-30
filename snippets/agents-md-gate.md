# The "Prompt it?" gate — for `~/.codex/AGENTS.md`

The installed skill performs the research and writes the brief. This loader
block makes Codex offer the workflow before substantial new tasks while leaving
questions, lookups, follow-ups, and small edits alone.

Append this to `~/.codex/AGENTS.md` (create the file if it does not exist):

```markdown
## Working mode: offer to prompt it first

Before a substantial new task, ask exactly `Prompt it?` and wait.

- Yes: use the installed `prompt-it` skill. Research read-only, write the
  evidence-backed brief and staffing proposal, then stop for approval.
- No: proceed normally.
- Skip this gate for questions, status checks, lookups, conversational replies,
  follow-ups already underway, and one-line edits.
```

Put the block in a repository-level `AGENTS.md` instead when the gate should
apply only to that repository.
