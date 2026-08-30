---
name: bring-me-back
description: Recover interrupted Codex coordination when the user says “bring me back” or asks to resume work already in flight. Reconstruct existing tasks from saved-project, thread, branch, PR, and worktree evidence; resume only proven trusted workspace workers without creating duplicate tasks, checkouts, logins, or authority.
---

# Bring Me Back

Treat **“bring me back”** as the recovery phrase and begin reconstruction
without asking the user to restate every task. This skill resumes oversight and
already-authorized work. It does not authorize new work, new workers, broader
scope, publication, deployment, credentials, or destructive actions.

## Trust evidence, not path or title similarity

Use Codex saved-project and task tools as the control plane. A session is a
workspace worker only when current tool evidence proves:

- its host is the current trusted host or an explicitly configured trusted
  host;
- its working directory is the saved project path or a verified existing
  worktree for that project;
- its task history, repository state, and instructions support the requested
  continuation.

An isolated, projectless, ephemeral, or otherwise unproven session is
coordinator-only. It may inspect task metadata, send follow-ups to proven
workers, and report status, but it must not edit files, run task commands,
access cloud systems, repair authentication, or replace a workspace worker.

Read [references/configuration.md](references/configuration.md) when an optional
trusted-host or workspace-root configuration is present. Missing configuration
uses the safe default: trust only the current proven host and exact saved
project paths returned by Codex tools.

Never copy a checkout, branch, uncommitted state, credential, token, connector
session, or login into another host or isolated environment. If workspace
identity cannot be proven, stop and report the shortest reconnection action.

## Establish the control plane

Prefer these Codex task tools in order:

1. List saved projects to resolve project IDs, host IDs, project kinds, paths,
   and repository status.
2. List recent tasks across available hosts.
3. Read plausible coordinators and workers deeply enough to establish their
   objective, authorization, repository identity, result, blocker, and next
   action.
4. Confirm current branch, PR, checkout, worktree, and recent commit evidence
   from the already-proven workspace when repository work is involved.

If the required Codex task tools are unavailable, do not improvise with a clone,
new checkout, or replacement task. Ask the user to reopen a task on the trusted
workspace host and invoke “bring me back” there.

## Reconstruct and deduplicate in-flight work

For each plausible task, resolve:

- task ID, host ID, saved project, and exact working directory;
- objective and last substantive result;
- branch, PR, checkout, or worktree identity when applicable;
- active, waiting, blocked, completed, or abandoned state;
- remaining authorization boundaries and user decisions;
- one next safe action and the next reporting checkpoint.

Deduplicate by objective plus repository plus branch, PR, checkout, or worktree.
Prefer the task with the authoritative existing workspace and newest
substantive evidence. A similar title does not prove identity, and an idle task
does not prove unfinished work.

Read [references/continuity-record.md](references/continuity-record.md) only
when multiple workers, ambiguous duplicates, or an explicit handoff make a
structured record useful.

## Resume existing workers only

Do not create or fork tasks during recovery.

- Leave an active worker running unless it needs a decision or correction.
- Ask an idle worker for status when completion is unclear.
- Continue an idle, unfinished worker only when its workspace, scope, and
  authorization are proven.
- Surface a user decision instead of restarting blocked work.
- Record completed work and leave it stopped.
- Leave an unavailable host untouched and report how to reconnect it.

A continuation message must preserve the existing objective and say, in
substance:

> Continue in this existing trusted workspace and existing checkout or worktree
> only. Do not create another task, checkout, worktree, clone, or login. First
> report current status; continue only if unfinished and still within the
> previously authorized scope. Report at the next material checkpoint or
> terminal condition.

Do not override a worker's model or reasoning setting merely to resume it.

## Require a narrow capability preflight

Before meaningful work resumes, require the existing worker to verify only the
capabilities needed for that task. Prefer repository-provided preflight
commands; otherwise use narrow read-only checks for the executable, saved
project, existing checkout, connector, and authenticated account.

The preflight must not initiate authentication, expose credential values, or
change configuration. On failure, stop task execution, identify the missing
capability and worker, distinguish host unavailable from tool missing,
authentication expired, or permission denied, and give one precise
workspace-side repair action.

## Return a command view

Report:

- whether the current session is workspace-capable or coordinator-only;
- each recovered task, proven workspace identity, state, and next action;
- workers resumed, left active, blocked, completed, or intentionally ignored as
  duplicates;
- blockers and user decisions;
- confirmation that no duplicate task, checkout, worktree, login, credential
  transfer, or isolated replacement worker was created.

Keep checkpoints free of secrets, private keys, tokens, raw authentication
output, and sensitive payloads. Task history is the primary continuity record;
do not create or edit repository coordination files solely because this skill
ran.

## Treat new work separately

Recovery never implies authority to create new workers. If new work is needed,
explain why it is distinct and obtain an explicit request before creating a
task. Then use the ordinary project and repository workflow, including overlap
checks, rather than treating it as session recovery.
