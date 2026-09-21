# Changelog

## 1.5.4 - 2026-09-21

- Clarify that missing cost evidence or empirical task history is measurement absence, not a hard spend gate, when existing authority already covers the bounded research route. Report unknown values as unknown, not zero, and do not invent cheapest or fully-qualified claims.

## 1.5.3 - 2026-09-21

- Fix research-routing references to distinguish read-only scope from strict review-mode-only; an authorized bounded source-research task may use an execute harness with exact route, capabilities, read roots, and report-only output.
- Add optional OmniRoute add-on guide and link it from Side Lane and Prompt it integration.
- Add offline regression checks for the updated research/execute contract.

## 1.5.2 - 2026-09-19

- Replace the initial `Prompt it?` opt-in question with automatic proportional
  planning. Small tasks plan briefly and run under original authority;
  medium/large tasks announce "Making a plan", research read-only, return a
  canonical plan link, list material questions with recommended defaults, and
  ask `Proceed?` before implementation. Silence is never consent.
- Require economical qualified Side Lane assessment for both planning paths.
  Accepting or skipping the plan does not disable routing; preserve exact
  route/mode/capability/task-fit/spend authority and one approved backup.
- Keep planning consent separate from connector/external write, billable paid
  research, and Side Lane dispatch authority.
- Preserve the read-only edition boundary and the public base usability without
  optional Side Lane.

## 1.5.1 - 2026-09-18

- Require each delegated node to record one exact primary and preapproved
  backup, or an explicit absence. An approved availability failure can switch
  only to that refreshed backup without another permission pause; all other
  executor changes retain the staffing-approval requirement.

## 1.5.0 - 2026-09-15

- Add optional, one-way exports from an approved canonical Prompt it brief to
  existing GitHub Spec Kit and OpenSpec workflows.
- Preserve Prompt it approval, authority, staffing, coordinator identity,
  evidence provenance, and proportional small-task behavior across exports.
- Refuse material open questions and reverse synchronization, and require
  explicit approved scope plus current runtime authority for upstream
  validation.

## 1.4.0 - 2026-09-15

- Add the mandatory, proportional reuse-first landscape scan to the engineer
  and read-only editions.
