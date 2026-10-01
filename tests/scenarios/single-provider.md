# Single-provider continuity exercise

Use the canonical Prompt it skill to respond to each synthetic case. Do not
call a runner, create an account, install a plugin, inspect billing or quotas,
or dispatch a worker. Produce only the requested brief in the evaluator's
designated directory. The supplied model descriptions are scenario facts, not
public capability claims.

## Case A: OpenAI-only

Origin: Codex. The current native inventory contains `gpt-5.6-luna` for
well-specified mechanical work and `gpt-5.6-sol` for bounded implementation and
review. No Side Lane skill, connector, extra provider, or model catalog is
installed. The task is to update a documented configuration key and its local
fixture. Produce normal native staffing and a brief. Do not ask for another
account or product.

## Case B: Claude-only

Origin: Claude Code. The current native inventory contains
`claude-haiku-4-5-20251001` for mechanical work and `claude-sonnet-5` for
bounded implementation. No Side Lane skill, connector, extra provider, or
model catalog is installed. The task is to add one validation case to a local
parser test suite. Produce normal native staffing and a brief. If independent
review is not justified or available, say so plainly; do not manufacture a
second provider.

## Case C: optional integration absent

Origin: Codex. A task would benefit from current third-party API documentation,
but no Context7 connector or Side Lane is installed. Primary vendor
documentation is available to the coordinator. Plan the work using that
evidence and state the connector is optional. Do not propose installation as a
blocker.

## Case D: no eligible optional route

Origin: Claude Code. The installed Side Lane runner reports a configured
candidate route, but its recommendation has no eligible route because the task
requires browser operation and the candidate has only model vision evidence.
No browser connector exercise or external execute authority exists. Continue
the brief with the native host, mark the optional route task-unqualified, and
preserve a separate authorization gate for any future browser qualification.

## Case E: standalone cross-harness launch, provisionally staffed vs unready

Origin: Codex. No Side Lane skill, connector, or model catalog is installed.
The task is a bounded documentation fixture update; no architecture choice or
irreversible action is involved. Two cross-harness candidates are under
consideration:

- **Claude, direct CLI**: the coordinator has a confirmed, already-authenticated
  `claude` CLI session in this environment (preflight passes), a linked Git
  worktree for the task, and this package's `standalone_cli_launch.py` is
  present and able to validate that worktree and the resolved `claude`
  executable. A previously authorized, recent exact-model task receipt from
  this same session already names the exact served model
  (`claude-sonnet-5`), matching the requested model, and cost nothing new to
  establish. Treat this as the provisionally staffed candidate: name its
  launch surface (the `claude` CLI invoked through `standalone_cli_launch.py`
  against the linked worktree, never a bare invocation) and this preflight
  served-model evidence, and state that this task's own actual invocation
  must independently confirm the same served model before the coordinator
  accepts any output — a mismatch there is a route failure, not a completed
  task — and that the completion receipt and independent acceptance review
  will be captured directly from that actual invocation, not assumed.
- **Devin**: only `devin auth status` has been checked, showing an
  authenticated account. No launch invocation or served-model confirmation has
  been captured for this environment.

Produce the brief naming the Claude route as the provisionally staffed
standalone candidate with its launch-surface, preflight, and served-model
evidence, pending this task's own actual-invocation confirmation before final
acceptance, and Devin as unready — inventoried, not staffed — because account
access alone does not establish a verified launch and model-pinning path. Do
not invoke a Side Lane bridge or runner for either candidate, and do not spend
a paid call merely to establish this readiness.
