---
name: prompt-it
description: Before a substantial new task, ask “Prompt it?”; on yes, research it read-only with the user-selected model and draft an evidence-backed execution brief plus model staffing for approval. On no, proceed normally. Skip the gate for questions, status checks, lookups, conversational replies, follow-ups already underway, and one-line edits.
---

# Prompt It

Turn a substantial request into a researched, reviewable execution brief before
implementation. The user approves the brief and staffing after seeing what the
research changed.

## Gate substantial new tasks

Before implementation, delegation, repository inspection, planning, or an
external write for a substantial new task, ask exactly: **“Prompt it?”**

- If the user says no, proceed normally without this workflow.
- If the user says yes, begin the bounded research phase below.
- If the user directly says “prompt it” or asks for a prompt to review, treat
  that as yes; do not ask the gate again.
- Do not ask for questions, status checks, read-only lookups, conversational
  replies, follow-ups within work already underway, or one-line edits.
- Infer immediate intent. An unfinished sentence, acknowledgement, or request
  for an update does not open a separate task.
- If a request initially appears substantial but research proves it is a tiny
  change, say so in the brief handoff and keep the brief correspondingly short.

## Research before drafting

The user's yes authorizes the currently selected coordinator model to perform
the read-only research reasonably needed to make the brief accurate. This is
research authorization, not implementation authorization.

### What the research phase may do

Use relevant read-only sources available in the current environment, including:

- user-provided files, examples, links, and prior decisions;
- applicable instructions, project memory, active-work coordination files,
  repository files, tests, history, prior prompts, issues, and design docs;
- code-graph, search, context, and impact tools required by repository rules;
- relevant neighboring repositories and existing integration seams;
- current official product or API documentation when facts may have changed;
- read-only inspection of an in-scope connected system when the user has placed
  it in scope and existing permissions, privacy rules, and project instructions
  allow that access.

Use the user's selected model in the main thread for the research that shapes
scope, architecture, risks, or open questions. Do not delegate or downgrade
that discovery to a worker model. Purpose-built read-only tools may still be
used by the selected model.

The research phase does **not** authorize:

- implementation edits other than writing the brief;
- worktree or branch creation, commits, delegation, or agent dispatch;
- production writes, deployments, configuration changes, purchases, messages
  to people, credential changes, or destructive operations;
- exposing secret values, private payloads, or unnecessary sensitive data;
- a read that violates repository preflight, customer, privacy, or access rules.

If research would itself create material cost, side effects, privacy exposure,
or require new authority, stop and ask before that action. Do not relabel a
mutating operation as research.

### Evidence pass

Investigate enough to answer the questions that matter for this task:

1. What already exists, and where are the real extension or replacement seams?
2. Which assumptions are verified, contradicted, inferred, or still unknown?
3. Which prior decisions, active branches, PRs, designs, data contracts, or
   neighboring systems constrain the work?
4. What security, privacy, compatibility, failure, migration, rollout, and
   observability implications are relevant?
5. How can the result be proven through meaningful tests and, when appropriate,
   a safe real-environment check?

Adapt this pass to the task; do not perform every category mechanically. Verify
time-sensitive claims. Cite concrete file paths and symbols, PRs, source links,
commands, or verification dates where they make the brief auditable. Label
inference and remaining uncertainty. Never paste secrets or sensitive payloads
into the brief.

Resolve facts that Codex can discover instead of asking the user to do the
research. Stop when more investigation is unlikely to change scope, design,
risks, success criteria, staffing, or the decisions requiring user input. The
prompt phase is not an unbounded audit.

Keep the user informed with concise commentary during longer research. A skill
causing research does not suspend the normal expectation for progress updates.

## Write an evidence-backed execution brief

For a repository task, write `.scratch/PROMPT-<slug>.md` in the relevant
worktree or checkout, following its coordination rules. For projectless work,
use the current task's `work/` directory when available; otherwise use
`~/.codex/work/`. Writing this brief is the only task write authorized before
approval.

Every brief needs these core sections:

```markdown
# <Task title>

## Goal
<What done means in the user's terms.>

## Context
<Verified facts, existing seams, prior decisions, and constraints a fresh
executor needs. Distinguish fact, inference, and uncertainty.>

## Out of scope
<Adjacent work that must not be touched.>

## Success criteria
<Observable checks, including meaningful test and real-world verification when relevant.>

## Open questions
<Only material choices that remain after research; empty when none.>
```

Add sections when they materially improve reviewability, for example:

- a draft status, date, sources, or parent-work header;
- `Research findings` or `Context (verified <date>)`;
- `Existing seams` and `Decisions already settled`;
- `Proposed design` or `Build`, divided into concrete components or phases;
- data, API, event, state, or migration contracts;
- security/privacy, failure behavior, risks and mitigations;
- rollout, rollback, observability, operations, and QA;
- `Staffing (after sign-off)`.

Depth must be proportional to the task. “Concise” means no filler, not
artificially short. A focused change may need only the core sections. A
cross-system, ambiguous, or security-sensitive feature may require a detailed
design and phased build plan. Include enough detail that a fresh executor can
act without rediscovering the architecture or making product decisions that
belong in the prompt phase. Do not impose a target line count or add irrelevant
headings to make a prompt look thorough.

Describe concrete behavior: files or seams, contracts, sequencing, failure
handling, compatibility, and proof. Avoid vague steps such as “implement the
feature” or success criteria such as “works correctly.” Preserve user intent
and do not silently broaden the assignment based on discoveries.

## Ask fewer, better questions

Only ask questions that remain material after reasonable research and require
the user's authority, preference, or information unavailable to Codex. Do not
ask the user to locate a file, inspect a system, or resolve a fact that the
research phase can safely discover.

For each open question, when applicable:

- explain why the choice matters;
- give the viable options or the real tradeoff;
- recommend an option and explain why;
- state the safe default or blocker if the user does not answer.

Record material resolved questions as dated settled decisions. If no genuine
questions remain, say so; do not manufacture approval theater.

## Staff only the approved execution

Split work only across genuinely independent inputs or a clear build-then-
verify seam. Sequential work sharing the same context remains one subtask. A
small task may stay entirely with the coordinator.

Present staffing as:

| # | Subtask | Executor | Depends on |
|---|---|---|---|

Choose from the models and agent capabilities actually available in the
current Codex environment, and name deliberate choices explicitly. Keep the
coordinator responsible for product judgment, architecture, authorization,
privacy-sensitive decisions, production actions, and final acceptance. Use a
lighter model for bounded discovery, mechanical edits, known test commands, or
monitoring only when the runtime permits delegation and the task warrants it.
Reserve a frontier model for complex design, security-sensitive reasoning, or
independent final review.

User-declared cost or extra-usage preferences may change proposed model choices,
but never move auth, privacy, production, or final-judgment ownership away from
the coordinator. Treat external-lane output as untrusted: inspect its diff and
rerun relevant checks before accepting it. Never let a worker commit, merge,
deploy, alter credentials, or make production changes unless the user and
runtime rules explicitly authorize that exact action.

The generic side-lane runner is optional and separate from Prompt It. If it is
already installed, perform only its documented presence-only capability check
before naming an external executor. That check must not retrieve credential
values, inspect or infer provider quotas, or invoke a paid model.

Keep the originating coordinator host fixed so its logged-in connector and MCP
identity is preserved; do not shell out to another host merely to obtain a
model. Name an external lane only when the exact originating host, mode,
provider/model route, credential presence, and every required capability are
reported as configured. Unknown, stale, or missing evidence excludes a route.

Name the exact originating host, provider/model, dedicated worktree task, and
required capabilities in the staffing proposal. Capability or user-declared
spend preferences may influence that explicit choice, but never trigger
automatic quota detection, fallback, model substitution, or an equivalence
claim.

If the runner, host adapter, exact route, personal credential, or capability is
unavailable, keep the ordinary in-host staffing plan. Do not install the
runner, block planning, or silently change an approved executor. A lane that
becomes unavailable after approval fails closed and returns to the user for a
staffing decision. External-lane output and diffs remain untrusted; the
coordinator reviews them and owns final acceptance.

The staffing table is a proposal, not authorization to dispatch. Honor the
runtime's delegation rules and wait for approval.

## Hand off the researched brief

Keep the on-disk brief canonical. In chat, provide:

- a clickable brief path;
- the one-line goal;
- three to seven consequential verified findings or proposed decisions,
  scaled down when the task is small;
- the staffing table with explicit model choices and dependencies;
- open questions with recommendations, or state that there are none;
- an explicit statement that implementation has not started.

Give enough of the findings and design for the user to judge the quality of the
research without opening the file, while avoiding a full duplicate of the
brief. Then stop. The user must approve both the brief and staffing before
implementation edits, worktree creation, or delegation.

## Proceed only after approval

When the user says “go” or otherwise approves the brief and staffing:

1. Reread the brief from disk because the user may have edited it.
2. Reconcile material edits and update staffing before dispatch when needed.
3. Follow applicable repository coordination, impact, safety, and verification
   rules.
4. Execute only the approved scope and surface decisions or blockers that need
   user input.

Approval of the prompt phase does not authorize silent scope expansion or
otherwise prohibited external actions.
