# TASK_363D QA Evidence: Fee Pricing Draft Prior Defaults Attestation

Date: 2026-07-19

Role: QA / Smoke Owner

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Task: `TASK_363D_FEE_PRICING_DRAFT_PRIOR_DEFAULTS_ATTESTATION`

Lane: `fee-pricing-draft-prior-defaults-attestation`

Gate result: `qa_pass`

## Environment And Safety Boundary

- Every pytest database and API fixture was contained in
  `tmp\\task_363d_qa*` via `--basetemp`.
- No real `data/connlab.sqlite3`, project folder, workbook, public-drive path, output
  artifact, or user data was opened or changed.
- No product/test code was changed by QA. The staging index remained empty.
- TASK_363C remains blocked; QA did not release, resume, or package that lane.

## Disposable Functional Validation

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363d_qa_bounded tests\unit\test_fee_pricing_draft_prior_defaults_attestation.py tests\unit\test_fee_pricing_draft_automatic_build_safety.py tests\unit\test_fee_rule_transition_safe_rebase_measurement_plan.py tests\integration\test_fee_pricing_draft_measurement_plan_rebase_attestation.py -q
```

Actual result: `27 passed in 2.72s`.

This covers the private single-authority build/no-second-provider-read boundary,
pre-flattening row safety, canonical automatic-default attestation codec and
fingerprints, malformed/unsafe/missing attestation fail-closed behavior, changed
Measurement Plan reviewed rebase, manual CR Base Fee non-blocking, V1/unattested V2
compatibility, CAS conflict/no-overwrite, reload, and `current_v2` sequencing.

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363d_qa_v2 tests\unit\test_fee_evaluation_pricing_draft_v2_rebase.py tests\unit\test_fee_evaluation_pricing_draft_persistence_service.py tests\integration\test_confirmed_matrix_fee_evaluation_export_api.py -q
```

Actual result: `23 passed in 5.01s`.

The V2 persistence/rebase/export boundary remained green, including server-side
currentness and consumer protection.

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363d_qa tests\unit\test_fee_pricing_draft_prior_defaults_attestation.py tests\unit\test_fee_pricing_draft_automatic_build_safety.py tests\unit\test_fee_rule_transition_safe_rebase_measurement_plan.py tests\integration\test_fee_pricing_draft_measurement_plan_rebase_attestation.py tests\unit\test_fee_evaluation_pricing_draft_v2_rebase.py tests\unit\test_fee_evaluation_pricing_draft_persistence_service.py tests\integration\test_confirmed_matrix_fee_evaluation_export_api.py tests\unit\test_confirmed_matrix_fee_draft_service.py tests\unit\test_fee_default_fill.py tests\integration\test_fee_evaluation_pricing_draft_compatibility_api.py -q
```

Actual result: `154 passed in 6.82s`.

The combined regression confirms unchanged mechanical split/default-fill behavior and
existing Confirmed Fee, compatibility API, and export boundaries alongside TASK_363D.

## Attestation Findings

- `build_draft()` delegates to one private authority build; automatic defaults, ordered
  row identities, captured Matrix/rule/Measurement Plan/Point Profile facts,
  pre-flattening safety, and source context derive from that same result.
- The additive server-owned `fee-automatic-defaults:v1` payload object binds automatic
  values, defaults/identity/safety/source-context fingerprints, row-safety objects,
  and the enclosing generation. Payload/token validation covers that canonical data.
- Attestation failures such as unsafe or missing rows, duplicate/mismatched identities,
  malformed fingerprinted payloads, changed non-Measurement-Plan lineage, invalid
  quantity/diagnostic states, stale CAS, and unattested changed V2 source remain typed
  blocked/conflict with no write.
- A safe changed Measurement Plan path refreshes server-derived CR Units/Testing Fee
  only after reviewed save; proven manual fields remain preserved. No Fee-side editing
  authority was introduced.

## Static, Scope, And Package Checks

```powershell
py -m py_compile <nine TASK_363D candidate application modules>
git diff --check -- <tracked TASK_363D candidate modules>
Select-String -Pattern '[ \t]+$' <candidate modules/tests>
git diff --cached --name-only
git status --short -- data
```

- Compilation passed. Candidate diff and trailing-whitespace scans found no defect;
  only established LF/CRLF normalization notices were emitted.
- Candidate physical UTF-8 lines are all below 500: build result `22`, build support
  `39`, core Fee service `450`, V2 contract `219`, attestation `221`, automatic build
  `184`, persistence `447`, authority context `161`, safe rebase `241`; bounded tests
  are `154`, `285`, `301`, and `221`.
- No candidate reference or diff addition targets a real database/folder, workbook/COM,
  public-drive/LTR, frontend/API client, or SQLite DDL. `data/` remains clean.
- Fee rules/seeds, formula/pricing/UI, public DTO/client, schema/repository, authority
  writes, outputs, TASK_363C, TASK_364B, TASK_365A, release/dist, and external dirty
  worktree residuals remain excluded.

### Mixed-File Packaging Constraint

`backend/application/confirmed_matrix_fee_draft_service.py` contains external dirty
hunks. TASK_363D packaging may include only the private authority-result/historical
helper-extraction fragments: `build_draft()` delegation, `build_authority_result()`,
`ConfirmedMatrixFeeAuthorityBuildResult`, and the moved status/warning/time helpers.
It must exclude the visible external CR routing, matrix rule-resolution, base-fee
policy, and other non-TASK_363D imports/behavior. Do not stage the whole file.

## External Residual

The known unchanged LLCR Point Profile API regression remains external:
`test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units` expects `20` and
currently receives `None`. It is caused by excluded dirty Point Profile/LLCR routing
work, is not covered by TASK_363D candidate changes, and was neither fixed nor
packaged here.

## QA Disposition

`QA gate: pass`

Recommend only `Integrator packaging/readiness`. Integrator must hunk-isolate the
mixed core Fee service and exclude the LLCR residual, TASK_363C (which remains blocked),
TASK_364B/TASK_365A, and all other dirty worktree content.
