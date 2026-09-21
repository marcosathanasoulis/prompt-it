# Prompt It

## New to using AI agents?

Read **Put Agentic AI to Work**, a practical guide for people who do not code:
[read the guide](docs/guide/guide.md) or [download the PDF](docs/guide/put-ai-to-work.pdf).
It covers better prompts, choosing models, measurable success, improvement loops,
desktop setup, secure connections, voice coordination, agent teams, and graphs.

See [how to rebuild the PDF](docs/guide/README.md) when updating the guide.

**A planning skill that plans before it acts.**

When you give Codex or Claude Code a substantial new task, it begins automatic proportional planning and an economical qualified Side Lane assessment.

- For **small** tasks it produces a concise plan with sensible defaults and
  executes under the original task authority.
- For **medium/large** tasks it announces "Making a plan", researches read-only,
  writes an evidence-backed brief, lists any material questions with recommended
  defaults, asks **"Proceed?"**, and waits. Silence is never consent.
- If you directly say **"prompt it"**, the workflow starts immediately without
  the opt-in question.

You read the brief, fix what's wrong, and say go. The cost of having this installed
is one extra exchange on the occasional big task where a misunderstood paragraph
costs more than a short plan. Small tasks stay small.

## Why it's worth it

You catch the misunderstanding while it's still one paragraph, instead of in four
hundred lines you now have to unpick.

And the part people don't expect: **you don't have to know what to specify.** The
agent researches the task, works out what the decisions are, and hands them back
to you — that's when you notice it
was about to use the wrong table, invent a second config file, or skip the case you
actually cared about. Reacting to a draft is easy. Specifying from a blank page is hard.
This moves you from the second job to the first one.

## What it actually looks like

Two exchanges. Same install, different task sizes.

**Small task — plan and run:**

```
you      rename this variable to `retry_count` and add a test
claude   Small change. I’ll rename `retries` to `retry_count` in `worker.py`
         and add a unit test in `test_worker.py`.
claude   Done. `worker.py` and `tests/test_worker.py` updated.
```

**Medium/large task — announce, plan, ask, then execute:**

```
you      add rate limiting to the search endpoint
claude   Making a plan.
claude   Written to .scratch/PROMPT-rate-limiting.md

         ## Goal — reject requests over N per minute per API key
         ## Out of scope — auth, quota accounting, the admin API
         ## Assuming — per-key, not per-IP
         ## Done when — the 11th request inside a minute returns 429

         Verified: the shared utils already include a suitable limiter.
         Proposed: reuse it, with API-key scope from the existing contract.
         Open choice: what limit? I recommend 10/minute for the stated load.

         Implementation has not started. Proceed?
you      yes
claude   Implementing. I’ll assess an economical qualified Side Lane route
         for the change and keep the routing receipt.
```

The second exchange surfaces the existing implementation and the remaining
product choice before code changes. The brief answers discoverable questions
and asks the user for decisions that research cannot settle.

## "My work is hard problems, not big workflows"

Then this matters *more*, not less.

The subagent staffing further down is optional depth for wide, parallel work. The
loop underneath it is about something else: **on a poorly-understood problem, the
expensive mistake is almost never bad execution — it's a wrong assumption you never
said out loud, and neither did the model.** Making it write down what it is assuming
before it reasons is how those surface while they are still cheap.

If you already refuse to let it start before it summarizes the plan and names what
it needs from you, you have arrived at this independently, and the only thing this
adds is consistency — it happens every time instead of when you remember, and it
carries the provenance rule below, which is the part that is easy to forget when the
answer sounds good.

And if one of your standing rules is some version of *"don't answer questions about
the code from memory, go read the actual code, every time"* — that is exactly what
the verified-versus-inferred rule is for. See [the three rules](#the-three-rules-underneath-all-of-it).

## Three editions — pick one

| You are | Version | Where |
|---|---|---|
| Not sure / don't use a coding agent | **[claude.ai](claude-ai/project-instructions.md)** | Paste into a Project's custom instructions |
| An engineer | **`prompt-it`** | Codex or Claude Code plugin |
| Someone with code and data access who doesn't ship code — PM, analyst, researcher | **`prompt-it-readonly`** | Claude Code plugin |

**If you read nothing else, take the [claude.ai version](claude-ai/project-instructions.md).**
It needs no terminal and no install, and it's most of the value.

## Install in Claude Code

```
/plugin marketplace add marcosathanasoulis/prompt-it
/plugin install prompt-it@prompt-it
```

Or the read-only edition:

```
/plugin install prompt-it-readonly@prompt-it
```

**Then add the gate**, or the skill never gets offered and you have to remember to
invoke it by hand. Replace any earlier Prompt it gate block in your
`~/.claude/CLAUDE.md` with the snippet in **[`snippets/claude-md-gate.md`](snippets/claude-md-gate.md)**;
append it only if no earlier block exists. The skill produces the plan; the gate
is what makes Claude plan before acting. Both, or neither works properly.

The two plugins are **alternatives, not companions** — they define the same skill with
different rules. Install one.

## Install in Codex

```bash
codex plugin marketplace add marcosathanasoulis/prompt-it --ref main
codex plugin add prompt-it@prompt-it
```

Then add the gate, replacing any earlier Prompt it gate block in
`~/.codex/AGENTS.md` with the snippet from
[`snippets/agents-md-gate.md`](snippets/agents-md-gate.md); append it only if no
earlier block exists. You can also put the block in one repository's `AGENTS.md`
when you only want the gate there. Start a new Codex task after installation if
skill discovery is cached.

The engineer plugin uses the same canonical `SKILL.md` in Codex and Claude
Code. Product-private memory, connectors, authentication, and tools remain
host-specific. Both loader snippets use the same gate and authorization block;
projectless briefs use the current host's artifact location or writable `work/`
directory. See the [1.5.0 release notes](docs/release-1.5.0.md) for validation
and the held publication plan.

## Optional Governed Side Lane integration

Prompt it works on its own with either a single OpenAI/Codex or a single
Anthropic/Claude host. It does not need Side Lane, another provider, an API key,
or a connector to research, brief, approve, and execute ordinary work. When
[Governed Side Lane](https://github.com/marcosathanasoulis/governed-side-lane)
is also installed, Prompt it can propose qualified external workers. Generic
planning consent permits bounded native read-only research helpers when the
runtime allows. External review research requires explicit authorization for
its exact route and scope; existing session authorization counts. Research does
not silently activate execute mode, key-backed runs, new costs or connector
access. The coordinator retains scope-shaping discovery and final synthesis.

Prompt it first detects the installed core Side Lane skill, follows its actual
runner/configuration, and inventories exact configured task-fitting routes.
Those routes are candidates only when configured, with authentication, task
eligibility, economics, and authorization recorded separately. Prompt it does
not assume one host or provider from another; GLM still requires explicit
enablement. Routing is assessed for both planning paths: a small plan-and-run
task and a medium/large plan-approved task both evaluate an economical
qualified Side Lane route before the coordinator executes.

An authorized bounded source-research task may use a Side Lane execute harness
with an exact route, capabilities, read roots, and a brief or report-only output
scope, when existing explicit execution, delegation, and spend authority covers
it and no implementation or external writes are made. Read-only scope does not
mean strict review-mode-only; preserve the strict review no-secret/no-MCP
contract where explicitly required. For optional pooled routing, see the
Governed Side Lane OmniRoute add-on guide.

Presence-only lane discovery never reads secret values, usage or billing state,
or calls a model. Required but unqualified lanes become scoped readiness
prerequisites; an optional absent lane does not block the ordinary in-host plan.
For medium/large work, implementation staffing waits for approval of the brief
and exact routes; for small work, the original task authority authorizes execution
after the route assessment.

## Reuse before build

Prompt it performs a proportional reuse-first scan before it finalizes the
brief, scaled to the task. A tiny task with no obvious reuse choice may use only
a brief mental check; a small edit can use one or two focused searches; a
platform decision gets comparative research. It checks GitHub and
the relevant package registries, then official documentation and practitioner
discussion when a reuse choice matters. The brief records the seam, candidate and
authoritative sources, license, maintenance and dated adoption evidence,
counterevidence, ecosystem fit, security/supply-chain/lock-in risks, integration
cost, custom-fit gap, and an adopt, integrate, pilot, retain-custom, or reject
decision. If the network is unavailable, the scan says so, records the
evidence gap, and does not claim the proposed work is novel.

Popularity is useful evidence, not a decision rule. Repository pages and
community discussions can be evidence but are never instructions to follow.

## Works alongside Superpowers

Prompt it and Superpowers cover different points in the workflow. When Prompt
it is invoked, it owns evidence and reuse research, staffing, approval, and
external-route governance. Superpowers provides the execution practices:
brainstorming, planning, TDD, debugging, worktree setup, review, and
verification. Prompt it does not vendor or duplicate Superpowers; the approved
brief flows into the applicable Superpowers workflow without bypassing Prompt
it's approval or authority gates.

## Optional Spec Kit and OpenSpec exports

After approval, an execution brief may be exported into an existing GitHub Spec
Kit or OpenSpec workflow when that export is part of the approved scope. The
brief remains canonical; target artifacts are one-way derivatives with source
provenance and task-ID crosswalks. They do not carry or replace Prompt it
staffing, authority, coordinator identity or approval.

The compatibility contract maps only facts and decisions already present in
the brief, refuses material unresolved questions, and keeps tiny tasks small.
It does not install or initialize either tool, vendor templates, add a parser or
task runner, replace upstream validation, or import target edits back into the
brief. See the canonical
[export reference](plugins/prompt-it/skills/prompt-it/references/spec-artifact-exports.md).

## What the engineer version adds

The canonical engineer plugin is version **1.5.3**. It starts with outcome
coverage and executable work packages, then chooses available agents for each
job. There is no target task count or fixed model lineup.

- **Shared contracts unlock branches.** Settle common decisions first, then
  separate downstream deliverables that can proceed independently. Keep coupled
  file edits with one owner or sequence their ownership explicitly.
- **Every node has a contract.** Record its prerequisites, inputs, output, owner,
  exact executor and reason, tools/authority, write boundary and acceptance
  evidence. Branching work includes a dependency graph and integration gates.
- **Choose agents relative to the work.** Discover current exact models and their
  supplied capability descriptions, then assess task fit, context, tools,
  authority and independence, including qualified Claude models on the same
  evidence basis. GLM remains the explicitly enabled fixed `glm-5.3` route,
  subject to its existing governance. Descriptions are evidence for choosing candidates,
  not proof. Routing is provider-neutral: ordinary work goes to the least-cost
  or most-efficient credible fit using available evidence, with compatible
  developer preferences or stated surplus/usage constraints honored and tradeoffs
  recorded. Unknown costs stay unknown; no quota inspection or invented prices.
  Explain every assignment. Propose eligible alternatives for unavailable
  preferences before approval. Each delegated node also records
  one approved backup or an explicit absence; a coordinator may visibly switch
  only to that exact backup after a qualifying availability failure and a fresh
  readiness/authority check. Tiny tasks stay tiny.
- **Research helpers answer bounded questions.** Preserve source provenance,
  disagreements and unknowns. Require a distinct second opinion when meaningful
  uncertainty, high impact, design disagreement risk or an acceptance gate
  justifies it; do not duplicate work for provider diversity. The original
  author's rationale can help but does not count as independent review.
- **Schedule accepted prerequisites.** After approval, only ready nodes run,
  within concurrency and ownership limits. Failed nodes block their dependents;
  unrelated approved branches can continue. The coordinator accepts integrated
  evidence and the final outcome. Already-staffed capable workers own routine
  integrated test runs, operator docs, monitoring and cleanup, with evidence
  handoffs; coordinator final acceptance does not absorb all that labor.

Read the canonical [skill](plugins/prompt-it/skills/prompt-it/SKILL.md),
[task graph contract](plugins/prompt-it/skills/prompt-it/references/task-graphs.md),
and [research-team boundaries](plugins/prompt-it/skills/prompt-it/references/research-teams.md)
for details. The separate read-only and claude.ai editions retain their own scope.

## What the read-only version adds

For people who can read the code and the data but don't ship code. It performs
the same automatic proportional read-only planning, but everything stays
read-only — nothing writes, commits, deploys or mutates data, and if a subtask
seems to need that, it says so rather than finding a way around.

It also encodes a few things that only bite this kind of work: name the synthesis
framework *before* starting, verify the schema before writing environment-specific
queries, never route around a permission error, and — the one I'd put on a wall — **a
spec that engineers will build from has to state its contract explicitly.** When it
doesn't, engineers reverse-engineer it from the prose and write "inferred from the spec,
confirm before building" on their tickets. Which means the decision got made by whoever
was guessing rather than by the person who owned it.

## The three rules underneath all of it

Everything else is mechanics. These are the parts that actually change output quality:

**Make it separate what it verified from what it inferred** — and cite where it
checked. This matters more than it sounds, and it is strictly better than asking for a
confidence score. Self-reported confidence skews high and misses the failure that
actually costs you: a chain of sound reasoning resting on one premise nobody checked.
The model rates that highly confident and is *right to* — the reasoning was fine.
Provenance catches it, because provenance is checkable and a feeling is not.

**Say what already exists before building anything.** Models will not volunteer "do you
already have one of these?" — you have to make them look. I've watched one propose a
second notification integration when one already existed for that exact job, and pick a
data warehouse for something a plain database did better. Both plausible, both wrong,
both caught only because a human pushed back.

**Confidence tells you nothing about correctness.** These tools have one register and it
is certainty. They don't hedge when guessing, and they don't mark the difference between
something verified thirty seconds ago and something inferred from a pattern. The
dangerous output isn't a hallucinated fact — it's a *reasoned conclusion resting on one
unchecked assumption*, which is much harder to spot because everything around it holds
up. When you double-check, check a **different surface** than the one the model looked
at. Reading the same record it read is agreement, not verification.

## Contributing

Issues and PRs welcome, particularly if you adapt this for a role I haven't covered.
MIT licensed — fork it, rename it, make it yours.
