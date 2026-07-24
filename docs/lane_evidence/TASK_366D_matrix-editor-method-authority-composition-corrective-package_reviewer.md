# TASK_366D Reviewer Plan Evidence

Date: 2026-07-24
Role: Reviewer
Status: `reviewer_plan_pass`
Task: `TASK_366D_MATRIX_EDITOR_METHOD_AUTHORITY_COMPOSITION_CORRECTIVE_PACKAGE`
Lane: `matrix-editor-method-authority-composition-corrective-package`

## Gate Result

`reviewer_pass` for the planned-only plan gate. The current board makes
TASK_366D the active planned lane and permits this review only; product and
test implementation remain unauthorized.

## Reviewed Facts

- Accepted TASK_366C commit `0f51848f9fb64d326d5b95ddbee9cebb07fab9f1` and
  current Child 3 HEAD `c2104e106bad81a827e49714fb6d84ef4b9c09dd` are both
  ancestors of the checked-out HEAD.
- The accepted direct `get_matrix_import_commit_service()` composition creates
  one `CachedStandardResourceStore`, supplies it to both
  `MatrixImportMethodAuthorityResolver` and `ExternalExcelReadService`, and
  passes `session.begin_nested`.
- The proposed nested Matrix Editor composition mirrors precisely that wiring:
  its six-addition hunk introduces the one shared store, required resolver,
  reader, and nested transaction scope. It adds no fallback, second provider
  read, route/API/schema/database/frontend behavior, or business rule.
- `MatrixImportCommitService` still declares `method_authority` as a required
  keyword-only constructor argument, so the clean-HEAD defect cannot be
  silently hidden by a default resolver.
- The exact focused test hunk is limited to its import expansion and
  `test_matrix_editor_session_composes_import_method_authority`; it constructs
  the real dependency graph with temporary SQLite and proves the nested commit
  service receives a `MatrixImportMethodAuthorityResolver`.

## Scope And Package Isolation

- Candidate product numstat is exactly `backend/api/dependencies.py` `6/0`;
  candidate test numstat is exactly
  `tests/integration/test_matrix_import_method_authority_commit_api.py` `29/1`.
- Blank-inclusive UTF-8 line counts are `2248` for the pre-existing oversized
  composition root and `386` for the focused test. The former is acceptable
  only as the declared narrow wiring exception; neither mixed file may be
  whole-file staged.
- Diff and path inspection found no allowed hunk outside those two files.
  Fee Child 1/2/3, TASK_366C accepted source, frontend, API contracts,
  schema/database, rules, real data/files, and all other dirty residuals stay
  excluded.

## Independent Validation

- Exact composition regression:
  `test_matrix_editor_session_composes_import_method_authority` -> `1 passed`.
- Declared TASK_366C focused gate -> `29 passed`.
- `py_compile` of the exact product and test paths passed.
- `git diff --check` and UTF-8 trailing checks passed; only existing LF/CRLF
  notices were emitted. Staging is empty.

## Next Legal Role

User approval for Developer planning-first. Do not route Developer
implementation, QA, or Integrator from this planned-only gate.

## Implementation-Readiness Gate

Date: 2026-07-25

### Result

`reviewer_implementation_readiness_pass`.

### Readiness Verified

- Board, task, plan, Planner, Developer, reconciliation, and prior Reviewer
  evidence consistently place TASK_366D at implementation-readiness only:
  the user approved Developer docs-only planning-first, but product/test
  implementation remains unauthorized.
- The actual candidate is still the frozen two-hunk package: dependencies
  `6/0` and focused regression `29/1`. Checked-out line/hash facts match the
  reconciled values: dependencies `2248`,
  `AF4270423716E9B90925AE6A53435E4C8B65243D2F9FE8024F64824021273D27`; test
  `386`, `B627C8CA8D988DD8678D7DB1ACD353F0657A9DE3F89E111CA1B72373A1AEC942`.
- The nested session composition uses one request-local
  `CachedStandardResourceStore` for both the resolver and Excel reader and
  supplies the required resolver plus `session.begin_nested`. It preserves the
  accepted direct Import Matrix composition, has no default/null authority,
  fallback, second authority read, or changed publication/authority path.
- The focused disposable regression constructs the real Matrix Editor service
  graph and fails on the clean baseline's required constructor omission. The
  later Developer implementation must retain the stated clean-HEAD RED before
  applying only this hunk; no production/test work was performed in this
  readiness gate.
- The oversized composition root exception remains narrow and mechanically
  reviewable. Both mixed files require hunk-level reconstruction/staging;
  no adjacent residual is admitted.

### Independent Validation

- Exact composition regression: `1 passed`.
- Declared TASK_366C eight-module focused gate: `29 passed`.
- Exact-path `py_compile`, diff-check, and UTF-8 trailing checks passed;
  staging remains empty. Existing unrelated dirty paths were observed and left
  untouched.

## Next Legal Role

User product/test implementation approval plus Planner final
source-of-truth reconciliation. Do not route Developer implementation, QA, or
Integrator directly.

## Implementation Gate

Date: 2026-07-25

### Result

`reviewer_pass`.

### Implementation Review

- The candidate is self-contained against accepted HEAD: the former nested
  Matrix Editor composition constructed `MatrixImportCommitService` without
  its required keyword-only `method_authority`, while the direct accepted
  Import Matrix composition supplied the resolver and transaction scope.
- The only product hunk exactly mirrors that accepted wiring. Inside
  `get_matrix_editor_session_service()` there is one
  `CachedStandardResourceStore`, one resolver using that same store, one
  `ExternalExcelReadService(resources)`, and one
  `transaction_scope=session.begin_nested`.
- This preserves the resolver's one-resource-snapshot behavior and existing
  commit-service preflight/persist boundary. No permissive default, fallback,
  second authority read, method-rule change, API/DTO, persistence, schema, or
  frontend behavior was introduced.
- The focused disposable regression uses the real dependency composition and
  verifies the nested commit service receives the resolver. Developer evidence
  separately records the clean accepted-HEAD RED as the expected missing
  keyword-only `TypeError`, followed by the exact two-hunk GREEN.
- Isolation remains exact: `backend/api/dependencies.py` is `6/0` and the
  focused integration test is `29/1`. The oversized composition root is still
  authorized solely for this narrow hunk; neither mixed file may be staged as
  a whole file.

### Independent Validation

- Exact composition regression: `1 passed`.
- TASK_366C declared focused gate: `29 passed`.
- Matrix Editor session API smoke: `11 passed`.
- Exact-path `py_compile`, diff-check, and UTF-8 trailing checks passed;
  staging remains empty. Only existing LF/CRLF notices were emitted.

## Next Legal Role

QA gate for `TASK_366D_MATRIX_EDITOR_METHOD_AUTHORITY_COMPOSITION_CORRECTIVE_PACKAGE`.
Do not route Integrator directly; all external dirty residuals remain excluded.
