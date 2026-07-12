# TASK_361F Production Compatibility Smoke - Operational QA Evidence

Date: 2026-07-13
Role: QA / Smoke Owner
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Result: `operational_smoke_blocked`

## Authorization And Boundary

User explicitly authorized a controlled production compatibility smoke against the existing SQLite database:

- Target DB: `D:\PythonProject\connlab\data\connlab.sqlite3`
- Allowed mutation: only TASK_361F-approved, idempotent, non-destructive canonical-index schema bootstrap during current application `init_db()` startup.
- Forbidden: business data writes, table rebuild/delete, data repair/delete, real workbook/LTR/public-drive file operation, TASK_361E resume, product source/test/board edits, commit/push.

QA followed this boundary. No product source, tests, or board files were modified. No real workbook/LTR/public-drive operations were attempted.

## Before Startup Sampling

Command scope: Python read-only metadata/count/index probe, plus file hash.

DB metadata before:

```text
path: D:\PythonProject\connlab\data\connlab.sqlite3
size: 43102208
mtime_utc: 1783824722.987148
sha256: 2468cc5766eb119855e104cb05653096e4469ac784d512a193a722ddf89a29b7
```

Authority business-row counts before:

```text
measurement_plan_roots: 0
measurement_plan_revisions: 0
measurement_plan_target_snapshots: 0
measurement_plan_family_snapshots: 0
measurement_plan_impacts: 0
measurement_plan_audits: 0
```

Canonical semantic indexes before:

```text
measurement_plan_revisions: []
measurement_plan_target_snapshots: []
measurement_plan_impacts: []
```

Candidate Matrix project lookup:

- Source: `confirmed_matrix_versions.project_id` only.
- Active confirmed Matrix project count: `13`.
- Selected project id for endpoint smoke: `1ee3f8389c2243b0b324247ae5555bd3`.
- No product/customer/requestor/test fields were queried for this selection.

## Current Application Startup Path

Command scope: current application `create_database_engine(Settings(...data/connlab.sqlite3...))` plus `init_db(engine)`.

Observed result:

```text
RuntimeError: Contact measurement plan authority schema is incompatible: measurement_plan_target_snapshots is missing required checks.
```

Interpretation:

- Startup failed before TASK_361F canonical index bootstrap could complete.
- This is a fail-closed non-index schema compatibility blocker, not the missing-index case TASK_361F was authorized to bootstrap.
- Because the existing authority business row counts are all `0`, this appears to be an empty authority-table schema-shape mismatch, but QA did not perform any repair.

## After Startup Sampling

DB metadata after:

```text
path: D:\PythonProject\connlab\data\connlab.sqlite3
size: 43102208
mtime_utc: 1783824722.987148
sha256: 2468cc5766eb119855e104cb05653096e4469ac784d512a193a722ddf89a29b7
```

Authority business-row counts after:

```text
measurement_plan_roots: 0
measurement_plan_revisions: 0
measurement_plan_target_snapshots: 0
measurement_plan_family_snapshots: 0
measurement_plan_impacts: 0
measurement_plan_audits: 0
```

Canonical semantic indexes after:

```text
measurement_plan_revisions: []
measurement_plan_target_snapshots: []
measurement_plan_impacts: []
```

Safety conclusion:

- File hash unchanged.
- Size unchanged.
- mtime unchanged.
- Authority business-row counts unchanged.
- No canonical index DDL was applied.
- No business data write occurred.

## Read-Only Schema Evidence

Read-only schema flag probe:

```text
measurement_plan_target_snapshots exists: true
has ck_measurement_plan_group_anchor_xor: false
has ck_measurement_plan_row_anchor_xor: false
has ck_measurement_plan_target_key_shape: false

measurement_plan_impacts exists: true
has ck_measurement_plan_impact_subject_shape: false
has ck_measurement_plan_impact_identity_shape: false
```

QA did not rebuild tables or inspect sensitive business fields.

## Endpoint Smoke

All endpoint probes used `TestClient(app, raise_server_exceptions=False)` and the current default application startup/dependency path. No write endpoints were executed.

### Matrix Editor Session

Endpoint:

```text
GET /api/projects/1ee3f8389c2243b0b324247ae5555bd3/matrix-editor/session
```

Result:

```text
HTTP 500
Body prefix: Internal Server Error
```

Conclusion: blocked. Matrix Editor session still returns 500 due to startup schema compatibility failure.

### Cancel Path

Endpoint considered:

```text
DELETE /api/projects/{project_id}/matrix-editor/session/draft
```

Execution: skipped.

Reason: the route is explicitly `discard_matrix_editor_session_draft` and calls the business write/delete service `discard_editor_draft(...)`. The user required no business writes; therefore QA did not execute Cancel against the real database. Because startup already fails, this path cannot be safely proven non-500 without a separate no-write harness or disposable fixture.

### Test Record Path

Write endpoint considered:

```text
POST /api/projects/{project_id}/matrix-editor/test-record-draft/generate
```

Execution: skipped.

Reason: the route writes a preview `.docx` under `data/generated_test_record_previews`; the user forbade real file operations/business side effects.

Safe read-only substitute:

```text
GET /api/projects/1ee3f8389c2243b0b324247ae5555bd3/confirmed-matrix/test-record-preview
```

Result:

```text
HTTP 500
Body prefix: Internal Server Error
```

Conclusion: blocked. A read-only Test Record preview path also fails through the same application startup schema blocker.

## Final Safety Recheck

Final DB metadata:

```text
size: 43102208
mtime_utc: 1783824722.987148
sha256: 2468cc5766eb119855e104cb05653096e4469ac784d512a193a722ddf89a29b7
```

Final authority business-row counts remained:

```text
measurement_plan_roots: 0
measurement_plan_revisions: 0
measurement_plan_target_snapshots: 0
measurement_plan_family_snapshots: 0
measurement_plan_impacts: 0
measurement_plan_audits: 0
```

## Operational Result

`Operational smoke: blocked`

Blocking finding:

```text
Existing data/connlab.sqlite3 fails current application init_db() before canonical index bootstrap:
Contact measurement plan authority schema is incompatible: measurement_plan_target_snapshots is missing required checks.
```

This means the requested production compatibility smoke does not pass:

- four canonical indexes are still absent;
- Matrix Editor session GET returns 500;
- read-only confirmed Test Record preview GET returns 500;
- Cancel and Matrix Editor Test Record generate were not executed because they are real write/file paths.

## Recommended Next Role

Recommended next role: `Planner / User decision`, then likely a separate Developer corrective lane if approved.

Reason:

- TASK_361F was accepted for semantic-index bootstrap and intentionally fail-closed on non-index schema incompatibility.
- The real DB issue is now proven to be a non-index CHECK-shape compatibility gap on empty authority tables.
- Repairing missing CHECK constraints in SQLite generally implies table rebuild/recreation or a governed compatibility strategy, which TASK_361F explicitly forbids.
- Do not route Integrator as ready based on this operational smoke.
- Do not resume TASK_361E.
