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

---

# TASK_361F/G Production Compatibility Smoke - Corrective Operational Re-run

Date: 2026-07-13
Role: QA / Smoke Owner
Result: `operational_smoke_pass`

## Authorization And Safety Boundary

The user explicitly authorized this corrective run against
`D:\PythonProject\connlab\data\connlab.sqlite3` after TASK_361F/G acceptance.

- Allowed real-library mutation: current-HEAD `init_db()` only, limited to the accepted idempotent authority schema bootstrap.
- Not executed: any business INSERT/UPDATE/DELETE, Cancel/Delete, Matrix confirm, Fee update, Test Record generate, workbook generate/download, LTR/public-drive operation, or real Office file operation.
- No product source, test, or board file was changed. This evidence update is the only tracked-file change made by QA.

## Controlled Backup And Baseline

Before startup, QA opened the source database in SQLite `mode=ro` and used SQLite's
online backup API to create a contained copy:

```text
source: D:\PythonProject\connlab\data\connlab.sqlite3
backup: D:\PythonProject\connlab\tmp\task_361fg_operational_smoke\connlab-prebootstrap-20260712T222440Z.sqlite3
source pre-bootstrap sha256: 670f8b1bdb4fee7c2b27b79c6216ce2f3c9b94bedd800666db423da39532b691
backup sha256: b7f254c60d00b15e1ea6b90cb830a574eb2b5bcc7f1fe6ba304655bb1241b76b
source/backup size: 43143168 bytes
```

The online backup has a different physical SHA-256, so QA did not treat byte identity
as the backup criterion. It was retained as a separately hashed, SQLite-readable
pre-bootstrap snapshot. The subsequent logical schema comparison is exact.

Business-row counts before startup:

```text
measurement_plan_roots: 0
measurement_plan_revisions: 0
measurement_plan_target_snapshots: 0
measurement_plan_family_snapshots: 0
measurement_plan_impacts: 0
measurement_plan_audits: 0
projects: 88
confirmed_matrix_versions: 103
confirmed_matrix_groups: 914
confirmed_matrix_rows: 2202
project_matrix_draft_records: 267
```

## Current-HEAD Bootstrap And Idempotency

Executed current application startup boundary twice:

```powershell
create_database_engine(Settings.load())
init_db(engine)
```

Both calls returned successfully. Captured stdout/stderr were empty. The authority
schema validation completed without `authority_corrupt`, schema compatibility, or
traceback output.

The accepted semantic-index contract is satisfied by:

```text
uq_measurement_plan_confirmed_per_root
uq_measurement_plan_editable_per_root
sqlite_autoindex_measurement_plan_target_snapshots_2
sqlite_autoindex_measurement_plan_impacts_2
```

The latter two are the pre-existing SQLite `UNIQUE` constraint indexes with the exact
accepted `(measurement_plan_revision_id, stable_target_key)` and
`(editable_revision_id, impact_identity_key)` semantics. The migration accepts these
as equivalent semantic indexes and did not create redundant named indexes.

All four canonical TASK_361G compatibility guards are present and stable:

```text
trg_cmp_target_checks_insert_v1
trg_cmp_target_checks_update_v1
trg_cmp_impact_checks_insert_v1
trg_cmp_impact_checks_update_v1
```

Safety verification:

- All listed authority/core business-row counts were unchanged before, after the first startup, after the second startup, and after API smoke.
- `PRAGMA integrity_check` returned `ok` throughout.
- Pre-bootstrap backup and final live `sqlite_master` have the same 130 logical schema objects and the same `sqlite_master` digest: `f8f50fc998362d67b3dcead8da816c6e5a74ed224748467e6b2e2924f9f75ba9`.
- The logical schema definitions, canonical object SQL digests, page count, and freelist count were stable on the second `init_db()` invocation.
- The live database raw SHA-256 and mtime changed across startup/API invocation despite the stable logical schema and row counts. QA records this fact rather than claiming byte stability; it is consistent with SQLite header/change-counter activity during the authorized application startup boundary. No business-row or logical-schema difference was observed.

## Read-Only Existing-Project Smoke

Selected one existing active Confirmed Matrix project by identifier only; no customer,
requestor, or test-content fields were collected. The project identifier is redacted
to suffix `68ff900f` below. All requests were made through
`TestClient(app, raise_server_exceptions=False)` using current dependencies and the
real configured database.

| Read-only path | HTTP result | Observed safe summary |
| --- | --- | --- |
| `GET /matrix-editor/session` | 200 | `draft_status: missing` |
| `GET /confirmed-matrix/test-record-preview` | 200 | `preview_status: ready` |
| `GET /confirmed-matrix/fee-draft` | 200 | `draft_status: needs_review` |
| `POST /confirmed-matrix/llcr-cr-record-workbook/preview` | 200 | no-write preview, `status: empty`, `row_count: 0` |

The TASK_360B preview endpoint is a no-write projection; Generate and Download were
not called. No smoke endpoint returned 500. TestClient captured no stdout/stderr
traceback. The only log file found under `logs/` was an older LTR error log last
modified before this run; it contained no `schema compatibility` or
`authority_corrupt` entry from this smoke.

`data/connlab.sqlite3` is ignored by Git (`.gitignore:52`). QA did not introduce any
product-source change.

## Operational Conclusion

`Operational smoke: pass`

TASK_361F/G compatibility bootstrap starts successfully against the authorized real
database, preserves all sampled business-row counts, retains the exact logical schema
from the controlled pre-bootstrap backup, and no longer causes Matrix session,
read-only Test Record preview, Fee confirmed-consumer draft, or TASK_360B formal
workbook preview to return 500.

Residual limitation: this database currently has no Measurement Plan authority rows,
so live complete/partial/corrupt plan-consumer scenarios remain covered by the
accepted disposable-fixture suites rather than this operational smoke. No business
write was used to manufacture such data.
