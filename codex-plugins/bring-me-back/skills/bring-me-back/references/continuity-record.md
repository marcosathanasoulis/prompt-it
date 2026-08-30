# Continuity record

Use this record only when multiple workers, an explicit handoff, or ambiguous
duplicates make a structured snapshot useful. Keep it in the coordinator task
unless an existing repository-owned workflow already defines an approved
location.

## Coordinator state

- current task ID, host ID, and location;
- workspace-capable or coordinator-only classification;
- trusted workspace hosts currently available;
- reconciliation timestamp with timezone.

## In-flight work

For each task record:

- stable task name;
- worker task ID and host ID;
- saved project, exact working directory, and existing branch, PR, checkout, or
  worktree;
- one-sentence objective;
- active, waiting, blocked, completed, or abandoned state;
- newest substantive evidence;
- authorization boundary;
- blocker or required decision;
- next safe action;
- next reporting checkpoint.

## Deduplication decisions

Record tasks intentionally not resumed and why, such as a completed
predecessor, duplicate objective, stale checkout, or unavailable host. Do not
archive or delete tasks merely because they appear duplicative.

## Capability state

Record only pass, fail, or unknown for required capabilities and the precise
workspace-side repair action. Never record credential values, tokens, private
keys, raw authentication output, or sensitive payloads.

## Resume summary

End with workers resumed, workers left active, workers blocked, user decisions
needed, and confirmation that no isolated replacement worker, duplicate task,
checkout, worktree, credential transfer, or login was created.
