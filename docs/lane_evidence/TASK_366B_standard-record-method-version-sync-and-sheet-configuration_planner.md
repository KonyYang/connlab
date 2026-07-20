# TASK_366B Planner Discovery Evidence

Date: 2026-07-20

Role: Planner

Lane: `standard-record-method-version-sync-and-sheet-configuration`

Status: `implementation authorized / pending Developer implementation`

Implementation authorization: TASK_366B frozen scope only.

## Current Phase / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- TASK_366A is the current HEAD and is Integrator accepted at
  `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- The board's older TASK_366A pending-Developer wording is governance lag; this Planner
  pass closes that lag and creates only a planned TASK_366B lane.
- The user explicitly requested Discovery/task/plan/evidence and a Reviewer plan gate,
  while forbidding implementation.
- Reviewer plan gate returned B1 on worksheet-name null/blank semantics. The Planner
  docs-only fix reconciled that contract.
- Reviewer plan re-gate passed; the user approved Developer planning-first; Developer
  docs-only planning-first completed. This reconciliation updates source-of-truth for
  Reviewer implementation-readiness only.
- Reviewer implementation-readiness passed, and the user explicitly approved TASK_366B
  product implementation. Final reconciliation authorizes only the frozen scope and
  does not itself modify product code.

## Confirmed By User

- Settings needs a manually editable Standard record Sheet input, default `认可标准`.
- The configured source may be `.xls` or `.xlsx` and must remain read-only.
- The source layout has row 1 title, row 2 headers, row 3+ data, and standard numbers in
  column B under `文 件 编 号`.
- Methods use a case-insensitive `364-\d{2}` core, and catalog revision must be parsed
  immediately after that core rather than from an arbitrary letter.
- Multi/no matches, normalization, downgrade/upgrade, row-state reset, preview/review,
  confirmation, audit, and no-write behavior must be deterministic.
- The attachment was inspected read-only outside this pass. It must not be reopened or
  modified here, and VBA must not run.

## Confirmed By Repository Evidence

- Git verifies the TASK_366A accepted commit exists and is an ancestor of/current HEAD.
  Integrator evidence records `74 passed`, py_compile/package checks, and temp-only COM
  smoke with unchanged hash/size/mtime.
- `ExternalResource`, ORM, repository, API, and frontend DTO currently persist only
  path/active/validation fields. There is no Sheet metadata field.
- Standard validation/read still expects English headers and regex sheet names; it
  cannot accept the confirmed Chinese directory structure.
- Both TASK_366A tabular gateways use the first non-empty row as the header. The title
  in row 1 therefore prevents current Standard read/validation.
- `.xlsx` dispatches to the ZIP/XML gateway and `.xls` to the hidden read-only COM
  gateway. The accepted COM path has bounded UsedRange and no-write lifecycle guards.
- Matrix draft rows persist `method`; confirmation copies it to immutable
  `ConfirmedMatrixRow.method`. Confirmed Test Record preview reads that method directly.
- No product runtime path named `ConfirmSpec` exists. TASK_360B is a separate LLCR/CR
  record workbook and is not the method authority.
- Matrix revision/session flows already provide editable draft, saved payload
  signature, stale conflict, Cancel, and Confirm Matrix behavior.
- The Standard record rows API has no production frontend consumer beyond its routes
  and tests, allowing its internal mapping to align with the real catalog while keeping
  the response shape compatible.

## Planner Decisions

- Map legacy ConfirmSpec Method synchronization to Matrix draft row Method, not to a
  generated workbook.
- Use a read-only preview plus a fingerprint-protected server apply to the editable
  draft; keep Confirm Matrix as the only publication gate.
- Persist Sheet name in an additive nullable External Resource column. `NULL` resolves
  to effective `认可标准` without backfill.
- Freeze worksheet-name input semantics:
  - omitted field preserves the existing stored value; for a new Standard row, store
    `NULL` and return effective `认可标准`;
  - explicit `null` resets Standard record to stored `NULL` and effective `认可标准`;
  - explicit whitespace-only input also resets Standard record to stored `NULL` and
    effective `认可标准`;
  - trimmed legal nonblank text persists as the independent worksheet setting;
  - invalid characters, control characters, over-31-character names, and any supplied
    `worksheet_name` for non-Standard resources are typed no-write failures.
- `ExternalResourceResponse.worksheet_name` returns the effective Standard value and
  `null` for non-Standard resources.
- Persist bounded sync source context on the Matrix draft, not the confirmed Matrix;
  confirmed authority already points to the source draft.
- Extend both Office tabular gateways with optional explicit header-row/column rules;
  defaults preserve TASK_366A behavior.
- Do not import catalog year into normal ConnLab Method text. Preserve an existing
  Matrix year and expose catalog year only as preview/audit metadata.
- Fail closed on distinct revision duplicates and downgrades. Duplicates with the same
  revision are safe after deterministic diagnostic selection.
- Keep the workflow in one serialized lane because Settings schema, Office layout,
  backend preview/apply, and Matrix UI share one contract and cannot be independently
  packaged without temporary incompatible states.

## Not Yet Confirmed

- Reviewer may challenge the choice to omit catalog year from proposed Method text.
  Repository examples support that choice (`EIA-364-18B`), and the plan freezes it so
  disagreement is a plan-gate finding rather than an implementation ambiguity.
- A future audit-history UI is not part of V1. The persisted draft context plus existing
  confirmed revision history is the frozen audit boundary.
- Automatic downgrade remains out of scope. Operators may use existing manual Matrix
  editing if a deliberate downgrade is required.

These items do not block a planned lane because each has an explicit conservative V1
decision and non-goal. They must not be silently broadened during implementation.

## Planning Risk

- Treating Test Record or TASK_360B as the authority would invert the accepted Matrix
  ownership model.
- Reusing first-nonempty-row behavior would keep the actual Chinese workbook invalid.
- Encoding Sheet name in the path would corrupt path ownership and picker behavior.
- First-match or loose letter scans could choose an arbitrary revision and repeat the
  legacy row-state contamination bug.
- Direct confirmed authority mutation would bypass Matrix revision history and stale
  protection.
- Broad edits to oversized composition files could absorb unrelated dirty work.

## Evidence Read

- `AGENTS.md`, Planner/parallel/orchestration/role protocols.
- `PRODUCT.md`, `DESIGN.md`, architecture and frontend architecture rules.
- `docs/task_board.md` and all TASK_366A task/plan/Planner/Developer/Reviewer/QA/
  Integrator/reconciliation evidence.
- External Resource domain/model/repository/service/routes/dependencies and Settings
  config/selectors/page/panel/client.
- TASK_366A XLSX/COM gateways, facade, lifecycle contracts, and focused tests.
- Matrix draft/session/revision/confirmed authority models, repositories, services,
  routes, frontend workspace/actions, and Test Record preview/generation projections.
- TASK_360B specialized workbook context. The real attachment and real DB were not
  accessed in this pass.

## Planned Source Of Truth

- Task: `tasks/TASK_366B_STANDARD_RECORD_METHOD_VERSION_SYNC_AND_SHEET_CONFIGURATION.md`
- Plan: `docs/task_366b_standard_record_method_version_sync_and_sheet_configuration_plan.md`
- Planner evidence: this file.
- Board: TASK_366A accepted closeout plus planned-only TASK_366B row.

## Definition Of Ready

Satisfied for Developer implementation pass. The plan has a concrete workflow,
authority chain, data/migration contract, deterministic parser, stale/no-write
behavior, exact future May Touch/locks, acceptance cases, validation, rollback, and
package isolation. Developer planning-first refined the physical schema shape,
field-presence sentinel, saved signature, method-only CAS, typed errors, and package
sequence; Reviewer readiness passed; user implementation approval is now recorded.

Implementation is authorized only for the frozen TASK_366B scope: worksheet-name
field-presence/reset/default behavior, additive migration, explicit `.xlsx`/COM Chinese
catalog layout, canonical saved signature, method-only root+row CAS, typed no-write
`400/404/409`, preview zero-write, selected apply to editable Matrix draft, existing
Confirm Matrix publication, focused bounded tests, and existing May Touch/locks.

## Validation Performed

- Read-only Git commit/ancestor and Integrator evidence verification.
- Read-only source search and UTF-8 file inspection.
- No real database, public-drive file, or attachment access.
- No product/test edit, VBA execution, stage, commit, or push.

## Next Legal Role

Developer implementation pass.
