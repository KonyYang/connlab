# TASK_317E_TEMPORARY_PROJECT_STOP_AND_SAFE_DELETE

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317E_TEMPORARY_PROJECT_STOP_AND_SAFE_DELETE` completed. Do not enter TASK_319 without separate approval.

Allowed reason: The user identified a lifecycle hygiene gap after TASK_317D and approved implementation. ConnLab does not have a product-level archive concept; it has project lifecycle states. `Show cancelled` is a historical cleanup visibility control and is no longer the right primary UI for active project work, stopped project lookup, or mistaken temporary project deletion.

Executable plan:

- `docs/task_317e_temporary_project_stop_and_safe_delete_plan.md`

---

## 1. Background

ConnLab's current project status model includes lifecycle states such as `draft`, `ltr_registered`, `folder_created`, `closed`, and `cancelled`. There is no current product concept called `archived`.

The existing `Show cancelled` Projects Registry checkbox came from historical cleanup tasks:

- historical no-LTR residue rows were marked `cancelled`,
- the registry then hid `cancelled` rows by default,
- `Show cancelled` was added so operators could inspect those hidden rows.

TASK_317D changed the temporary project direction: active no-LTR projects are valid `Temporary Planning` records and should appear in `Planning` without using `Show cancelled`.

The remaining gap is now clearer:

- a real project may be stopped and should keep traceable lifecycle history,
- a mistaken or duplicate temporary project may need safe deletion,
- the Projects Registry primary view should not be centered on stopped/cancelled records.

---

## 2. Product Decision

Do not introduce `archive` / `archived` as a new project concept in this task.

Use user-facing terminology:

```text
Stopped
```

Internal compatibility may continue to use:

```text
ProjectStatus.CANCELLED = "cancelled"
```

Meaning:

- `Stopped` is the operator-facing lifecycle label for projects that intentionally no longer continue.
- `cancelled` remains an internal storage/API compatibility value until a future schema migration explicitly renames it.
- `Deleted temporary project` is different from `Stopped`: deletion is only for mistaken or duplicate temporary records that should not remain as business project history.

---

## 3. Registry UI Direction

The Projects overview should focus on what lab users actually need daily:

1. Active in-progress registered projects.
2. Temporary planning projects that may still start.
3. Registered projects needing Matrix or folder readiness.

Completed and stopped projects are lookup/history cases, not the default daily view.

The Projects overview should use one compact Project view selector instead of combining a top queue bar with a separate lifecycle scope:

```text
Ongoing
Planning
Matrix Needed
Ready to Test
Folder Blocked
Completed
Stopped
All
```

TASK_317E should remove the primary toolbar checkbox:

```text
Show cancelled
```

and remove the always-visible note:

```text
N cancelled projects hidden
```

V1 should not keep `Stopped` as a seventh top queue beside another lifecycle filter. The final UI should collapse queue and lifecycle lookup into the single Project view selector.

Recommended V1 behavior:

- Default view: `Ongoing`, meaning all non-completed, non-stopped work.
- `Planning`, `Matrix Needed`, `Ready to Test`, and `Folder Blocked` remain business-specific work views.
- `Completed` and `Stopped` remain lookup/history views.
- `All` means all registry records.
- Stopped projects are hidden by default.
- Selector options should show view names only.
- `Project ID` column header may expose a compact two-state sort control. Registered DL/LTR IDs sort by year, month, and sequence; temporary IDs sort by the `TMP-` suffix.
- The table footer should show the current view count, e.g. `Showing 1-20 of 20 Ongoing projects`.
- Search composes with the selected Project view.

V1 should use this lightweight Project view selector rather than implementing the disabled advanced `Filter` button. The existing broad `Filter` affordance may remain disabled or be handled by a future task, but TASK_317E must not keep the old `Show cancelled` checkbox wording or show a separate `Lifecycle` label.

---

## 4. Stopped Lifecycle Semantics

A stopped project:

- is a real business record,
- remains traceable,
- is hidden from the default `Ongoing` view,
- can be opened in a read-only or review-only Workbench state,
- does not appear as `Planning`, `Matrix Needed`, `Ready to Test`, or `Folder Blocked`,
- must not show temporary planning promotion actions.

Examples:

- customer decides not to continue,
- temporary feasibility evaluation will not start,
- project stopped after request review,
- project is intentionally terminated but still has useful history.

User-facing copy should use `Stopped`, not `Cancelled`.

---

## 5. Safe Temporary Delete Semantics

Deletion is for mistaken or duplicate temporary project records only.

TASK_317E should introduce a backend guard and Workbench-only delete entry for safe temporary deletion.

Delete is allowed only when all conditions are true:

- project has no registered LTR/DL,
- project is temporary planning,
- project is not already stopped,
- no active Confirmed Matrix exists,
- no official project folder or formal local workspace exists,
- no ConnLab-owned temporary workspace or temporary project folder exists in V1,
- no formal project folder record exists,
- no project-scoped file assets or source material records exist,
- no ProjectOutputRecord exists,
- no confirmed Fee authority or generated output exists,
- no public-drive operation record exists,
- no formal package or submitted material record exists.

Deletion blockers are divided into two categories:

- Formal or controlled project artifacts always block deletion and the user should stop the project instead. This includes registered LTR/DL, active Confirmed Matrix, official project folder, ProjectOutputRecord, confirmed fee/generated output, public-drive operation records, formal package records, or submitted material records.
- Temporary-only planning material also blocks deletion in V1 if it has already created a ConnLab-owned temporary workspace/folder or file-backed temporary drafts. This is conservative by design: the user should either manually clean the temporary material first through a future approved cleanup path, or use `Stop project` to preserve the record.

Delete must remove only ConnLab-owned temporary records required for the temporary project:

- project row,
- temporary project context,
- temporary-only planning drafts when explicitly safe,
- no public-drive files,
- no LTR workbook data,
- no official folder content.

Deletion must be guarded server-side. The frontend cannot be the authority.

---

## 6. Stop Project Semantics

If deletion is blocked, the recommended action is to stop the project instead.

Stop is allowed for temporary projects and formal projects when business work should not continue. For V1, it may reuse the existing internal `cancelled` status and expose `Stopped` in the UI.

Stopping a project:

- preserves the project record,
- preserves context/material references,
- removes the project from active work views,
- keeps it available through the `Stopped` or `All` Project view,
- prevents formal temporary promotion from stopped no-LTR records.

Stop requests should accept at least an optional operator-facing reason. If the current data model cannot persist a full lifecycle audit event, TASK_317E must keep the implementation honest: store the reason only where an existing safe field supports it, or return/display the stop result without claiming full audit coverage. A complete lifecycle event/audit trail can be deferred to a later task.

---

## 7. API Direction

Recommended backend API:

```http
GET /api/projects/{project_id}/delete-preview
```

Response:

```ts
{
  project_id: string;
  can_delete: boolean;
  blockers: string[];
  warnings: string[];
  recommended_action: "delete" | "stop";
}
```

Recommended delete endpoint:

```http
DELETE /api/projects/{project_id}/temporary
```

Rules:

- re-run server-side guards,
- only delete temporary planning projects,
- return blockers when deletion is not allowed,
- do not delete formal projects,
- do not touch public-drive files,
- do not recycle LTR/DL numbers.

Recommended stop endpoint:

```http
POST /api/projects/{project_id}/stop
```

Rules:

- updates lifecycle to internal `cancelled`,
- returns user-facing status label `Stopped`,
- accepts an optional stop reason from the UI/API,
- records reason/operator only when the current model supports it safely,
- otherwise documents reason/audit expansion as a follow-up and does not claim full audit coverage.

---

## 8. Workbench UI Direction

Projects overview remains lightweight. Do not add row-level Delete or Stop buttons there.

Temporary Planning Workbench should include a low-priority lifecycle management area:

```text
Project lifecycle
[Stop project] [Delete temporary project]
```

Behavior:

- `Delete temporary project` appears only for temporary no-LTR projects.
- If delete is blocked, show disabled state and blocker reasons.
- `Stop project` should remain available for valid projects that should not continue.
- Both actions require confirmation.
- Confirmation copy must distinguish:
  - stop: preserves project history,
  - delete: removes mistaken/duplicate temporary record from ConnLab.

Stopped Workbench state:

- show `Stopped project`,
- show review-only summary,
- no temporary planning actions,
- no promotion actions,
- no Matrix/Fee/Test Record/Execution active workflow actions.

Registered or artifact-bearing Workbench states:

- must not expose `Delete temporary project`,
- should expose a low-priority `Stop project` lifecycle entry for active projects that should not continue,
- must preserve formal LTR/DL, Matrix, folder, file asset, output, and request-material records.

---

## 9. Non-Goals

Do not implement in TASK_317E:

- no public-drive upload/update,
- no LTR/DL registration bridge,
- no Matrix execution expansion,
- no StepInstance/TestResult/evidence/report/AI/permissions/LAN/multi-user work,
- no delete of formal projects,
- no public-drive file deletion,
- no LTR workbook mutation or LTR number recycling,
- no broad advanced filter system; only the compact Project view selector is allowed,
- no new `archived` project status.

---

## 10. Acceptance Criteria

1. `/projects` no longer shows the primary `Show cancelled` checkbox.
2. `/projects` no longer shows the persistent `N cancelled projects hidden` note.
3. User-facing lifecycle copy uses `Stopped`, not `Cancelled`, for stopped/cancelled projects.
4. Default Projects view is `Ongoing`, focusing on unfinished non-stopped work; stopped projects are hidden by default.
5. Stopped projects are reachable through the compact Project view selector, not a separate lifecycle filter.
6. The table footer shows the current selected Project view count.
7. Project ID sort toggles ascending/descending order for registered DL/LTR IDs and temporary TMP IDs.
8. Search composes with the selected Project view.
9. Temporary Planning Workbench exposes lifecycle management, not Projects overview row actions.
10. Safe temporary delete preview returns `can_delete`, blockers, warnings, and recommended action.
11. Safe delete succeeds only for temporary no-LTR projects with no formal LTR/DL, Confirmed Matrix, official folder/workspace, file assets, output records, package/submitted-material/public-drive records, formal generated outputs, or V1 temporary workspace/folder/file-backed temporary draft blockers.
12. Formal projects and temporary projects with formal artifacts or project-scoped file assets cannot be deleted; they can only be stopped.
13. Stopped no-LTR projects do not show Temporary Planning or `Convert to Formal Project`.
14. Stop accepts an optional reason and does not claim full audit coverage unless the current model safely persists it.
15. Backend, frontend, and static tests cover Project view filtering, stopped copy, delete guards, stop reason handling, and Workbench gating.

---

## 11. Manual Smoke Checklist

1. Open `/projects`.
2. Confirm `Show cancelled` is gone.
3. Confirm the hidden cancelled note is gone.
4. Confirm active temporary projects remain in `Planning`.
5. Confirm stopped projects are not visible in the default view.
6. Use the Project view selector to view stopped projects.
7. Toggle Project ID sort and confirm DL/LTR rows sort by year, month, and sequence while TMP rows sort by suffix.
8. Search while a Project view is active and confirm both filters compose.
9. Open an active temporary project.
10. Confirm Workbench shows `Stop project` and, if guards allow, `Delete temporary project`.
10. Attempt delete for a safe temporary project and confirm it is removed.
11. Attempt delete for a temporary project with temporary workspace/folder material and confirm V1 blocks deletion with a clear reason.
12. Attempt delete for a project with LTR/DL, Confirmed Matrix, official folder/workspace, or output records and confirm it is blocked with reasons.
13. Stop a temporary project with a reason and confirm it leaves `Planning`.
14. Reopen the stopped project and confirm review-only Workbench state.

---

## 12. Stop Point

Stop after TASK_317E plan review. Do not implement until the user explicitly approves.

Do not enter TASK_319 or public-drive upload/update work.
