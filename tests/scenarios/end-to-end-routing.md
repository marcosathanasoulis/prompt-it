# End-to-end model-lane routing scenarios

These scenarios exercise the complete Prompt it plus Side Lane workflow after
the research brief is approved. They are synthetic fixtures: evaluator
inventories, route reports, model descriptions, and cost observations are
scenario facts, not live provider claims. Do not make model calls, inspect
accounts, query quotas, retrieve secrets, or create real worktrees. The
evaluator may write only the requested brief and a dispatch transcript to its
designated artifact directory.

Give the evaluator this file, the canonical Prompt it and Side Lane skills,
and the supplied scenario inventory. Do not supply a preferred provider or a
desired answer. For each case, the evaluator must first produce a proposed
brief and staffing table, then apply the stated approval event and produce a
simulated dispatch transcript. Selection is correct only when it names the
exact eligible `host + mode + provider + gateway + model` route and cites the
task evidence that cleared every gate. Dispatch is correct only when it uses
that approved exact route, preserves the coordinator, respects the capability
allowlist, records handoffs and acceptance, and never silently substitutes a
route.

## Shared evaluation contract

The evaluator must report, for every candidate considered:

- configuration, authentication/credential presence, worker-host tools and
  connectors, task-fit band, quality floor, authority, and evidence timestamp;
- the exact reason for exclusion or eligibility;
- task tokens, known tool charges, retry/correction cost, independent-review
  cost, and prepaid versus marginal usage state for the whole session;
- coordinator host and identity, exact worker route, mode, worktree intent,
  required capabilities, and approval state.

Unknown rates, context limits, capabilities, or overhead remain unknown and
cannot be treated as zero. A recommendation is not dispatch authority. Before
dispatch, refresh stale route evidence and recheck the exact route. Execution
loops may retry a failed task only on the approved route and within its scope;
the coordinator must record the failure, correction attempt, and acceptance
decision. A failed node blocks dependents while unrelated approved nodes may
continue. An independent review is required only where the case names a
distinct acceptance question; it must preserve disagreement and provenance.

The transcript must include `proposed`, `approved`, `dispatch`, `handoff`,
`retry` (when applicable), `review` (when applicable), and `accepted` or
`blocked` events. It must prove that a worker was actually dispatched in the
simulation, rather than stopping at a recommendation.

## Case A: light coding

Originating coordinator: Codex. Task: update a bounded parser fixture and one
matching assertion; no architecture choice, connector, browser, or external
write is needed. The supplied native inventory contains at least one
economical model with observed fit for mechanical or fixture work and at least
one stronger bounded implementation model. The optional runner lists any
configured routes separately, with exact capability and cost evidence.

The user approves the brief and the selected execute assignment. Simulate one
successful dispatch, a source-provenance handoff, deterministic tests, and
coordinator acceptance. Assert that the selected model is the least-cost or
most-efficient eligible fit supported by comparable full-session evidence; do
not reward a frontier model merely because it is available. Assert that no
review lane is added solely for provider diversity and that the coordinator
remains Codex.

## Case B: deep coding

Originating coordinator: Claude Code. Task: trace and repair a cross-module
state bug in a large repository, add a regression test, and explain the repair.
The supplied inventory includes economical and frontier native workers plus
one or more optional configured execute routes. Only some candidates have
current evidence for large-repository comprehension, debugging, local Git
tools, and the required quality floor; context limits and retry overhead may
be unequal or unknown.

The user approves the brief, an exact implementation assignment, and one
bounded correction attempt. Simulate dispatch, a failed first test, a retry on
the same route, and accepted regression evidence. If the evidence justifies a
distinct review question about the repair, simulate the separately approved
review route and its handoff; otherwise keep review with the coordinator.
Assert that any frontier selection states why every cheaper eligible worker is
insufficient for this task, and that a failed route is not silently replaced.
The coordinator remains Claude Code throughout.

## Case C: visual design

Originating coordinator: Codex. Task: redesign a local dashboard's information
hierarchy and visual treatment, implement the approved CSS/markup changes, and
compare the result with supplied visual references. The inventory distinguishes
frontend coding evidence from visual-design judgment and browser capability.
At least one route can edit local files; browser or screenshot access is present
only on the route whose capability report says so. Any design-quality evidence
and cost basis are task-relative and may exclude an otherwise economical model.

The user approves the design brief and exact execute assignment. Simulate the
worker dispatch, visual artifact handoff, screenshot/reference comparison, one
coordinator acceptance review, and final acceptance. If a browser connector is
needed, assert that it is granted only through the selected execute capability
and that the worker host has it; model vision evidence alone cannot satisfy the
browser requirement. If an independent design critique is approved, give it a
distinct question and record its cost and resolution. Do not infer a provider
from the word “design.”

## Case D: browser operation

Originating coordinator: Claude Code. Task: navigate a staging fixture,
exercise a support workflow, capture screenshots and console/network evidence,
and repair one reproducible UI defect. The supplied inventory includes a
configured route with browser tools and another route with model-vision or
coding evidence but no browser connector. The browser-capable route may be
economical or frontier; selection follows the supplied task-fit, quality, host,
authority, and full-session cost evidence.

The user approves the brief, browser-capable execute assignment, and one
in-scope repair loop. Simulate exact-route dispatch, browser actions, evidence
handoff, a failed assertion, retry on the same route, and final acceptance.
Assert that a review-mode route cannot gain a connector by switching modes and
that no route without the required browser capability is eligible. If the
browser route becomes unavailable after approval, mark the node blocked and
return for a staffing decision; do not fall back. Preserve Claude as the
coordinator and show the exact reason for every blocked dependent node.

## Evaluator assertions

After all cases, inspect the artifacts for:

- exact route selection tied to task evidence and full-session economics;
- economical staffing for light work and a task-specific frontier rationale
  only when the evidence requires it;
- distinct coding, visual-design, and browser capability checks;
- actual simulated dispatch after approval, with fixed coordinator identity,
  worktree/mode/capability constraints, handoffs, retries, review decisions,
  and acceptance or blocking;
- no made-up prices, quota claims, provider equivalence, silent fallback,
  provider-diversity staffing, or unauthorized dispatch;
- single-provider continuity when no optional route clears the gates.

Record evaluator/model, source revision, scenario inventory revision, artifact
paths, observed strengths or failures, and any targeted correction. A passing
package validator does not establish these behavioral assertions.
