---
name: prompt-it
description: Before a substantial new task, ask “Prompt it?”; on yes, research read-only and draft an evidence-backed execution brief plus staffing for approval. On no, proceed normally. Skip questions, status checks, lookups, follow-ups already underway, and one-line edits.
---

# Prompt It

Turn a substantial request into a researched, reviewable execution brief before
implementation. The user approves the brief and staffing after seeing what the
research changed.

## Gate

Before implementation, delegation, repository inspection, planning, or an
external write for a substantial new task, ask exactly: **“Prompt it?”**

- No means proceed normally.
- Yes authorizes the bounded read-only research below, not implementation.
- A direct “prompt it” means yes; do not ask again.
- Skip the gate for questions, status checks, read-only lookups, conversation,
  follow-ups already underway, and one-line edits.

## Research before drafting

Read the applicable instructions, project memory, coordination files, source,
tests, history, prior prompts, issues, connected read-only sources, and current
official documentation needed to establish the real seams and constraints.
Use the selected coordinator model for research that shapes scope or design.
Do not delegate this discovery.

Research may not implement, create branches/worktrees, dispatch agents, mutate
external systems, expose secrets, or incur material cost without approval.
Distinguish verified facts from inference and cite the surface checked.

## Write the brief

For repository work, write .scratch/PROMPT-name.md while following repository
coordination rules. This brief is the only pre-approval task write. Include:

- Goal
- verified context and existing reuse seams
- Out of scope
- Success criteria with meaningful tests
- Proposed design/build detail proportional to the task
- Security, compatibility, failure, rollout, and operational implications when relevant
- Open questions only when a material user decision remains
- Staffing after sign-off

Ask fewer, better questions. Resolve discoverable facts yourself. When a user
choice remains, explain the tradeoff and recommend an option.

## Staff approved execution

Split only genuinely independent inputs or a clear build-then-verify seam.
Sequential work sharing context stays together. Present:

| # | Subtask | Executor | Required capabilities | Depends on |
|---|---|---|---|---|

Choose only executors actually available in the current environment. Pin every
model. Keep architecture, authorization, privacy-sensitive decisions,
production actions, and final acceptance with the coordinator.

### Optional external side lanes

The generic side-lane package is optional and separate from Prompt It. If the
side-lane executable is already installed, Prompt It may run a presence-only
check-capabilities command for a candidate exact host/provider/model route.
That check must not retrieve a key or invoke a paid model.

Name an external lane only when the package, originating host adapter, exact
route, credential presence, and required capabilities report configured.
Staffing must name host, provider/model, worktree task, and capabilities.
Capability or spend/extra-usage may influence the explicit choice, but never
causes automatic fallback, quota detection, substitution, or equivalence
claims.

If side-lane is absent or any route is unavailable, continue ordinary in-host
staffing unchanged. Do not install it, block brief creation, or swap an
approved executor. After approval, a route that becomes unavailable fails
closed and returns to the user for a staffing decision.

## Handoff and stop

Provide the clickable brief path, one-line goal, consequential verified
findings/decisions, staffing table, and open questions or “none.” State that
implementation has not started. Then stop.

On “go,” reread the brief from disk, reconcile user edits, follow repository
coordination rules, and execute only the approved scope and staffing.
