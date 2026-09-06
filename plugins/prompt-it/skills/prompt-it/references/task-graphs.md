# Executable task graphs and task-relative staffing

Use this reference for multi-part work. Scale the representation to the outcome;
a tiny task needs no manufactured branches, reviewers or readiness ceremony.

## Build the graph before staffing

Start from observable outcomes and existing implementation seams. Map every
success criterion to task IDs. Expose research, contracts, implementation,
integration, verification and handoff only where the task needs them. A label
such as “implementation” is not an executable node when it conceals distinct
outputs, ownership, capabilities or acceptance checks.

Shared decisions belong in a prerequisite contract node. Once accepted, that
contract can enable independent UI, backend, test-design or documentation
branches. Separate integration from independent review when those have distinct
evidence. Keep edits to a shared route, schema or compiler with one owner, or
sequence transfers of ownership explicitly. Do not use shared architecture as a
blanket reason to keep all subsequent work on the coordinator.

## Node contract

Use a compact table, for example:

| ID | Objective and output | Prerequisites | Owner / exact executor and reason | Acceptance evidence |
|---|---|---|---|---|

For each ID include here or in linked node details:

- relevant source/input paths or links and provenance;
- concrete output and its handoff location;
- required tools, host identity, capabilities and authority;
- affected files or isolated worktree when applicable, and exclusive write owner;
- completion checks and the coordinator who accepts their evidence.

## Discover candidates and justify each assignment

At planning time inspect the originating host's current model inventory, exact names and
supplied capability descriptions; use documented presence-only discovery for
installed external lanes. First follow the canonical skill’s installed-core and
configured-route discovery pass; separate configuration, task eligibility and
authorization. Coordinator origin does not imply which other providers exist.
Use the native inventory available in Codex or Claude
Code; do not assume either host exposes the other's models or tools. Include qualified currently available Anthropic/Claude
models using their supplied capability descriptions in the same comparison.
Record the relevant inventory evidence in the brief.
Descriptions are candidate-selection evidence, not demonstrated performance or
route qualification. Do not hardcode a permanent ranking or infer capability
from a model name alone.

Use this compact rubric for each node:

| Decision | Evidence to consider |
|---|---|
| Reasoning fit | Ambiguity, architecture/integration consequences, boundedness, supplied model descriptions and relevant observed capability |
| Context fit | Required sources and handoff size, known context-window limits, continuity needed; mark unknown limits rather than inventing them |
| Operational fit | Available tools, exact host/identity, provider/model, gateway when applicable, mode, authority and demonstrated route readiness |
| Independence | Whether a reviewer authored the work or can provide a distinct evidence-based critique |
| Efficiency and preference fit | Least-cost/most-efficient credible fit using supplied evidence; explicit developer preferences or stated surplus/usage constraints, with tradeoffs recorded |

For example, **if currently available and supported by supplied evidence**, GPT-6
Astra may fit complex high-ambiguity architecture, consequential integration or
final synthesis; GPT-5.6 Sol or Terra may fit bounded implementation or review;
a faster/smaller candidate may fit well-specified mechanical or low-risk work.
A currently available qualified Claude model can fit any of these task roles
when its supplied description and task evidence support that assignment; the
Claude brand does not automatically make it an independent reviewer.
These examples do not assign those models universally or require any lineup.
Discover exact names and capabilities afresh, and explain why the specific node
fits the selected candidate. A required tool or authority gap overrides an
otherwise promising description.

GLM model choice is fixed, not discretionary: staff only `glm-5.3` when
explicitly enabled. Preserve its exact worker host, provider, gateway and mode
and all existing route, authority and task-fit gates. Never add other GLM choices
or a fallback, or infer task suitability from availability. Its execute-only
constraint remains; it cannot substitute for review-mode research.

Routing is provider/company-neutral. For ordinary work choose the least-cost or
most-efficient currently available candidate that credibly satisfies the
reasoning, tools, authority, context and quality requirements. Honor explicit
developer preferences or stated surplus/usage constraints when compatible,
including preferences for Codex or Claude, and record the tradeoff. Never query
quotas or invent numerical prices, cost rankings or efficiency estimates. When
cost evidence is absent, label it unknown and use evidenced efficiency and fit.

Every assignment needs a task-specific reason. Explain coordinator/frontier
execution relative to eligible bounded workers: no capable eligible worker is a
valid reason; inertia or vague shared context is not. Multiple nodes may share
one executor. Require an independent second opinion when meaningful uncertainty
or non-determinism, high impact or irreversibility, material design disagreement
risk, or a specified acceptance gate justifies it. Record the distinct question
and expected value in that node. No redundant multi-model work is justified by
provider diversity alone. When capable workers are already staffed, assign routine integrated
test execution, operator documentation, monitoring and cleanup to those workers,
including their evidence handoffs. Do not bury these deliverables in a coordinator
“final integration” node. The coordinator owns consequential integration decisions
and final acceptance of worker-produced evidence; this does not require doing
all routine verification personally. Tiny tasks need no additional agent.

If a preferred model is unavailable before approval, explain the gap and propose
an eligible alternative for that task. Preserve required-lane readiness as a
prerequisite. After approval, stop affected dispatch and revise staffing rather
than silently substituting; existing authority does not imply a new route.

A required unready route gets a prerequisite node with the missing capability,
owner, permitted qualification/repair scope and acceptance evidence. A configured
route alone does not pass: require an authorized bounded round trip or other
real evidence of the needed capability, at the proper stage. A planned test is
not a passed test. If qualification needs new permission, record that gate.
Optional absent routes do not create blocking prerequisites or installation work.

## Validate before handoff

For branching work use Mermaid with the table's exact IDs. Mark parallel
branches, integration and review gates, and describe the critical dependency
chain without inventing timing estimates. Verify:

- every outcome has a producing node and acceptance check;
- IDs and prerequisite references resolve and the graph is acyclic;
- prerequisites include required contracts, authority and readiness;
- overlapping file ownership is removed or explicitly sequenced;
- inputs, outputs and acceptance criteria are concrete enough for a fresh worker;
- staffing is justified per task and independent review is independent of authorship.

Resolve defects before presenting the brief. A larger table or more model names
does not compensate for hidden work or missing evidence.

## Schedule after approval

Only dispatch a node when the coordinator has accepted every prerequisite
output, its authority is present, and its route is qualified. Honor concurrency
limits and exclusive ownership; graph independence is not permission to exceed
runtime limits. Each worker receives the accepted contracts, bounded sources,
output location, authority and acceptance checks.

Collect provenance, artifacts, validation results and unresolved issues in each
handoff. A failure blocks dependents, not unrelated approved branches. Reuse
owners for fixes within their approved route/scope; revise staffing before a
material executor change. The coordinator integrates accepted branches and
requires evidence on the integrated artifact, not merely successful isolated
nodes. Independent findings inform final acceptance; no worker self-approves
production actions or the complete outcome.
