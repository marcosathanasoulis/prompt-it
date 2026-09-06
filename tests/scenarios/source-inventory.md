# Synthetic repository evidence

This fixture represents an inspected repository, not a live service. Names and paths are invented for this evaluation. No external calls or repository edits are permitted.

- `service/runner.py` executes deterministic browser plans. `plan.py` defines its closed action vocabulary. A plan has one browser context; it supports presence assertions but no explicit absence assertion. Runner changes and the plan vocabulary must agree.
- `service/authoring.py` compiles user descriptions and saves drafts. It accepts a profile ID but does not carry login mode; it and `compiler.py` share the draft schema.
- `service/profiles.py` and `contracts/member.yaml` define profile attributes, sign-in type, and provisioning readiness. Not every saved profile is ready to run.
- `service/dashboard.py` aggregates test rows from repository files and authored storage. It treats a recent suite run as fresh even when individual required checks are missing. There is no versioned monitor definition or expected occurrence store.
- `service/notifications.py` sends every failing result through existing adapters. It has no incident ownership or deduplication. External sends are prohibited in this task; fake adapters exist.
- `service/web.py` owns all web routes and current permission checks. `service/static/` and `service/templates/` own UI files. One developer changing all route handlers simultaneously would collide with another route writer.
- Existing local tests use fixture browser pages, fake stores and a fake clock. No full workflow acceptance harness exists. The local fixture browser runtime is available.
- Scope approval covers planning only. No product changes, account provisioning, production writes, external sends or new purchases are authorized. The runtime supports native read-only research helpers within its policy; their findings are supplementary.
- Applicable repository rules require exclusive file ownership, branch review and no self-merge. This evaluation allows writing the requested brief artifacts only.
