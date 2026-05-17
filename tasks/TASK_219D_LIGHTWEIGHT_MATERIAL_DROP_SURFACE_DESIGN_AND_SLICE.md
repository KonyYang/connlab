# TASK_219D_LIGHTWEIGHT_MATERIAL_DROP_SURFACE_DESIGN_AND_SLICE

## Status

Draft task document. Pending user review and explicit approval.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. This task should run after `TASK_219A` removes the old lower Workbench preparation flow, because the drop surface must be lightweight and must not recreate the old evidence-placement workbench.

## Why This Task Is Allowed Now

The business conclusion says:

- product materials are already archived during LTR import
- other materials only need drag & drop

The current Workbench has `ProjectWorkbenchEvidencePanel`, which is a preview/place workflow over backend evidence placement. That is heavier than the new direction.

This task is allowed only as a lightweight material intake/status surface. It must not implement image asset management, Step evidence persistence, or report binding.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for the planning and a narrow frontend/backend adapter slice, provided the task explicitly handles the browser-vs-desktop drag/drop limitation. It is not suitable for unbounded desktop shell integration in this slice.

## Objective

Define and implement the smallest safe "Other materials" surface for Project Runtime Console.

The intended UX:

```text
Other materials
  Drop files here or choose source paths.
  Preview placement.
  Confirm placement.
  Show latest placement result.
```

But implementation must respect current platform limits:

- Browser drag/drop normally exposes `File` objects, not trusted local absolute paths.
- Current backend evidence placement APIs operate on existing project assets/source paths.
- PyWebView desktop shell is not the current baseline unless explicitly requested.

## Existing Code Context

Frontend:

- `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/api/client.ts`

Backend:

- `backend/api/routes_evidence.py`
- `backend/application/evidence_placement_service.py`
- `backend/modules/folder/evidence_placement_rules.py`

## Scope

Allowed:

- produce a technical feasibility plan before implementation
- reuse existing evidence preview/place APIs if sufficient
- create a lightweight UI surface that is clearly labeled as support action
- support paste/typed source path fallback if drag/drop absolute paths are not available
- keep actions preview-first
- add tests for UI boundary/static expectations

Forbidden:

- storing Step evidence
- implementing image asset management
- binding materials to reports
- adding browser file upload storage unless explicitly approved
- adding PyWebView APIs unless explicitly approved
- scanning arbitrary local folders
- turning Other materials into a generic file manager
- exposing future Step Workspace evidence behavior as active

## Required First Deliverable

Before coding, create:

```text
docs/task_219d_lightweight_material_drop_surface_plan.md
```

The plan must include:

- current evidence placement API behavior
- browser drag/drop limitation analysis
- desktop-shell assumption, if any
- chosen minimal implementation path
- UI copy and disabled/fallback states
- exact files to change
- validation commands

Stop after writing the plan and wait for explicit user approval.

## Implementation Guidance After Approval

Acceptable implementation paths:

1. If no trusted local paths are available in browser mode, implement a lightweight support panel that explains "drop is available in desktop workspace" and preserves paste-path/preview behavior.
2. If existing source archive assets are sufficient, implement "Add from Source Archive" or "Preview source materials" without browser file upload.
3. If the user explicitly approves upload storage, create a separate backend asset-ingest task before implementing drag/drop file upload.

## Acceptance Criteria

- Other materials surface is lightweight and secondary.
- Preview-before-place remains enforced.
- UI does not imply Step evidence persistence exists.
- UI does not imply image/report binding exists.
- Browser limitations are handled honestly in copy and behavior.
- No new unapproved storage model is added.
- `npm run build` passes if frontend is changed.

## Validation

Required if frontend changes:

```powershell
cd frontend
npm run build
```

Recommended:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Manual smoke:

1. Open Project Workbench.
2. Locate Other materials support action.
3. Confirm it is secondary to Runtime Console.
4. Confirm preview-first behavior or desktop-mode limitation copy.
5. Confirm no Step evidence or report binding is exposed.

