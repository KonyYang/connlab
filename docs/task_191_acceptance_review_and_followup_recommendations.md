# TASK_191 Acceptance Review And Follow-up Recommendations

> Created: 2026-05-14  
> Reviewed task: `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE`  
> Phase: Phase 11 - Project planning data foundation before downstream document automation

## 1. Review Conclusion

`TASK_191` is acceptable as a Matrix starter foundation.

It delivered the originally approved scope:

- Matrix empty state has a real starter workflow.
- `.docx` source path can be previewed through the existing Matrix preview API.
- Preview can create a persisted Project test-plan draft.
- Manual Matrix creation persists a draft with explicit `Group 1` identity.
- Existing authority/candidate semantics remain the normal post-creation path.

The implementation does not yet match the richer real operator workflow discussed after completion: source selection should prefer already-imported email attachments before asking the operator to browse or enter an external path.

That gap should be handled as a controlled follow-up correction, not as an unbounded edit to the completed TASK_191.

## 2. Current Implementation Shape

Current TASK_191 implementation is primarily frontend/API-client wiring:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixStarter.tsx`
  - renders Matrix starter UI;
  - supports source path input, preview, create draft from preview, and manual Matrix creation.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - owns starter state and actions;
  - calls Matrix preview and draft-create APIs;
  - reloads Matrix draft state after creation.
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`
  - maps preview payload into draft payload;
  - builds manual starter draft request.
- `frontend/src/api/client.ts`
  - adds typed Matrix preview and draft-create client functions.

Current behavior is still path-first:

```text
Paste source .docx path -> preview -> create draft
or
Create manual Matrix
```

## 3. Important Business Correction

The correct lab workflow should be source-archive first:

```text
Project's imported email package and attachments
  -> candidate product specification / Matrix attachments
  -> preview selected candidate
  -> create Matrix draft with source_asset_id
  -> external browse fallback only if no suitable attachment exists
  -> manual Matrix only if no usable source exists
```

Reason:

- The project already preserves incoming `.msg` and extracted attachments under controlled intake storage.
- Project confirmation registers those files as project `file_assets`.
- Matrix traceability should point back to the exact source attachment when possible.
- Operators should not have to manually re-find a file that ConnLab already imported.

## 4. Confirmed Intake Storage Facts

Imported email material is stored under:

```text
data/intake/{package_id}/
  source/
    original email .msg
  attachments/
    extracted attachments
  snapshots/
    parser or manual snapshots
```

Relevant records:

- `intake_packages.source_stored_path`: stored source email path.
- `intake_assets.stored_path`: stored attachment path.
- `intake_assets.asset_role`: source/application/spec/supporting role before project confirmation.
- `intake_cases.confirmed_project_id`: links an intake case to the confirmed project.
- `file_assets.path`: project-level registered file path after confirmation.

## 5. Recommended Follow-up Task

Recommended next controlled task:

```text
TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION
```

Purpose:

Make Matrix starter source selection follow real lab priority:

1. show candidate source files already attached to the Project;
2. preview selected candidate directly;
3. persist `source_asset_id` when creating the draft;
4. provide a Browse fallback for local/public-drive specification files;
5. keep manual Matrix as the final fallback.

## 6. Proposed Scope For Follow-up

Backend/read model:

- Add a Project-scoped Matrix source candidate read model.
- Candidate sources should be derived from Project `file_assets` first.
- Candidate detection should include at minimum:
  - `.docx` files;
  - asset original names containing likely specification/Matrix terms;
  - existing `specification` role where available;
  - supporting attachments that are Word documents.
- Include source metadata:
  - `source_asset_id`;
  - `original_name`;
  - `stored_path` only if safe for backend use;
  - `extension`;
  - `asset_type`;
  - `reason` or `candidate_kind`.
- Add an API endpoint such as:

```text
GET /api/projects/{project_id}/test-plan/source-candidates
```

Preview/create flow:

- Prefer preview by asset ID or by selected candidate, not only raw path.
- When draft is created from a project file asset, set:
  - `source_asset_id`;
  - `source_document_path`;
  - `source_document_name`;
  - `source_format`.
- Preserve the existing path-based preview as external fallback.

Frontend:

- Matrix starter should show source candidates before the external path area.
- Candidate UI should support:
  - select candidate;
  - preview selected source;
  - create draft from preview.
- External fallback should use a Browse action instead of making manual path entry the primary flow.
- If native browse is not available in current web runtime, show the Browse action as shell-dependent and keep manual path paste as a fallback.
- Default browse location should come from configuration, not a hard-coded path.

Settings/future configuration:

- Add or reserve an external resource such as:

```text
product_spec_root
```

- This should represent the local or public-drive folder where product specifications are usually stored.
- The Browse fallback should default there when desktop shell support is available.

## 7. Browse Button Design Decision

The user's supplement is accepted:

If no suitable candidate exists, the operator should be allowed to click a Browse button to open a file picker. The picker should default to the configured local/public-drive product specification folder.

Implementation boundary:

- In a plain browser, a web app cannot freely open arbitrary local/public-drive file dialogs and return trusted absolute paths without browser constraints.
- In the later PyWebView/desktop shell, a native file dialog can provide this path safely.
- Therefore the next task should separate:
  - UI affordance and configuration now;
  - shell-native browse integration when the desktop shell boundary is active.

Do not hard-code real public-drive paths into frontend code.

## 8. Acceptance Criteria For Follow-up

- Matrix starter lists Project source candidate files before any external path or manual action.
- Candidate preview uses the existing Matrix preview logic and creates drafts only after preview succeeds.
- Drafts created from Project assets persist `source_asset_id`.
- External fallback provides a Browse action and a manual path fallback.
- Browse default root is configuration-driven or explicitly deferred with clear UI copy.
- Manual Matrix remains available, but no longer appears as equivalent to imported source when candidates exist.
- No PDF parsing, report generation, record import, image management, fee mapping, or historical reuse is added.

## 9. Recommended Model

Recommended implementation model: `gpt-5.3-codex high`.

Reason:

- This is a cross-boundary correction involving Project file assets, intake traceability, API read models, Workbench state, and UI priority.
- The main risk is source traceability, not visual complexity.
- `medium` is acceptable only if the task is split into a backend candidate API first and a separate frontend wiring task later.
