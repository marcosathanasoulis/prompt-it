---
name: prompt-it
description: Use when the user says "prompt it", answers yes to "Prompt it?", or asks for a plan to review before work starts. Drafts a reviewable plan, splits it where that genuinely helps, and assigns a model to each piece. Read-only edition — research, analysis and design work only, never code changes.
---

# Prompt It (read-only edition)

For people who have access to the code and the data but do not ship code: product
managers, analysts, researchers, designers, technical writers.

Turn a request into a **reviewable plan** before any work starts. The user edits it;
you execute only what they approve. A misunderstanding then shows up in one paragraph
they can fix in thirty seconds, instead of in a finished document nobody can use.

## Step 1 — Draft the plan. Do not start the work.

Write it to `~/prompts/PROMPT-<slug>.md` — create the folder if needed, and **never
write inside a repository.**

```markdown
# <Title>

## Goal
<1-3 sentences: what "done" looks like, in the user's own terms.>

## Context
<Only what you could not work out for yourself: which area of the product, what was
already decided, who has to approve it, links to prior documents.>

## Out of scope
<What this deliberately does NOT cover. The highest-value section — for a
requirements document it is half the value.>

## What "good" looks like
<Checkable, not vague. "Covers all seven interviews and names every theme that appears
in at least three of them" — not "a good synthesis".>

## Open questions
<Anything you would otherwise guess at.>
```

Then present in chat: the file path, the goal line, the staffing table, and the open
questions. Do not restate the plan body.

## Step 2 — Split the work, and say who does each piece

Split only where the split is real: **independent inputs**, or a natural
gather-then-synthesize seam. Two pieces that must happen in order and share all their
context are ONE piece. Many tasks do not split at all — say so.

Work that genuinely splits, in research and product work:

- **Many documents, one conclusion.** Seven interview write-ups, each summarized
  against the same framework, then converged into cross-source themes. The summaries
  are independent, so they run at once. The convergence is judgment, so it does not.
- **Several sources, one picture.** A metrics query, a support-ticket scan and a
  competitor review all answering the same question.
- **Options to compare.** Three approaches drafted separately, so they stay genuinely
  different instead of converging into one.

| Which model | Use it for |
|---|---|
| The strongest one | Planning, judgment calls, anything ambiguous, and reviewing what the others produced. Stays in your main session. |
| The fast capable one | One well-defined piece with clear instructions: synthesize this interview, draft this section, run this analysis. |
| The cheap quick one | Mechanical work: reformat this, list everything closed last week, extract the dates. |
| The read-only explorer | Reading widely when you only want the conclusion, not the reading. |

These are roles, not a required collection of accounts. With one OpenAI or
Anthropic assistant, keep the work in that session. If optional Side Lane
integration is installed, use its current exact route inventory and qualification
evidence to consider other providers. Compare task fit and total cost rather
than automatically choosing a flagship. Saved credentials and research-catalog
entries do not prove a route is runnable. This edition remains read-only: do
not enable execute mode to obtain provider keys or connectors.

Rules:

- **Everything stays read-only.** No lane writes files, commits, deploys, or modifies
  data. If a subtask seems to need that, it is out of scope — say plainly what would
  need to change and who should do it, rather than finding a way around.
- **Name the model on every delegated piece.** Unnamed means the expensive one.
- **Independent pieces go out together in one message**, so they run at the same time.
- **Give each piece everything it needs up front.** They cannot see each other's work.
- **Tell each one: if you cannot verify something, flag it rather than filling the gap
  with something plausible.**
- **Never split the judgment.** What the themes mean, the recommendation, the call on
  scope — those stay with you and the strongest model.

Present staffing as a table:

| # | Piece | Model | Depends on |
|---|---|---|---|

## Step 3 — Before proposing anything, always

1. **Ask your questions first.** Prioritize the ones where a wrong assumption wastes the
   most work: who the audience is, what decision this feeds, what is already settled.
   Then wait.
2. **Say what already exists.** A prior document, an existing query, a component already
   built, an analysis someone ran last quarter. **Default to reusing.** The most common
   expensive mistake is confidently producing a second version of something that
   already exists.
3. **Offer two or three approaches with real tradeoffs**, and say which you recommend
   and why. Judging reasoning is far easier than producing a design from nothing.
4. **Separate what you verified from what you inferred, and say where you checked.**
   For every claim the conclusion rests on, mark it *verified* — naming the query, the
   document or the file you read — or *inferred*, and from what. Cite sources for
   anything external.

   Do **not** substitute a confidence score. Self-reported confidence skews high and
   tells you nothing about whether the underlying premises were ever checked. A
   well-reasoned synthesis built on one unverified assumption will be reported as
   confident, correctly, because the reasoning was fine. Provenance is checkable;
   confidence is a feeling.

## Rules that matter for this kind of work

- **Name the framework up front.** If the task is synthesis, ask which lens before
  starting — a behavior-change model, jobs-to-be-done, a friction map. Synthesis with a
  stated framework is reviewable. Freeform notes are not.
- **A specification that engineers will build from must state its contract explicitly.**
  What goes in, what comes back, what happens when it fails, and what is deliberately
  left undecided. When that is implicit, engineers reverse-engineer it from the prose
  and write "inferred from the spec, confirm before building" on their tickets — which
  means the decision got made by whoever was guessing rather than by the person who
  owned it.
- **Requirements documents carry their approvers.** Name who signs off on what:
  technical feasibility, domain correctness, commercial. Different sections have
  different approvers, and saying so up front prevents a late round of surprise
  objections.
- **Check claims against the system, not against documents about it.** Read access
  exists so a spec can be checked against what actually exists before review. Internal
  documents go stale; the schema does not.
- **Verify the schema before writing environment-specific queries.** Column names differ
  between environments more often than anyone expects. Inspect the table first rather
  than assuming.
- **Never work around a permission error.** Sensitive columns and tables are often
  denied at the grant level deliberately. A query that errors on one is the system
  working correctly — do not go looking for another route to the same data.

## Step 4 — Stop

Hand back the file path and the table, then **wait**. Do not start drafting, do not
spawn agents. On "go", re-read the plan from disk — it may have been edited — and
execute it as written.

## When this skill does not apply

A single question, a lookup, or a quick query is not a task. Say "this is a one-liner,
doing it directly" and just do it. Producing a planning document for a five-minute task
is the main way this becomes annoying rather than useful.
