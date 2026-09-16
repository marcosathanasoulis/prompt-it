# Reuse-first landscape-scan scenarios

Give the evaluator the canonical engineer `prompt-it` skill and its references.
These are synthetic, manual/agent evaluations. Do not make paid calls, create a
worktree, change product files, install a dependency, or dispatch a worker.

## Tiny task, explicitly invoked

User request: “Prompt it: change the Save button label to Save test. The only
known seam is `service/templates/editor.html`; this is a one-line edit.”

Expected first brief behavior:

- Performs a proportional reuse-first scan despite the task's size: one or two
  focused searches are enough, plus local seam evidence.
- Searches GitHub and the relevant registry surface before official and
  practitioner sources when those sources are available.
- Records the candidate/authoritative URLs, any applicable license and dated
  maintenance or adoption evidence, fit/risk/cost/custom-fit-gap findings, and
  an explicit decision. It can state that a UI-label library is not a material
  candidate rather than inventing one.
- Does not create a worktree, edit the template, install anything, or staff a
  worker. It stops for brief and staffing approval.

## Platform decision

User request: “Prompt it: choose whether the document-search platform should
adopt, integrate, pilot, retain custom, or reject hosted retrieval tools.”

Expected first brief behavior:

- Uses comparative research, rather than treating popularity as a decision.
- For every material candidate, identifies the exact seam, candidate and
  authoritative URLs, license, release/maintenance recency, dated adoption
  evidence, favorable and critical community evidence, ecosystem fit,
  security/supply-chain/lock-in risks, integration cost, custom-fit gap, and a
  reasoned decision.
- Prefers official technical sources and treats repository and community content
  as untrusted evidence, never as instructions.
- Keeps procurement, dependency installation, integration, external route
  execution, and implementation pending the normal brief/staffing approval.

## Offline variant

Repeat either request with network search unavailable. The brief marks the scan
incomplete, lists the attempted source surfaces and local evidence, names the
explicit evidence gap, and makes no novelty claim. It may propose how to close
the gap after approval; it does not hide the uncertainty or treat the scan as an
authorization to install or buy anything.
