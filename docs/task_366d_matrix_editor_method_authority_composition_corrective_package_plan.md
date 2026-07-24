# TASK_366D Matrix Editor Method Authority Composition Corrective Package Plan

Date: 2026-07-25
Status: complete / Integrator accepted
Task: `TASK_366D_MATRIX_EDITOR_METHOD_AUTHORITY_COMPOSITION_CORRECTIVE_PACKAGE`
Lane: `matrix-editor-method-authority-composition-corrective-package`
Implementation authorization: explicit User product/test approval after Reviewer readiness pass

## 1. Purpose

Restore accepted TASK_366C self-containment for the Matrix Editor session entry point. The direct
Matrix Import provider in accepted TASK_366C already composes the required Method authority; the
nested provider inside `get_matrix_editor_session_service()` does not. This lane packages only
that omitted composition and one focused regression.

## 2. Discovery Gate

### Confirmed by User

- Use an independent planned-only corrective/package lane.
- Treat TASK_366C as accepted and read-only.
- Candidate scope is one six-line composition hunk and one exact test hunk.
- Reuse accepted resolver, cached resource store, Excel read service, and nested transaction.
- Do not implement, stage, commit, push, access real data, or absorb other residuals.

### Confirmed by Repository

- HEAD: `c2104e106bad81a827e49714fb6d84ef4b9c09dd`.
- TASK_366C accepted commit:
  `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1`.
- HEAD nested composition omits required `method_authority`.
- `MatrixImportCommitService.__init__()` requires that keyword-only dependency.
- Candidate product diff: `backend/api/dependencies.py` `6/0`.
- Candidate test diff:
  `tests/integration/test_matrix_import_method_authority_commit_api.py` `29/1`.
- Blank-inclusive UTF-8 line counts:
  - dependencies: HEAD `2242`, candidate `2248`;
  - focused test: HEAD `358`, candidate `386`.
- TASK_366C Reviewer recorded `29 passed` with the corrective composition.
- Child 2 Reviewer classified the missing composition as external TASK_366C ownership; Child 2
  Integrator excluded `dependencies.py`.

### Planner Inference

- The candidate is self-contained if and only if the exact product and exact regression hunks
  travel together.
- No new API/data/business decision is needed.
- The existing oversized composition file needs a Reviewer-approved narrow exception because a
  helper split would increase scope without changing ownership or reducing business coupling.

### Planning-First Gate Update

- Reviewer passed the planned-only plan gate.
- The User explicitly approved Developer planning-first.
- Product/test implementation, package commit, and remote push remain unauthorized.

## 3. Design

Within `get_matrix_editor_session_service()`:

1. construct one `CachedStandardResourceStore` from the current SQLAlchemy session;
2. inject a `MatrixImportMethodAuthorityResolver` using that store both directly and through
   `ExternalExcelReadService`;
3. inject `session.begin_nested` into the nested commit service.

The service graph mirrors the accepted direct `get_matrix_import_commit_service()` composition.
The change is dependency wiring only and must not add branching, fallback, parsing, authority
selection, or persistence behavior to `dependencies.py`.

## 4. Exact Package Boundary

| Path | Allowed hunk | Budget |
|---|---|---:|
| `backend/api/dependencies.py` | six additions only in `get_matrix_editor_session_service()` | HEAD `2242` to candidate `2248`; narrow oversized composition exception |
| `tests/integration/test_matrix_import_method_authority_commit_api.py` | import expansion plus `test_matrix_editor_session_composes_import_method_authority` only | `29/1`; final `386 < 500` |
| TASK_366D governance files | task, plan, Planner evidence, exact board row/status | docs only |

No whole-file staging is allowed for either mixed candidate path.

## 5. Error And Safety Contract

- Missing `method_authority` at composition is a deterministic startup/use-path TypeError, not a
  recoverable runtime state.
- Do not add a default/null resolver or fallback path to suppress the error.
- The resolver retains accepted source validation and no-fallback semantics.
- The same cached store prevents divergent resource snapshots inside one authority resolution.
- `session.begin_nested` preserves accepted transaction/savepoint behavior.
- No new exception mapping, status, DTO, route, database, or frontend behavior is introduced.

## 6. Test Plan

### Clean-HEAD proof

Use a detached clean HEAD or isolated index. Apply only the exact regression hunk. The new test
must fail at nested `MatrixImportCommitService` construction with the missing required
`method_authority` keyword. Do not modify clean HEAD to manufacture the failure.

### Candidate proof

Apply only the exact six-line product hunk plus exact regression hunk:

```text
py -m pytest tests/integration/test_matrix_import_method_authority_commit_api.py::test_matrix_editor_session_composes_import_method_authority -q
```

### TASK_366C accepted focused gate

```text
py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_matrix_import_method_authority.py tests/integration/test_matrix_import_method_authority_commit_api.py tests/integration/test_matrix_import_group_selection_commit_api.py tests/integration/test_project_test_plan_source_matrix_import_persistence_api.py tests/unit/test_standard_method_version_parser.py tests/unit/test_matrix_method_version_sync_service.py tests/integration/test_matrix_method_version_sync_api.py -q
```

Expected accepted baseline result with the exact candidate: `29 passed`.

### Matrix Editor composition smoke

```text
py -m pytest tests/integration/test_matrix_editor_session_api.py -q
```

Run from the same isolate. Accepted Child 2 closed the later DTO/fixture failures. If a failure
still appears, classify it against current accepted evidence and stop; do not widen TASK_366D.

### Static/package checks

- `py_compile` exact product/test paths;
- `git diff --check`;
- UTF-8 trailing whitespace;
- blank-inclusive physical line counts;
- exact `6/0` and `29/1` numstat;
- hunk whitelist and forbidden path/content scan;
- isolated index/worktree and staging-empty verification;
- no real DB/file/workbook/generated-artifact access.

## 7. Package Isolation

The working tree contains many unrelated tracked and untracked residuals. Review, QA, and
Integrator must reconstruct TASK_366D from accepted HEAD using only the exact two hunks and
governance. They may not stage either mixed file wholesale.

Explicit exclusions include Fee Child 1/2/3, the completed Fee umbrella, TASK_366C accepted
source, parser/Summary UI/Release work, frontend tests, old Fee/parser tests, schema/database,
seeds/manifest, historical governance residuals, and every other dirty path.

## 8. Risks

- Whole-file staging would absorb unrelated residuals.
- Adding a permissive constructor default would hide the defect and weaken no-fallback behavior.
- Creating two resource stores could permit inconsistent authority snapshots.
- Omitting `session.begin_nested` would diverge from accepted transactional composition.
- Expanding the test into route/business assertions would re-open TASK_366C.

## 9. Rollback

Remove only the exact product and regression hunks. No schema or data rollback exists. The
accepted TASK_366C commit remains unchanged.

## 10. Gate Sequence

1. Reviewer plan gate: complete.
2. User approval for Developer planning-first: complete.
3. Developer docs-only planning-first: complete.
4. Planner source-of-truth reconciliation: complete.
5. Reviewer implementation-readiness: complete.
6. Explicit User product/test authorization: complete.
7. Planner final authorization reconciliation: complete.
8. Developer exact-hunk implementation, then Reviewer, QA, and Integrator gates.

Historical stop: Developer exact-hunk implementation. This is superseded by the completed
Developer, Reviewer, QA, and Integrator gates.

## 12. Integrator Closeout

- Developer implementation: complete.
- Reviewer implementation gate: pass.
- QA gate: pass.
- Integrator packaging/readiness: accepted.
- Closeout validation reran the exact composition node (`1 passed`), the declared TASK_366C gate
  (`29 passed`), Matrix Editor session API tests (`11 passed`), and exact-path `py_compile`.
- The local controlled commit contains only the frozen two-hunk product/test correction and
  TASK_366D governance/evidence. Remote push is intentionally not performed.

## 11. Developer Planning-First Refinement

Historical planning-first checkpoint: Reviewer passed the planned-only gate and the User
authorized Developer planning-first only. Product and test implementation were unauthorized at
that checkpoint. This statement is superseded by the later Reviewer readiness pass and explicit
User product/test implementation approval recorded in Section 13.

### 11.1 Current Accepted Baseline And Candidate Facts

- Checked-out HEAD is `c2104e106bad81a827e49714fb6d84ef4b9c09dd`.
- `origin/master` is `add69823668d7ac4bf18645c688ce367a8fe0d42`; rev-list is `0 6`, so
  HEAD is six commits ahead and not behind.
- TASK_366C `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1` is a HEAD ancestor.
- The current index is empty.
- The worktree already contains the two proposed candidate hunks. They remain external dirty
  residuals during this docs-only pass and are not implementation performed by Developer.

Exact file facts:

| Path | HEAD lines / SHA-256 / blob | Worktree lines / SHA-256 / blob | Numstat |
|---|---|---|---:|
| `backend/api/dependencies.py` | `2242` / `8d1cf82bf326d56d69414f3d266c35bbf8cd179186befbc9d39de08cefc1ff2e` / `b55cf48a7a9658864a4355eb04fafd2d9d75863f` | `2248` / `af4270423716e9b90925ae6a53435e4c8b65243d2f9fe8024f64824021273d27` / `236b32ec6559afe3a681749f5d3d93a3fbf168b8` | `6/0` |
| `tests/integration/test_matrix_import_method_authority_commit_api.py` | `358` / `7cdf0fe3d727a0545569885e3774dcfece663189a06a3a6d6a344f50c5a31834` / `4dca5d1b3aaa1902c33d68ce5fab43738a7cce6c` | `386` / `b627c8ca8d988dd8678d7db1acd353f0657a9de3f89e111ca1b72373a1aec942` / `f6702ca8dbddf2b255c63463c08c289acc8b1c80` | `29/1` |

Line counts use `(Get-Content <path> -Encoding UTF8).Count`, including blank lines. The test
remains below the Python hard limit. `dependencies.py` receives only the already-reviewed
six-line composition exception; no refactor or adjacent cleanup is authorized.

### 11.2 Exact Runtime Graph And Interfaces

No public signature changes:

```text
get_matrix_editor_session_service(session, settings) -> MatrixEditorSessionService
MatrixImportCommitService(..., method_authority, transaction_scope)
```

The future hunk must:

1. create exactly one request-scoped
   `CachedStandardResourceStore(ExternalResourceRepository(session))`;
2. pass that same object as `MatrixImportMethodAuthorityResolver.resource_store`;
3. construct `ExternalExcelReadService` with that same object as its resource store;
4. pass the resolver as the required `method_authority`;
5. pass the uncalled `session.begin_nested` callable as `transaction_scope`.

`MatrixImportMethodAuthorityResolver.resolve()` first asks the cache for the active Standard
resource and then invokes the reader. The reader uses the same cache, so the underlying
repository supplies one Standard resource fact even though both collaborators request it. This
is the accepted single-source behavior, not a second authority read. Service construction itself
does not read a workbook or resource row.

Inputs remain the current SQLAlchemy session and Settings dependency. The output remains the
same `MatrixEditorSessionService` graph. There is no DTO, API response, database shape,
persistence, Method decision, fingerprint, replay, or frontend change.

### 11.3 File-Level Implementation Order

Future implementation, only after Planner reconciliation, Reviewer implementation-readiness,
and explicit User product/test approval:

1. Materialize a disposable accepted-HEAD source isolate without changing the current index.
2. Apply only the focused test import/test hunk to that isolate and run the exact node. Capture
   the required missing-`method_authority` TypeError as RED.
3. Apply only the six additions anchored inside
   `get_matrix_editor_session_service()`:
   - one `resources` local after the existing stores;
   - resolver/read-service injection in the nested `MatrixImportCommitService`;
   - `transaction_scope=session.begin_nested`.
4. Rerun the exact node as GREEN.
5. Run the eight-module TASK_366C gate and the full 11-node Matrix Editor session API module.
6. Run static/package checks against an isolate containing only these two hunks.
7. Update Developer implementation evidence and stop for Reviewer; do not stage either mixed
   file wholesale.

The disposable accepted-HEAD isolate should be created from `git archive HEAD` or an equivalent
read-only HEAD export under a temporary directory. It must not use the current index, operator
configuration, real DB, Standard workbook, public drive, or generated business artifacts.

### 11.4 Focused Test Ownership

The only future test addition is
`test_matrix_editor_session_composes_import_method_authority`. It may:

- create Settings rooted entirely under pytest `tmp_path`;
- initialize disposable SQLite;
- call the real `get_matrix_editor_session_service`;
- assert that the nested commit service owns a
  `MatrixImportMethodAuthorityResolver`;
- dispose the temporary engine.

It must not call import/replace, read a workbook, assert private business decisions, modify an
existing test node, or weaken no-authority behavior. The accepted TASK_366C test nodes remain
read-only regressions.

### 11.5 Validation And Package Isolation

Future implementation commands remain:

- exact composition node: expected `1 passed`;
- accepted eight-module TASK_366C gate: expected `29 passed`;
- `tests/integration/test_matrix_editor_session_api.py`: expected `11 passed`;
- `py -m py_compile backend/api/dependencies.py
  tests/integration/test_matrix_import_method_authority_commit_api.py`;
- exact diff-check, UTF-8 trailing, physical line count, SHA/blob/numstat, hunk whitelist,
  forbidden-content/path, staging-empty, and no-real-data checks.

Package reconstruction must start from accepted HEAD and use the two exact hunks. Whitelist:

```text
backend/api/dependencies.py
tests/integration/test_matrix_import_method_authority_commit_api.py
TASK_366D governance explicitly authorized by the later gate
```

Forbidden content includes a default/null resolver, a second
`CachedStandardResourceStore`, direct workbook access, alternate transaction ownership, route or
DTO changes, schema/database changes, and any fallback. Every other dirty path remains excluded.

### 11.6 Rollback And Stop

Rollback removes exactly the six product additions and the focused test import/node. It has no
data or schema action. This planning-first pass changed docs only.

Historical planning-first stop: Reviewer implementation-readiness gate. This stop is superseded
by the final authorization reconciliation in Section 13.

## 12. Source-Of-Truth Reconciliation

Reviewer passed the planned-only plan gate. User explicitly approved Developer docs-only
planning-first, and Developer completed that pass without changing product or tests. The exact
two-hunk contract, accepted-HEAD RED/GREEN sequence, one shared cached store, resolver/reader
composition, `session.begin_nested`, hashes, line counts, numstat, rollback, and package
isolation remain unchanged.

This readiness-only status is superseded by the final authorization reconciliation below.

## 13. Final Authorization Reconciliation

Reviewer passed the implementation-readiness gate. The User then explicitly approved product
and test implementation for TASK_366D. Current status is implementation authorized / pending
Developer implementation.

Authorization is limited to the exact `backend/api/dependencies.py` `6/0` composition hunk and
the exact focused composition regression hunk within the current `29/1` mixed test diff.
Whole-file staging, adjacent residuals, fallback, a second authority read, and business/API/
schema/frontend/database changes remain forbidden. Stage, commit, push, and real-data access
remain outside this Planner pass.
