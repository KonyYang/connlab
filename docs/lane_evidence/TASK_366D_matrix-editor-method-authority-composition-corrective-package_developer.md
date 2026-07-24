# TASK_366D Developer Evidence

Date: 2026-07-25
Role: Developer
Status: `ready_for_review / developer_implementation_complete`
Task: `TASK_366D_MATRIX_EDITOR_METHOD_AUTHORITY_COMPOSITION_CORRECTIVE_PACKAGE`
Lane: `matrix-editor-method-authority-composition-corrective-package`
Implementation authorization: explicit User product/test approval after Reviewer readiness

## Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

This implementation pass is allowed because Reviewer passed implementation-readiness, the User
explicitly approved product/test implementation, and Planner reconciled the board, task, plan,
and evidence to `implementation_authorized_pending_developer_implementation`.

Authorization is limited to the exact six-line composition hunk in
`get_matrix_editor_session_service()` and the focused composition regression hunk. The
planning-first evidence below is retained as the historical baseline for this implementation.

## Required Reads

Read and applied:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- TASK_366D task and plan
- TASK_366D Planner and Reviewer evidence
- accepted TASK_366C composition, resolver, commit-service, and focused test code

## Planning Result

The implementation remains a two-hunk corrective package:

- `backend/api/dependencies.py`: exact `6/0` additions inside
  `get_matrix_editor_session_service()`;
- `tests/integration/test_matrix_import_method_authority_commit_api.py`: exact `29/1` import and
  focused composition regression.

The runtime graph is frozen:

```text
SQLAlchemy session
  -> one CachedStandardResourceStore(ExternalResourceRepository(session))
  -> MatrixImportMethodAuthorityResolver
       resource_store = same cache
       catalog_reader = ExternalExcelReadService(same cache)
  -> MatrixImportCommitService
       method_authority = resolver
       transaction_scope = session.begin_nested
  -> MatrixEditorSessionService
```

The cache makes the resolver and reader share one Standard resource fact. The correction adds no
fallback, provider reread, Method business logic, API/DTO, schema/database, persistence, or
frontend behavior. Public signatures remain unchanged.

## Baseline And Candidate Audit

- HEAD: `c2104e106bad81a827e49714fb6d84ef4b9c09dd`.
- origin/master: `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- `origin/master...HEAD`: `0 6`.
- TASK_366C `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1` is a HEAD ancestor.
- Index: empty.
- Worktree dirty entries observed: `54`; all unrelated residuals remain excluded.

Exact file facts:

| Path | HEAD | Current candidate |
|---|---|---|
| `backend/api/dependencies.py` | `2242` lines; SHA-256 `8d1cf82bf326d56d69414f3d266c35bbf8cd179186befbc9d39de08cefc1ff2e`; blob `b55cf48a7a9658864a4355eb04fafd2d9d75863f` | `2248` lines; SHA-256 `af4270423716e9b90925ae6a53435e4c8b65243d2f9fe8024f64824021273d27`; blob `236b32ec6559afe3a681749f5d3d93a3fbf168b8`; numstat `6/0` |
| `tests/integration/test_matrix_import_method_authority_commit_api.py` | `358` lines; SHA-256 `7cdf0fe3d727a0545569885e3774dcfece663189a06a3a6d6a344f50c5a31834`; blob `4dca5d1b3aaa1902c33d68ce5fab43738a7cce6c` | `386` lines; SHA-256 `b627c8ca8d988dd8678d7db1acd353f0657a9de3f89e111ca1b72373a1aec942`; blob `f6702ca8dbddf2b255c63463c08c289acc8b1c80`; numstat `29/1` |

Counts are UTF-8 physical lines including blanks. The oversized production module receives only
the reviewed composition exception. The test is below 500 lines.

## Future TDD And Implementation Order

After Planner reconciliation, Reviewer implementation-readiness, and explicit User
implementation approval:

1. Export accepted HEAD into a disposable source isolate without changing the current index.
2. Apply only the test hunk; run the exact node and capture missing `method_authority` as RED.
3. Apply only the six-line product hunk.
4. Rerun the exact node as GREEN.
5. Run the TASK_366C eight-module `29`-node gate and Matrix Editor session API `11`-node smoke.
6. Run pycompile, diff/trailing/physical-line/hash/numstat/hunk-whitelist/forbidden/staging/no-real
   checks.
7. Update implementation evidence and stop for Reviewer.

The test uses only pytest `tmp_path` and disposable SQLite. It does not invoke import/replace or
read an external workbook.

## Read-Only Validation

The existing candidate was inspected and executed without modifying product or test files:

- exact composition node -> `1 passed`;
- accepted TASK_366C eight-module gate -> `29 passed`;
- Matrix Editor session API module -> `11 passed`;
- candidate numstat -> exact `6/0` and `29/1`;
- candidate `git diff --check` -> passed with only existing LF/CRLF notices;
- staging -> empty.

This pass did not rerun the clean-HEAD RED in a disposable source isolate because implementation
and test application remain unauthorized. That RED/GREEN isolate is a mandatory later
implementation gate.

## Authorized Implementation Pass

The checked-out worktree already contained the exact frozen product and test candidates. Their
line counts, SHA-256 hashes, Git blobs, and numstat matched the reconciled authorization, so no
product or test byte rewrite was necessary. Developer adopted and validated only those existing
hunks.

### TDD Isolate

Developer exported accepted HEAD `c2104e106bad81a827e49714fb6d84ef4b9c09dd` into a disposable
source isolate under `tmp/`. The isolate used only pytest `tmp_path` SQLite databases.

1. Applied only the focused test patch.
2. Ran:
   `tests/integration/test_matrix_import_method_authority_commit_api.py::test_matrix_editor_session_composes_import_method_authority`.
3. RED reproduced as `1 failed`: the real nested composition raised
   `TypeError: MatrixImportCommitService.__init__() missing 1 required keyword-only argument:
   'method_authority'`.
4. Applied only the six-line product patch.
5. Reran the exact node: `1 passed`.

The normalized UTF-8 contents of both GREEN isolate files exactly equal the checked-out
candidate files. Raw hashes differ only in the disposable archive's LF representation versus
the checked-out Windows line-ending representation.

### Focused Validation

All commands ran against the disposable accepted-HEAD plus exact two-hunk candidate:

- exact composition node: `1 passed`;
- accepted TASK_366C eight-module gate: `29 passed`;
- complete Matrix Editor session API smoke: `11 passed`;
- `py -m py_compile backend/api/dependencies.py
  tests/integration/test_matrix_import_method_authority_commit_api.py`: passed.

The target function contains exactly:

- one `CachedStandardResourceStore(`;
- one `MatrixImportMethodAuthorityResolver(`;
- one `ExternalExcelReadService(resources)`;
- one `transaction_scope=session.begin_nested`.

It contains no null `method_authority` and no fallback token. TASK_366C remains a HEAD ancestor.

### Package And Safety Checks

- candidate physical lines including blanks: `2248` and `386`;
- candidate SHA-256:
  `af4270423716e9b90925ae6a53435e4c8b65243d2f9fe8024f64824021273d27` and
  `b627c8ca8d988dd8678d7db1acd353f0657a9de3f89e111ca1b72373a1aec942`;
- candidate Git blobs: `236b32ec6559afe3a681749f5d3d93a3fbf168b8` and
  `f6702ca8dbddf2b255c63463c08c289acc8b1c80`;
- exact numstat: product `6/0`, focused test `29/1`;
- zero-context diff contains only the frozen function import/node and composition hunks;
- isolate patch paths are exactly the two authorized product/test paths;
- `git diff --check`: passed;
- UTF-8 trailing-whitespace scan: clean;
- index name-status and numstat: empty;
- `data`, `dist_release`, and `frontend/dist` status scan: clean;
- no real database, public-drive file, attachment, Standard workbook, or generated business
  artifact was accessed;
- no stage, commit, or push was performed.

## Locks And Rollback

Locked:

- every other hunk in both mixed candidate files;
- accepted TASK_366C and Child 1/2/3 source;
- Matrix import/resolver/service/repository behavior;
- API/DTO/schema/database/frontend, seeds/manifest, Fee/parser/Summary UI/release residuals;
- real DB, public-drive files, attachments, Standard workbooks, generated artifacts;
- stage, commit, push, cleanup, restore, or deletion.

Rollback removes only the six product additions and the focused test import/node. There is no
schema or data rollback.

## Changed Files

The historical planning-first pass changed only:

- `docs/task_366d_matrix_editor_method_authority_composition_corrective_package_plan.md`
- this Developer evidence

The implementation pass updates this evidence. The exact authorized product/test candidates
were already present and matched the frozen hashes; Developer did not rewrite or absorb adjacent
dirty hunks.

## Result

Implementation blocker: none.

Status is `ready_for_review / developer_implementation_complete`.
Next legal role is Reviewer implementation gate. Do not route QA or Integrator before Reviewer.
