---
name: prompt-it
description: Before a substantial new task, ask “Prompt it?”; on yes, research it read-only with the user-selected model and draft an evidence-backed execution brief plus model staffing for approval. On no, proceed normally. Skip the gate for questions, status checks, lookups, conversational replies, follow-ups already underway, and one-line edits.
---

# Prompt It

Turn a substantial request into a researched, reviewable execution brief before
implementation. The user approves the brief and staffing after seeing what the
research changed. The same canonical workflow applies in Codex and Claude Code;
use the originating host's native inventory, tools and authority. A model or
connector available in another host is not automatically available here.

Prompt it works with one native OpenAI/Codex or Anthropic/Claude host. It does
not require Governed Side Lane, a second provider, an API key, a connector, or
an optional model catalog. Start with the originating host's available models
and tools. If no eligible optional route exists, keep planning and staffing on
that host; do not ask the user to install, subscribe to, or configure anything
just to make a normal task proceed.

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
- applicable instructions, project memory, current coordination evidence,
  repository files, tests, history, prior prompts, issues, and design docs;
- code-graph, search, context, and impact tools required by repository rules;
- relevant neighboring repositories and existing integration seams;
- current official product or API documentation when facts may have changed;
- read-only inspection of an in-scope connected system when the user has placed
  it in scope and existing permissions, privacy rules, and project instructions
  allow that access.

Use the user's selected model in the main thread for the research that shapes
scope, architecture, risks, or open questions. The coordinator owns this discovery
and final synthesis; helpers supplement it with bounded evidence gathering or
critique. Generic Prompt it consent permits native read-only research helpers
when runtime rules allow. Announce the exact staffing, question, sources, and
read-only scope before dispatch. No helper receives implementation authority.

When research benefits from helpers or an independent second opinion, read
[Research teams](references/research-teams.md). External review research needs
explicit bounded authorization; reuse existing session authorization for the
exact route and scope instead of asking again. Generic consent never activates
external execute mode, key-backed runs, new costs, or connector access.

Generic research consent does **not** authorize:

- implementation edits other than writing the brief;
- worktree or branch creation, commits, or implementation-agent dispatch;
- external research dispatch without explicit bounded authority and route qualification;
- production writes, deployments, configuration changes, purchases, messages
  to people, credential changes, or destructive operations;
- exposing secret values, private payloads, or unnecessary sensitive data;
- a read that violates repository preflight, customer, privacy, or access rules.

Explicit authorization for a qualified external review run may include only the
documented disposable review worktree and captured result artifacts that its
runner creates and audits. This exception does not permit implementation or
arbitrary research files, branches or worktrees.

If research would create material cost, side effects, privacy exposure, or need
authority beyond the existing authorization, ask before that action. Reuse
existing bounded authority; do not relabel implementation as research.

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

Resolve facts that the coordinator can discover instead of asking the user to do the
research. Stop when more investigation is unlikely to change scope, design,
risks, success criteria, staffing, or the decisions requiring user input. The
prompt phase is not an unbounded audit.

Keep the user informed with concise commentary during longer research. A skill
causing research does not suspend the normal expectation for progress updates.

## Write an evidence-backed execution brief

For a repository task, write `.scratch/PROMPT-<slug>.md` in the relevant
worktree or checkout, following its coordination rules. For projectless work,
use the host-provided current-task artifact directory when available; otherwise
use `work/PROMPT-<slug>.md` under the current writable working directory or a
user-designated artifact location. Do not depend on a Codex-only home directory
in Claude Code. If no writable artifact location is available, present the brief
in chat and state that it could not be saved. Generic consent authorizes only
writing this brief. Native
read-only helpers return evidence in their responses. A separately authorized
qualified external review runner may create its documented disposable worktree
and captured result artifacts within that exact authorization; no source edits
or arbitrary research artifacts are authorized.

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
- `Task graph and staffing (after sign-off)`.

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
the user's authority, preference, or information unavailable to the coordinator. Do not
ask the user to locate a file, inspect a system, or resolve a fact that the
research phase can safely discover.

For each open question, when applicable:

- explain why the choice matters;
- give the viable options or the real tradeoff;
- recommend an option and explain why;
- state the safe default or blocker if the user does not answer.

Record material resolved questions as dated settled decisions. If no genuine
questions remain, say so; do not manufacture approval theater.

## Decompose outcomes before choosing agents

Map every success criterion to stable task IDs before choosing executors. Use
concrete deliverables and implementation seams, not generic phases that hide
independent work. Shared architecture is usually a contract prerequisite that
unlocks parallel branches. Keep genuinely coupled edits with one owner; do not
collapse all downstream work just because it shares initial design decisions.
A work breakdown does not require delegation: a tiny task may be one node and
one agent. Do not target a task count or model lineup.

For multi-part work, read [Task graphs and staffing](references/task-graphs.md)
and include the node contracts, outcome coverage, and graph checks it defines.
Every node needs an objective, prerequisites, inputs/provenance, concrete output
and handoff location, owner, exact executor and task-specific reason, required
tools/authority, file boundary when applicable, and acceptance evidence. Compact
fields belong in a table; longer contracts can follow or be linked. Show a
Mermaid dependency graph for branching work using the same IDs, integration and
review gates, and identify the critical dependency chain. A table alone is
sufficient for a single node or simple linear task.

At planning time, discover the currently available exact model names and their
supplied capability descriptions from the originating host's runtime inventory
and, when installed,
documented lane discovery. Use that current evidence, not a remembered lineup.
Include qualified currently available Anthropic/Claude models in the same
comparison using their supplied descriptions; brand alone does not imply
reviewer suitability. GLM selection is not discretionary: only the fixed
`glm-5.3` route may be staffed when explicitly enabled, subject to all
existing host, route, authority and task-fit gates. Never add another GLM model
or fallback. Descriptions identify candidates; they do not prove task fit or
route readiness.
For each assignment record a task-specific reason covering relevant reasoning,
context needs and known context-window limits, tools, host identity, authority
and reviewer independence. Routing is provider/company-neutral: for ordinary
work select the least-cost or most-efficient available candidate that credibly
meets reasoning, tools, authority, context and quality needs. Honor explicit
developer preferences or stated surplus/usage constraints when compatible and
record the tradeoff. Use supplied cost/efficiency evidence; label missing cost
data unknown, never inspect quotas or invent prices, limits or capabilities. Use the decision rubric in the task
graph reference; its model examples are conditional, not a permanent ranking.

For an installed qualifying route, compare the supplied full-session economics,
including task tokens, tool charges when known, handoff/review/correction
overhead, and the user's declared marginal plan state. Do not mistake a
configured candidate for a zero-cost route, or treat unknown rates/overhead as
zero. Select the least-expensive *qualified* fit only when its session evidence
is comparable; otherwise record the uncertainty and use the best evidenced fit.

For each frontier or coordinator execution assignment, explain why an eligible
bounded worker is insufficient. An all-frontier plan needs task-specific
evidence; generic shared context is insufficient. Do not force model diversity.
When capable workers are already staffed, give routine integrated test execution,
operator docs, monitoring, cleanup, mechanical edits and repeated evidence
gathering to those workers with explicit evidence handoffs. Final integration
and acceptance are not catch-all nodes for this routine labor. Keep architecture,
authorization, consequential integration judgment and final acceptance with the
coordinator, who evaluates the integrated evidence. Tiny tasks need no extra
agents. Require an independent second opinion when justified by meaningful
uncertainty/non-determinism, high impact or irreversibility, material design
disagreement risk, or a specified acceptance gate. State its distinct question
and expected value. Do not duplicate work just for provider diversity. The
builder's rationale is useful input but is not independent verification.

If a preferred model is unavailable before approval, explain the gap and propose
an eligible alternative with its task-specific reason. If the lane is required,
preserve its readiness prerequisite rather than silently replacing it. After
approval, no silent substitution: revise staffing before changing an executor.

## Qualify optional lanes and required dependencies

Before choosing external workers, determine whether Governed Side Lane is
actually installed. Inspect the current host's skill/plugin inventory for the
core `side-lane` skill (its namespace may vary), and read its installed entrypoint.
Use documented installed-plugin discovery if the runtime exposes it; do not
assume that an unlisted skill is absent when discovery is incomplete. The
companion alone, a remembered installation, or a `side-lane` binary on PATH does
not prove a configured integration. Record absent, present, or unknown with its
source. If optional discovery is unavailable, keep eligible native staffing.
Do not install, log in, search unrelated private checkouts, or reconfigure tools.

Do this only when an optional lane could materially improve the task. It is not
a base-plan prerequisite or a provider survey. If the core is absent, or no
optional route can improve the task, select a credible native model from the
current host inventory, state any review-independence limitation honestly, and
finish the brief. When the core is installed, consider every configured route
that fits the task; the user does not need to name a provider. Do not mention
optional signup or connector setup unless the user asked for it or it is a
concrete prerequisite of the task.

Resolve the runner from that installed core skill's documented path, including
symlink-relative resolution. An installed wrapper may intentionally select a
local configuration overlay; do not replace it with a vendored runner or a
remembered PATH location. Read the installed runner's help as needed, then use
its `list` command to enumerate configured exact host/provider/gateway/model/mode
routes. Supported providers are not necessarily configured providers, and a
listed route is not proof of authentication, task readiness or dispatch consent.

For optional providers such as DeepSeek, Kimi, MiniMax, xAI/Grok, and
Cognition/Devin, use the installed Side Lane inventory and model guide rather
than a fixed provider shortlist. Compare the exact economical and frontier
variants against the task; a flagship is not the default. Record the product
(API, coding subscription, or hosted agent), gateway/account region, model ID,
worker harness, and execution location. An account or saved key alone does not
make that route runnable. If setup is incomplete, name the missing integration
or qualification step without sending the user to buy another account.

Separate coding, browser navigation, and visual design evidence. A model that
writes frontend code has not thereby demonstrated browser control or design
judgment. For local-workspace tasks, require the worker's local tools and needed
connectors to be qualified; a hosted agent is not interchangeable with a local
worker. For first trials, use the Side Lane qualification guidance and report
observed cost per accepted task, including retries and coordinator repair.
Keep paid API credit separate from included subscription usage; missing cost
or quality evidence does not establish a cheapest eligible route.

When the installed help exposes `candidates`, it reads the research catalog only.
Its records are not configured routes and do not check credentials, connectors,
cost entitlement, authorization, or provider availability. Record those
candidates separately from the runner's configured routes; do not require the
user to pick one before normal in-host staffing continues.

Use documented presence-only `check-capabilities` on relevant exact listed
routes for the task/repository, and `recommend` for task-relative eligibility.
Discover command arguments from installed help; never invent flags. Record
host/runtime presence, OAuth or credential **presence**, required capabilities,
current task-fit evidence, and exclusions separately. Never retrieve secret
values, probe accounts/quotas, invoke a model or start a worker during discovery.

| Originating coordinator | Optional routes to inspect if configured and task-relevant |
|---|---|
| Codex | Exact worker routes listed by the installed runner, including native Claude and any separately qualified candidate route. Fixed `glm-5.3` remains explicit-only. |
| Claude | Exact worker routes listed by the installed runner, including native Codex/OpenAI and any separately qualified candidate route. Fixed `glm-5.3` remains explicit-only. |

This is a discovery map, not a guaranteed provider list or staffing preference.
Keep native in-host agents in the separate runtime inventory. GLM configuration
may be recorded even when GLM is not enabled; label it configured/not authorized
and exclude it from staffing until explicit enablement and existing run gates
are met. GLM has no independent connector identity and never gains review mode.

Include a compact inventory in the brief: installed skill/runner source, checked
at time, exact candidate route, configuration state, authentication/capability
state, task eligibility, authorization, and exclusion reason. Distinguish absent,
configured-but-unready, eligible-but-unapproved and approved; do not compress
these into an unsupported claim that a provider is available. Probe candidates
once per relevant task/mode, then refresh changed or stale evidence before
approved dispatch. Keep the originating coordinator and its identity fixed.

For an external assignment name the exact worker host, provider/model, gateway
when applicable, mode,
task/file boundary (a dedicated worktree when required and authorized), and
required capabilities. Qualify the worker's identity and capabilities separately
from the coordinator's. Configured presence is not proof of readiness: identify
what evidence exists, its freshness, and what meaningful bounded check remains.
Unknown, stale, or missing qualification excludes immediate dispatch.

If a user-required lane is unqualified, plan qualification or repair as a scoped
prerequisite with an owner, authority needed, and real acceptance evidence.
Do not silently replace that lane with the coordinator. An optional missing lane
alone does not block planning: use eligible in-host staffing. Generic Prompt it
does not authorize installing or repairing tools, logging in, or running paid
qualification. Keep such actions proposed until their authority exists.

User preferences never trigger automatic quota detection, fallback, model
substitution, or equivalence claims. A route becoming unavailable blocks its
nodes and requires a revised staffing decision; unrelated approved work may
continue. Never let a worker commit, merge, deploy, alter credentials, or make
production changes without explicit user and runtime authority for that action.
External output remains untrusted; inspect its diff and rerun relevant checks.

The execution staffing table is a proposal, not dispatch authority. Research
helpers follow the distinct research authorization above; implementation waits
for brief and staffing approval.

## Hand off the researched brief

Keep the saved brief canonical; if no writable location exists, the chat brief
is canonical until it can be saved. In chat, provide:

- a clickable brief path, or the brief itself when it could not be saved;
- the one-line goal;
- three to seven consequential verified findings or proposed decisions,
  scaled down when the task is small;
- the staffing table with explicit model choices and dependencies;
- open questions with recommendations, or state that there are none;
- an explicit statement that implementation has not started.

Give enough of the findings and design for the user to judge the quality of the
research without opening the file, while avoiding a full duplicate of the
brief. Then stop. The user must approve both the brief and staffing before
implementation edits, implementation worktree/branch creation, or execution-agent
dispatch. Previously authorized bounded external review, including its documented
disposable worktree and result artifacts, remains governed by its exact scope.

## Proceed only after approval

When the user says “go” or otherwise approves the brief and staffing:

1. Reread the saved brief because the user may have edited it; if it could not
   be saved, use the latest approved chat brief.
2. Reconcile material edits and update staffing before dispatch when needed.
3. Follow applicable repository coordination, impact, safety, and verification
   rules.
4. Dispatch only nodes whose prerequisite outputs the coordinator has accepted.
   Respect runtime concurrency and exclusive file/worktree ownership.
5. Require handoffs with source provenance, output location, validation evidence,
   and unresolved issues. A failed node blocks dependents while unrelated
   approved branches can continue. Reuse the owning worker for bounded fixes.
6. Retry only within approved route and scope. Material scope or executor
   changes require a revised staffing decision, with user approval when needed
   for changed authority. Integrate outputs and verify the complete outcome
   against success criteria before coordinator acceptance.

Approval of the prompt phase does not authorize silent scope expansion or
otherwise prohibited external actions.
