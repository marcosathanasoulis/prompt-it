# Bring Me Back configuration

Configuration is optional. Without it, Bring Me Back trusts only the current
proven Codex host and exact saved-project paths returned by Codex project tools.

An installation may explicitly allow additional workspace hosts or restrict
workspace roots with a local file at `$CODEX_HOME/bring-me-back/config.json`
when `CODEX_HOME` is set, or otherwise at:

```text
~/.codex/bring-me-back/config.json
```

Example:

```json
{
  "schema_version": 1,
  "trusted_host_ids": ["host-id-from-codex-project-tools"],
  "allowed_workspace_roots": ["/absolute/path/to/projects"],
  "allow_existing_worktrees": true
}
```

## Safe interpretation

- `trusted_host_ids` contains exact stable host IDs returned by Codex tools,
  not display names guessed from conversation.
- `allowed_workspace_roots` contains absolute local paths on those trusted
  hosts. A matching prefix never proves a workspace by itself; saved-project,
  task, and repository evidence must still agree.
- `allow_existing_worktrees` permits only already-existing worktrees whose task,
  project, repository, and branch metadata can be proven. It never permits
  creating a worktree during recovery.
- Treat the configuration as advisory only when it is a local regular file
  controlled by the current user. If its provenance or permissions are
  ambiguous, ignore it and use the safe default.
- Missing fields use the safe default. Unknown fields, malformed JSON, relative
  paths, unavailable hosts, and contradictory evidence fail closed.

Configuration may narrow trust or explicitly add a host; it cannot authorize
new task scope, credentials, login, deployment, publication, destructive
actions, or a sandbox replacement worker.

Do not store tokens, keys, passwords, account cookies, connector state, or raw
authentication output in this file.
