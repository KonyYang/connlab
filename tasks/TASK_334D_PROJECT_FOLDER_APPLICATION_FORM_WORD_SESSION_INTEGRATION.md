# TASK_334D_PROJECT_FOLDER_APPLICATION_FORM_WORD_SESSION_INTEGRATION

## Status

Complete on 2026-06-24. Planned, approved, implemented, and validated.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_334C_APPLICATION_FORM_WORD_COM_SESSION_LIFECYCLE_OPTIMIZATION` is complete and its completion notes explicitly stop before production Project Folder session wiring.

The user asked to start the next plan after TASK_334C. This task is the bounded follow-up that decides whether the 334C explicit Word session path should be integrated into the real Project Folder Application Form write-back path.

## Problem

TASK_334C introduced a ConnLab-owned hidden Word COM session abstraction and proved it can be faster in focused copied-document smoke tests:

- standalone median: about `7.91s`
- explicit single-document session median: about `4.90s`
- explicit reused-session median: about `4.85s` per document

However, that smoke was not wired into the real Project Folder `Update project folder` path and was not an interleaved production-path A/B measurement. Shipping the session path without that proof could add Office lifecycle risk without actually shortening the user-visible operation.

## Goal

Run an interleaved production-path A/B validation for Application Form write-back and integrate the explicit Word session path into Project Folder only if it materially improves real `Update project folder` Application Form timing without leaving Word orphan processes or corrupting the copied request form.

## In Scope

- Measure the real Project Folder Application Form write-back path with current standalone behavior.
- Measure an equivalent candidate path that uses a facade-owned 334C ConnLab Word session without exposing the session object to the application layer.
- Use interleaved A/B/A/B-style timing so warm/cold Word variance does not decide the result.
- Add the smallest backend seam needed to run Application Form write-back inside a ConnLab-owned Word session:
  - `OfficeFacade`
  - `WordDocumentGateway`
- The Project Folder Application Form write-back service path must call an Office port method only; it must not import or construct Word COM session infrastructure.
- Preserve the default standalone behavior for callers that do not opt into a session.
- Wire the optimized path into Project Folder only if the evidence gate passes.
- Keep structured timing snapshots available for Application Form write-back.
- Verify the generated Word document opens with `OpenAndRepair=False`.
- Verify no ConnLab-created orphan `WINWORD.EXE` process remains after the operation.

## Out Of Scope

- No frontend changes.
- No Project Folder API response contract changes.
- No progress modal changes.
- No Application Form field-scope changes.
- No Application Form header LTR layout changes.
- No Basic Information schema, API, source-provider, or UI changes.
- No Fee Form, Customer Feedback, Test Record, LTR workbook, or Report generation changes.
- No `.docx` template redesign.
- No global long-lived Word singleton.
- No attaching to or closing user-owned visible Word sessions.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Evidence Gate

Production integration is allowed only if same-run interleaved timing proves the candidate path is materially better.

Minimum timing rule:

- Use at least five paired runs after one warm-up pair when feasible.
- If real-file smoke cost makes five pairs impractical, use at least three paired runs and record the reason.
- Compare medians for Application Form write-back total time through `ProjectApplicationFormWriteBackService`.
- Candidate must improve median Application Form write-back time by at least `15%` or `2.0s`, whichever is easier to satisfy.
- Required Forms regression tests must pass; full Project Folder required-forms timing may be recorded as an observation but is not the TASK_334D evidence gate unless an equivalent service graph is explicitly measured.
- A single fastest run does not qualify.

Safety rule:

- Pre-run and post-run Word process ids must be recorded.
- Pre-existing user Word processes are not failures and must not be killed.
- Any newly-created ConnLab-owned Word process must disappear after cleanup and a bounded wait.
- The generated Application Form must open with `OpenAndRepair=False` and no repair exception.

If the evidence gate fails, this task must stop after documenting the rejected candidate path. Do not wire the session path into Project Folder.

The low-level seam for a facade-owned session is allowed as a no-behavior-change infrastructure capability, but the Project Folder production path must remain unchanged if the evidence gate fails.

## Acceptance Criteria

- Existing Project Folder Application Form write-back behavior remains functionally unchanged.
- Current standalone behavior remains available and covered by tests.
- Candidate session behavior is measured through `ProjectApplicationFormWriteBackService` with a candidate Office writer, not only through a standalone gateway call.
- If the optimized path is integrated:
  - Project Folder Application Form write-back uses a facade-owned ConnLab hidden Word session for the scoped write-back operation.
  - The application layer does not import `ApplicationFormWordSession` or any pywin32/COM infrastructure.
  - The session is closed on success and failure.
  - Default non-Project-Folder callers still work without passing a session.
  - Unit tests prove pass-through and cleanup behavior.
  - Project Folder required-forms tests still pass.
- If the optimized path is not integrated:
  - The task file records timing evidence and the reason.
  - No production behavior changes are shipped.
- Real smoke records timing, Word open validation, and Word process cleanup results.

## Validation Plan

Unit tests:

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_application_form_word_session.py tests/unit/test_project_application_form_write_back_service.py -q
```

Required Forms regression:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Focused timing smoke:

1. Record pre-run `WINWORD.EXE` process ids.
2. Run one warm-up pair using copied Application Form material.
3. Run interleaved current/candidate pairs against equivalent copied inputs.
4. Record structured timing snapshots for each run.
5. Reopen the final generated Word document with `OpenAndRepair=False`.
6. Record post-run Word process ids after a bounded wait.
7. Report median current vs candidate timings and whether the evidence gate passed.

## Plan

Detailed plan:

`docs/task_334d_project_folder_application_form_word_session_integration_plan.md`

## Stop Point

Stop after TASK_334D completion. Do not start Report generation, Application Form field-scope changes, Project Folder UI changes, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope without separate explicit approval.

## Evidence Gate Result

Evidence gate: PASSED.

Interleaved same-service A/B smoke used `ProjectApplicationFormWriteBackService` for both paths. The current path used the normal Office writer, while the candidate path used a writer whose `write_word_application_form_fields(...)` delegated to the facade-owned session helper. One warm-up pair was discarded.

- Current median Application Form write-back: about `8.91s`.
- Candidate median Application Form write-back: about `5.36s`.
- Improvement: about `39.8%`.
- Pre-run `WINWORD.EXE` pids: none.
- Post-run `WINWORD.EXE` pids: none.
- Remaining new Word pids: none.

The candidate passed the required `15%` or `2.0s` improvement gate and did not leave a ConnLab-created Word process.

Required Forms graph timing was not used as a hard gate in the completed follow-up; Required Forms was covered by regression tests and the final Application Form integrated smoke.

## Completion Notes

- Added `OfficeFacade.write_word_application_form_fields_with_owned_session(...)`.
- `OfficeFacade` owns `ApplicationFormWordSession` inside infrastructure; application code does not import or construct Word COM session objects.
- `OfficeFacade` only starts the owned Word session when `application_form_requires_com(...)` returns true, preserving python-docx fallback behavior for simple table-only `.docx` documents.
- Review follow-up added direct facade fallback regression coverage proving the owned-session helper does not start Word for non-COM documents.
- `WordDocumentGateway.write_application_form_fields(...)` now accepts an optional infrastructure-only `application_form_word_session` and passes it through to the COM writer only when the document requires COM.
- `ProjectApplicationFormWriteBackService` now calls the session-owning Office port method for the Project Folder Application Form write-back path.
- Review follow-up corrected evidence wording so TASK_334D does not overclaim a Required Forms service graph timing gate.
- Default non-Project-Folder callers can still call `OfficeFacade.write_word_application_form_fields(...)` with unchanged behavior.
- Final real smoke on a copied request form completed the integrated service path in about `4.75s`; gateway timing was about `3.48s`.
- Final generated document opened with `OpenAndRepair=False`, `paragraph_count=256`, and `table_count=18`.
- Final pre-run and post-run Word pid checks showed no remaining new `WINWORD.EXE` process.

## Validation Summary

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Result: `37 passed`.

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `37 passed`.
