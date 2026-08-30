# Prompt It

**A planning skill that asks before it plans.**

When you give Codex or Claude Code a substantial new task, it stops and asks
you one question:

> **Prompt it?**

Say **no** and it gets on with the work, exactly as it would have anyway. Say
**yes** and it researches the task read-only, writes an evidence-backed brief,
states what it will deliberately *not* do, and proposes explicit model staffing.
You read that, fix what's wrong, and say go.

So the cost of having this installed is one word on the occasional task where you didn't
want it. That's the whole design. Every planning prompt I'd tried before this one got
uninstalled within a week, because a planning document for "rename this variable" is
worse than no planning at all.

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

Two exchanges. Same install, opposite outcomes.

**You didn't want a plan:**

```
you      bump the timeout on the health check to 30s
claude   Prompt it?
you      no
claude   Done — timeout is now 30s in the health check config.
```

**You did:**

```
you      add rate limiting to the search endpoint
claude   Prompt it?
you      yes
claude   Written to .scratch/PROMPT-rate-limiting.md

         ## Goal — reject requests over N per minute per API key
         ## Out of scope — auth, quota accounting, the admin API
         ## Assuming — per-key, not per-IP
         ## Done when — the 11th request inside a minute returns 429

         Two questions before I start:
           1. What limit, and per key or per IP?
           2. There's already a limiter in the shared utils — reuse it?

         Nothing written yet. Edit that file or say go.
```

The second one is the whole product. Neither question had occurred to me when I
typed the request, and one of them — the existing limiter — would have meant
throwing the work away.

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
invoke it by hand. Append the snippet in **[`snippets/claude-md-gate.md`](snippets/claude-md-gate.md)**
to your `~/.claude/CLAUDE.md`. The skill produces the plan; the gate is what makes
Claude *ask*. Both, or neither works properly.

The two plugins are **alternatives, not companions** — they define the same skill with
different rules. Install one.

## Install in Codex

```bash
codex plugin marketplace add marcosathanasoulis/prompt-it --ref main
codex plugin add prompt-it@prompt-it
```

Then add the gate from
[`snippets/agents-md-gate.md`](snippets/agents-md-gate.md) to
`~/.codex/AGENTS.md`, or to one repository's `AGENTS.md` when you only want the
gate there. Start a new Codex task after installation if skill discovery is
cached.

The engineer plugin uses the same canonical `SKILL.md` in Codex and Claude
Code. Product-private memory, connectors, authentication, and tools remain
host-specific.

## Optional Governed Side Lane integration

Prompt it works on its own. When
[Governed Side Lane](https://github.com/marcosathanasoulis/governed-side-lane)
is also installed, Prompt it can include an exact Codex, Claude, or explicitly
configured GLM worker in its staffing proposal. It never dispatches a worker
during planning, reads usage or billing state, or changes the originating
coordinator. The human still approves the brief and exact route before work.

## What the engineer version adds

Optional depth for wide work. Skip this entirely if your tasks are deep rather than
broad — the loop above is the part that matters. But when you do fan work out, most
people either never delegate or delegate everything to the most expensive model:

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

Before proposing a design it researches what already exists, separates verified
facts from inferences, asks only the material questions that remain, and records
approaches and tradeoffs in the brief.

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
