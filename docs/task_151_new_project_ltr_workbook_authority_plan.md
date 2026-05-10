# TASK_151 New Project LTR Workbook Authority Plan

> Current phase: Phase 10E - External resource settings and LTR workbook authority
> Active task for planning: TASK_151_NEW_PROJECT_LTR_WORKBOOK_AUTHORITY
> Status: awaiting user review before implementation
> Date: 2026-05-10

## 1. Task Goal

Make New Project `Apply LTR Number` use the configured LTR workbook as the current number authority and write target.  
New Project must stop assigning official LTR numbers from local SQLite alone.

This task is allowed now because the board marks TASK_150 complete and explicitly sets TASK_151 as the next task pending approval.

## 2. Inputs

- New Project completion request:
  - `ltr_mode` (`auto` or `specified`)
  - `specified_ltr_number` when mode is `specified`
  - setup fields (`test_item`, `sample_description`, `location`, `test_type_in_sheet`, `project_leader`)
- Configured LTR workbook runtime settings:
  - path
  - write_enabled
  - modify_password
  - lock_dir
  - backup_dir
- Existing external workbook write stack:
  - `LtrWorkbookWritePreviewService`
  - `LtrWorkbookWriteCommitService`
  - transaction gateway (lock + backup + short transaction)

## 3. Outputs

- `complete-new-project` uses workbook-backed number authority and write commit.
- Workbook write happens before local LTR record persistence.
- If workbook write fails, New Project does not leave a local registered LTR as if successful.
- API still returns New Project completion result with project id/status/ltr number.
- Errors are actionable for missing settings, invalid workbook, lock timeout, write-disabled, or conflict.

## 4. Scope Boundaries

In scope:

- Switch New Project completion from `LtrLocalCommitService` path to workbook commit path.
- Use workbook-visible numbers for auto mode.
- Preserve specified-number validation semantics already established in TASK_137/138/147.
- Keep future authority seam explicit in application design.

Out of scope:

- No server authority implementation.
- No Settings native picker.
- No workbook migration/import project.
- No Matrix/Report/AI/email/permissions/LAN.

## 5. Current Code Reality

- `NewProjectCompletionService` currently resolves auto numbers from local `ltr_records`:
  - `_resolve_ltr_number()` reads `self._ltrs.search("DL-")`
  - commit path uses `LtrLocalCommitService`
- Dependency wiring (`get_new_project_completion_service`) injects `LtrLocalCommitService`.
- Workbook write service already exists and already persists local LTR only after successful workbook write in one flow:
  - `LtrWorkbookWriteCommitService.commit_project()`
  - lock + backup + write + then `register_ltr()`

This means TASK_151 should reuse existing workbook write commit service rather than rebuild write logic.

## 6. Design Direction

Application seam:

```text
NewProjectCompletionService
  -> LtrNumberAuthorityPort (new abstraction)
     -> WorkbookLtrNumberAuthority (current adapter)
```

Pragmatic first step:

- Keep seam minimal and local to New Project completion.
- Reuse `LtrWorkbookWriteCommitService` directly in adapter implementation.
- Avoid broad refactor across unrelated modules.

## 7. Data Structure / API Design

New command/result (application layer):

```python
@dataclass(frozen=True, slots=True)
class CommitAuthoritativeLtrCommand:
    ltr_mode: NewProjectLtrMode
    specified_ltr_number: str | None
    plan_date: date
    operator_confirmed: bool
    test_item: str
    sample_description: str
    location: str
    test_type_in_sheet: str
    project_leader: str
    requested_by: str | None
```

Authority port:

```python
class LtrNumberAuthorityPort(Protocol):
    def apply_for_project(self, project_id: str, command: CommitAuthoritativeLtrCommand) -> LtrRecord: ...
```

Workbook adapter behavior:

- Auto mode:
  - pass `number_input=None` to workbook commit service (service computes next from workbook-visible numbers)
- Specified mode:
  - pass `number_input=specified_ltr_number`
- Always pass `preview_acknowledged=True` and `operator_confirmed` from request.

No New API route is required; keep:

- `POST /api/intake-cases/{case_id}/complete-new-project`

Response DTO remains unchanged for TASK_151:

- `project_id`
- `project_status`
- `ltr_number`

## 8. File-Level Change Plan

Backend application:

- `backend/application/new_project_completion_service.py`
  - Replace local-only numbering/commit path with authority adapter call.
  - Remove dependence on `LtrLocalCommitService` and local `next_monthly_dl_number` for official assignment.
  - Keep existing setup-field validation and project confirmation flow.

- `backend/application/new_project_ltr_authority.py` (new)
  - Define authority port + workbook adapter implementation.
  - Map New Project mode/fields to `CommitLtrWorkbookWriteCommand`.

Backend dependency wiring:

- `backend/api/dependencies.py`
  - Build workbook-backed authority adapter and inject it into `NewProjectCompletionService`.
  - Reuse existing `LtrWorkbookWritePreviewService` + transaction gateway + commit service construction.

Potential API error handling updates:

- `backend/api/routes_new_project_completion.py`
  - Ensure workbook commit exceptions surface as `400` with clear message (most already covered via `ValueError`/`LtrError` buckets).

Tests:

- `tests/integration/test_new_project_completion_api.py`
  - Add/adjust cases proving workbook authority path is used and failure does not produce local registered LTR.
- `tests/unit/test_ltr_workbook_write_commit_service.py`
  - Reuse existing coverage; only extend if TASK_151 mapping needs new behaviors.
- `tests/unit/test_frontend_shell_files.py`
  - Only adjust static assertions if required by response/copy changes (expected minimal/no change).

## 9. Workflow Semantics

Auto number:

1. Confirm intake case / resolve project.
2. Validate setup confirmation fields.
3. Call workbook authority adapter in auto mode.
4. Adapter triggers workbook commit with `number_input=None`.
5. Workbook commit service:
   - calculates from workbook-visible numbers
   - lock + backup + short transaction write
   - registers local LTR after save
6. Return project + new LTR.

Specified number:

1. Same prechecks.
2. Adapter passes specified value as `number_input`.
3. Workbook commit service validates and writes with conflict checks.
4. Local record persists only after successful write.

## 10. Risks

- Existing local historical invalid LTR entries can differ from workbook state; authority switch may expose mismatches. This is expected and desired.
- If workbook settings are absent/invalid (`path`, `password`, `lock_dir`, `backup_dir`, write disabled), New Project completion will now fail earlier; copy must remain clear.
- `complete-new-project` currently expects quick local path behavior; workbook lock/write introduces more IO latency.

## 11. Validation Plan

Automated:

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
py -m pytest tests\integration\test_new_project_completion_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr"
cd frontend
npm run build
git diff --check
```

Manual smoke:

1. In Settings, set and validate local simulated `ltr_workbook`.
2. Prepare lock/backup/password config in local settings.
3. Run New Project `Apply LTR Number` with auto mode.
4. Confirm workbook row is created and local SQLite gets same LTR.
5. Force write failure (e.g., disable write or bad password) and confirm no local registered LTR is created for that attempt.

## 12. Acceptance Criteria Mapping

- No official numbering from local-only SQLite: achieved by removing local auto-number path in New Project completion.
- Configured workbook as authority: achieved via workbook adapter + commit service.
- Write failure blocks official registration: achieved by single workbook-first commit flow.
- Local SQLite remains structured copy: achieved by post-write register inside workbook commit service.
- Future server cutover seam remains possible: achieved with authority port/adapter boundary.

## 13. Self-Check Before Implementation

- Scope constrained to TASK_151 only.
- No frontend scope expansion required unless error copy adjustments become necessary.
- No Office direct calls from API/UI layers.
- No hard-coded public-drive paths.
- No migration of legacy/future features bundled into this task.
