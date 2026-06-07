# TASK_304 New Project Lab Performing Tests Confirmation - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task for planning: TASK_304_NEW_PROJECT_LAB_PERFORMING_TESTS_CONFIRMATION.
- Allowed now because: the task board currently has no active implementation task, and the user explicitly assigned this correction to TASK_304.
- Status: complete.

## Step 1: Task Understanding

Goal: add a required `Lab Performing the Tests` setup confirmation field to New Project creation, promote the confirmed value into `ApplicationForm.lab`, and make the downstream Section 2 Word gateway compatible with the real application-form label.

Input data:

- Operator selection from `Dongguan` or `Valley Green`.
- Existing New Project intake case and draft setup values.
- Existing New Project completion request.
- Existing `.docx` Section 2 write-back target field `lab`.

Output data:

- `project_setup.lab_performing_tests` saved with the intake draft.
- New Project completion request/command carries `lab_performing_tests`.
- The confirmed project's `ApplicationForm.lab` stores the selected lab for downstream Section 2 and LTR readiness consumption.
- Completion audit/operator note records the selected lab.
- Section 2 gateway can write `lab` when the target label is `Lab Performing the Tests:`.

Modules involved:

- Frontend New Project setup feature.
- Frontend intake page state and setup payload helpers.
- Frontend API DTOs.
- Backend intake case review service.
- Backend New Project completion route/service.
- Backend application form repository/update boundary used by completion.
- Backend Word document gateway Section 2 label matching.
- Focused frontend/backend tests.

Not allowed:

- No automatic Section 2 write-back during New Project completion.
- No LTR workbook Location/Mfg. Site mapping change.
- No new database column.
- No settings UI.
- No Matrix, fee, report, StepInstance, or deployment changes.

## Step 2: Design

### Data Structure

Use a narrow string field in the existing New Project setup payload:

```text
lab_performing_tests
```

Allowed values:

```text
Dongguan
Valley Green
```

Default:

```text
Dongguan
```

The field remains part of `project_setup` rather than becoming a new database column. This matches the existing setup confirmation design and avoids a persistence migration for a confirmation value.

During New Project completion, the validated value is also promoted to `ApplicationForm.lab`. This is the persistent consumption source for TASK_304 because:

- current Section 2 preview/write-back APIs accept `lab` as an explicit request field and do not read `project_setup`;
- current LTR readiness for `lab_performing_tests` reads `application_form.lab`;
- `ApplicationForm.lab` is already the domain field representing the application form Section 2 lab value.

TASK_304 does not make Section 2 APIs read `project_setup` directly.

### Frontend Changes

Files:

- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/api/client.ts`
- relevant frontend tests

Planned changes:

1. Extend `NewProjectSetupConfirmationValues`:

```ts
labPerformingTests: string;
```

2. Add a feature-local constant:

```ts
const LAB_PERFORMING_TESTS_OPTIONS = ["Dongguan", "Valley Green"] as const;
```

3. Render a required select in the setup card:

```text
Lab Performing the Tests*
```

4. Initialize empty setup values with `labPerformingTests: "Dongguan"`.
5. Restore from `project_setup.lab_performing_tests`, falling back to `Dongguan`.
6. Include `lab_performing_tests` in `projectSetupPayload`.
7. Add missing-key handling for `lab_performing_tests`.
8. Send `lab_performing_tests` in `completeNewProject`.

### Backend Changes

Files:

- `backend/application/intake_case_review_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/application/new_project_completion_service.py`
- `backend/infrastructure/storage/repositories/intake.py` or the existing application-form repository port, if an update method is needed
- `backend/infrastructure/office/word_document_gateway.py`
- relevant backend tests

Planned changes:

1. Add `lab_performing_tests` to `_normalized_project_setup` allowlist.
2. Validate `lab_performing_tests` during setup draft update/autosave:

```text
missing/blank may be omitted for backward compatibility, but unsupported non-empty values are rejected with a business-readable error
```

3. Add `lab_performing_tests` to `CompleteNewProjectRequest`.
4. Add `lab_performing_tests` to `CompleteNewProjectCommand`.
5. Validate the field during completion:

```text
required and one of Dongguan, Valley Green
```

6. Promote the validated completion value into the confirmed project's latest `ApplicationForm.lab`.
7. Include the field in `_operator_note`.
8. Add `"lab performing the tests"` to `SECTION2_FIELD_LABELS["lab"]`.

The implementation should not change `CommitLtrAuthorityCommand.location`; LTR workbook Location remains its existing source/mapping.

### Promotion Timing And Idempotency

Promotion must happen in the New Project completion request after setup validation and after the project is confirmed or loaded, but before LTR commit returns success:

```text
validate setup
  -> confirm new project or load already-confirmed project
  -> if project has no registered LTR, update latest ApplicationForm.lab
  -> commit or load LTR
  -> return success
```

Rules:

- Fresh confirmation path: write the selected lab into the newly confirmed project's latest `ApplicationForm.lab`.
- Already-confirmed but not yet registered path: write the selected lab into the latest `ApplicationForm.lab` before the LTR commit attempt.
- Already registered/idempotent path: do not mutate `ApplicationForm.lab`; return the existing registered LTR behavior unchanged unless a later task explicitly implements frozen-field correction.
- If no application form exists for the confirmed project, fail with a business-readable completion error instead of silently dropping the lab value.
- The update must happen inside the same request transaction as New Project completion, using the existing repository/session boundary.

### Section 2 Consumption Path

TASK_304 closes the consumption path by using `ApplicationForm.lab` as the durable project source:

```text
Project setup confirmation
  -> project_setup.lab_performing_tests draft value
  -> complete-new-project request
  -> NewProjectCompletionService validation
  -> confirmed ApplicationForm.lab
  -> existing LTR readiness source
  -> future Section 2 request defaulting can read ApplicationForm.lab
```

TASK_304 creates the durable domain source for Section 2. It does not wire the current Section 2 preview/write-back request body to auto-default from `ApplicationForm.lab`; that UI/API defaulting can be a later approved task.

### API Contract

Extend `POST /api/intake-cases/{case_id}/complete-new-project` request body:

```json
{
  "lab_performing_tests": "Dongguan"
}
```

The response does not need a new field for TASK_304.

### Dependency Direction

The dependency flow remains:

```text
Frontend -> API route -> application service -> infrastructure gateway
```

The frontend must not inspect or modify Word files. The Word label compatibility fix stays inside `backend/infrastructure/office/word_document_gateway.py`.

## Test Plan

### Frontend Tests

Add or update focused tests to verify:

- `Lab Performing the Tests*` appears in the setup card.
- `Dongguan` and `Valley Green` options are present.
- default state is `Dongguan`.
- `projectSetupPayload` includes `lab_performing_tests`.
- completion payload includes `lab_performing_tests`.

Use concrete test targets rather than a broad pattern:

```powershell
cd frontend
npm test -- --run NewProjectSetupConfirmationPanel IntakeInboxPage useNewProjectCompletion --watch=false
```

### Backend Tests

Update `tests/unit/test_intake_case_review_service.py`:

- `project_setup.lab_performing_tests` is persisted.
- unsupported `project_setup.lab_performing_tests` is rejected during update/autosave.
- unknown setup keys are still ignored.

Update `tests/integration/test_new_project_completion_api.py`:

- completion accepts `lab_performing_tests`.
- missing or invalid `lab_performing_tests` returns 400 with a readable message.
- successful completion persists the selected value into the confirmed project's `ApplicationForm.lab`.
- already-confirmed but not-yet-registered completion persists the selected value before LTR commit.
- already-registered/idempotent completion does not mutate `ApplicationForm.lab`.
- fake LTR commit path still succeeds with valid setup.

Update `tests/unit/test_ltr_readiness_service.py` or add an integration assertion:

- after successful completion, `lab_performing_tests` readiness resolves from the promoted `ApplicationForm.lab` value.

Update `tests/unit/test_word_document_section2_write_gateway.py`:

- a table label `Lab Performing the Tests:` is recognized as the `lab` field.

Optionally add a fixture-style check against the real template only if test policy allows using `D:\Source\Template`; otherwise keep the unit fixture deterministic.

### Validation Commands

Run after implementation:

```powershell
cd frontend
npm test -- --run NewProjectSetupConfirmationPanel IntakeInboxPage useNewProjectCompletion --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_intake_case_review_service.py tests/integration/test_new_project_completion_api.py tests/unit/test_ltr_readiness_service.py tests/unit/test_word_document_section2_write_gateway.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or section2 or task304"
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/intake
```

- Import or continue a New Project package.
- Confirm `Lab Performing the Tests*` defaults to `Dongguan`.
- Change it to `Valley Green`.
- Confirm the field remains selected while editing the application draft.

## Risks And Mitigations

- Risk: confusing `Lab Performing the Tests` with LTR workbook Location.
  - Mitigation: use a distinct key `lab_performing_tests` and do not alter `location` behavior.
- Risk: Section 2 write-back still fails on the real template.
  - Mitigation: add the real label alias and a targeted Word gateway test.
- Risk: future lab option changes require code edits.
  - Mitigation: keep TASK_304 options hard-coded by explicit task scope; defer settings-driven options to a later approved task.
- Risk: users assume Section 2 is written during New Project completion.
  - Mitigation: TASK_304 only stores the value and fixes gateway compatibility; no new write-back action is added.
- Risk: Section 2 still does not auto-default from the stored lab in the UI.
  - Mitigation: TASK_304 writes the durable domain source `ApplicationForm.lab`; a later UI wiring task can default the Section 2 request field from that source without changing persistence again.

## Review Checklist Before Implementation

- Scope is limited to the setup confirmation field and Section 2 label compatibility.
- No automatic Office write is introduced.
- No database migration is introduced.
- No Matrix or downstream output behavior changes are introduced.
- Tests cover default, draft validation, persistence, API validation, ApplicationForm.lab promotion, registered-idempotent non-mutation, LTR readiness consumption, and Word label matching.

## Approval Gate

Implementation was approved by the user and completed for TASK_304. Stop here; do not proceed to another task.
