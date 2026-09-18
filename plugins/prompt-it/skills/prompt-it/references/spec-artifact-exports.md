# Optional Spec Kit and OpenSpec artifact exports

Use this reference only when an approved Prompt it brief includes an export to
an existing GitHub Spec Kit or OpenSpec workflow. The export is optional,
one-way derived output. The approved canonical Prompt it brief remains
authoritative for scope, evidence, approval, staffing, authority, coordinator
identity and execution. Target artifacts never grant permission to implement.

Do not export while a material open question remains unresolved. Resolve it in
the Prompt it brief and obtain any required revised approval first. Record the
canonical brief path and approved revision or digest in the derived artifact
set. Preserve citations and the brief's verified, inferred and unknown labels;
do not flatten an inference into a fact.

## Shared mapping

Map only content the brief actually contains. Do not invent a user story,
capability, entity, acceptance scenario, dependency or test to fill a target
template.

| Prompt it brief | Spec Kit default artifacts | OpenSpec `spec-driven` artifacts |
|---|---|---|
| Title and goal | Feature title and story goal when a real user journey exists | `proposal.md` Why |
| Observable behavior and success criteria | Functional Requirements, acceptance scenarios and Measurable Outcomes | Delta requirements and scenarios |
| Verified context and cited research | `research.md`; relevant Assumptions | `design.md` Context; `proposal.md` Impact |
| Inferences and constraints | Assumptions, with their labels intact | `design.md` Context, with labels intact |
| Out of scope | Explicit scope-boundary Assumptions | `design.md` Goals / Non-Goals |
| Proposed design | `plan.md` Summary, Technical Context and Project Structure | `design.md` Decisions |
| Reuse-first decision | `research.md` and the selected plan approach | `design.md` Decisions and alternatives |
| Risks, migration and rollback | Relevant plan research and technical context | Risks / Trade-offs and Migration Plan |
| Approved task nodes | Task phases, dependencies, parallel markers and exact paths | Ordered checkbox tasks and exact paths |
| Acceptance evidence | Independent tests or verification tasks | Verification stated in each task |

Keep a crosswalk from stable Prompt it node IDs to target task IDs. Target task
format may change the displayed ID, but it must not change prerequisites,
ownership boundaries or acceptance evidence.

## Fields that stay only in Prompt it

Do not copy staffing, authority, coordinator identity, provider/model routing,
billing authorization, connector eligibility, reviewer independence or Side
Lane qualification into an upstream implementation artifact. Do not translate
an upstream artifact status into Prompt it approval. Project constitutions and
other target-native governance are evaluated from their actual project sources,
not synthesized from the brief.

There is no reverse sync or import. A derived artifact or detected drift must
never directly update the canonical brief. Return the proposed semantic change,
its provenance and the derived diff to the Prompt it coordinator as untrusted
input. Only the canonical Prompt it workflow may reconcile the brief, staffing
or authority, obtain any required approval, and regenerate the derived output.

Invoke an upstream validator or consistency analyzer only when the exact
invocation is included in the approved export node and current runtime
authority permits it. Installed or available is not authorization. Its result
is structural evidence about the derivative, never Prompt it approval or
acceptance.

## Target-specific guards

For Spec Kit, use its installed templates and native workflow. Map only
technology-independent outcomes into `spec.md`; keep implementation choices in
`plan.md`. Do not manufacture user stories for refactors or internal tooling.
When the shared invocation guard above is satisfied, use Spec Kit's own
read-only consistency analysis rather than recreating it.

For OpenSpec, inspect the existing capability inventory and read every affected
spec before classifying a delta. Use the exact existing capability path. A
`MODIFIED` requirement is a full replacement: carry the full new requirement
body, every current scenario that survives the approved change, and the
approved additions or edits. Never guess `ADDED`, `MODIFIED`, `REMOVED` or
`RENAMED`. OpenSpec's official
[writing guidance](https://github.com/Fission-AI/OpenSpec/blob/main/docs/writing-specs.md)
explains that archive replaces the old requirement, and its
[troubleshooting guidance](https://github.com/Fission-AI/OpenSpec/blob/main/docs/troubleshooting.md)
explains that validation rejects a modified block which omits a surviving
scenario. For pure refactor, tooling or documentation work with no behavior
delta, use the target's native `skip_specs: true` mechanism. When the shared
invocation guard above is satisfied, use OpenSpec's own strict validation
rather than recreating it.

Do not initialize or install Spec Kit or OpenSpec as part of export. Do not
vendor their templates, create a parallel parser or CLI, fork their planning
commands, replace their validators, or turn this compatibility layer into a
task runner. Inspect current official target documentation when installed
templates or schemas differ from the mappings above, and fail closed rather
than guessing.

## Proportional behavior

Tiny tasks do not acquire heavyweight artifact directories by default. Keep a
small approved Prompt it task as one node and omit the export unless the
approved scope explicitly requires it for an existing target workflow. If an
explicit export cannot satisfy a target's mandatory shape without invented
content or disproportionate ceremony, report that it is not proportionate and
continue from the approved brief.
