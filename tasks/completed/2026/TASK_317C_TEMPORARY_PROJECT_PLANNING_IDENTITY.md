# TASK_317C_TEMPORARY_PROJECT_PLANNING_IDENTITY

Status: Implemented. TASK_317C scope is complete.

Post-completion amendment: the Projects overview table direction is clarified for first-version registered/temporary identity display. The preferred registry table structure is `Project ID | Sample Description | Test Item | Status | Next Step | Action`. `Next Step` is informational copy only and does not add row-level actions.

Implementation amendment: the Projects overview registry table now uses the first-version structure `Project ID | Sample Description | Test Item | Status | Next Step | Action`. `Status` and `Next Step` use conservative queue-derived copy until explicit registry read-model fields are available.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Interleaving note:

`TASK_317C` is a separate interleaved identity/UI task implemented after `TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR` completion. It does not consume, rename, or reopen `TASK_318`.

---

## 1. Background

ConnLab currently treats `Project` as the lifecycle container and `Matrix` as the execution authority map. The Workbench lifecycle model already recognizes a no-DL/LTR state as `temporary_planning`: a project without a registered DL/LTR number can still use Matrix and Fee planning surfaces for early feasibility, duration, and cost estimation.

In real laboratory work, customers often ask whether a test project is feasible before a formal LTR number is requested. Operators may need to:

- review the specification or customer request,
- import or inspect a Matrix,
- estimate test groups and steps,
- estimate execution time,
- estimate fee,
- record feasibility notes,
- later register an LTR number and continue the same project.

These are not throwaway drafts. They are temporary planning projects that may become formal registered LTR projects later.

---

## 2. Current Problem

The current UI and data language can confuse three different concepts:

1. a formal project with a registered LTR/DL number,
2. a temporary planning project without an LTR/DL number,
3. an incomplete or invalid project record.

If a no-LTR project is shown only as `Draft`, users may think it is disposable or not business-relevant.

If a no-LTR project is treated as `Folder Blocked`, users may think the project has an error, even though lacking an LTR number is expected during planning.

If a temporary planning project is assigned a random value in the LTR field, users may mistake the temporary ID for a formal registered LTR number.

The system needs a clear identity model for temporary planning projects before the Projects overview and Workbench UI are polished further.

---

## 3. Business Intent

A temporary project is a valid planning container before formal LTR registration.

It should support early customer-project analysis and should share selected formal-project capabilities that are safe before registration:

- Matrix planning,
- group/step analysis,
- Test Record preview or draft planning where safe,
- Fee planning or estimation,
- duration/workload estimation,
- feasibility notes,
- source/specification attachment references where already supported.

It must not be treated as an invalid project simply because it has no LTR number.

It must also not be allowed to perform formal package actions that require registered project identity.

---

## 4. Scope

This task defines and implements the minimum temporary planning project identity needed for Projects overview and Project Workbench consistency.

In scope:

- Define temporary planning project identity and copy rules.
- Ensure a project without registered LTR/DL number can be displayed as `Temporary Planning` rather than as a broken formal project.
- Introduce or normalize a temporary project display ID such as `TMP-YYYY-MM-NNNN`, if the existing data model does not already provide one.
- Preserve a strict distinction between temporary ID and formal LTR/DL number.
- Update Projects overview display rules so temporary planning projects are understandable.
- Update Workbench identity copy so no-LTR projects are presented as planning projects.
- Add or update conservative tests around classification and display copy.
- Document promotion boundary from temporary planning project to formal registered LTR project.

---

## 5. Non-goals

Do not implement these in `TASK_317C`:

- Do not implement full formal LTR registration workflow unless a minimal existing route already supports it and only copy/entry-point text needs correction.
- Do not implement a complete promote-to-registered backend workflow if it does not already exist.
- Do not generate official Project Folder, Submitted Material, Application Form Section 2, public-drive upload, or final package outputs for temporary projects.
- Do not change ConfirmedMatrix authority semantics.
- Do not introduce StepInstance, TestResult, execution evidence, report generation, AI review, permissions, LAN, or multi-user behavior.
- Do not fold Matrix Workspace, Fee Evaluation, or Test Record detailed actions into the Projects overview page.
- Do not rename `TASK_318` or change its Official Project Folder check/repair scope.

---

## 6. Terminology

### Temporary Planning Project

A valid ConnLab project record without a registered LTR/DL number, used for feasibility, Matrix, duration, and fee planning.

### Temporary ID

A system-derived identifier for a temporary planning project.

**V1 implementation**: `TMP-<project_id 前 8 字符大写>`

```text
TMP-2CD4B0E7
TMP-A1B2C3D4
```

Stable and deterministic — derived from the existing `project_id`, no migration or sequence counter needed.

**Future improvement** (not in TASK_317C): `TMP-YYYY-MM-NNNN` 月度序列号（需要序列计数器、迁移、并发控制）。

### LTR Number

The formal registered customer/lab tracking number. A temporary ID must not be stored or displayed as if it were an LTR number.

### Registered Project

A formal project with a registered LTR/DL number.

### Promotion

The future transition from temporary planning project to formal registered project after an LTR/DL number is assigned.

---

## 7. Identity Rules

1. A project may exist without a registered LTR/DL number.
2. A no-LTR project is not automatically invalid.
3. A no-LTR project should derive lifecycle mode `temporary_planning`.
4. A temporary project should have a stable temporary display ID.
5. The temporary ID must not be treated as an LTR number.
6. The UI must not show `Folder Blocked` only because the LTR number is missing.
7. Formal package and official folder actions remain unavailable or clearly gated for temporary projects.
8. Temporary project planning data should be preserved if the project is later promoted to a registered LTR/DL project.

---

## 8. Projects Overview Display Rules

The Projects overview page remains a high-level registry and entry point.

For temporary planning projects, display should make the identity clear.

First-column label: `Project ID`

The first column must be `Project ID`, not `LTR Number`. Registered projects show the formal registered LTR/DL number. Temporary planning projects show the temporary display ID, for example `TMP-2CD4B0E7`, and a small secondary label such as `Temporary Planning`.

Recommended first-version table structure:

```text
Project ID | Sample Description | Test Item | Status | Next Step | Action
```

Column guidance:

- `Project ID`: registered LTR/DL number or temporary display ID. Temporary ID must be visually and semantically distinct from formal LTR/DL.
- `Status`: aligns with business queue semantics: `Planning`, `Matrix Needed`, `Ready to Test`, `Folder Blocked`, `Completed`. Do not rely on `LTR Number Registered` as the only meaningful registry status when a better business state is available.
- `Next Step`: user-facing informational copy that helps operators decide what they will likely do after opening the Workbench.
- `Action`: keep the existing `Open` button only.

Row content for temporary project:

```text
TMP-2CD4B0E7
Temporary Planning
```

Row content for registered project:

```text
DL-2026-05-011
```

Recommended status badge: `Planning` or `Temporary Planning`, depending on the first-version status component vocabulary.

Recommended `Next Step` copy:

```text
Continue planning
```

Other `Next Step` examples:

```text
Open Matrix authority
Open Execution map
Confirm Fee
Review request material
Complete Section 2 dates
No action
```

`Next Step` replaces earlier `Readiness / Reason` or readiness/notes wording when referring to the Projects overview table column. It is informational text only. It must not be rendered as a row-level action button, and it must not add Matrix, Fee, Test Record, Execution, Project Folder repair, or Workbench-specific actions to the Projects overview page. Detailed actions remain inside the Project Workbench after clicking `Open`.

If current DTO fields cannot compute an exact `Next Step`, TASK_317C should document the limitation and use conservative display copy rather than parsing Workbench details in the frontend.

V1 implementation uses conservative queue-derived copy:

- `Planning` -> `Continue planning`
- `Matrix Needed` -> `Open Matrix authority`
- `Ready to Test` -> `Open Execution map`
- `Folder Blocked` -> `Review request material`
- `Completed` / `Cancelled` -> `No action`

Temporary projects should appear in:

- `All`,
- `Planning` in the TASK_317B Queue Filter Bar,
- optional advanced filter `Temporary` if advanced filtering exists.

Temporary projects should not appear in:

- `Folder Blocked` solely because no LTR number exists,
- `Matrix Needed` solely because no LTR number exists,
- `Completed` unless explicitly closed/completed.

If `TASK_317B_PROJECT_REGISTRY_QUEUE_FILTER_BAR` has already introduced queue filters, `TASK_317C` must preserve the final business queue set: `All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed`.

---

## 9. Workbench Display Rules

TASK_317C **只改身份展示和说明文案，不新增操作入口**。

For temporary planning projects, the Workbench should show a clear temporary planning identity banner:

```text
Temporary Planning
This project has no registered LTR Number yet. Matrix and Fee planning tools are available for feasibility, duration, and cost estimation. Official package actions require LTR registration.
```

**Active actions**: TASK_317C does not add new buttons or entries. Existing Matrix/Fee planning entries (if already rendered by the current Workbench for no-LTR projects) may remain. No "Register LTR Number" button is created.

Temporary planning mode must hide or gate:

- Official Project Folder creation,
- Submitted Material placement,
- Application Form Section 2 write-back,
- final package execution,
- public-drive upload/update.

---

## 10. Promotion Boundary

`TASK_317C` should document the intended future transition:

```text
Temporary Planning Project
→ Register LTR Number
→ Formal Registered Project
```

Promotion should preserve:

- internal project ID,
- temporary ID as historical alias if present,
- Matrix planning work,
- group selection/planning state where applicable,
- fee planning draft where applicable,
- feasibility notes,
- source/specification references where already supported.

Promotion should add:

- formal LTR/DL number,
- formal lifecycle eligibility,
- Project Folder / Official Workspace eligibility,
- package preparation eligibility.

Do not implement full promotion unless already supported. If not supported, this task should only clarify copy, identity, DTO/display fields, and future boundary.

---

## 11. Data and DTO Guidance

Use the best existing backend fields first.

If existing project records have a registered `ltr_number`, latest LTR lookup, or equivalent formal LTR/DL identity source, the temporary classification should only apply when no formal identity is present. `project_no` is not a registered LTR/DL fallback and must not be displayed as the registered project identity.

**V1 registry DTO fields** (confirmed, minimal):

```text
display_project_id: string          # "DL-2026-05-011" or "TMP-2CD4B0E7"
display_project_id_kind: string     # "temporary" or "registered"
has_registered_ltr: boolean
temporary_project_id: string | null
registered_ltr_number: string | null
```

**Explicitly excluded from registry DTO**: `lifecycle_mode`. It depends on Matrix, folder, package, and request-material context. The registry summary service should not assemble Workbench lifecycle truth. Workbench lifecycle stays in the existing Workbench selector/model.

Do not parse Matrix/Fee/Workbench detail payloads in the Projects frontend to invent lifecycle truth.

The registry and Workbench should consume explicit identity/readiness fields where available.

Future registry read-model fields may include:

- `primary_queue`
- `next_step_label`
- `primary_blocker`
- `has_active_matrix`
- `folder_readiness`
- `testing_readiness`

---

## 12. Expected Implementation Areas

Likely backend areas, if needed:

- project identity resolver,
- project registry summary DTO/service,
- project creation/default identity service,
- migration or seed behavior for existing no-LTR projects,
- tests for temporary ID generation/normalization.

Likely frontend areas:

- Projects overview registry table display,
- Projects queue classification if `TASK_317B` exists,
- Workbench lifecycle selector/display copy,
- project identity components or helper functions,
- frontend tests for temporary planning display.

Documentation areas:

- `docs/task_board.md`,
- `docs/task_plan_index.md` if the repository uses it for active task indexing,
- this task file,
- optional task-specific plan file.

---

## 13. Implementation Plan

Executable plan: `docs/task_317c_temporary_project_planning_identity_plan.md`

1. Extend `ProjectIdentity` in `project_identity.py` with 5 new identity fields.
2. Extend `ProjectRegistryRow` and `ProjectRegistryRowResponse` with the same 5 fields.
3. Update `list_rows()` to populate new fields from identity resolver.
4. Update frontend `ProjectRegistryRow` type in `client.ts`.
5. Update `ProjectListPage.tsx` table column: `businessIdentifier()` → `display_project_id`, add temp badge, rename header to "Project ID".
6. Add TASK_317C temporary banner copy to Workbench (no new buttons).
7. Add backend identity tests (`test_project_registry_summary_service.py`).
8. Add frontend static guard test (`test_frontend_shell_files.py`).
9. Update `docs/task_board.md`.

---

## 14. Acceptance Criteria

- A project without registered LTR/DL number is presented as `Temporary Planning`, not as an invalid formal project.
- Temporary projects have a stable temporary display ID or clear `Not registered` identity display.
- Temporary ID is visually and semantically distinct from formal LTR/DL number.
- Projects overview can display temporary planning projects without confusing them with registered LTR projects.
- Temporary projects are classified as `Planning` in the Projects overview queue filter.
- Temporary projects are not classified as `Folder Blocked` or `Matrix Needed` solely because no LTR number exists.
- Workbench no-LTR mode copy explains that Matrix/Fee planning may be used for feasibility, duration, and cost estimation.
- Formal package actions remain hidden or gated for temporary planning projects.
- Existing registered project display remains unchanged except for any intentional shared identity component cleanup.
- No Matrix authority, Confirmed Fee authority, StepInstance, report, evidence, AI, permission, or multi-user scope is added.
- `TASK_318` remains reserved for Official Project Folder check and repair.

---

## 15. Manual Smoke Checklist

1. Open `/projects`.
2. Confirm registered projects still show their formal LTR/DL identity.
3. Create or locate a no-LTR project.
4. Confirm the no-LTR project is shown as Temporary Planning or equivalent business-readable copy.
5. Confirm the no-LTR row does not show a temporary ID as if it were a formal LTR number.
6. Confirm the no-LTR row is counted as Planning, not Folder Blocked or Matrix Needed only because the LTR number is missing.
7. Open the no-LTR project Workbench.
8. Confirm Workbench shows Temporary Planning mode/copy.
9. Confirm Matrix planning entry remains available where supported.
10. Confirm Fee planning entry remains available only where supported.
11. Confirm Official Project Folder, Submitted Material, Section 2 write-back, package execution, and public-drive upload are not available as active formal actions.
12. Open a registered project Workbench.
13. Confirm registered project lifecycle behavior is unchanged.
14. Run relevant backend/frontend tests.

---

## 16. Validation Plan

Adjust exact test names after code inspection.

Suggested backend validation if backend identity/DTO changes:

```powershell
py -m pytest tests/unit/test_project_registry_summary_service.py -q
py -m pytest tests/unit/test_project_identity_resolver.py -q
py -m pytest tests/integration/test_project_registry_api.py -q
```

Suggested frontend validation:

```powershell
cd frontend
npm test -- --run Projects ProjectWorkbench --watch=false
npm run build
```

Suggested shell/static guard validation:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "projects or project_workbench or task317c"
git diff --check
```

---

## 17. Stop Point

Stop after implementing and validating temporary planning identity display, classification, and Workbench copy.

Do not proceed to full LTR registration promotion, Official Project Folder repair, public-drive upload, package execution, StepInstance, evidence/data persistence, report generation, AI review, permissions, LAN, or multi-user work without a separate approved task.
