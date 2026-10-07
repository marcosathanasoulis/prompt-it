# Changelog

## 1.6.1 - 2026-10-07

- Route each node of a task graph on its own (`side-lane auto-route --nodes`), not the whole job once, when the governed Side Lane core is installed. The read-only edition is version-aligned and has no content change.

## 1.6.0 - 2026-10-05

- Add a two-family question pass. When both Claude Code and Codex are reachable on included usage, Prompt it asks the other family, read-only, for its list of the genuinely ambiguous decisions and merges it with its own into one short question list with defaults. Measured on six real tasks (plans implemented and scored against the issues later found in review), this had the fewest defects and beat native planning on every task.
- Prompt it no longer layers Superpowers brainstorming or writing-plans on top of its own planning: that added cost and time with no reduction in defects. Superpowers still supplies TDD, debugging, worktree, review and verification. The read-only edition is version-aligned and has no content change.

## 1.5.9 - 2026-10-04

- Model choice now follows one Auto Router order, with or without Side Lane: an explicit
  request first, then a signed-in host with included usage, then metered models only when
  nothing included can do the task, and never extra usage without authorization. When the
  governed Side Lane core is installed, Prompt it cites its `side-lane auto-route`
  decision. Without Side Lane, or when the user declines OpenRouter, Prompt it lists the
  reachable models with strengths, weaknesses and relative cost and picks the cheapest
  that fits. OpenRouter stays optional. The read-only edition is version-aligned and has
  no content change.

## 1.5.8 - 2026-09-30

- When the public governed Side Lane package ships its `model-select` skill,
  Prompt it uses that skill to rank eligible routes by expected cost per
  successful task. The ranking is cited in staffing and stays advice under
  the existing eligibility and authority gates. The read-only edition is
  version-aligned and has no content change.

## 1.5.7 - 2026-09-26

- Add per-harness Ask first and Just go approval modes, first-use setup, and
  mid-session switching. Both retain research, necessary questions, a brief,
  staffing, and separate action/dispatch gates.
- With the private local-direct Side Lane package installed, use its shared
  selector and full qualified route inventory. With the public Governed Side
  Lane package installed instead, use its `check-capabilities`/`recommend`
  flow rather than the shared selector. Without either, staff verified local
  Claude, Codex, Devin, or Gemini access according to task fit.
- Add ten offline real-task scenario checks.

## 1.5.6 - 2026-09-26

- Let an installed local Side Lane skill supply a shared model-selector decision for staffing, using requester-bound local access and nonzero included-capacity opportunity cost. Keep the public planning workflow usable without that optional selector and preserve its exact-route and authority gates.

## 1.5.5 - 2026-09-21

- Separate a verified included subscription from unknown pricing. A route verified as covered by a subscription the user already pays has a known `$0` additional usage cost, which is neither an unknown price nor a zero-cost provider key, and it does not make every OAuth or hosted route free — coverage is route-specific and some are metered. A missing empirical task median for an otherwise authorized task is measurement absence: report the history as unavailable, never rewrite it to zero, and do not alert solely because it is missing.

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
