# TASK_361A Contact Measurement Plan Authority Impact Contract Developer Evidence

Status: developer_planning_first_complete
Task: `TASK_361A_CONTACT_MEASUREMENT_PLAN_AUTHORITY_IMPACT_CONTRACT`
Lane: `contact-measurement-plan-authority-impact-contract`
Date: 2026-07-12
Role: Developer

## Gate

Developer planning-first only. No product code, schema, migration, API/client, UI, dependency, or test implementation changed.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_361A_CONTACT_MEASUREMENT_PLAN_AUTHORITY_IMPACT_CONTRACT`.
Why allowed: the board records TASK_361A as the current planned contract lane, Reviewer plan gate passed, and the user explicitly authorized Developer planning-first only.

## Repository Facts Used

- Matrix revision creation regenerates draft and confirmed Group/Row ids. Imported source snapshot ids survive, while manually created Group/Row lineage is nullable and cannot safely be inferred across revisions.
- Current typed `MatrixStepContactPlan` is persisted only as `contact_plan_json` in draft and confirmed Matrix Step quantity rows. It is copied through `build_confirmed_step_quantities()` when Matrix confirmation occurs.
- The active Matrix consumer paths, including Fee and the specialized LLCR/CR workbook projection, read active confirmed Matrix Step quantities. They do not have an independent plan revision lifecycle.
- Existing contact-plan migration is additive-only and adds JSON columns. It cannot express independent immutable plan revisions, target-impact decisions, manual rebinds, or a partial-compatible projection.

## Contract Decisions Frozen For Readiness

1. Use the plan-owned `cmp-target:v1` stable key: imported source lineage where available; plan-owned manual anchors otherwise; step sequence plus normalized suffix; generated Matrix ids are binding locators only.
2. Use an independent Project-scoped root with immutable `confirmed` / `superseded` revisions and one editable `draft` / `needs_review` revision. Drafts are never formal-consumer input.
3. Store target coverage/override and materialized family snapshots in first-class additive records. Do not use `review_reason` or existing Matrix JSON as the independent authority data transport.
4. Classify Matrix impact deterministically. Text-only and valid sample-quantity changes are compatible; structural, eligibility, manual-unmatched, or invalid-quantity changes need review. The formal projection is explicitly partial-compatible rather than all-or-nothing.
5. Schema is required, but no schema work is authorized in TASK_361A. TASK_361B must re-gate the exact additive migration, idempotent active-confirmed bootstrap, compatibility adapter, and rollback boundary.
6. Bootstrap only from active confirmed legacy Matrix contact plans, preserve exact target snapshots, never rewrite legacy JSON, and use unique provenance for idempotency.

## Downstream Boundary

- `361B`: schema, authority backend, classifier, bootstrap, effective projection API.
- `361C`: typed client and dedicated setup workspace after `361B` acceptance.
- `361D`: draft-only managed workbook after `361B`, parallel with `361C` only after their own gates.
- `361E`: confirmed consumer migration last; Fee and specialized workbook become consumers of the effective confirmed projection only.

Locked: generic Test Record, Matrix parser/import, Basic Information, LTR/public-drive, real workbooks/folders, StepInstance, Report, release/settings, `.agents/**`, `docs/project_management/**`, cleanup, commit, and push.

## Planning Validation

- Required task, plan, Planner, Reviewer, and Discovery evidence were read.
- The updated plan names stable-key, lifecycle, family snapshot, impact/projection, bootstrap/rollback, migration gate, downstream, validation, and package-isolation decisions.
- `git diff --no-index --check -- /dev/null docs/task_361a_contact_measurement_plan_authority_impact_contract_plan.md` and the equivalent Developer evidence check passed with existing LF/CRLF working-copy warnings only.
- Trailing-whitespace scan of both touched documents returned no matches.
- Targeted `git status --short` shows TASK_361A board/task/plan/evidence documents only. The board, Planner, Reviewer, task, and Discovery files are external lane documentation; no backend, frontend, test, API-client, schema, migration, or real-file path was edited by this Developer pass.

## Stop Point

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none for Developer planning-first. Product implementation remains unauthorized.
