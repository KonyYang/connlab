# TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN

## Status

Complete/accepted by Integrator.

## Lane

`matrix-contact-measurement-plan`

## Planner Discovery Result

This lane is the planned successor to the accepted Matrix quantity chain (`TASK_357A` through `TASK_358A`) for the LLCR/CR-specific contact measurement model. The user suggested `TASK_359A`, but that identifier is already occupied by `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX`; therefore this planned lane uses `TASK_360A`.

## Current Phase / Active Task / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state before this lane: `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX` is complete.
- Role: Planner source-of-truth reconciliation.
- Why allowed: Reviewer plan gate and Reviewer implementation-readiness passed, Developer planning-first completed as docs-only, and the user explicitly approved reconciliation plus Developer implementation. This reconciliation changes governance records only; it does not implement product code or route Developer.

## User-Confirmed Scope

- Contact Measurement Plan is Matrix-wide across all included groups and eligible LLCR/CR Group-Step rows.
- It is not a current selected Group local panel and is not Basic Information.
- UI belongs below the Matrix Editor main table in the functional card area near `Project Schedule`, but not inside `Project Schedule`.
- V1 must stop exposing the generic duplicate fields `Test points`, `Readings / point`, and `Contact points` for this business workflow.
- V1 Fee quantity is `readings_per_sample`, derived from structured contact breakdown such as High Power Pin + Low Power Pin + Signal Pin + custom contacts.
- Fee Evaluation is a passive consumer: units for each LLCR/CR Fee row are `readings_per_sample * group sample qty` for the corresponding Group-Step row. No cross-Step aggregation is needed.
- Contact family breakdown is required for a later LLCR/CR specialized record workbook, but that workbook is a separate downstream lane and is not the existing generic `Test record` output.
- Matrix-wide common plan must support explicit Group/Step overrides. Updating the common plan must not silently overwrite confirmed or manually overridden Step values.
- LLCR and CR may use different contact families; CR must not be assumed to use all contacts.
- After Matrix Confirm, the confirmed Matrix Step contact snapshot is the authority for Fee and the downstream LLCR/CR specialized record workbook.

## Repository Evidence

- `TASK_357C` implemented generic Matrix Step quantities using `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- `TASK_357D` Fee consumption currently derives per-reading units from generic Step quantity facts.
- `TASK_357E` Test Record metadata currently projects the same generic Step quantity facts.
- `TASK_358A` removed Basic Information as the quantity default entry and moved transient defaults into Matrix Editor Step quantity setup.
- Current Matrix Editor UI still exposes generic Step quantity wording that is not suitable for the LLCR/CR contact measurement business model.
- No dedicated LLCR/CR specialized record workbook generation lane is currently active.

## Planned Data Authority Contract

- Draft authority: Matrix contact measurement plan state belongs to Matrix Editor, not Basic Information or Fee Evaluation.
- Common plan: project/Matrix-wide default contact breakdown for eligible LLCR/CR steps.
- Override plan: each eligible Group-Step may have its own explicit contact family selection and counts.
- Confirmed authority: Matrix Confirm copies the resolved Group-Step contact breakdown into a confirmed Matrix Step contact snapshot.
- Derived quantity: `readings_per_sample` is derived from selected contact family counts and is the only V1 quantity Fee needs.
- Legacy compatibility: existing generic Step quantity tables/data must not be destructively deleted. They may remain for historical compatibility or non-LLCR/CR fallback, but LLCR/CR contact measurement should use the new structured contact snapshot once implemented.

## Planned UI Contract

- Add a `Contact measurement plan` functional card below the Matrix Editor main table, adjacent to or near `Project Schedule`.
- Do not embed this card inside `Project Schedule`.
- Show common LLCR/CR contact family configuration and derived `readings / sample`.
- Show eligible included Group-Step coverage and explicit override status.
- Built-in contact families should include High Power Pin, Low Power Pin, and Signal Pin, with a planned custom contact entry mechanism for necessary project-specific contacts.
- Applying a common plan is explicit and blank/unconfirmed-only; it must preserve manual overrides and confirmed values.
- Do not expose the generic labels `Test points`, `Readings / point`, or `Contact points` for the LLCR/CR contact workflow.

## Fee Contract

- Fee Evaluation remains passive and editable only for fee review fields.
- Fee does not author High Power / Low Power / Signal / custom contact details.
- Each LLCR/CR Fee line uses the corresponding confirmed Group-Step `readings_per_sample`.
- Units are `readings_per_sample * Matrix group sample qty`.
- If the confirmed contact snapshot is missing or review-required, Fee marks the row review-required/manual instead of falling back silently to Basic Information or Fee-side entry.

## Downstream Specialized Workbook Boundary

- `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK` should be planned after `TASK_360A` is accepted.
- `TASK_360B` should generate a dedicated LLCR/CR record workbook from confirmed Matrix Step contact snapshots.
- That workbook is separate from the existing generic top-page `Test record` output.
- `TASK_360A` must not change the existing generic Test Record semantics or output.

## May Touch For Future Implementation

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- Matrix draft/confirmed storage models, repositories, and non-destructive migrations for contact measurement plan/snapshot tables.
- New backend application service(s) for Matrix contact measurement planning and authority building.
- Existing Matrix confirm/revision/carry-forward flow only as needed to copy resolved contact snapshots.
- New or focused Matrix contact measurement API routes and dependency wiring.
- `frontend/src/api/client.ts` only for typed contact measurement DTO/helpers.
- Matrix Editor feature components/selectors/tests for the contact measurement plan card.
- Fee Evaluation backend default-fill helpers/tests only to consume derived `readings_per_sample`.
- TASK_360A docs/evidence/board through normal lane flow.

## Must Not Touch / Locked Paths

- No product code in this Planner pass.
- No Basic Information quantity default UI restoration.
- No destructive schema/data deletion of existing generic quantity data.
- No LLCR/CR specialized workbook generation in `TASK_360A`.
- No change to existing generic `Test record` button, generic Test Record output semantics, or Word document generation.
- No Matrix parser/import changes.
- No StepInstance/execution persistence.
- No Fee-side contact authoring UI.
- No Report generation implementation.
- No LTR/public-drive/workbook authority changes.
- No real `D:\LabOfficeAuto`, `D:\Test Project`, `D:\PublicProject`, public-drive, or workbook mutation.
- No release/settings/template cleanup.
- No `.agents/**`, `docs/project_management/**`, or remote push.

## Validation Gate Draft

- Backend tests for common plan, contact family selection, derived `readings_per_sample`, override preservation, blank-only/common apply behavior, confirmed snapshot copy, and non-destructive compatibility with generic quantity data.
- Fee tests proving LLCR/CR units are per Group-Step `readings_per_sample * sample qty`, with no cross-Step aggregation and review-required behavior when snapshot data is missing.
- Frontend tests proving card placement below the Matrix table, not inside Project Schedule, common/override interaction, no generic quantity labels for this workflow, and no silent overwrite.
- Regression tests for `TASK_358A`, Fee passive consumption, and generic Test Record output boundaries.
- `npm run build`, focused `pytest`, `git diff --check`, trailing whitespace scan, forbidden-scope scan, and no-real-file-mutation scan.

## Authorization And Merge Gate

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation is authorized only within this task's May Touch, Must Not Touch, and Locked Paths boundaries.
- Developer implementation completed.
- Reviewer implementation re-gate passed after B1/B2/B3 fixes.
- QA gate passed.
- Integrator package isolation/readiness accepted the controlled TASK_360A package.
- Integrator excluded downstream workbook generation, unrelated Fee seed/rule/test residuals, release/settings/desktop/packaging residuals, `.agents/**`, `docs/project_management/**`, and real workbook/folder scope.

## Parallel / Serial Lane Assessment

- `TASK_360A` must precede the LLCR/CR specialized workbook lane because it creates the confirmed contact snapshot authority.
- `TASK_360B` is serial and should not start until `TASK_360A` is accepted.
- Fee consumption adjustments within `TASK_360A` can be developed with the same lane because they define the contract for derived `readings_per_sample`; broader Fee UI changes remain out of scope.

## Definition Of Ready

Definition of Ready, implementation readiness, Reviewer implementation gate, QA gate, and Integrator package/readiness gate are satisfied. The lane is complete/accepted.

## Integrator Acceptance

- Accepted package scope: Matrix contact measurement draft/confirmed authority, structured contact plan persistence/API, Matrix Editor contact measurement plan card/selectors/tests/CSS, focused Fee passive bridge, focused backend/frontend tests, and TASK_360A docs/evidence/board closeout.
- Validation accepted: backend contact plan/service/API/Fee suite `64 passed`; generic Test Record regression `30 passed`; frontend Matrix Editor/contact selector suite `2 files / 46 tests passed`; `npm run build` passed with existing Vite chunk-size warning only; `py_compile` passed; cached diff, trailing whitespace, line-count, staged whitelist, forbidden-path, and no-real-mutation scans passed.
- Browser smoke tooling limitation remains non-blocking because bundled Chromium is missing and system Chrome launch is blocked by EPERM; focused UI tests/source/static coverage passed.
- Remote push intentionally not performed.

## Blocking Questions

None blocking for planned `TASK_360A`.

Future `TASK_360B` should separately confirm the dedicated workbook template/sheet/column mapping from `D:/LabOfficeAuto/Test Project Confirm 20250423.xlsm` before implementation.
