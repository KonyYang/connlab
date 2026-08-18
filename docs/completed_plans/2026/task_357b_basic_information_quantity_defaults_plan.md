# TASK_357B Basic Information Quantity Defaults Plan

Status: complete/accepted by Integrator
Task: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`
Lane: `basic-information-quantity-defaults`
Date: 2026-07-08
Role: Planner

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` has Reviewer plan/readiness pass and is reconciled as the contract/downstream basis.
- Current role: Planner.
- Why allowed: User/Orchestrator requested source-of-truth reconciliation for TASK_357A and creation of downstream planned TASK_357B. This pass creates planned docs only and does not authorize implementation.

## 2. User Goal Restatement

Basic Information should hold project-level default quantity values for test points/readings/contact points. These values can be imported into Matrix Step setup as defaults. Matrix Step setup remains the final confirmation and override point. Fee Evaluation later consumes confirmed Matrix Step quantities passively.

## 3. Confirmed By User

- Basic Information may provide project-level defaults.
- Draft Basic Information values may be used as import defaults.
- Confirmed Basic Information values are stronger defaults when available.
- V1 fields are based on `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and `total_readings`.
- V1 final authority is one parameter set per Matrix Step, not group/condition/sample-size split.
- TASK_357B must not implement Matrix Step override, Fee consumption, or Test Record/Report reuse.

## 4. Confirmed By Repository Evidence

- `backend/application/project_basic_information_service.py` currently persists Basic Information draft and confirmed records as generic `values` and has no structured test quantity defaults.
- TASK_353A makes confirmed Basic Information a display identity authority, but it does not add quantity defaults.
- `backend/domain/project_matrix_draft_models.py` and `backend/domain/confirmed_matrix_authority_models.py` have no structured per-step quantity fields.
- TASK_351 Fee Evaluation default-fill currently derives reading units from confirmed Matrix text plus group sample quantity when possible.
- `docs/task_357a_matrix_quantity_authority_contract_plan.md` defines Basic Information as default source only and Matrix Step as final authority.

## 5. Planner Inferences

- TASK_357B should be limited to Basic Information source fields and read-model exposure.
- `total_readings` should probably be treated as derived downstream rather than a primary Basic Information input in V1, unless Reviewer/User explicitly wants direct entry.
- UI should keep labels concise and operational, consistent with ConnLab product guidance.
- Backend should own persisted default values and source metadata; React should not invent authority.
- If the existing generic Basic Information `values` record can hold new fields safely, schema changes may be avoidable. Developer planning-first must verify persistence/API behavior.

## 6. Not Yet Confirmed

No blocker for Reviewer plan gate.

Implementation-level decisions for Developer planning-first:

1. Whether `total_readings` is displayed as derived/read-only in Basic Information or omitted until Matrix Step setup.
2. Exact UI placement within Basic Information without crowding identity/required business fields.
3. Whether API DTOs need explicit typed fields or can preserve the current generic values map with frontend type helpers.

## 7. Scope And Contract

TASK_357B should plan:

- new Basic Information default fields for project-level test quantities;
- draft save behavior;
- confirm behavior;
- source/review metadata needed for TASK_357C import;
- clear downstream boundary that Basic Information defaults are not final authority.

Field recommendations:

| Field | Basic Information behavior | Notes |
|---|---|---|
| `test_points_per_sample` | editable optional default | Useful for common project default, e.g. 20 points per sample. |
| `readings_per_point` | editable optional default | Used with points to derive readings. |
| `contact_points_per_sample` | editable optional default | Useful for LLCR/CR/contact resistance. |
| `total_readings` | derived or manual review candidate | Planner recommends not making this a primary Basic Information field in V1 unless Reviewer/User approves. |

## 8. May Touch

Current planning pass:

- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_planner.md`
- `docs/task_board.md`

Future implementation draft:

- `backend/application/project_basic_information_service.py`
- Basic Information storage repository/model/API DTO files if Developer planning proves needed.
- `backend/api/routes_project_basic_information.py`
- `backend/api/dependencies.py` only for service wiring changes if needed.
- `frontend/src/features/project-basic-information/**`
- `frontend/src/api/client.ts` only for typed Basic Information DTO changes.
- focused Basic Information backend/frontend tests.
- TASK_357B developer/reviewer/QA evidence and board updates.

## 9. Must Not Touch / Locked Paths

Must not touch:

- Matrix Step setup model/UI.
- Matrix draft/confirmed authority persistence.
- Fee Evaluation default-fill/consumption implementation.
- Test Record/Report reuse implementation.
- Matrix parser/import.
- LTR workbook/public-drive authority.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user.
- release/settings/template residual cleanup.

Locked paths:

- `frontend/src/features/matrix-editor/**`
- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/project_matrix_*`
- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## 10. Dependency Relationship

- Upstream: TASK_357A contract.
- Direct downstream: TASK_357C Matrix Step setup model/UI.
- Later downstream: TASK_357D Fee passive consumption.
- Future contract: TASK_357E Test Record/Report quantity reuse.

TASK_357B implementation should not be treated as sufficient for Fee Evaluation. Fee must wait for Matrix Step confirmed quantity authority from TASK_357C.

## 11. Validation Gate Draft

Backend:

- Basic Information service tests for draft values, confirmed values, source priority, empty/invalid optional values, and no mutation of Intake/LTR source records.
- API tests if DTO/route shape changes.

Frontend:

- Basic Information UI/model tests for labels, optional inputs, draft save, confirm payload, and disabled/readonly behavior.
- No Matrix/Fee UI changes in this lane.

General:

- `npm run build`
- focused pytest for Basic Information
- `git diff --check`
- trailing whitespace scan
- forbidden-scope scan for Matrix/Fee/Test Record/Report/LTR/public-drive/release residual changes.

## 12. Merge Gate Draft

- Developer planning-first evidence completed before implementation readiness.
- Reviewer implementation-readiness gate passed.
- User approval and source-of-truth reconciliation before Developer implementation.
- Reviewer implementation gate pass after code.
- QA required if UI fields are added.
- Integrator packaging/readiness must exclude external release/settings/template residuals.

## 13. Definition Of Ready

Ready for Reviewer plan gate: yes.

Not ready for implementation: yes, by design. Implementation requires Developer planning-first, Reviewer readiness, user approval, and source-of-truth reconciliation.

## 14. Developer Planning-First Refinement

Status: developer planning-first complete.

This refinement keeps TASK_357B as a Basic Information-only planning lane. It does not authorize product code. It narrows the future implementation boundary for project-level quantity defaults that can later be imported into Matrix Step setup.

### 14.1 Current Repository Boundary

Developer planning-first confirmed these implementation facts:

- Basic Information persists draft/confirmed records in `project_basic_information_records.values_json`, exposed as `values: dict[str, str]` / `Record<string, string>`.
- The Basic Information API route already accepts and returns a generic values map for draft save and confirm.
- The Basic Information frontend is config-driven through `basicInformationFieldConfig.ts`; `ProjectBasicInformationWorkspace.tsx` renders fields from config and should not gain ad hoc quantity JSX.
- Existing repository and database structure can carry new optional quantity fields without a schema migration if fields remain stored as values-map entries.
- Current Matrix draft/confirmed authority and Fee Evaluation do not consume Basic Information quantity defaults. That must remain locked for TASK_357B.

### 14.2 Backend Strategy

Future implementation should keep Basic Information persistence compatible:

- Store `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample` as optional string values in the existing `values_json` map.
- Do not add database columns or schema migration in V1 unless implementation discovers the values-map path cannot meet validation or export requirements.
- Add service-level normalization/validation for these controlled numeric fields in `ProjectBasicInformationService` or a small adjacent helper.
- Accepted value shape: blank or non-negative decimal string. Prefer preserving operator-entered decimal text after trimming and normalizing only obvious whitespace.
- Reject invalid values on confirm with business-readable field labels; draft save may either preserve invalid draft text for correction or return warnings, but implementation planning should prefer non-blocking draft and blocking confirm.
- Do not add these fields to `REQUIRED_FIELD_LABELS`; they are optional defaults.
- Extend field suggestions only if there is a real source. There is currently no upstream deterministic source, so no source suggestions should be invented.

Recommended constants:

- `BASIC_INFORMATION_QUANTITY_DEFAULT_FIELDS`
- `BASIC_INFORMATION_QUANTITY_DEFAULT_LABELS`
- a decimal validation helper shared by save/confirm responses if needed.

### 14.3 API / DTO Strategy

Keep the existing endpoint shape:

- `GET /api/projects/{project_id}/basic-information`
- `PUT /api/projects/{project_id}/basic-information/draft`
- `POST /api/projects/{project_id}/basic-information/confirm`

The response may continue using `draft.values` and `latest_confirmed.values`. If frontend TypeScript needs safer field access, add typed key helpers or a narrow `BasicInformationQuantityDefaults` type in `frontend/src/api/client.ts` only if the implementation plan explicitly needs it.

No new endpoint is required in TASK_357B.

### 14.4 Draft Versus Confirmed Default Semantics

Draft and confirmed semantics:

- Draft values are operator-entered defaults and may later be imported into Matrix Step setup as draft defaults.
- Confirmed values are stronger defaults and should be preferred by TASK_357C when importing defaults for Matrix Step setup.
- Neither draft nor confirmed Basic Information quantity defaults are final downstream authority.
- Basic Information changes must not update Matrix Step quantities directly.
- TASK_357B should not emit Fee Evaluation rows, Test Record data, or Matrix Step override records.

Source precedence handed to TASK_357C:

1. confirmed Basic Information quantity defaults when available;
2. draft Basic Information quantity defaults when no confirmed value exists or when Matrix Step setup explicitly imports draft state;
3. no value, with Matrix Step setup showing manual review.

### 14.5 `total_readings` Policy

Developer planning-first decision:

- Do not store `total_readings` as a primary Basic Information editable field in TASK_357B V1.
- Treat `total_readings` as a derived/display-only preview if shown at all.
- The derived display should be local to Basic Information UI and must not be persisted unless a later lane approves direct storage.
- Suggested formula for display only: `test_points_per_sample * readings_per_point` when both are valid decimals. Do not multiply by sample quantity in Basic Information because sample/group quantity becomes Matrix Step context.
- If either input is missing or invalid, show a compact unavailable state such as `Derived in Matrix Step setup`, not a fake numeric value.

This keeps final total-reading authority tied to Matrix Step context.

### 14.6 Frontend UI Strategy

Use the existing config-driven Basic Information UI:

- Add a compact field group under the `Laboratory execution` panel, after core laboratory ownership fields and before schedule/commercial details.
- Suggested group title: `Quantity defaults`.
- Suggested helper copy, if needed, should be short: `Defaults for Matrix Step setup.`
- Fields:
  - `Test points / sample`
  - `Readings / point`
  - `Contact points / sample`
  - derived display: `Total readings`, read-only or omitted in V1.
- Inputs should use existing field styling. If a numeric input kind is added, keep it as a small extension of field config rather than page-local JSX.
- These fields are optional, not required, and should not block Basic Information confirm when blank.
- Invalid confirmed values should block confirmation with concise field-level copy.
- No future Matrix Step, Fee Evaluation, Test Record, or Report UI should appear in this Basic Information lane.

## 15. Planner Source-Of-Truth Reconciliation

Date: 2026-07-08
Status: complete/accepted by Integrator

Facts reconciled:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only.
- Reviewer implementation-readiness gate passed.
- User approved source-of-truth reconciliation and Developer implementation.

Implementation authorization remains bounded to Basic Information quantity defaults:

- store/expose optional `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`;
- keep `total_readings` derived/read-only or omit it from Basic Information V1 per the Developer planning-first decision;
- keep Basic Information as default source only;
- preserve Matrix Step final authority for TASK_357C.

Still locked:

- Matrix Step override/model/UI;
- Matrix draft/confirmed authority persistence;
- Fee Evaluation default-fill or consumption changes;
- Test Record/Report reuse implementation;
- LTR workbook/public-drive authority;
- schema migration unless implementation proves the values-map strategy cannot satisfy validation and route returns to Planner/Reviewer;
- unrelated release/settings/template residual cleanup.

Recommended next role: Integrator packaging/readiness accepted this lane after Developer implementation, Reviewer implementation pass, QA pass, package isolation, and validation.

Product design constraints:

- Keep the panel dense and operational.
- Do not use a separate card-heavy workflow, modal, hero text, or decorative treatment.
- Avoid long explanatory copy; explain authority with short helper/status text only.

### 14.7 Exact Future May Touch

Future implementation may touch, after Reviewer readiness and user approval:

- `backend/application/project_basic_information_service.py`
- optionally a new small backend helper under `backend/application/` for Basic Information quantity validation if it keeps the service below size limits
- `backend/api/routes_project_basic_information.py` only if response/error details need a narrow addition
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx` only for generic numeric/read-only rendering support, not ad hoc quantity layout
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts` only if derived display or normalization belongs in the model
- `frontend/src/api/client.ts` only for typed key helpers or response typing, not endpoint changes
- `tests/unit/test_project_basic_information_service.py`
- `tests/unit/test_project_basic_information_repository.py` only for values-map persistence regression if needed
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- TASK_357B Developer/Reviewer/QA evidence and board docs through normal lane flow

### 14.8 Must Not Touch / Locked Paths

Implementation must not touch:

- Matrix Step setup model/UI;
- Matrix draft/confirmed authority persistence;
- Fee Evaluation default-fill or consumption;
- Test Record/Report reuse;
- Matrix parser/import;
- LTR workbook/public-drive authority;
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user;
- release/settings/template residual cleanup;
- unrelated dirty files.

Locked paths remain:

- `frontend/src/features/matrix-editor/**`
- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/project_matrix_*`
- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

### 14.9 Test And Validation Plan

Backend focused tests:

- blank quantity defaults are accepted and do not become required fields;
- valid decimal strings survive draft save and confirm;
- confirmed values beat source/default suggestions without mutating source records;
- invalid numeric values block confirm with business-readable field labels;
- values-map persistence round-trips the new keys without schema migration;
- Basic Information changes do not create or mutate Matrix/Fee/Test Record records.

Frontend focused tests:

- Quantity defaults appear in the Basic Information page in a compact group;
- fields are optional and editable in non-readonly lifecycle state;
- fields are disabled in lifecycle readonly state;
- confirm payload includes valid quantity defaults;
- invalid numeric values show concise field-level blocking copy;
- derived `Total readings` display is read-only or omitted according to final implementation choice;
- no Matrix/Fee/Test Record action or copy appears in the Basic Information UI.

General validation:

- focused pytest for Basic Information service/repository/API if API behavior changes;
- focused ProjectBasicInformationWorkspace tests;
- `npm run build`;
- `git diff --check`;
- trailing whitespace scan;
- forbidden-scope scan proving no Matrix/Fee/Test Record/LTR/release/settings/real folder changes.

### 14.10 Package Isolation Risks

The current worktree contains external residuals under Settings/LTR helper files, backend desktop/release helpers, `dist_release/**`, `packaging/**`, frontend New Project tests, release/settings focused tests, `temp_agents_stash.md`, and pre-existing TASK_357A/357B docs/board files. TASK_357B must package only its Basic Information quantity defaults changes and evidence. Do not absorb those residuals.

## 15. Developer Planning-First Stop Point

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none.

Implementation remains not authorized until Reviewer readiness passes, the user approves implementation, and source-of-truth reconciliation records implementation authorization.
