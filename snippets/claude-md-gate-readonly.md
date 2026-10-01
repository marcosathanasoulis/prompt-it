# Automatic proportional planning loader — for `~/.claude/CLAUDE.md` (read-only edition)

The installed `prompt-it-readonly` skill performs the planning research and
writes the reviewable plan document. This loader block makes Claude Code begin
automatic proportional planning before substantial new research or analysis
tasks while leaving questions, lookups, and follow-ups alone; small tasks get
a concise plan and proportional research under existing authority.

The read-only edition has no `scripts/mode.py` and no Ask first/Just go mode
file — use this snippet, not `claude-md-gate.md`, when `prompt-it-readonly` is
the installed plugin. `claude-md-gate.md` references first-use mode setup that
only the engineer `prompt-it` edition implements.

Replace any earlier Prompt it gate block in `~/.claude/CLAUDE.md` with the block
below. Look for a heading such as `## Working mode:` or any block containing
`Ask exactly "Prompt it?" and wait.` Append the block below only if no such block
is present. Create the file if it does not exist. Preserve unrelated global instructions.

```markdown
## Working mode: automatic proportional planning (read-only)

Before a substantial new research, analysis, or design task, use the installed
Prompt it read-only skill.

- For medium/large or plan-only work, draft the plan file, present the goal,
  staffing table, and open questions, then wait. Silence is never approval.
- For mini/small tasks, continue bounded read-only analysis under the
  original request authority when no material question or gate remains.
- This edition never implements, writes code, commits, deploys, or mutates
  data. There is no Ask first/Just go mode file; every task follows this same
  proportional wait rule.
- Skip automatic planning for questions, status checks, lookups, conversational
  replies, and follow-ups already underway.

```

Put the block in a project-level `CLAUDE.md` instead when the gate should apply
only to one repository.
