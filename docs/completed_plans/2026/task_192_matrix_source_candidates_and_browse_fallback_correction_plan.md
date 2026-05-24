# TASK_192 Matrix Source Candidates And Browse Fallback Correction Plan

> Status: proposed for review  
> Created: 2026-05-14  
> Task: `TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION`  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 1. Execution Protocol

- Current phase: `Phase 11`.
- Current active task: `TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION`.
- Why this task is allowed now:
  - TASK_191 is complete.
  - TASK_191 acceptance review identified a bounded correction: Matrix source selection should prefer project-owned imported attachments.
  - `docs/task_board.md` currently has no active implementation task.

This document is the required plan artifact. Implementation must wait for explicit user approval.

---

## 2. Problem Summary

TASK_191 made the Matrix empty state usable, but the main import path is still:

```text
operator pastes .docx path -> preview -> create draft
```

The real lab workflow should be:

```text
incoming email attachments already stored by ConnLab
  -> select likely product specification / Matrix candidate
  -> preview
  -> create draft with source_asset_id
```

Only when no suitable attachment exists should the operator browse local/public-drive specification folders or create a manual Matrix.

---

## 3. Existing Facts To Reuse

ConnLab already preserves imported request material:

```text
data/intake/{package_id}/
  source/
  attachments/
  snapshots/
```

After project confirmation, source files are registered as project `file_assets`:

- selected application form becomes `FileAssetType.APPLICATION_FORM`;
- original `.msg` and other attachments become `FileAssetType.ATTACHMENT`;
- `file_assets.path` points to the ConnLab-controlled stored copy.

Project test-plan draft creation already accepts optional source IDs:

- `source_asset_id`;
- `source_case_id`;
- `source_draft_id`.

Therefore this correction should add a read model and frontend selection flow rather than changing the core Matrix parser.

---

## 4. Proposed Backend Design

### 4.1 Source Candidate Service

Add a focused application service, for example:

```text
backend/application/project_test_plan_source_candidate_service.py
```

Responsibilities:

- Load Project by `project_id`.
- Load project `file_assets`.
- Filter and rank likely Matrix source candidates.
- Return a typed read model without parsing the documents.

Candidate detection:

- include `.docx` assets;
- prefer names containing:
  - `spec`;
  - `specification`;
  - `matrix`;
  - `qualification`;
  - `test`;
  - `product`;
- include all `.docx` attachments even when name confidence is low, but mark the reason clearly;
- exclude generated downstream outputs when identifiable by type/name in this task's available data.

Response item:

```text
source_asset_id
original_name
extension
asset_type
candidate_kind
reason
stored_file_available
```

Do not expose raw local paths as the main user-facing label. Backend may use paths internally for preview.

### 4.2 API Endpoint

Add route:

```text
GET /api/projects/{project_id}/test-plan/source-candidates
```

Response:

```text
project_id
candidates[]
warnings[]
```

Warnings may include:

- no Project file assets found;
- no `.docx` candidate found;
- candidate file path missing on disk.

### 4.3 Candidate Preview

Preferred implementation:

- Add a candidate preview endpoint, for example:

```text
POST /api/projects/{project_id}/test-plan/source-candidates/{source_asset_id}/matrix-preview
```

- It loads the asset, validates it belongs to the Project, validates stored path exists, and then calls the existing Matrix preview service with that path.
- The preview response should carry `source_asset_id` or the frontend should keep it together with the preview selection.

Alternative if endpoint count must stay smaller:

- The existing frontend path-preview can still be used internally only if the backend exposes a safe preview-by-asset helper. Do not require the frontend to know or paste the stored path.

### 4.4 Draft Creation

When creating a draft from a selected candidate:

- use preview source metadata;
- set `source_asset_id`;
- keep status `draft`;
- keep preview payload mapping from TASK_191.

Path fallback draft creation remains unchanged but has no `source_asset_id`.

---

## 5. Proposed Frontend Design

Files expected:

- `frontend/src/api/client.ts`
  - add source candidate DTOs/functions;
  - add preview selected candidate function if backend endpoint exists.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - load source candidates for draftless Matrix workspace;
  - track selected source candidate;
  - support preview/create from candidate;
  - keep external path fallback from TASK_191.
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixStarter.tsx`
  - render candidate list first;
  - render external source fallback second;
  - render manual fallback last.
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`
  - include selected `source_asset_id` when building create request from candidate preview.
- `frontend/src/workbench.css`
  - style candidate rows compactly.

UI priority:

1. Candidate source files from this Project.
2. External Browse/path fallback.
3. Manual Matrix fallback.

### Browse Fallback

Add a `Browse` action in the external fallback area.

Current Web limitation:

- If no native desktop bridge exists, the button may show a concise unavailable/help message and keep the path input available.
- Do not fake a browser upload as if it provides a reusable absolute local path.

Future desktop-shell behavior:

- Browse should open a native file picker.
- Default folder should come from a configured external resource such as `product_spec_root`.

This task may reserve the copy and UI affordance. Full native file-picker implementation should happen only if an existing safe bridge already exists.

---

## 6. Out Of Scope

- PDF parsing.
- `.doc` parsing.
- Direct Outlook access.
- New email import behavior.
- Report generation.
- Filled record import.
- Image/evidence per step.
- Fee mapping.
- Historical reuse.
- AI review.
- Hard-coded public-drive folders.
- Frontend direct filesystem access.

---

## 7. Risks And Controls

Risk: exposing stored paths in UI.

Control: show original name, type, availability, and reason; keep raw paths backend-side or diagnostic-only.

Risk: selecting the application form as product spec.

Control: candidate scoring should rank likely spec/matrix names higher and mark low-confidence `.docx` as generic Word attachment.

Risk: draft loses traceability.

Control: draft creation from candidate must set `source_asset_id`.

Risk: Browse is impossible in current browser runtime.

Control: expose Browse affordance with clear fallback and defer native bridge if needed.

Risk: scope creep into PDF.

Control: `.pdf` may appear as non-actionable future-capability candidate or warning only; do not parse it.

---

## 8. Validation

Backend:

```powershell
python -m pytest tests\unit\test_matrix_source_candidate_service.py tests\integration\test_project_test_plan_source_candidates_api.py -q
```

Regression:

```powershell
python -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_draft_api.py -q
```

Frontend/static:

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task191 or task192"
```

Frontend build:

```powershell
cd frontend
npm run build
```

Task-board guard:

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke:

- Project with `.docx` source attachment: candidate appears, preview succeeds, draft creation persists `source_asset_id`.
- Project without candidate: external fallback area is available.
- Plain browser without native picker: Browse fallback behavior is clear and path input still works.
- Manual Matrix remains available.

---

## 9. Acceptance Criteria

- Draftless Workbench loads Project Matrix source candidates.
- Candidates appear before external path/manual fallback.
- Selecting a candidate can preview Matrix using existing parser logic.
- Creating draft from candidate stores `source_asset_id`.
- Existing TASK_191 path import and manual Matrix remain functional.
- Browse fallback is present and does not hard-code a public path.
- No PDF/report/record/image/fee/history/AI scope is added.
- Validation commands pass or any inability to run is documented.

---

## 10. Approval Needed

Please approve this plan before implementation.

Implementation must stop at TASK_192. It must not continue into group/step detail deepening, record generation, record import, images, fee mapping, reports, or historical reuse.
