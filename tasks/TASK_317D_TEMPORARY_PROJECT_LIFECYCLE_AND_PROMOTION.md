# TASK_317D_TEMPORARY_PROJECT_LIFECYCLE_AND_PROMOTION

Status: Complete. Implemented and validated on 2026-06-13.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317D_TEMPORARY_PROJECT_LIFECYCLE_AND_PROMOTION` completed after explicit user approval.

Allowed reason: The user identified a product gap after TASK_317C: no-DL/LTR temporary planning projects need a first-class New Project entry and Workbench planning path, while prior Workbench planning already defines `temporary_planning` as a distinct lifecycle mode.

Executable plan:

- `docs/task_317d_temporary_project_lifecycle_and_promotion_plan.md`

Implementation summary:

- Added `POST /api/projects/temporary` for active no-LTR temporary planning project creation.
- Added typed frontend API support and a New Project page secondary `Create Temporary Project` entry.
- Temporary creation navigates directly to the created project's Workbench and uses existing `TMP-XXXXXXXX` registry identity.
- Workbench temporary planning mode now includes Matrix planning, Fee expectation, and a Workbench-only `Convert to Formal Project` entry.
- V1 promotion stops at a clear same-project LTR registration routing gap message and does not create a duplicate project.
- Historical cancelled no-LTR rows are not auto-restored or mutated.

Review correction summary:

- Temporary creation now persists planning context separately from the formal Project record: request summary, sample description, test item, notes, and source intake asset IDs.
- Registry and project detail API responses expose the persisted temporary context so Workbench and future promotion can reuse or review it.
- Cancelled no-LTR projects are treated as review-only cancelled projects in Workbench and do not show Temporary Planning or `Convert to Formal Project`.
- Temporary Fee Evaluation is gated until a Matrix draft is available.

Validation:

- `py -m pytest tests\unit\test_project_service.py tests\integration\test_project_registry_summary_api.py tests\unit\test_frontend_shell_files.py`
- `py -m pytest tests\unit\test_project_registry_summary_service.py`
- `cd frontend; npm test -- --run ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false`
- `cd frontend; npm run build`

---

## 1. Background

Existing planning already establishes two important facts:

1. `TASK_313A_PROJECT_WORKBENCH_LIFECYCLE_MODE_REDESIGN` defines a Workbench lifecycle-mode model:

```text
temporary_planning
registered_setup
package_preparation
execution_console
```

2. `TASK_317C_TEMPORARY_PROJECT_PLANNING_IDENTITY` defines no-DL/LTR projects as valid `Temporary Planning` projects with a stable `TMP-XXXXXXXX` display identity.

The remaining gap is lifecycle management. A temporary planning project should not be treated as a cancelled or broken project. It should be an active planning container that can start from an email discussion, optional attachments, customer product/specification information, and early Matrix/Fee planning before formal LTR/DL registration.

---

## 2. Current Problem

The Projects overview currently has both:

- a `Planning` queue for no-DL/LTR temporary planning projects,
- a `Show cancelled` toggle for hidden cancelled rows.

These are different concepts. However, some existing no-LTR rows may only appear when `Show cancelled` is enabled because they are stored or classified as `cancelled`.

This creates user confusion:

- a valid temporary planning project looks abandoned or hidden,
- the `Planning` queue appears empty even when planning work exists,
- users may think `Show cancelled` is the way to access temporary projects,
- Workbench temporary planning behavior is not fully connected to temporary project creation, source material storage, or later LTR promotion.

---

## 3. Business Intent

A temporary project is a first-class planning container before formal LTR/DL registration.

It should support the real lab workflow:

1. A customer discussion starts from an email or conversation.
2. The email may include an application form, product specification, images, historical report, or other attachments.
3. The email may also have no formal application form yet.
4. The operator may skip LTR/DL registration temporarily.
5. The operator may still evaluate feasibility, create or import Matrix planning content, estimate test groups, estimate duration, prepare fee planning, and store planning material.
6. The operator can start this path from the existing New Project page through a clear `Create Temporary Project` entry.
7. The backend creates and manages the temporary project record, then the frontend opens the new project's Workbench.
8. The same temporary project appears in the Projects overview as a `Planning` row.
9. When the project should become formal, the operator promotes the same temporary project into the existing LTR/DL registration flow.
10. Existing temporary material and planning outputs should be reused instead of creating a duplicate project.

---

## 4. Scope

TASK_317D defines and implements the controlled lifecycle bridge for temporary planning projects.

In scope:

- Correct the distinction between active temporary planning projects and cancelled/archived projects.
- Add a `Create Temporary Project` entry on the existing New Project page.
- Create a backend-managed active temporary planning project without registering LTR/DL.
- Navigate to the newly created temporary project's Workbench after successful creation.
- Ensure active no-DL/LTR temporary planning projects appear in the `Planning` queue without requiring `Show cancelled`.
- Preserve `Show cancelled` for genuinely cancelled/archived rows.
- Introduce or normalize the minimum project status/read-model fields needed to distinguish active temporary planning from cancelled state.
- Align Workbench `temporary_planning` layout with the prior TASK_313A lifecycle-mode direction.
- Ensure temporary Workbench mode shows planning surfaces and hides or gates formal LTR-dependent surfaces.
- Define a Workbench-only promotion entry for starting conversion from a temporary project to a formal registered project.
- Route promotion into the existing LTR readiness/registration context with the same `project_id` where the current codebase supports it; do not create a duplicate Project.
- Document how temporary project source materials, Matrix/Fee drafts, and notes are carried forward.
- Add tests for classification, visibility, Workbench mode, and promotion entry gating.
- Add tests for New Project temporary creation entry, backend creation behavior, Workbench navigation, and Projects registry visibility.

---

## 5. Non-Goals

Do not implement these in TASK_317D:

- Do not add Matrix, Fee, Test Record, Execution, Project Folder repair, or promotion buttons to the Projects overview table.
- Do not replace the existing New Project / LTR registration workflow with a new unrelated registration engine.
- Do not write to the public-drive LTR workbook unless the existing approved registration path already does so under its own settings and guards.
- Do not implement public-drive upload/update.
- Do not generate final Test Record, Fee Form, Customer Feedback, Application Form Section 2, or approval package outputs for temporary projects.
- Do not implement StepInstance, TestResult, execution evidence/photos, report generation, AI review, permissions, LAN, or multi-user behavior.
- Do not change ConfirmedMatrix authority semantics.
- Do not remove the `Show cancelled` concept unless a reviewed design explicitly replaces it with an archive/cancelled filter.
- Do not treat missing LTR/DL as a folder blocker, matrix blocker, or cancellation reason by itself.

---

## 6. New Project Temporary Entry

The existing New Project page should provide a secondary entry:

```text
Create Temporary Project
```

This entry is for customer discussions or feasibility requests that are not ready for LTR/DL registration.

Expected V1 behavior:

1. The operator enters or imports the available discussion/source information supported by the current New Project page.
2. Application form and attachments are optional.
3. Clicking `Create Temporary Project` calls a backend temporary-project creation path.
4. The backend creates an active temporary planning project without LTR/DL registration.
5. The backend persists the minimum project/source context required for Workbench and Projects registry display.
6. The frontend navigates directly to the new project's Workbench.
7. The Projects overview shows the project as a `Planning` row with `TMP-XXXXXXXX`.

The entry should not perform LTR preview, LTR commit, official project folder creation, package generation, or public-drive upload.

Minimum backend contract:

```text
POST /api/projects/temporary
```

Minimum request fields:

- `request_summary: string | null`
- `sample_description: string | null`
- `test_item: string | null`
- `requestor: string | null`
- `source_asset_ids: string[]`
- `notes: string | null`

Minimum response fields:

- `project_id: string`
- `display_project_id: string`
- `display_project_id_kind: "temporary"`
- `has_registered_ltr: false`
- `status: "temporary_planning"` or current storage-compatible active planning status
- `next_route: string`

If the existing routing/API pattern strongly favors another endpoint shape, the implementation plan may adapt the path, but it must preserve this request/response meaning.

---

## 7. Required Semantics

### Active Temporary Planning

An active temporary planning project:

- has no registered LTR/DL number,
- is not cancelled or archived,
- has a stable temporary display ID,
- appears in the Projects overview `Planning` queue,
- can be opened in Workbench,
- may use safe Matrix/Fee/planning surfaces,
- may have a local temporary project workspace or source material collection,
- must not expose formal package actions that require LTR/DL registration.

### Cancelled / Archived

A cancelled or archived project:

- is intentionally hidden by default,
- appears only when the cancelled/archive visibility toggle is enabled,
- should not be counted in normal business queues,
- should not be used as the default storage state for valid temporary planning projects.

### Planning Queue

`Planning` means active temporary planning work, not hidden cancelled work.

If a no-DL/LTR project is active, it belongs in `Planning` without requiring `Show cancelled`.

If a no-DL/LTR project is actually cancelled, it remains hidden until `Show cancelled` is enabled and should not be counted as active planning.

---

## 8. Workbench Temporary Planning Layout

TASK_317D should reuse the lifecycle mode direction from TASK_313A.

When Workbench derives `temporary_planning`, show:

- project identity with `TMP-XXXXXXXX` and `Temporary Planning`,
- source/request material summary if available,
- Matrix planning entry,
- existing safe Fee planning or fee draft entry if available; otherwise show disabled/gated copy,
- feasibility / duration / planning notes surface if already supported or can be introduced narrowly,
- clear copy that formal folder/package outputs require LTR/DL registration.

Hide or gate:

- official project folder creation,
- Submitted Material formal readiness,
- Application Form Section 2 write-back,
- package preview/execution,
- public-drive upload,
- Step Workspace as primary execution content,
- any final output generation that assumes registered LTR/DL identity.

---

## 9. Promotion Boundary

The Workbench may show a controlled promotion entry for active temporary planning projects:

```text
Register LTR / Convert to Formal Project
```

This entry belongs inside the temporary project's Workbench, not in the Projects overview row actions.

TASK_317D V1 promotion should:

- preserve the same internal `project_id`,
- route into the existing LTR readiness/registration context with project context if current routing supports it,
- prefill from temporary project source materials where reliable,
- allow missing application form or missing fields to remain review blockers,
- carry forward temporary Matrix/Fee planning artifacts where compatible,
- rely on the existing LTR commit path to replace the user-facing identity with the registered LTR/DL number after successful registration,
- keep `TMP-XXXXXXXX` as historical alias/reference if a future model supports aliases.

If the current New Project/LTR flow cannot safely register an existing `project_id` without creating a duplicate Project, TASK_317D must stop at the promotion entry plus a documented routing/contract gap. The actual same-project LTR commit bridge must then be split into a follow-up task.

Promotion must not:

- create a duplicate formal project unless the user explicitly chooses a conflict-resolution path,
- silently register LTR/DL without readiness review,
- silently discard temporary materials,
- enable formal folder/package/public-drive operations before registration succeeds.

---

## 10. Data And Read-Model Guidance

Use existing data structures conservatively first.

If current DTOs cannot safely distinguish active temporary planning from cancelled/archive state, TASK_317D should add explicit read-model fields rather than infer lifecycle truth from labels.

Candidate future fields:

- `project_lifecycle_state`
- `is_temporary_planning`
- `is_archived`
- `archive_reason`
- `primary_queue`
- `next_step_label`
- `has_registered_ltr`
- `has_active_matrix`
- `has_temporary_workspace`
- `temporary_material_summary`
- `promotion_eligible`
- `promotion_blockers`

Do not leak a broad Workbench lifecycle model into the registry DTO unless it is explicitly scoped as a read model. Registry should expose only the facts needed for queue/visibility and entry-point decisions.

---

## 11. Acceptance Criteria

1. New Project page exposes a `Create Temporary Project` entry.
2. Clicking `Create Temporary Project` creates an active backend-managed temporary planning project without LTR/DL registration.
3. After creation, the frontend navigates to the temporary project's Workbench.
4. The new temporary project appears in Projects overview as a `Planning` row with `TMP-XXXXXXXX`.
5. Active no-DL/LTR temporary projects appear in the `Planning` queue without enabling `Show cancelled`.
6. `Show cancelled` remains for genuinely cancelled/archived records, not for active temporary planning work.
7. No-DL/LTR alone does not classify a project as cancelled, Folder Blocked, Matrix Needed, or invalid.
8. Workbench `temporary_planning` mode uses a different layout from registered/formal modes.
9. Temporary Workbench mode shows planning-safe surfaces and hides/gates formal LTR-dependent surfaces.
10. A Workbench-only promotion entry is defined for converting a temporary project to formal LTR/DL registration.
11. Promotion reuses the existing LTR registration workflow or stops at a documented routing/contract gap if same-project registration is not yet supported.
12. Temporary materials and planning artifacts are preserved or explicitly marked for review during promotion setup.
13. Projects overview still keeps `Open` as the only row action.
14. No Matrix/Fee/Test Record/Execution/Project Folder repair detailed actions are added to Projects overview.
15. Historical cancelled no-LTR rows are not automatically restored; TASK_317D may only produce a dry-run/manual review list for them.
16. Tests cover New Project temporary creation, registry visibility/classification, temporary Workbench mode, and promotion gating.
17. Documentation records the boundary between temporary planning, cancelled/archive, and formal registered projects.

---

## 12. Manual Smoke Checklist

1. Open `/intake`.
2. Confirm `Create Temporary Project` is available as a secondary New Project entry.
3. Create a temporary project with minimal discussion/source information and no LTR/DL registration.
4. Confirm the app navigates to the new temporary project's Workbench.
5. Open `/projects`.
6. Confirm the active temporary no-DL/LTR project appears under `Planning` without `Show cancelled`.
7. Confirm cancelled rows remain hidden by default.
8. Enable `Show cancelled` and confirm only cancelled/archived rows are added.
9. Open an active temporary planning project.
10. Confirm Workbench shows `Temporary Planning` identity and temporary planning layout.
11. Confirm Matrix/Fee planning entry points are available where safe.
12. Confirm official folder/package/Section 2/public-drive actions are hidden or gated.
13. Confirm a Workbench promotion entry is visible only for active temporary projects.
14. Start promotion and confirm it enters the existing LTR readiness/registration path with temporary material available for reuse/review.
15. Cancel promotion and confirm the temporary project remains intact.
16. If same-project LTR registration is supported by the current flow, complete promotion in a test path and confirm the project now displays its formal LTR/DL identity. Otherwise confirm the promotion entry reports the documented routing/contract gap without creating a duplicate project.

---

## 13. Stop Point

Stop after TASK_317D plan review or implementation validation, depending on the approved step.

Do not proceed to TASK_319, public-drive upload/update, package execution, StepInstance, execution evidence, report generation, permissions, LAN, or multi-user work without a separate approved task.
