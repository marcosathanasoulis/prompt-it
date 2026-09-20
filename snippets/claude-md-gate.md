# Automatic proportional planning loader — for `~/.claude/CLAUDE.md`

The installed skill performs the planning research and writes the brief. This
loader block makes Claude Code begin automatic proportional planning before
substantial new tasks while leaving questions, lookups, and follow-ups alone;
small edits get a concise plan and proportional Side Lane assessment.

Replace any earlier Prompt it gate block in `~/.claude/CLAUDE.md` with the block
below. Look for a heading such as `## Working mode:` or any block containing
`Ask exactly "Prompt it?" and wait.` Append the block below only if no such block
is present. Create the file if it does not exist. Preserve unrelated global instructions.

```markdown
## Working mode: automatic proportional planning

Before a substantial new task, begin automatic proportional planning and an
economical qualified Side Lane assessment.

- **Mini/small work (including one-line edits):** produce a concise plan with
  sensible defaults, then execute under the original task authority. Unresolved
  safety, scope, credential, destructive-action, or spend gates still require
  explicit consent. A one-line trivial edit can use an implicit brief mental plan
  and a proportional Side Lane assessment.
- **Medium/large work or an explicit plan request:** announce "Making a plan",
  research read-only, return a canonical plan link and any material questions
  with recommended defaults, then ask `Proceed?` and wait. Silence is never
  consent. Write the evidence-backed brief and staffing, then stop for execution approval.
- A direct "prompt it" request begins planning immediately; the request itself
  authorizes bounded read-only research.
- In the engineer edition, native read-only helpers follow runtime rules;
  external research requires explicit bounded authority (reuse existing
  authorization). The read-only edition retains its own rules.
- Skip automatic planning for questions, status checks, lookups, conversational
  replies, and follow-ups already underway.
- Planning consent does not authorize connector/external writes, billable paid
  research, or Side Lane dispatch; those keep their existing explicit gates.
- Always assess an economical qualified Side Lane route before substantial
  execution; accepting or skipping a plan does not disable routing. Small work
  uses a proportional Side Lane assessment under existing authority. Preserve
  exact route/mode/capability/task-fit/spend authority, the approved backup, and
  one primary at a time. A missing eligible route is an explicit recorded
  exception, never silent coordinator execution. Public packages do not impose a
  global eligible-route percentage mandate.
```

Put the block in a project-level `CLAUDE.md` instead when the gate should apply
only to one repository.
