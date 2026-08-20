# Prompt It

**A planning skill that asks before it plans.**

When you give Claude a real task, it stops and asks you one question:

> **Prompt it?**

Say **no** and it gets on with the work, exactly as it would have anyway. Say **yes**
and it writes you a plan first — what it's going to do, what it's deliberately *not*
going to do, what it's assuming, and how you'll both know it worked. You read that, fix
what's wrong, and say go.

So the cost of having this installed is one word on the occasional task where you didn't
want it. That's the whole design. Every planning prompt I'd tried before this one got
uninstalled within a week, because a planning document for "rename this variable" is
worse than no planning at all.

## Why it's worth it

You catch the misunderstanding while it's still one paragraph, instead of in four
hundred lines you now have to unpick.

And the part people don't expect: **you don't have to know what to specify.** Claude
works out what the decisions are and hands them back to you — that's when you notice it
was about to use the wrong table, invent a second config file, or skip the case you
actually cared about. Reacting to a draft is easy. Specifying from a blank page is hard.
This moves you from the second job to the first one.

## Three versions — pick one

| You are | Version | Where |
|---|---|---|
| Not sure / don't use Claude Code | **[claude.ai](claude-ai/project-instructions.md)** | Paste into a Project's custom instructions |
| An engineer | **`prompt-it`** | Claude Code plugin |
| Someone with code and data access who doesn't ship code — PM, analyst, researcher | **`prompt-it-readonly`** | Claude Code plugin |

**If you read nothing else, take the [claude.ai version](claude-ai/project-instructions.md).**
It needs no terminal and no install, and it's most of the value.

## Install (Claude Code)

```
/plugin marketplace add marcosathanasoulis/prompt-it
/plugin install prompt-it@prompt-it
```

Or the read-only edition:

```
/plugin install prompt-it-readonly@prompt-it
```

**Then add the gate**, or the skill never gets offered and you have to remember to
invoke it by hand. Append the snippet in **[`snippets/claude-md-gate.md`](snippets/claude-md-gate.md)**
to your `~/.claude/CLAUDE.md`. The skill produces the plan; the gate is what makes
Claude *ask*. Both, or neither works properly.

The two plugins are **alternatives, not companions** — they define the same skill with
different rules. Install one.

## What the engineer version adds

Subagent staffing, because most people either never delegate or delegate everything to
the most expensive model:

- **Split only where the split is real.** Two subtasks that must run in sequence and
  share all their context are one subtask. Most tasks don't decompose, and inventing
  parallelism costs more than it saves.
- **Pin the model on every delegated call.** An unpinned subagent inherits the expensive
  one, and nobody notices until the bill arrives.
- **Independent agents go out in one message**, so they actually run concurrently.
- **Agents that write files get their own git worktree.** Two agents in one checkout
  overwrite each other.
- **Never delegate the judgment** on regulated data, authentication, or production
  writes — however mechanical the edit looks.

Plus the three things it must do before proposing a design: ask its questions and wait,
say what already exists that you should reuse instead, and offer two or three approaches
with tradeoffs rather than one design to accept or reject.

## What the read-only version adds

For people who can read the code and the data but don't ship code. Everything stays
read-only — nothing writes, commits, deploys or mutates data, and if a subtask seems to
need that, it says so rather than finding a way around.

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
