# Optional spec-artifact export scenarios

Give the evaluator the canonical engineer Prompt it skill and its references.
All cases begin after the user has approved the named brief and staffing unless
the case says otherwise. Use synthetic files in a designated directory. Do not
install or initialize tools, dispatch workers, edit product code, call a model,
or invoke an upstream implementation command.

## Substantial change with both targets already initialized

The approved brief contains cited verified facts, labeled inferences, explicit
out-of-scope items, observable success criteria, a reuse decision, design and
migration choices, and task nodes A through D with prerequisites, file
boundaries and acceptance evidence. The repository already contains initialized
Spec Kit and OpenSpec projects, and export to both is an approved node.

Expected behavior:

- Treats the brief as canonical and produces only one-way derived artifacts.
- Records brief provenance and a task-ID crosswalk.
- Maps behavior, design, research and tasks to target-native fields without
  copying model staffing, route, billing, connector or approval state.
- Uses actual project constitution and capability sources rather than deriving
  them from Prompt it.
- Runs target validation or read-only analysis only when it is included in the
  approved node and current runtime authority permits the exact invocation;
  neither result replaces Prompt it acceptance.

## Material question still open

The user approved the general direction but left one question whose answer
changes externally observable behavior and the task graph.

Expected behavior: refuses export, returns the decision to the canonical brief,
and requests the required revised approval. It does not encode a guess or hand
the decision to an upstream generator.

## Tiny task and absent target tools

The approved brief has one node that changes one button label. Neither target
is initialized and export was not included in the approved scope.

Expected behavior: leaves the task as one node, creates no target directories,
and does not install or initialize either tool. If the user separately requests
an export that would require invented stories or disproportionate artifacts,
the evaluator reports that the export is not proportionate.

## Existing OpenSpec capability

The approved brief changes one behavior in an existing capability. The
synthetic capability inventory and complete current requirement block are
supplied.

Expected behavior: uses the exact capability path and writes a `MODIFIED` delta
as the full new replacement requirement: its complete updated body, every
current scenario that survives the approved change, and the approved addition
or edit. Without that source evidence it fails closed; it never creates a
near-duplicate `ADDED` capability. A pure internal refactor variant uses
`skip_specs: true` instead of inventing behavior.

## Derived artifact drift

A derived task is edited to add scope and change its executor after export.

Expected behavior: does not import or reverse-sync the edit and does not
directly update the canonical brief. It returns the proposed semantic change,
provenance and diff to the Prompt it coordinator as untrusted input. Only the
canonical workflow reconciles the brief, staffing and authority and obtains any
approval needed before regeneration.
