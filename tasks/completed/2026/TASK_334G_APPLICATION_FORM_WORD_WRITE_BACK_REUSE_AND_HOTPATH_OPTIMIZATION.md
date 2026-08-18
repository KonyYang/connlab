# TASK_334G_APPLICATION_FORM_WORD_WRITE_BACK_REUSE_AND_HOTPATH_OPTIMIZATION

## Status

Complete, including review follow-up fixes.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH` is complete and the task board is stopped, waiting for a separately approved next task.

The user explicitly requested returning to the Word Application Form write-back chain because real Workbench smoke showed the `Updating Application Form` step as the largest remaining cost, about `8.8s`.

## Problem

Recent real browser smoke on project `72fbbfa290294da9a507344b68ff900f` measured Project Folder update at about `19.5s` after choosing the conflict strategy. The largest remaining visible step was:

```text
Updating Application Form: about 8.8s
```

This conflicts with the best focused `TASK_334D` service smoke, where the integrated owned-session path completed around `4.75s`. The next task must resolve this real-path mismatch before adding another low-level COM optimization.

Observed current code behavior:

- `ProjectApplicationFormWriteBackService.write_back(...)` always calls the Word writer after safety checks.
- Existing output records block unsafe user edits, but they do not provide a fast path for unchanged Application Form outputs.
- The service registers a context signature using `application-form:{form_id}|{basic_information.context_signature}`, but the selected source attachment hash is not part of that signature.
- The context signature also lacks an explicit Application Form write-back mapping version, so old filled `.docx` files could be reused after write-back rules change.
- In `Backup and Rebuild` flows, the old official folder can be moved before Application Form write-back starts, so a simple output-record path lookup may not find the previous filled `.docx`.
- The Application Form write-back API response currently does not expose structured Word timing stages, making it hard to prove whether time is spent in dispatch/open, target index, save, close, or orchestration overhead.

## Goal

Reduce the real Workbench `Updating Application Form` stage while preserving visible Word correctness and safety.

Primary target:

- For unchanged Basic Information + unchanged selected Application Form source, repeated Project Folder update/rebuild should avoid unnecessary Word COM write-back when a safe reusable filled Application Form artifact is available.

Fallback target:

- If no safe reusable artifact exists, the existing owned-session Word COM path remains correct, timed, and no slower than the current path.

## In Scope

- Capture a current real-path baseline for Application Form write-back through the Workbench/Project Folder orchestration shape.
- Add structured timing visibility to `ProjectApplicationFormWriteBackService` and its API response without changing frontend layout.
- Add a safe Application Form reuse decision model for unchanged outputs.
- Include selected Application Form source identity in the write-back context signature when available.
- Include an explicit Application Form write-back mapping token, e.g. `application-form-output:lab_section_v1`, in every new reusable context signature.
- Add an infrastructure/application seam that can reuse a previously verified ConnLab-filled Application Form only when all safety checks pass:
  - same project
  - same selected Application Form identity
  - same selected source file hash when known
  - same confirmed Basic Information context
  - previous output record is current/system-managed and fingerprint-valid
  - reusable artifact file exists and matches its recorded fingerprint
  - target is a fresh source copy or an unchanged managed target
- For rebuild flows where the old official folder may be moved before write-back, explicitly evaluate whether reuse must be captured before folder replacement. If needed, add only a narrow pre-rebuild artifact capture seam; do not broaden the Official Workspace business flow.
- If Backup/Rebuild reuse is implemented, the data flow must be explicit:
  - capture happens before the official folder is moved or deleted
  - capture copies only a fingerprint-verified current `SECTION2_WRITE_BACK` artifact into a ConnLab-owned operation temp path
  - the later Application Form write-back step receives the captured path through an application-layer operation context, not by guessing moved backup paths
  - temp artifacts are cleaned after success, and retained only in a diagnostic operation folder on failure
- Preserve the existing Word COM owned-session path when reuse is unavailable or unsafe.
- Preserve all TASK_332C Application Form field scope and critical blocker rules.
- Add tests proving reuse avoids the Office writer and unsafe/mismatched cases still fall back or block.
- Run real timing smoke and record before/after Application Form stage timing.

## Out Of Scope

- No new Application Form fields.
- No writing multi-row fields such as Description P/N, Product Description, Test Item, or Applicable Specifications.
- No Word template redesign.
- No replacing Word COM for real E-3718-style Application Forms.
- No frontend layout, progress modal, or button changes.
- No Fee Form, Customer Feedback, Test Record, LTR workbook, or Report behavior changes.
- No Basic Information schema/API/source-provider changes.
- No Project Folder conflict workflow redesign beyond the minimum artifact-capture seam if real reuse requires it.
- No global long-lived Word singleton.
- No attaching to or closing user-owned visible Word sessions.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- Current Application Form write-back behavior remains functionally unchanged when reuse is unavailable.
- API/service timing distinguishes at least:
  - `application_form.resolve_target`
  - `application_form.safety_check`
  - `application_form.reuse_lookup`
  - `application_form.reuse_copy` when used
  - `application_form.office_write` when used
  - `application_form.register_output`
  - `application_form.total`
- If Word COM is used, existing gateway timing stages remain available for diagnosis.
- Reuse must not happen if:
  - selected source hash changed
  - Basic Information context changed
  - reusable file is missing
  - reusable file hash differs from the output record
  - target was manually changed outside ConnLab
  - previous output source/status cannot prove ConnLab-managed current output
- When reuse succeeds, the Office writer is not called and the final target receives the verified filled `.docx`.
- Application Form output record registration uses a context signature that includes selected source identity when known.
- Application Form output record registration uses a context signature that includes the write-back mapping token.
- Rebuilt target restored to original source copy is still allowed, but safe reuse may replace it with the verified filled artifact if context matches.
- Real smoke records before/after `Updating Application Form` timing:
  - target: reduce unchanged repeat/rebuild Application Form stage by at least `50%` or `4.0s`
  - if target is not met, document whether the blocker is lack of reusable artifact after backup/overwrite, Word COM open/close variance, or orchestration outside this task.
- Generated Application Form opens with Word using `OpenAndRepair=False`.
- No new ConnLab-created orphan `WINWORD.EXE` remains after fallback COM smoke.

## Validation Plan

Unit tests:

```powershell
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
```

Add or extend tests for:

- context signature includes selected source hash when known.
- safe reusable Application Form artifact skips the Office writer.
- source hash mismatch falls back to Word write-back or blocks according to target state.
- Basic Information context mismatch does not reuse.
- missing or fingerprint-mismatched reusable artifact does not reuse.
- rebuilt target restored to source hash can be replaced by safe reusable artifact.
- unsafe manually modified target still blocks before reuse or Office write.
- timing entries are present for reuse and Office paths.

Regression tests:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Real timing smoke:

1. Use project `72fbbfa290294da9a507344b68ff900f`.
2. Record current Workbench `Update project folder` Application Form timing.
3. Run a no-change repeat update/rebuild with the same Basic Information and selected Application Form.
4. Record whether reuse path or Word COM fallback was used.
5. Reopen the final Application Form with Word `OpenAndRepair=False`.
6. Check no new ConnLab-created `WINWORD.EXE` process remains.

## Plan

Detailed plan:

`docs/task_334g_application_form_word_write_back_reuse_and_hotpath_optimization_plan.md`

## Stop Point

Stop after TASK_334G completion. Do not start Report generation, Application Form field-scope expansion, Project Folder UI changes, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, or any next task without separate explicit approval.
