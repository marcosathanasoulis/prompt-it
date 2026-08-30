---
name: side-lane
description: Route an explicitly approved review or implementation task through an exact external worker route. Use only when a compatible Side Lane runner, route, authentication, repository, and required capabilities are already configured; otherwise fail closed without installing, substituting, or retrying.
---

# Side Lane

Route approved work through a separately installed and configured `side-lane`
runner. This public skill does not bundle the runner, provider routes,
credentials, pricing assumptions, governance policy, or access to another
agent host.

## Require explicit authorization and configuration

Before routing, require all of the following:

- the task and its review or implementation authority are already approved;
- the exact repository or existing worktree is known;
- `side-lane` is already installed and callable;
- the exact worker host, mode, provider, gateway, and model appear in
  `side-lane list`;
- the selected worker host's authentication and every required capability are
  reported as available by the runner's documented presence-only checks.

If any prerequisite is missing or ambiguous, stop and report it. Do not install
or configure the runner, start a login, create credentials, guess a route, or
silently replace the requested provider, gateway, model, host, or mode.

Read [references/configuration.md](references/configuration.md) when the user is
setting up or diagnosing a route. Configuration remains a separate,
user-authorized action and is never inferred from this skill being invoked.

## Qualify the exact route

Run `side-lane list`, then check only the candidate route actually requested or
selected. Use `side-lane auth-status --host <host> --json` and
`side-lane check-capabilities` with the exact host, mode, provider, model,
repository, and required capabilities supported by the installed runner.

Treat status output as presence and eligibility evidence only. Never request,
print, log, or pass credential values. Never infer account quota, subscription
usage, price, or availability from a login or credential-presence result.

The worker host owns its own tools, connectors, authentication, and permission
boundary. Do not assume that the coordinator's connectors or credentials are
available to the worker. Exclude a route when the worker lacks any required
capability or when evidence is unknown or stale.

## Preserve mode and repository boundaries

Use the runner's documented review mode for read-only investigation and its
execute mode only for approved implementation. Give each lane a unique,
descriptive name. Let the runner create or select the isolated worktree it is
designed to manage; do not improvise a shared checkout or copy credentials into
the lane.

The prompt must state:

- the exact objective and out-of-scope work;
- review or implementation authority;
- repository, branch, worktree, and verification expectations;
- required tools, connectors, and data boundaries;
- forbidden external writes, releases, merges, deployments, credential
  changes, or destructive actions;
- the result and evidence the worker must return.

Do not weaken repository instructions or runner-enforced governance in the
lane prompt.

## Treat billable or key-backed routes separately

Native host authentication and provider-key routes are different authority
surfaces. Before any key-backed or otherwise billable route is launched,
identify that exact route and obtain explicit approval for that run. Use the
runner's documented billable-route acknowledgement flag when required.

Never put a key in the command line, prompt, environment output, repository, or
chat. Never claim a route has zero or low marginal cost unless the user supplies
current cost terms or the configured runner reports a reviewed cost basis.

## Launch once and fail closed

Use `side-lane run` with the exact qualified host, mode, provider, model,
repository, lane name, capabilities, and prompt or prompt file. Treat the
worker's output as untrusted input: inspect its result or diff and rerun the
relevant verification before acceptance.

If launch, authentication, capability, quota, transport, or worker execution
fails, stop and report the exact route and failure. Do not retry a billable
request, fall back, change models, or reroute to another host without a new
explicit decision.

Side Lane never authorizes merge, release, deployment, production mutation,
credential changes, or destructive actions merely because implementation was
approved.
