# TASK_334C_APPLICATION_FORM_WORD_COM_SESSION_LIFECYCLE_OPTIMIZATION

## Status

Complete as a Word COM session lifecycle foundation. Created, approved, implemented, and validated on 2026-06-24. Production Project Folder session wiring remains a separate decision.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_334B_APPLICATION_FORM_WORD_COM_PERFORMANCE_OPTIMIZATION` is complete and its completion notes identify Word COM lifecycle cost as the remaining Application Form write-back bottleneck.

The user explicitly asked to execute the next step after TASK_334B, with the next direction being Word COM session lifecycle and reducing or reusing open/close cost.

## Problem

TASK_334B added structured timing and reduced repeated body lookup behavior, but it did not produce a stable end-to-end runtime reduction.

Final real timing on a copied Application Form showed remaining large costs in:

- `word_dispatch`
- `document_open`
- `target_index_build`
- `document_close_quit`

The current Project Folder update usually writes one Application Form document per operation, so a persistent or reused Word session may or may not improve the real path. Reusing Word COM without evidence is risky because it can leave hidden `WINWORD.EXE` processes, lock documents, trigger invisible modal dialogs, or accidentally attach to user-opened Word documents.

## Goal

Determine whether Word COM session lifecycle reuse can safely reduce Application Form write-back time, then implement only the proven safe optimization.

## In Scope

- Profile Word COM lifecycle stages with current TASK_334B timing snapshots as the baseline.
- Measure a same-process hidden Word session path against the current one-session-per-document path.
- Distinguish `DispatchEx`, `Documents.Open`, `Document.Close`, and `Word.Quit` costs.
- If proven useful and safe, introduce a ConnLab-owned Word COM session/context abstraction behind the infrastructure Office layer.
- Allow Application Form write-back to use an explicitly provided ConnLab-owned session where appropriate.
- Preserve the existing default behavior unless the optimized path is selected by the owning application service or smoke runner.
- Ensure every opened document is closed and every ConnLab-owned Word application is quit on success and failure.
- Add tests for lifecycle cleanup on success and exceptions.
- Run real smoke timing and Word open/recovery validation after any implementation.

## Out Of Scope

- No frontend changes.
- No Project Folder API contract changes.
- No progress UI changes.
- No Application Form field scope changes.
- No header LTR layout changes.
- No Basic Information schema/API/source-provider changes.
- No Fee Form, Customer Feedback, Test Record, or LTR workbook behavior changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No global long-lived Word singleton unless a future separately approved task explicitly requests it.
- No attaching to or closing a user-owned visible Word session.

## Acceptance Criteria

- Current TASK_334B Application Form write-back behavior remains functionally unchanged.
- Lifecycle profiling records at least:
  - `word_dispatch`
  - `document_open`
  - `document_close`
  - `word_quit`
  - total write-back time
- A real baseline is captured before implementation on the current code path.
- A same-run comparison measures current one-session-per-document behavior versus any candidate session reuse path.
- If a Word session abstraction is introduced:
  - it uses ConnLab-owned hidden Word instances only
  - it is an explicit context manager or explicit lifecycle object
  - it closes opened documents on failure
  - it calls `Quit` on owned Word application exit
  - it does not attach to user-opened Word by default
  - tests prove cleanup on success and exception
- If lifecycle reuse is not materially faster or not safe, implementation stops after profiling and documents the rejected path instead of shipping risky persistent Word reuse.
- `Materially faster` means the candidate path must pass same-run timing comparison with at least three repetitions per shape:
  - the single-document candidate must not regress versus the standalone baseline median
  - the reuse candidate must improve the applicable median by at least `15%` or `2.0s`, whichever is easier to satisfy
  - one-off fastest runs do not qualify
- Real smoke confirms the generated Application Form opens normally with no recovery prompt.
- No orphan ConnLab-created `WINWORD.EXE` process is left by the focused smoke path. The smoke must record pre-run Word process ids and verify only newly-created ConnLab-owned Word process ids are gone after cleanup; it must not kill or treat user pre-existing Word processes as failures.

## Validation Plan

Unit tests:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Regression tests:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Real smoke:

1. Copy a real Application Form document into `tmp\task_334c_*`.
2. Run the current one-session-per-document path and record timings.
3. Run any candidate ConnLab-owned session path against an equivalent copy and record timings.
4. Reopen the generated document in Word with `OpenAndRepair=False`.
5. Record Word process ids before and after the smoke.
6. Confirm no recovery prompt and no orphan ConnLab-created Word process, without killing or failing on user pre-existing Word processes.

## Plan

Detailed plan:

`docs/task_334c_application_form_word_com_session_lifecycle_optimization_plan.md`

## Stop Point

Stop after TASK_334C completion. Do not start broader Project Folder orchestration, Application Form field-scope changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope without separate explicit approval.

## Completion Notes

- Added `ApplicationFormWordSession`, an explicit ConnLab-owned hidden Word COM session context.
- The session owns only the Word application it creates through `DispatchEx`, never attaches to user-opened Word, tracks opened documents, closes tracked documents, quits Word, and uninitializes COM.
- Session cleanup is defensive: document close failure no longer prevents best-effort `Word.Quit` and COM uninitialization.
- `write_application_form_fields_with_com()` now supports an optional caller-provided session while preserving standalone default behavior.
- Standalone default behavior still creates and cleans up its own ConnLab-owned session internally.
- Timing now records separate `document_close` and `word_quit` stages while preserving `document_close_quit` for compatibility.
- Application Form field scope, header LTR layout, visible read-back, and critical blocker semantics are unchanged.
- Document tracking now removes a document only after `Document.Close` succeeds, so close failures keep the document eligible for retry or session-level cleanup.
- `word_quit` timing is recorded even if session cleanup raises.
- The Project Folder production path still uses the standalone default call shape; explicit session orchestration is not wired into Project Folder in TASK_334C.

## Timing Summary

Pre-implementation current-path baseline on copied real Application Form:

- total: about `10.63s`
- `word_dispatch`: about `1.76s`
- `document_open`: about `0.85s`
- `target_index_build`: about `3.31s`
- `document_close_quit`: about `3.55s`

Post-implementation focused smoke, three repetitions per shape:

- standalone median: about `7.91s`
- explicit single-document session median: about `4.90s`
- explicit reused-session median: about `4.85s` per document

This smoke shows a promising explicit-session path, but it was not wired into the production Project Folder call path and was not an interleaved A/B/A/B production-path measurement. Treat it as evidence for a follow-up production integration decision, not as proof that `Update project folder` runtime is already reduced.

## Word Process / Open Smoke

- Pre-run `WINWORD.EXE` pids: none.
- Post-run `WINWORD.EXE` pids after condition-based wait: none.
- Waited about `3.77s` for Word asynchronous shutdown.
- Final generated Application Form opened with `OpenAndRepair=False`.
- Open check returned `opened=true`, `paragraph_count=256`, `table_count=18`.

## Validation Summary

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Result: `33 passed`.

Follow-up cleanup validation:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Result: `34 passed`.

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `37 passed`.
