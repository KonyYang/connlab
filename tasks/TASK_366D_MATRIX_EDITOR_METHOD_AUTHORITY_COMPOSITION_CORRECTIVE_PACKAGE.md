# TASK_366D_MATRIX_EDITOR_METHOD_AUTHORITY_COMPOSITION_CORRECTIVE_PACKAGE

Status: complete / Integrator accepted
Lane: `matrix-editor-method-authority-composition-corrective-package`
Owner role: Integrator
Implementation authorization: completed after Reviewer and QA gates
Date: 2026-07-25

## Current Phase / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: this corrective lane, pending exact-hunk Developer implementation.
- Why allowed: Reviewer passed the plan gate, User approved Developer docs-only planning-first,
  Developer completed planning-first, Reviewer passed implementation-readiness, and the User
  explicitly approved product/test implementation.
- Product and test implementation are authorized only within the exact frozen two-hunk boundary.

## Goal

Package the smallest correction that makes the accepted Matrix Editor session composition supply
the required TASK_366C Method authority dependency. Reuse the accepted resource store, Excel read
service, resolver, and nested transaction composition without changing authority behavior,
business rules, API shape, persistence, or frontend behavior.

TASK_366C remains complete/accepted at
`0f51848f9fb64d326d5b95ddbee9cebb07fab9f1` and is a read-only upstream baseline. TASK_366D
does not amend, re-open, or re-label that accepted commit.

## Confirmed Repository Facts

1. Current HEAD is `c2104e106bad81a827e49714fb6d84ef4b9c09dd`; origin/master is
   `add69823668d7ac4bf18645c688ce367a8fe0d42`; HEAD is six commits ahead.
2. The staging index is empty.
3. `MatrixImportCommitService.__init__()` requires keyword-only `method_authority`; its
   `transaction_scope` remains optional but the accepted direct provider supplies
   `session.begin_nested`.
4. Clean HEAD's nested `get_matrix_editor_session_service()` constructs
   `MatrixImportCommitService` without `method_authority`, so construction raises the reproduced
   missing-keyword `TypeError`.
5. The current product candidate adds exactly six lines inside that nested composition:
   one shared `CachedStandardResourceStore`, one accepted
   `MatrixImportMethodAuthorityResolver(ExternalExcelReadService(resources))`, and
   `transaction_scope=session.begin_nested`.
6. `backend/api/dependencies.py` is an existing oversized composition module: clean HEAD is
   `2242` UTF-8 physical lines including blanks and the candidate is `2248`. This task grants
   only a narrow composition exception and adds no business logic.
7. The test candidate is exactly `29 additions / 1 deletion`: import formatting plus
   `test_matrix_editor_session_composes_import_method_authority`. The clean file is `358` lines
   and the candidate is `386`, below the Python hard limit.
8. TASK_366C Reviewer evidence independently recorded the focused gate as `29 passed` with this
   composition present. Child 2 evidence identified the missing nested dependency as external to
   Child 2, and Child 2 Integrator explicitly excluded `backend/api/dependencies.py`.

## Frozen Contract

- `get_matrix_editor_session_service()` must construct its nested
  `MatrixImportCommitService` with a required `MatrixImportMethodAuthorityResolver`.
- The resolver must use:
  - `CachedStandardResourceStore(ExternalResourceRepository(session))`;
  - `ExternalExcelReadService` backed by that exact same cached resource store;
  - `session.begin_nested` as the transaction scope.
- No fallback resolver, null authority, text inference, second resource-store instance, second
  authority provider read, or alternate transaction scope is permitted.
- The correction changes composition only. Accepted TASK_366C authority matching, replay,
  fingerprint, zero-write, and error behavior remain unchanged.

## Exact Future May Touch

### Product hunk

`backend/api/dependencies.py`, only inside `get_matrix_editor_session_service()`:

1. add `resources = CachedStandardResourceStore(ExternalResourceRepository(session))` after the
   existing store locals;
2. pass `method_authority=MatrixImportMethodAuthorityResolver(...)` to the nested
   `MatrixImportCommitService`;
3. pass `transaction_scope=session.begin_nested`.

The exact product delta is `6 additions / 0 deletions`. Whole-file staging is forbidden.

### Test hunk

`tests/integration/test_matrix_import_method_authority_commit_api.py`, only:

1. extend the existing dependency import to include `get_matrix_editor_session_service`;
2. add `test_matrix_editor_session_composes_import_method_authority`;
3. use pytest `tmp_path`, disposable SQLite initialization, and engine disposal;
4. assert construction succeeds and the nested commit service owns a
   `MatrixImportMethodAuthorityResolver`.

The exact test delta is `29 additions / 1 deletion`. Existing TASK_366C test nodes and fixtures
are locked. Whole-file staging is forbidden.

### Governance

- this task;
- `docs/task_366d_matrix_editor_method_authority_composition_corrective_package_plan.md`;
- `docs/lane_evidence/TASK_366D_matrix-editor-method-authority-composition-corrective-package_planner.md`;
- the exact TASK_366D board hunk.

## Must Not Touch / Locked Paths

- Every other hunk in `backend/api/dependencies.py`, including the accepted direct
  `get_matrix_import_commit_service()` provider.
- Every other import, fixture, helper, and test node in
  `tests/integration/test_matrix_import_method_authority_commit_api.py`.
- TASK_366C accepted product/tests/task/plan/evidence and commit.
- Matrix import/commit/resolver/domain/repository/service implementations.
- API routes/DTOs, schema/database, frontend/client, seeds/manifest, Fee Child 1/2/3, parser,
  Summary UI, release packaging, and all other dirty residuals.
- Real DB, public-drive files, attachments, Standard workbooks, generated artifacts.
- Stage, commit, push, remote publishing, cleanup, restore, or deletion.

## Validation Gate

All validation must use clean HEAD or an isolated index/worktree containing only the exact two
candidate hunks and approved governance.

1. Clean accepted HEAD plus the test hunk alone must reproduce construction failure:
   `MatrixImportCommitService.__init__() missing 1 required keyword-only argument:
   'method_authority'`.
2. Exact product plus test hunks must pass:
   `test_matrix_editor_session_composes_import_method_authority`.
3. Run the accepted eight-module TASK_366C import/Replace/replay/authority gate and reproduce
   `29 passed`.
4. Run `tests/integration/test_matrix_editor_session_api.py` against accepted HEAD plus this
   hunk. Any failure must be classified against accepted TASK_366C/Child 2 evidence; unrelated
   residuals cannot be absorbed.
5. Run `py_compile` on the exact product/test paths.
6. Verify exact numstat `6/0` and `29/1`, hunk whitelist, forbidden paths/content, UTF-8
   trailing whitespace, diff-check, staging/index isolation, and no-real-data access.

## Acceptance Criteria

- Matrix Editor session service construction no longer raises the missing
  `method_authority` TypeError.
- The nested service uses the accepted resolver/read-service/cached-store/nested-transaction
  composition exactly once.
- TASK_366C focused behavior remains unchanged and its accepted gate passes from an isolated
  candidate.
- No unrelated `dependencies.py` or test hunk enters the package.
- No real data/file access and no schema/API/frontend/business-rule change occurs.

## Rollback

Rollback removes only the six-line composition hunk and the exact regression import/test hunk.
There is no data migration or persistent-data rollback. Rollback intentionally restores the
clean-HEAD construction defect and is therefore suitable only for package reversal.

## Definition Of Ready / Stop Point

The user goal, accepted baseline, exact defect, two-hunk ownership, validation, rollback, and
non-goals are explicit. Reviewer plan and implementation-readiness gates passed; User approved
Developer planning-first and then explicitly approved product/test implementation.

Implementation and controlled packaging are complete. Do not activate a follow-up lane from this
closeout; the next action remains user- or Orchestrator-directed.

## Integrator Closeout

- Reviewer implementation gate: pass.
- QA gate: pass.
- Integrator gate: accepted.
- Package remains limited to the exact `6/0` nested composition hunk, the exact `29/1` focused
  regression hunk, and TASK_366D governance/evidence.
- Validation rerun at closeout: exact composition `1 passed`, TASK_366C focused gate `29 passed`,
  Matrix Editor session API `11 passed`, and exact-path `py_compile` passed.
- Remote push was not performed.
