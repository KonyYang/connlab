# TASK_367A Matrix Editor Live XLSX Export Planner Evidence

Date: 2026-07-26
Role: Planner
Status: `docs_only_source_of_truth_reconciliation_complete_pending_reviewer_docs_only_source_of_truth_re_gate`
Task: `TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT`
Lane: `matrix-editor-live-xlsx-export`

## Discovery Decision

The request belongs in an independent Matrix Editor output lane. It must not be folded into
accepted Test Record, Matrix import, Confirm Matrix, Fee, or project-output work.

The repository supports a narrow zero-write browser-download architecture. The User resolved
delivery, `Time`, and row-scope decisions; Developer completed planning-first; Reviewer passed
implementation-readiness; and the User explicitly authorized product/test implementation.
At that historical planning checkpoint, implementation could not start before the controlled
governance checkpoint and clean-primary gate; those gates are now completed.

## Protocols And Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- ConnLab Planner and lane orchestration skills
- Planner Discovery, parallel execution, worktree operations, and task execution protocols
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context
- Spreadsheet skill, style guidance, and artifact-tool API
- Matrix Editor workspace, schedule calculation, API client, current-state Test Record route and
  service, desktop path picker, XLSX writers, focused tests, and related accepted task evidence

## Git Baseline

- HEAD: `033e530c2d6a9c01c210f35b938678672b6449ad`.
- Branch: `master`.
- origin/master: `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- rev-list left/right: `0/7`.
- Primary worktree was clean and the index empty at Discovery start.
- No implementation worktree was created.

## User-Confirmed Facts

- Add `Export Matrix` beside `Import Matrix`.
- Export current state without Confirm Matrix.
- Export only checked Groups, matching Test Record selection.
- Samples Quantity maps to `Sample size`; Test Days maps to `Time`.
- Keep `Fee`; all Fee values are blank.
- Reference workbook is read-only.
- Desktop and 514 px must remain coherent.
- Delivery uses the same browser Blob download path as Test Record; native Save As is excluded.
- Each checked Group's `Time` is exactly the current Matrix Editor `Test Days` display text:
  ```${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d```. Integers have no
  decimals, fractional values have at most two decimals without trailing zeros, and blank/no
  contributing Day values display as `0 d`.
- Export includes only non-sample test rows with a nonblank step in at least one checked Group
  after the existing selected-Group step-format/sequence gate passes.
- `Show selected groups only` is view-only and does not change export scope.

## Repository Findings

1. `MatrixEditorWorkspace.tsx` contains current local rows, Groups, cells, samples, and schedule
   results.
2. `buildMatrixEditorTestRecordDraftRequest()` proves a current-state checked-Group request can
   be built without Confirm Matrix.
3. `showSelectedGroupsOnly` is presentation-only and cannot be export authority.
4. Existing Blob download, filename parsing, and request errors are reusable.
5. Autosave/CAS belongs to persistence; a click-time zero-write snapshot need not wait for
   autosave or attest the saved payload.
6. `Test Days` already uses the same current rows and checked Groups.
7. PyWebView exposes open-file/folder selection only. Native Save As requires new bridge scope.
8. Current oversized surfaces require bounded modules and exact wiring: workspace 4093,
   workspace test 1934, client 4600, CSS 9455, dependencies 2248 lines.
9. `MatrixWorkspaceActionGroups.tsx` is not imported by current source and is excluded.

## Reference Workbook Evidence

Read-only artifact-tool inspection of
`D:\TestFlowManager\Projects\DL-2025-02-054 EK500 Connector Qualification Testing\matrix.xlsx`
found:

- `Sheet!A1:G5`;
- headers `Test Item`, `Section`, `Test Method`, `Condition`, `Requirement`, `1`, `Notes`;
- fixed rows `Sample size`, `Time`, `Fee`;
- Fee values blank;
- gray `#CCCCCC` header/A labels, thin borders, centered wrapped Calibri 11;
- A/B/D/E widths 20/8/20/20. The reference's observed row height 15 is historical only;
  generated wrapped rows now keep height unset for automatic fitting;
- no formula, drawing, or merge.

The source was not saved, converted, copied, or modified. File size was 5262 bytes and the
observed UTC modification time was 2026-04-09 11:15:56. Hashing was not a gate because the
external workbook was held open by another process after inspection. Runtime must not depend on
this file.

## Proposed Safety Contract

- one immutable request snapshot per click;
- checked Groups only, in current order;
- no save, autosave wait, Confirm Matrix, CAS, DB, output registration, or source read;
- exact display-text `Time`, including `0 d`, with no backend Day conversion;
- only existing-gate-valid rows containing steps in checked Groups;
- fresh in-memory macro-free workbook only;
- no server file or generated artifact;
- truly blank Fee cells;
- typed no-download failures;
- double-click suppression and Blob URL cleanup;
- external reference absent from runtime and tests.

## Reconciled User Decisions

1. Use the existing browser Blob download and `Content-Disposition` handling. PyWebView/native
   Save As remains locked.
2. Send and write the exact current `Test Days` display string. Backend code must not parse,
   convert, round, or recompute it.
3. Include only checked-Group test rows containing steps. Unchecked Groups, sample/information
   rows, and rows unrelated to checked Groups are omitted. The existing selected-Group step gate
   is reused; no second parser is introduced.

## Proposed Scope

Future product scope is bounded to:

- exact Matrix Editor workspace wiring;
- three new bounded frontend projection/hook/button modules;
- exact API-client request/download hunk;
- optional exact target-action responsive CSS hunk;
- new bounded route, dependency module, application service, and in-memory workbook gateway;
- exact router registration;
- six new bounded test modules;
- task/plan/evidence/board.

All Matrix persistence/Confirm/import/Test Record/Fee/schema/database/Settings/project-output,
PyWebView/native Save As paths, real files, and residuals are locked.

## Historical Worktree Plan (Completed)

Developer planning-first was governance-only in the primary worktree. The approved later
implementation sequence was:

- first create a controlled local docs-only governance checkpoint and make the primary
  worktree/index clean;
- branch `lane/task-367a-matrix-editor-live-xlsx-export`;
- sibling worktree
  `D:\PythonProject\connlab-task-367a-matrix-editor-live-xlsx-export`;
- primary remains planning/integration only;
- clean Developer checkpoint, base-to-lane Reviewer gate, clean QA, then Integrator.

## Planner Verification

- Read-only source, protocol, and workbook inspection completed.
- Reference workbook was not modified.
- No product or test file was modified.
- No real DB/project/public-drive data was accessed.
- No implementation worktree, stage, commit, push, cleanup, restore, or discard occurred.

## Post-Accept Source Of Truth

- Accepted lane HEAD:
  `53840b42ea73358c31fe40c5225646363d485829`.
- `f0880310f786ac98ad0f8437db02fc22cca93f08` changes the current button title to
  `Export Matrix`; the earlier `导出 Matrix` title is a superseded historical checkpoint.
- `1c9f8fc58ca72d21e020576d5aa611a307c335c3` leaves wrapped row heights unset for automatic
  fitting; fixed row height `15` is superseded as an output contract.
- Current primary/master HEAD:
  `1c9f8fc58ca72d21e020576d5aa611a307c335c3`.
- TASK_367A is complete/accepted; no product lane is active.

## Next Legal Role

Reviewer docs-only source-of-truth re-gate only. Product/test implementation, QA, integration,
remote push, worktree retirement, and new-lane activation are not actions in this reconciliation.
