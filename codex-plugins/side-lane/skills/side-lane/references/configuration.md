# Side Lane configuration

Use this reference only when the user explicitly asks to configure or diagnose
a Side Lane route. The public skill does not install a runner or define its
configuration file format.

## Required components

A usable route needs all of the following:

- a compatible `side-lane` executable already installed on the coordinator
  host;
- a runner catalog entry naming the exact worker host, provider, gateway,
  model, and supported modes;
- an existing repository the runner is allowed to use;
- worker-host authentication configured through that host's documented login
  flow, or a provider credential stored through the runner's documented secure
  credential mechanism;
- capability and governance evidence sufficient for the requested task.

Do not invent a catalog schema or edit an unknown configuration file. Use the
installed runner's own documentation and help output. Do not add a provider,
gateway, model, or credential merely because another installation uses it.

## Safe preflight

Begin with read-only discovery:

```text
side-lane list
side-lane auth-status --host <codex-or-claude> --json
side-lane check-capabilities \
  --host <codex-or-claude> \
  --mode <review-or-execute> \
  --provider <provider> \
  --model <model> \
  --repo <absolute-existing-repository> \
  --json
```

Use only flags confirmed by the installed runner's `--help`. A capability check
must not initiate login, retrieve credential values, make a paid model call, or
change runner configuration.

## Credential boundary

Prefer the selected worker host's documented native authentication when that is
the configured route. For a provider-key route, use only the runner's documented
secure storage integration. Never accept a secret pasted into chat, a prompt,
command-line argument, repository file, or diagnostic output.

The presence of authentication does not prove quota, billing state, connector
access, model entitlement, or task capability. Verify each independently using
documented presence-only checks.

## Launch shape

After the route and task are explicitly approved, use the installed runner's
documented command shape. A typical compatible runner accepts the following
fields:

```text
side-lane run \
  --host <codex-or-claude> \
  --mode <review-or-execute> \
  --provider <provider> \
  --model <model> \
  --repo <absolute-existing-repository> \
  --lane-name <unique-lane-name> \
  --capability <required-capability> \
  --prompt-file <approved-prompt-file>
```

Some key-backed routes also require an explicit billable-route acknowledgement.
Use it only after approval for that exact run. Never add undocumented flags or
silently select a default route.
