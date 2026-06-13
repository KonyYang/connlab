# TASK_317D Temporary Project Lifecycle And Promotion — Executable Plan

Status: Complete. Implemented after user approval on 2026-06-13.

Date: 2026-06-13

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317D` completed as a controlled follow-up before any TASK_319 public-drive/upload work.

Allowed reason: Current product behavior still confuses active temporary planning projects with cancelled/hidden records. Earlier planning (`TASK_313A`) already defines a `temporary_planning` Workbench mode, and `TASK_317C` already defines temporary identity. TASK_317D connects those decisions into New Project temporary creation, lifecycle, visibility, Workbench layout, and promotion boundaries.

Implementation note:

- V1 uses the existing storage-compatible active state: `Project.status == draft` with no registered LTR/DL. Registry identity and queue semantics classify this as temporary planning through the existing no-LTR/TMP identity path.
- `POST /api/projects/temporary` accepts the documented minimum request context and returns `project_id`, temporary display identity fields, storage status, and `next_route`.
- The temporary request context is persisted in a dedicated planning table, including request summary, sample description, test item, notes, and source intake asset IDs. Registry and project detail read models expose that context for Workbench display and future promotion review.
- The New Project page exposes `Create Temporary Project` as a secondary action and navigates to the created Workbench.
- The Workbench temporary planning surface includes a `Convert to Formal Project` entry only for active temporary projects. Cancelled no-LTR projects are review-only and do not show temporary planning or promotion actions.
- The Fee Evaluation entry is gated until a Matrix draft is available.
- Same-project LTR registration is not wired yet. The V1 promotion action reports the routing/contract gap and does not create a duplicate formal project.
- Existing cancelled no-LTR records remain cancelled and hidden by default unless `Show cancelled` is enabled; no automatic restoration was performed.

---

## 1. Task Understanding

### Goal

Create a controlled implementation slice that makes temporary planning projects first-class active records instead of cancelled/hidden records, adds a `Create Temporary Project` entry to the New Project page, aligns Projects overview `Planning` with Workbench `temporary_planning`, and defines a safe promotion path from temporary project to formal LTR/DL registration.

### Inputs

- Existing project records and statuses.
- Existing LTR records and identity resolver.
- Existing Projects registry DTO/API.
- Existing TASK_317B queue filter behavior.
- Existing TASK_317C temporary identity fields.
- Existing TASK_313A Workbench lifecycle-mode layout model.
- Existing New Project / LTR registration workflow.
- Existing Source Book / request material collection and local workspace records where available.

### Outputs

- New Project page exposes `Create Temporary Project`.
- Backend creates an active temporary planning project without LTR/DL registration.
- Frontend navigates to the new temporary project's Workbench after creation.
- Active temporary planning projects visible in `Planning`.
- Cancelled/archive visibility kept separate from temporary planning.
- Workbench temporary planning layout aligned with lifecycle-mode rules.
- Workbench-only promotion entry defined and gated.
- Promotion flow uses existing LTR registration path and reuses temporary material where possible.
- Tests and documentation validating the distinction.

### Modules

Likely modules:

- `backend/application/project_identity.py`
- `backend/application/project_registry_summary_service.py`
- `backend/api/routes_project.py`
- `backend/infrastructure/storage/models.py` or a narrow migration/helper if an explicit lifecycle/archive field is needed
- `frontend/src/pages/ProjectListPage.tsx`
- New Project page components and hooks under `frontend/src/features/new-project/` or the current intake route ownership
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/api/client.ts`
- existing New Project / LTR frontend and backend services
- relevant backend, frontend, and static tests

### Not Allowed

- No detailed action buttons in Projects overview.
- No duplicate LTR registration engine.
- No public-drive upload/update.
- No final generated output work for temporary projects.
- No StepInstance, execution persistence, evidence/photo capture, report generation, AI, permissions, LAN, or multi-user work.
- No direct Office operations outside existing gateways.
- No silent conversion of cancelled records into active temporary projects without explicit migration/review rules.

---

## 2. Design Decisions

### 2.1 New Project Temporary Entry

The existing New Project page should include a secondary action:

```text
Create Temporary Project
```

This action is for early customer discussions where LTR/DL registration is not ready or intentionally skipped for feasibility, Matrix, duration, or fee planning.

Expected V1 behavior:

1. The operator can enter the available discussion/source information supported by the current New Project page.
2. Application form and attachments are optional.
3. Clicking `Create Temporary Project` calls a backend creation service.
4. The backend creates a project in active temporary planning state without registering LTR/DL.
5. The project receives the existing TASK_317C display identity pattern, `TMP-XXXXXXXX`.
6. The frontend navigates directly to that project's Workbench.
7. The Projects overview shows the project in the `Planning` queue.

The button must not perform LTR preview, LTR commit, official folder creation, package generation, or public-drive upload.

Minimum backend contract:

```text
POST /api/projects/temporary
```

Minimum request DTO:

```ts
type CreateTemporaryProjectRequest = {
  request_summary?: string | null;
  sample_description?: string | null;
  test_item?: string | null;
  requestor?: string | null;
  source_asset_ids: string[];
  notes?: string | null;
};
```

Minimum response DTO:

```ts
type CreateTemporaryProjectResponse = {
  project_id: string;
  display_project_id: string;
  display_project_id_kind: "temporary";
  has_registered_ltr: false;
  status: "temporary_planning" | string;
  next_route: string;
};
```

If the current API conventions favor another route name, the implementation may adapt the endpoint path, but it must preserve these request/response semantics.

### 2.2 Separate Active Temporary Planning From Cancelled

`Planning` and `Show cancelled` must remain separate concepts.

Recommended V1 semantics:

```text
active no-LTR project -> Planning
cancelled no-LTR project -> hidden by default, visible only under Show cancelled
```

If existing data has no reliable field for this distinction, introduce a conservative project lifecycle/read-model marker rather than using `cancelled` as temporary planning.

Possible implementation choices:

1. Minimal status correction:
   - Use existing `Project.status`.
   - Treat newly created no-LTR active planning records as active temporary planning.
   - Existing no-LTR rows with `status === "cancelled"` remain cancelled unless a later explicit cleanup task changes them.
   - Add a reviewed dry-run/manual cleanup list for rows that might deserve restoration.

2. Explicit lifecycle field:
   - Add `project_lifecycle_state` or equivalent read-model field.
   - Keep `status` compatibility.
   - More robust, but higher migration cost.

Recommended first implementation: create new temporary projects as active planning records and avoid automatic historical status mutation. Add an explicit future DTO note unless code inspection shows status cannot safely represent active temporary planning.

### 2.3 Registry Queue And Visibility

Projects overview should keep:

```text
All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed
```

Rules:

- `Planning`: active temporary projects without registered LTR/DL.
- `Show cancelled`: archive/cancelled visibility only.
- Cancelled rows do not count toward normal queue counts.
- Search composes with queue and cancelled visibility.
- `Open` remains the only row action.

### 2.4 Workbench Temporary Planning Layout

Reuse `TASK_313A` lifecycle-mode direction:

```text
temporary_planning
registered_setup
package_preparation
execution_console
```

Temporary planning mode should show:

- TMP identity and Temporary Planning label.
- Request/source material summary.
- Matrix planning entry.
- existing safe Fee planning or fee draft entry if available; otherwise disabled/gated copy.
- feasibility/duration/planning note area if already available or introduced narrowly.
- formal registration requirement copy.

Temporary planning mode should hide or gate:

- official project folder creation.
- Submitted Material formal checklist.
- Section 2 write-back.
- package preview/execute.
- public-drive upload.
- Step Workspace as primary execution content.

### 2.5 Promotion Entry

Promotion is Workbench-only.

Preferred label:

```text
Register LTR / Convert to Formal Project
```

It should appear only when:

- project has no registered LTR/DL,
- project is active, not cancelled/archive,
- user is in temporary planning Workbench mode.

TASK_317D V1 promotion should route into the existing New Project / LTR readiness and registration context with the same `project_id` if current routing supports same-project registration. It must not create a duplicate Project.

If the current New Project/LTR flow cannot safely register an existing `project_id`, TASK_317D should stop at the Workbench promotion entry plus a documented routing/contract gap. The actual same-project LTR commit bridge should then be split into a follow-up task.

### 2.6 Material Carry-Forward

Promotion should reuse:

- request email/source material references,
- application form if present,
- specification attachments,
- sample/test item information,
- Matrix draft or selected planning groups where compatible,
- Fee draft or fee planning notes where compatible.

Promotion should not fake missing data. Missing application form, required LTR fields, or ambiguous materials remain review blockers in the existing readiness path.

---

## 3. Proposed File-Level Changes

### Backend

Inspect first:

- `backend/infrastructure/storage/models.py`
- `backend/application/project_registry_summary_service.py`
- `backend/application/project_identity.py`
- New Project / LTR registration services
- request material and workspace services

Likely changes:

- Add temporary project creation service or a narrow branch in the existing New Project orchestration boundary.
- Add or normalize a project lifecycle/readiness helper for active temporary planning vs cancelled.
- Extend registry row read model only if current fields are insufficient.
- Add promotion eligibility/blocker read-model service if needed, but avoid implementing a parallel LTR registration engine.
- Add tests around temporary creation, no-LTR active vs no-LTR cancelled rows, and registry visibility.

### Frontend

Inspect first:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- existing New Project route/state model.

Likely changes:

- Add `Create Temporary Project` as a secondary action on the New Project page.
- Wire temporary creation success to Workbench navigation for the returned `project_id`.
- Keep Projects overview queue/search behavior, but ensure active temporary rows appear in Planning without `Show cancelled`.
- Update temporary Workbench mode rendering to match TASK_313A mode layout.
- Add a gated Workbench-only promotion entry.
- Route promotion to existing New Project/LTR flow with project context if current routing supports it; otherwise render/document the routing gap and stop before duplicate project creation.

### Tests

Likely tests:

- registry summary/service test for active no-LTR vs cancelled no-LTR.
- API smoke test for registry identity/visibility fields if backend changes.
- backend/API tests for `Create Temporary Project` creation behavior.
- frontend test or static guard for the New Project temporary creation entry and navigation callback.
- frontend static/selector tests for queue classification and Workbench mode.
- frontend component test for temporary Workbench promotion entry gating.
- New Project/LTR route integration test if a same-project routing bridge is safely added.

---

## 4. Data Migration / Cleanup Strategy

Do not silently rewrite historical cancelled records as active temporary projects.

Recommended approach:

1. Add logic that correctly handles new active temporary planning records.
2. Add the New Project temporary creation path so future temporary projects are created as active planning records from the start.
3. Identify existing no-LTR cancelled rows that look like temporary planning records.
4. Provide a dry-run review output or manual remediation plan before changing their status.
5. Do not change those historical statuses in TASK_317D. Apply cleanup only under a separate explicit approval if it mutates existing records.

This keeps archive semantics safe and avoids accidentally restoring intentionally cancelled records.

---

## 5. Promotion Flow Sketch

```text
Temporary Planning Workbench
  -> Register LTR / Convert to Formal Project
  -> Existing LTR readiness/review flow
  -> Review imported temporary material and required fields
  -> Preview LTR registration
  -> Commit registration through existing guarded path
  -> Same project_id now has registered LTR/DL identity
  -> Workbench derives registered_setup / package_preparation / execution_console
```

If the existing LTR path cannot commit against the same `project_id`, the V1 flow becomes:

```text
Temporary Planning Workbench
  -> Register LTR / Convert to Formal Project
  -> Show existing-flow routing gap / blocked reason
  -> no duplicate project is created
```

Implementation rule:

- Preserve `project_id`.
- Do not create a second project unless a later conflict-resolution task explicitly allows it.
- Do not discard temporary artifacts.

---

## 6. Risks And Controls

| Risk | Control |
|------|---------|
| Existing cancelled rows include both abandoned records and useful temporary projects | No silent migration; dry-run review first |
| Promotion duplicates projects | Preserve same `project_id`; route through existing registration service; if unsupported, stop at documented gap |
| Projects overview becomes a workflow page | Keep only `Open` row action |
| Workbench exposes formal actions too early | Gate official folder/package/Section 2/public-drive surfaces on registered LTR/DL |
| Frontend invents lifecycle truth from labels | Add explicit read-model fields if current DTO is insufficient |
| Existing tests assume cancelled hidden behavior | Update tests to distinguish cancelled/archive from active temporary planning |

---

## 7. Validation Plan

Backend:

```powershell
py -m pytest tests/unit/test_project_registry_summary_service.py tests/integration/test_project_registry_summary_api.py -q
```

Frontend static / unit:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_dashboard or task303_project_registry or task317c or task317d or project_workbench"
```

Frontend component/build:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false
npm run build
```

Manual smoke:

1. Open `/intake`.
2. Confirm `Create Temporary Project` appears as a secondary New Project action.
3. Create a temporary project without LTR/DL registration.
4. Confirm the app navigates to the new temporary project's Workbench.
5. Open `/projects`.
6. Confirm active no-LTR project appears under `Planning` without `Show cancelled`.
7. Confirm cancelled rows remain hidden until `Show cancelled`.
8. Open active temporary project.
9. Confirm `Temporary Planning` layout appears.
10. Confirm formal folder/package/Section 2/public-drive actions are hidden or gated.
11. Confirm promotion entry appears in Workbench only.
12. Confirm promotion enters existing LTR readiness/registration path when same-project routing is supported, or shows the documented routing gap when it is not.
13. Cancel promotion and confirm temporary project remains intact.

---

## 8. Review Checklist

- [ ] Does this preserve TASK_317B queue semantics?
- [ ] Does this preserve TASK_317C identity semantics?
- [ ] Does this align with TASK_313A lifecycle-mode layout?
- [ ] Does New Project expose `Create Temporary Project` without triggering LTR registration?
- [ ] Does temporary project creation navigate to Workbench and appear in Planning?
- [ ] Does this keep Projects overview as registry only?
- [ ] Does this avoid public-drive upload and final output generation?
- [ ] Does promotion reuse existing LTR registration flow?
- [ ] If same-project LTR registration is unsupported, does TASK_317D stop at a documented gap instead of creating a duplicate Project?
- [ ] Does implementation avoid silently mutating historical cancelled data?
- [ ] Are tests added or updated for active temporary vs cancelled rows?

---

## 9. Stop Point

After approval, implement only TASK_317D.

Stop after tests, build, documentation update, and task board sync. Do not proceed to TASK_319 or public-drive upload/update without separate approval.
