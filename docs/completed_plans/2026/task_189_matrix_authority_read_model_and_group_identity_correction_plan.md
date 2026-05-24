# TASK_189 Correction Plan: Authority Read Model + Group Identity

> Task: `TASK_189_MATRIX_AUTHORITY_READ_MODEL_AND_GROUP_IDENTITY_CORRECTION`  
> Status: plan proposed (implementation not started)  
> Date: 2026-05-14

---

## 1) Execution Context

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`
- Current board state: TASK_189 correction partially accepted; further semantic correction required.
- Why this task is allowed now: acceptance review found a high-severity authority read-model mismatch and a medium-severity group-identity validation gap.

---

## 2) Problem Statement

Remaining semantic mismatches:

1. Active authority read model still selects latest non-superseded draft, so unconfirmed candidate can be treated as active.
2. Missing group identity is currently auto-filled and not blocked on confirm.

Impact:

- Output ledger stale timing can trigger before confirm.
- Workbench can display authority context from candidate instead of reviewed.
- Downstream traceability by stable group identity is weakened.

---

## 3) Scope

### In Scope

- Backend active-draft read model correction.
- Frontend Workbench authority/candidate distinction in draft selection usage.
- Matrix confirm validation correction for group identity blocker.
- Unit/integration/static tests for corrected semantics.

### Out Of Scope

- No new feature routes.
- No data model migration.
- No UI redesign.
- No TASK_190+ work.

---

## 4) Design Decisions

### A. Authority read model

- Authoritative active draft = latest `reviewed` draft in the project.
- `draft` candidate is editable but non-authoritative.
- Stale evaluation in persisted output summary must compare output linkage against authoritative reviewed draft only.

Deterministic selector rule (must be implemented explicitly, not by incidental repository ordering):

1. Filter to `status == reviewed`.
2. Sort by `reviewed_at desc`, then `version desc`, then `updated_at desc`.
3. Pick first as `active_draft`.
4. If no reviewed draft exists: `active_draft_id = null`, `active_draft_version = null`.
5. Candidate drafts (`status == draft`) never participate in output-ledger stale comparison.

### B. Workbench semantics

- Load/display candidate separately from authority signal where both exist.
- Avoid deriving stale from candidate unless confirm changes authority.

Required model contract:

- `matrixAuthorityDraft`: latest reviewed draft (authority/status/stale context).
- `matrixCandidateDraft`: latest draft candidate (continue editing context).
- Current editable object (`matrixDraft` or equivalent):
  - prefer `matrixCandidateDraft` when present
  - fallback to `matrixAuthorityDraft` when no candidate exists
- Output status binding:
  - authority-only (`matrixAuthorityDraft`)
  - never candidate-linked
- UI copy requirement:
  - must distinguish authority vs candidate (for example: "Confirmed authority v1" and "Editing candidate v2").

### C. Group identity validation

- Confirm must block when explicit stable group identity is missing.
- Accepted explicit stable identity inputs:
  - `group_key`, or
  - `group_number`, or
  - explicit source `group_label`
- Not accepted:
  - identity inferred only from array index/default generated label (for example implicit `Group {index}`).
- If explicit `group_label` exists, `group_key` may be derived, but source label must be preserved.
- Do not silently auto-generate identity from index during confirm validation.

---

## 5) File-Level Change Plan

Backend:

- `backend/application/project_output_record_service.py`
  - Replace active-draft selector from “first non-superseded” to “latest reviewed”.

- `backend/application/project_test_plan_matrix_edit_service.py`
  - Enforce missing group identity as blocker.
  - Keep existing corrected reviewed/candidate supersede timing.

Frontend:

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Draft loading logic: do not treat arbitrary non-superseded candidate as authority context.
  - If needed, maintain both `matrixAuthorityDraft` and `matrixCandidateDraft` in model while preserving existing panel contract (minimal change).

Tests:

- `tests/unit/test_project_output_record_service.py`
  - Add scenario: v1 reviewed + v2 candidate, active summary remains v1 until v2 confirm.

- `tests/unit/test_project_test_plan_matrix_edit_service.py`
  - Add/adjust missing group identity blocker test.

- `tests/integration/test_project_test_plan_matrix_edit_api.py`
  - Add API scenario for group identity blocker.
  - Add end-to-end reviewed/candidate authority transition verification.

- `tests/unit/test_frontend_shell_files.py`
  - Add static assertions for model-level authority/candidate distinction only if naming/contracts changed.

---

## 6) Risks and Mitigations

1. **Risk:** read-model correction breaks existing expectations for candidate visibility.  
   **Mitigation:** keep candidate loading for editing path; only authority comparator changes.

2. **Risk:** strict identity blocker may break legacy payloads missing `group_key`.  
   **Mitigation:** block on confirm only; update warning/blocker messages to business-readable remediation.

3. **Risk:** stale-status UX appears changed after reload.  
   **Mitigation:** expected behavior; verify with dedicated tests and explicit board note.

---

## 7) Validation Plan

```powershell
python -m pytest tests\unit\test_project_output_record_service.py tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

```powershell
python -m pytest tests\integration\test_project_output_records_api.py -q
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task188"
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 8) Completion Criteria

- Active authority in output status summary remains reviewed v1 when v2 candidate exists.
- After candidate confirm, authority switches to reviewed v2 and old reviewed supersedes.
- Missing explicit stable group identity is blocker and prevents confirm.
- Relevant tests pass and board wording is synchronized.
