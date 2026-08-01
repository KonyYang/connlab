# TASK_368E Developer Evidence

Date: 2026-08-01

Role: Developer implementation

Lane: `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`

Base: `e226bf1e54db4de54eb2366e96895999ce54652d`

Implementation checkpoint: `9cd39e2dc5e8b50f23fd3e3202913a96019d4999`

Status: `ready_for_review`

## Authorization And Scope

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY`.
- Primary governance was verified at
  `5432cf3d52078d6e9075fa05cb784c67a44457d8`; the production gate returned
  `ALLOW_DISPATCH`, and TASK_368E held the sole WIP=1 execution token.
- The implementation stayed inside the approved 17 product/test paths. Task, plan,
  primary board, Confirm Matrix, TASK_366B Preview/Apply, persistence/schema, Office
  gateways, real resources, and all other governance paths were not changed.

## Implemented Behavior

- Initial Replace now returns a typed, zero-write `409` choice only for the five frozen
  Standard-version availability states: missing registration, inactive registration,
  missing file, explicitly classified file/OS unavailability, and unavailable Excel COM
  runtime. Integrity, format, workbook, worksheet, range, cleanup, and unknown failures
  remain fail-closed `422` responses.
- Explicit `preserve_imported_methods` rechecks current facts, retains every imported
  Method value and source/draft lineage, writes a `matrix-import-method-fallback:v1`
  context with stable fingerprints, returns `source_preserved`, nullable authority
  metadata, and the exact controlled warning. Existing configured synchronization and
  strict created/reused read-verification remain intact.
- Matrix Editor recognizes only the controlled action-required detail. The accessible
  choice dialog supports focus entry/return and Escape. `Choose file` reuses the desktop
  picker and existing resource list/save/validate APIs while preserving the configured
  worksheet; picker cancel writes nothing. `Skip for now` immediately retries the same
  Replace with the narrow preserve action, applies the returned editable draft, closes
  both dialogs, and renders the exact amber polite status.
- Settings now exposes the exact visible label, accessible name, and title
  `Standard version file path` without producing `path path`; `Standard record sheet`
  and all other resource rows retain their prior behavior.
- The TypeScript warning field is optional-and-nullable for old typed fixtures/callers;
  the backend response model always emits `warning=null` on configured success and the
  controlled warning object on fallback.

## TDD Evidence

- Backend unit RED: 10 expected failures before the typed action, classifier, fallback,
  nullable summary, and warning implementation; GREEN after implementation.
- Backend API RED: four expected `422` results instead of typed `409`/`201` before route
  and service wiring; GREEN after implementation.
- Frontend RED: Settings still rendered `Standard record Excel`, and the new dialog/hook/
  workspace modules or behavior were absent. The four focused files then passed after
  implementation.
- Additional executable coverage proves all five allowed availability states return
  `201 source_preserved` after explicit Skip, production missing-file preflight performs
  no catalog read, and a frontend `422` integrity failure exposes no Skip action.

## Final Validation

Passing deterministic checks:

- New TASK_368E backend unit/API tests: `21 passed`.
- Complete relevant backend compatibility set covering TASK_366B/C authority/parser,
  strict reuse, source persistence, group selection, Matrix session, and confirmed
  Matrix authority: `98 passed, 1 deselected`.
- TASK_368E Settings shell assertion: `1 passed`.
- Focused and compatibility Vitest set covering the three new Matrix fallback files,
  Settings, Standard Method versions Preview/Apply, and Matrix Editor:
  `8 files / 61 tests passed`.
- `npm run build`: passed (`tsc -b` and Vite); only the existing chunk-size advisory was
  emitted. The lane had no dependency directory, so validation used a disposable temp
  frontend mirror with a junction to the primary worktree's existing `node_modules`;
  no repository file or dependency lock was changed.
- `py -m py_compile` for all three changed backend modules: passed.
- `git diff --check`, exact May Touch comparison, forbidden Office/workbook-write scan,
  and primary HEAD/clean checks: passed.

Bounded physical line counts (UTF-8, including blank lines):

- `matrix_import_method_authority.py`: 499
- `matrix_import_commit_service.py`: 449
- `routes_matrix_import_commit.py`: 291
- TASK_368E backend unit/API tests: 288 / 250
- new dialog/hook product modules: 96 / 113
- new frontend tests: 269 / 73 / 98

No real operator database, Excel, PDF, DOCX, public-drive path, or confirmed Matrix was
read or written. Tests used disposable SQLite paths, fake catalog readers, mock browser
APIs, and in-memory source payloads only.

## Baseline-Only Regression Notes

- The full legacy `tests/unit/test_frontend_shell_files.py` module reports
  `134 passed, 28 failed`. Those failures are stale assertions outside TASK_368E's
  changed hunks; the exact TASK_368E Settings node passes. No unrelated assertion was
  weakened or edited.
- `test_confirm_first_authority_initializes_default_fee_authority` is also broken at the
  lane base: base `MatrixImportCommitResult` already requires `method_authority_sync`,
  while the base test fake omits it. The remaining relevant backend set passes with only
  that exact node deselected. Fixing either baseline issue is outside this task's May
  Touch and was not attempted.

## Checkpoint And Handoff

Implementation and bounded tests are complete at the checkpoint above. The next legal
role is Reviewer. Blocker: none for TASK_368E; the two documented baseline-only test
debts remain outside this lane.
