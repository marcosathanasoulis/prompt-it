# Automatic proportional planning loader — for `~/.codex/AGENTS.md`

The installed skill performs the planning research and writes the brief. This
loader block makes Codex begin automatic proportional planning before substantial
new tasks while leaving questions, lookups, and follow-ups alone; small edits get
a concise plan and proportional Side Lane assessment.

Replace any earlier Prompt it gate block in `~/.codex/AGENTS.md` with the block
below. Look for a heading such as `## Working mode:` or any block containing
`Ask exactly "Prompt it?" and wait.` Append the block below only if no such block
is present. Create the file if it does not exist. Preserve unrelated global instructions.

```markdown
## Working mode: automatic proportional planning

Before a substantial new task, use the installed Prompt it skill and its saved
Ask first or Just go mode. At first setup ask which mode the user wants, save it
with the skill's `scripts/mode.py`, and explain that they can say “switch Prompt
it to Ask first” or “switch Prompt it to Just go” mid-session. A direct mode
request changes the current task's next gate immediately.

- **Ask first:** ask “Prompt it for this task?” before full research. If yes, announce “Making a plan”,
  research and write the evidence-backed brief and staffing, then ask `Proceed?`
  and wait for approval of both. Silence is never consent.
- **Just go:** research, write and show the proportional brief and staffing,
  ask only genuinely blocking questions, and execute with documented defaults
  under the original task authority.
- A plan-only request stops at the brief in either mode.
- A direct “prompt it” request satisfies Ask first's opt-in, not its plan approval.
- In the engineer edition, native read-only helpers follow runtime rules;
  external research requires explicit bounded authority (reuse existing
  authorization). The read-only edition retains its own rules.
- Skip automatic planning for questions, status checks, lookups, conversational
  replies, and follow-ups already underway.
- Planning never grants external writes, billable research, purchases,
  destructive action, or credentials. Preserve every separate authority gate
  and stronger repository rule. Side Lane dispatch — local or governed —
  keeps its own permission and authority contract from the installed Side
  Lane skill; this planning gate does not restate or substitute for it.
- At staffing time, with the private local-direct Side Lane package installed,
  use its shared selector. With the public Governed Side Lane package installed
  instead, use its own `check-capabilities`/`recommend` flow rather than the
  shared selector, which it does not have. Without either, assess verified
  local Claude Code, Codex, Devin, and Gemini access plus native agents; never
  infer readiness from CLI presence. Record exact model fit, capabilities,
  authority, and one qualified backup where available. A missing eligible
  route is an explicit recorded exception.

```

Put the block in a repository-level `AGENTS.md` instead when the gate should
apply only to that repository.
