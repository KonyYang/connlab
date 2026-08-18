# TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

In a normal browser Matrix Editor, `Import Matrix` first shows the current project's already
registered intake source candidates. The operator can explicitly preview one controlled candidate
or choose `Upload other file`. The desktop shell keeps its existing native directory picker.

## Confirmed Repository Facts

- Browsers cannot set the starting directory of an HTML file input.
- The existing source-candidate GET API returns ranked project candidates with file name,
  extension, asset type, candidate kind, recommendation reason, and availability.
- The existing source-candidate preview POST API previews an explicitly selected controlled asset.
- The existing service already ranks likely specification/Matrix files before fallback Word
  attachments; frontend code must preserve that order rather than invent another scoring rule.
- The current Matrix Editor browser branch immediately clicks the hidden upload input, while the
  desktop branch uses the existing project-aware native picker.

## Required Behavior

1. Browser `Import Matrix` opens a focused project-source chooser before file upload.
2. Each candidate shows its file name, type, availability, and API-provided recommendation reason.
3. `likely_spec_or_matrix` candidates have a clear `Recommended` label, but are never selected or
   previewed without an explicit operator action.
4. Selecting an available candidate calls the existing preview-by-candidate API and opens the
   current Matrix preview flow.
5. `Upload other file` opens the existing `.pdf/.doc/.docx` browser input.
6. No-candidate and API-failure states remain actionable through `Upload other file`.
7. Closing/cancelling the chooser changes no Matrix/import state.
8. Read-only lifecycle blocks before any chooser, picker, upload, or preview call.
9. Desktop native picker and its Submitted Material/intake-directory behavior remain unchanged.

## May Touch

1. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
2. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
3. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
4. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
5. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
6. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
7. `frontend/src/workbench.css`
8. `docs/task_board.md`

Role evidence uses the fixed task-derived Planner, Developer, Reviewer, QA, Integrator, and
closeout evidence paths.

## Must Not Touch

- Backend, API routes/contracts, database, schema/migrations, persistence, or project attachments.
- Matrix parsing, preview semantics, Replace/Confirm authority, or lifecycle authority.
- Desktop bridge/native picker behavior or preferred-directory resolution.
- Attachment management, upload refactoring, file copying, or new storage.
- Other frontend surfaces, generalized dialog frameworks, or broad CSS cleanup.
- Push, cleanup, archive, retire, reset, restore, stash, rebase, or destructive actions.

## Acceptance

- Browser candidates render in API-ranked order with operational file/type/recommendation copy.
- Explicit candidate selection generates preview through the existing candidate endpoint.
- Upload fallback, empty state, cancellation, read-only blocking, and desktop behavior are covered.
- Targeted frontend tests and production build pass.
- The task stops at `implemented_pending_human_review` until the User sends `关闭`.

