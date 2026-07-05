# TASK_351 Fee Evaluation Auto Default Fill Planner Evidence

Task: `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL`
Lane: `fee-evaluation-auto-default-fill`
Role: Planner
Status: planned - Reviewer plan gate passed; Developer planning-first authorized; implementation not authorized
Date: 2026-07-05

## Scope

Planner Discovery Gate and reviewable plan preparation for Fee Evaluation auto default-fill. This pass only updates planning/source-of-truth documents and does not implement product code.

## Required Reads Completed

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md` / `DESIGN.md` via `$impeccable` context loader
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `backend/modules/fee_evaluation/__init__.py`
- `backend/api/routes_confirmed_matrix_fee_draft.py`
- `frontend/src/api/client.ts` targeted Fee Evaluation DTO excerpts
- `tests/unit/test_confirmed_matrix_fee_draft_service.py` targeted evidence

## Discovery Findings

### Confirmed By User

- Auto default-fill should reduce Fee Evaluation manual entry but keep operator confirmation/correction.
- Unit Price Reference items should enter the rule-library layer.
- Only deterministic fields should auto-fill; complex/interval/multi-mode cases remain review-required.
- User resolved the prior 3 blockers: V1 can use user-confirmed rules plus existing seed JSON while treating `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` as reference authority; Temperature Rise Base Fee should prefill `500` with review-required/manual confirmation; LLCR should compute total readings when readings/specimen can be derived and otherwise remain review-required.
- Sample preparation, Visual Examination, LLCR, Durability, High temperature Life, Thermal Shock, Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance, MFG, Vibration, Microsecond discontinuity, Mechanical Shock, force-family rules, CR/Specified Current, Report preparation, and Temperature Rise have V1 business rules recorded in the plan.

### Confirmed By Repository

- Backend already has a Confirmed-Matrix-backed Fee Evaluation draft service.
- Backend already has `FeeRuleLibrary`, `FeeRuleMatcher`, seed loader, rule models, row status, review-required state, unit/base/discount/testing fee fields, and pricing source traceability.
- Seed JSON already contains Unit Price Reference-style rules for many target items, but many are intentionally review-required or not yet derived.
- Frontend already renders editable Fee Evaluation preview rows for the target fields.
- Frontend API client already has typed Fee Evaluation draft and line-item DTOs.

### Planner Inference

- This should be a formal lane, not a quick fix.
- Backend should own auto-fill rules; frontend should display editable defaults and review-required cues.
- Existing draft API may be sufficient, but Developer planning should decide whether field-level source/review metadata is needed.
- Implementation should avoid schema changes unless proven necessary.

### Not Yet Confirmed

No blocking product questions remain for Reviewer plan gate.

Developer planning should still make implementation-level details concrete: parsing patterns for hours/days/cycles/readings/current, whether field-level API metadata is necessary, and exact compact frontend treatment for auto-filled review-required values.

## Files Created / Updated

- `tasks/TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL.md`
- `docs/task_351_fee_evaluation_auto_default_fill_plan.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_planner.md`
- `docs/task_board.md`

## May Touch Draft

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- New focused helper under `backend/modules/fee_evaluation/`
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if response metadata changes.
- `frontend/src/api/client.ts` only if response metadata changes.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Focused Fee Evaluation backend/frontend tests.
- TASK_351 docs/evidence/board through normal lane flow.

## Must Not Touch / Locked Paths

- Matrix parser/import/Confirmed Matrix authority semantics.
- Fee workbook Office gateway/template layout except regression checks.
- Real external Testing Fee Evaluation `.xls`, public-drive files, LTR workbook files, and user folders.
- Folder Actions, Intake LTR, Projects registry/list, Project Workbench lifecycle, Matrix Editor unrelated behavior.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user.
- Release/settings/basic-information residual cleanup.
- `.agents/**`
- `docs/project_management/**`

Locked paths include:

- `backend/modules/test_plan/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `dist_release/**`
- `packaging/**`
- Real `D:\Test Project/**`, `D:\PublicProject/**`, public-drive roots, and external workbook authority files.

## Validation Gate Draft

- Backend unit coverage for fee rules and draft service calculation/review behavior.
- Backend integration coverage for fee draft API if DTO metadata changes.
- Frontend focused coverage for default-filled editable rows, review-required cues, manual overrides, and read-only state.
- Persistence/export regression for edited/default values.
- Build and package-scope scans.

## Discovery Gate Decision

Definition of Ready for planned lane: satisfied.

Definition of Ready for Reviewer plan gate: passed by conversational callback.

Definition of Ready for Developer planning-first: satisfied after user approval and Planner source-of-truth reconciliation.

Definition of Ready for approved implementation: satisfied after Developer planning-first completion, Reviewer implementation-readiness pass, explicit user implementation approval, and Planner source-of-truth reconciliation.

## Source-Of-Truth Reconciliation Checkpoint

Date: 2026-07-05

Status: reconciled for Developer planning-first only.

Facts recorded:

- Reviewer plan gate passed read-only and confirmed TASK_351 is a formal backend/frontend Fee Evaluation rule/default-fill lane, not a quick fix.
- Reviewer found the plan's May Touch, Must Not Touch, Locked Paths, acceptance criteria, and validation gates sufficient for Developer planning-first.
- User explicitly approved `TASK_351` entering Developer planning-first.
- Developer stopped before planning-first because repository source-of-truth still recorded TASK_351 as planned / Reviewer plan gate pending.
- Developer changed no product code during the blocked checkpoint.
- Planner reconciliation updated board/task/plan/evidence to align source-of-truth for Developer planning-first only.

Reconciliation evidence:

- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_reconciliation_planner.md`

## Implementation Authorization Reconciliation Checkpoint

Date: 2026-07-05

Status: implementation authorized; pending Developer implementation.

Facts recorded:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated TASK_351 plan/evidence only.
- Reviewer implementation-readiness passed.
- User explicitly approved TASK_351 reconciliation and Developer implementation.
- Planner reconciliation updated board/task/plan/evidence to align source-of-truth for Developer implementation pass.

Authorization scope:

- Fee Evaluation auto default-fill for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and review-required/manual confirmation metadata.
- Use user-confirmed V1 rules plus existing seed JSON.
- Keep `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` as template authority reference only; no runtime `.xls` ingestion.
- Preserve scope locks against real workbook/public-drive/folder mutation, Matrix parser/import/Confirmed Matrix authority changes, Fee workbook template redesign beyond regression checks, schema changes without separate re-gate, future scope, release/settings cleanup, `.agents/**`, and `docs/project_management/**`.

Implementation reconciliation evidence:

- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_implementation_reconciliation_planner.md`

## Stop Point

Stop after Planner source-of-truth reconciliation. Recommended next role: Developer implementation pass.

## External Residuals Excluded

Current `git status --short` shows unrelated New Project, Settings/LTR, release/packaging, desktop release, and `temp_agents_stash.md` residuals. They are not part of TASK_351 and must not be packaged with this planned lane.
