---
name: prompt-it
description: Use when the user says "prompt it", answers yes to "Prompt it?", or asks for a plan to review before work starts. Drafts a reviewable prompt, decomposes it into subtasks, assigns a model to each, then stops and waits for approval.
---

# Prompt It

Turn a request into a **reviewable prompt plus a staffed plan**, before any work
starts. The user edits the prompt; you execute only what they approve.

The point: a misunderstanding shows up in one paragraph they can fix in thirty
seconds, instead of in four hundred lines they have to unpick.

## Step 1 — Draft the prompt. Do not start work.

Write it to `.scratch/PROMPT-<slug>.md` in the repo (create the directory if needed;
use a temp directory if the project should not carry it). Keep it tight — this is a
document the user edits in place, not a proposal essay.

```markdown
# <Task title>

## Goal
<1-3 sentences: what "done" means in the user's own terms.>

## Context
<Only what a fresh agent could not derive for itself: file paths, prior decisions,
constraints, related branches or tickets. Cite paths as file.py:line.>

## Out of scope
<The adjacent things you will NOT touch. This is the highest-value section — it is
where scope creep gets killed.>

## Success criteria
<Checkable statements. "Test X passes", "the endpoint returns Z for input Y" —
never "works well".>

## Open questions
<Anything you would otherwise guess at. Empty is fine if there genuinely are none.>
```

Then present, in chat: the file path, the goal line, the staffing table from Step 2,
and any open questions. Nothing else — do not restate the prompt body.

## Step 2 — Decompose and staff

Split into subtasks only where the split is **real**: genuinely independent inputs, or
a natural build-then-verify seam. Two subtasks that must run in sequence and share all
their context are ONE subtask. Plenty of tasks do not decompose at all — say so and
move on rather than inventing parallelism.

| Lane | Use when |
|---|---|
| **Coordinator — strongest model** | Judgment, ambiguity, architecture, security decisions, and reviewing what the others produced. Stays in the main thread. |
| **Mid-tier model** | Well-scoped implementation with a spec to follow: one module, one migration, one connector. |
| **Cheapest model** | Mechanical work: lookups, file inventories, format conversions, running a known command. |
| **Read-only explorer** | Broad searching where you only need the conclusion, not the reading. |

Rules that override the table:

- **Anything touching regulated or sensitive personal data, authentication, or a
  production write stays with the coordinator in the main thread.** Never delegate that
  judgment, even when the edit itself looks mechanical.
- **Pin the model explicitly on every delegated call.** An unpinned subagent inherits
  the expensive one, and nobody notices until the bill arrives.
- **Independent subagents go out in one message, multiple tool calls**, so they run
  concurrently rather than in sequence.
- **Agents that write files get their own git worktree.** Two agents in one checkout
  will overwrite each other's work.
- **Give each subagent everything it needs up front.** They cannot see each other's
  progress, and a subagent that has to guess will guess confidently.
- **Tell every subagent: if you cannot verify something, flag it as an open question
  rather than filling the gap with a plausible answer.** This single instruction
  improves output quality more than any amount of prompt polish.

Present staffing as a table:

| # | Subtask | Lane | Depends on |
|---|---|---|---|

## Step 3 — Before proposing a design, always do these three

1. **Ask the questions you need answered.** Prioritize the ones where a wrong
   assumption wastes the most work. Then wait — do not answer them yourself.
2. **Say what already exists that we should reuse instead of building.** In this
   codebase, in the shared libraries, or off the shelf. **Default to reusing.** Do not
   skip this step: the most common expensive mistake is confidently building a second
   version of something that already exists, because nothing in the request said not to.
3. **Offer two or three approaches with real tradeoffs**, and say which you recommend
   and why. The user should be able to judge your reasoning rather than only accept or
   reject a single design.
4. **Separate what you verified from what you inferred, and say where you checked.**
   Mark each load-bearing claim as *verified* (with the file, command or doc you read)
   or *inferred* (and from what). Cite sources for anything external.

   Do **not** report a confidence score instead. Self-reported confidence is poorly
   calibrated and, worse, it misses the failure that actually costs you: a chain of
   sound reasoning resting on one premise nobody checked. The model will rate that
   highly confident and be right to — the reasoning *was* good. Provenance catches it
   because provenance is checkable and a feeling is not.

## Step 4 — Stop

Hand back the prompt path and the tables, then **wait**. Do not create branches, do not
spawn agents, do not write code.

On "go": **re-read the prompt file from disk** — the user may have edited it — and then
execute the plan as written, not as you originally proposed it.

## When this skill does not apply

If the request turns out to be a single small edit, a question, or a lookup, say
"this is a one-liner, doing it directly" and just do it. Producing a planning document
for a trivial task is the main way this skill becomes annoying instead of useful.
