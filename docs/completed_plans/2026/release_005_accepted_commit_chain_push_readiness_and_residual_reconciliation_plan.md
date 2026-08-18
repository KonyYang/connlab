# RELEASE_005 Accepted Commit Chain Push Readiness And Residual Reconciliation Plan

Date: 2026-07-25
Status: complete / historical push-readiness governance
Task: `RELEASE_005_ACCEPTED_COMMIT_CHAIN_PUSH_READINESS_AND_RESIDUAL_RECONCILIATION`
Lane: `accepted-commit-chain-push-readiness-and-residual-reconciliation`
Implementation authorization: no implementation commit exists
Push authorization: accepted chain already pushed

## 1. Discovery Gate

### Current Phase / Active Task / Role

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: RELEASE_005 planned-only governance/readiness Discovery.
- Role: Planner.
- Why allowed: TASK_366D is complete/accepted and the User explicitly requested a release
  readiness lane without push or cleanup.

### Confirmed By User

- Audit the exact seven-commit local chain before any remote push.
- Validate committed HEAD from an isolated source tree, never from dirty worktree files.
- Reclassify all `48` existing residual status entries without changing them.
- Produce only a push readiness conclusion for exact range `add69823..580fbb5e`.
- Do not push, stage, commit, clean, restore, create a long-lived worktree, run Git object
  maintenance, or access real data/generated outputs.

### Confirmed By Repository Evidence

- HEAD: `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- `origin/master`: `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- Left/right count: `0 0`.
- The seven commits are a strict single-parent chain in the requested order.
- Every object type is `commit`.
- Each `git show --check` is clean; aggregate `git diff --check origin/master..HEAD` is clean.
- `git fsck --connectivity-only` returns `0`. Historical dangling objects are present but are
  not connectivity failures.
- No accepted-range path matches `data/**`, `dist_release/**`, or common real Office/PDF input
  extensions.
- Pre-Discovery worktree snapshot: `48` status entries, `37` tracked and `11` untracked;
  tracked diff is `37 files changed, 572 insertions, 142 deletions`; index is empty.

### Inferred By Planner

- `git archive` is the narrowest clean-source mechanism because it exports an exact tree
  without checking out, resetting, or linking the current worktree.
- Existing installed Python/frontend dependencies may be reused read-only only if the exported
  source remains exact HEAD and dependency resolution is recorded. Dependency absence must
  block readiness rather than trigger installation or dirty-source fallback.
- Most status entries are post-acceptance governance closeout text. They are intentionally
  excluded from this seven-commit push and can be reconciled only in a later user-approved docs
  package.

### Not Yet Confirmed

- Whether a complete frontend dependency tree is available at the future aggregate gate.
- Whether the remote `master` ref will still equal `add69823668d7ac4bf18645c688ce367a8fe0d42`
  when a later push is requested.

These unknowns do not block a planned-only lane. They are fail-closed validation gates and do
block any future `push-ready` result until resolved.

### Discovery Decision

Reviewer plan gate is complete; RELEASE_005 is historical governance. It activates no Developer,
cleanup, QA execution, Integrator packaging, or push action.

## 2. Frozen Accepted Chain

| Order | Commit | Subject | Parent | Acceptance evidence | Accepted validation |
|---|---|---|---|---|---|
| 1 | `1cc97408d1532f2a07e4153b4aad5d37ce982755` | `build(release): reconcile RELEASE_004 browser packaging` | `add69823668d7ac4bf18645c688ce367a8fe0d42` | RELEASE_004 Reviewer/QA/Integrator evidence | static suite `8 passed`, Python compile, PowerShell parser |
| 2 | `44a6153ff4a16674bb15cb804887b774ebdae61f` | `feat(parser): reconcile Damp Heat condition extraction` | `1cc97408...` | Spec parser Reviewer/QA/Integrator evidence | seven modules `96 passed`, parser compile |
| 3 | `1658f33dd4ea41f3cf5d553bb33557335681527e` | `feat(frontend): reconcile contact measurement summary UI` | `44a6153f...` | Summary UI Reviewer/QA/Integrator evidence | frontend `2 files / 50`, build, controlled browser |
| 4 | `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` | `feat(fee): resolve matrix base fee policy` | `1658f33d...` | Child 1 Reviewer/QA/Integrator evidence | `57`, V2 `40`, retained subsets `31 + 35` |
| 5 | `dff635a6489f2664f7e496c424ceff8400237283` | `feat(fee): complete dependent field corrections` | `c5d91c36...` | Child 2 Reviewer/QA/Integrator evidence | `38 + 53 + 113 + 2`, frontend build |
| 6 | `c2104e106bad81a827e49714fb6d84ef4b9c09dd` | `feat(frontend): preserve pending pricing draft fields` | `dff635a6...` | Child 3 Reviewer/QA/Integrator evidence | frontend `65`, API `3`, V2 `37`, build |
| 7 | `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5` | `fix(matrix): complete TASK_366D method authority composition` | `c2104e10...` | TASK_366D Reviewer/QA/Integrator evidence | exact `1`, TASK_366C `29`, session `11`, compile |

Evidence files are committed in the corresponding commit and remain read-only inputs to this
lane. The chain audit must compare each evidence package against `git diff-tree` for its commit.

## 3. Stage 1 - Commit/Object Audit

Run read-only from the repository root:

```powershell
git rev-parse HEAD
git rev-parse origin/master
git rev-list --left-right --count origin/master...HEAD
git log --reverse --format='%H%x09%P%x09%s' origin/master..HEAD
git cat-file -t <each-of-seven-commits>
git show --check --format='' <each-of-seven-commits>
git diff --check origin/master..HEAD
git diff --name-status origin/master..HEAD
git fsck --connectivity-only
git status --porcelain=v1 -uall
git diff --cached --name-only
```

Fail closed if:

- refs, count, parent order, object type, or commit subjects differ;
- any commit or aggregate whitespace check fails;
- a real-data/generated-output forbidden path appears;
- any commit lacks its declared Reviewer/QA/Integrator evidence;
- the index is non-empty;
- connectivity returns non-zero.

Dangling objects are recorded as informational only. `gc`, `prune`, `repack`, restore, reset,
or object deletion is prohibited.

## 4. Stage 2 - Clean Committed-Tree Aggregate Gate

### 4.1 Isolation

1. Create a uniquely named directory under `%TEMP%`, outside the repository.
2. Export exact `580fbb5e...` with `git archive`.
3. Extract there and calculate an exported manifest/hash against `git ls-tree -r`.
4. Run all source-based tests with the exported directory as CWD.
5. Use pytest `--basetemp` under that same disposable root.
6. Do not copy any dirty source file into the export.
7. Frontend dependencies may be linked/read from an existing dependency tree only when
   `package-lock.json` matches the committed export. If unavailable, record the frontend gate
   as blocked. Do not install dependencies or fall back to the dirty frontend source.
8. Remove the disposable directory only in the later authorized validation gate, after
   resolving and verifying that the target is under `%TEMP%`. No cleanup occurs in Discovery.

### 4.2 Aggregate Commands

RELEASE_004 static-only:

```powershell
py -m pytest tests/unit/test_desktop_release_scripts.py -q
py -m py_compile packaging/connlab_browser_server.spec tests/unit/test_desktop_release_scripts.py
# Parse scripts/build_windows_browser_release.ps1 with System.Management.Automation.Language.Parser
```

Never execute the release script or PyInstaller.

Parser:

```powershell
py -m pytest tests/unit/test_condition_text_collectors.py tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_spec_section_text_extractor.py tests/unit/test_mfg_condition_parser.py tests/unit/test_thermal_shock_condition_parser.py tests/unit/test_voltage_surge_condition_parser.py -q
py -m py_compile backend/modules/test_plan/condition_text_collectors.py backend/modules/test_plan/damp_heat_condition_parser.py backend/modules/test_plan/spec_section_text_extractor.py
```

Summary UI:

```powershell
cd frontend
npm test -- --run src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx --watch=false
npm run build
```

Fee Child 1:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_base_fee_policy.py tests/unit/test_confirmed_matrix_fee_rule_resolution.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q
```

Also rerun the exact TASK_361L/TASK_363D V2 protection modules named by Child 1 QA evidence;
the expected accepted total is `40 passed`.

Fee Child 2:

```powershell
py -m pytest tests/unit/test_fee_default_fill_explicit_hour_authority.py tests/unit/test_fee_default_fill_temperature_rise_units.py tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py tests/unit/test_confirmed_matrix_fee_duration_authority.py tests/integration/test_matrix_typed_duration_authority_round_trip_api.py tests/unit/test_matrix_duration_authority_projection.py tests/unit/test_matrix_duration_authority_session_signature.py tests/integration/test_matrix_duration_authority_publication_api.py -q
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q
```

Frontend Child 2:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace.durationAuthority --run
npm run build
```

Fee Child 3:

```powershell
py -m pytest tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py -q
cd frontend
npm test -- --run src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
npm run build
```

TASK_366C and TASK_366D:

```powershell
py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_matrix_import_method_authority.py tests/integration/test_matrix_import_method_authority_commit_api.py tests/integration/test_matrix_import_group_selection_commit_api.py tests/integration/test_project_test_plan_source_matrix_import_persistence_api.py tests/unit/test_standard_method_version_parser.py tests/unit/test_matrix_method_version_sync_service.py tests/integration/test_matrix_method_version_sync_api.py -q
py -m pytest tests/integration/test_matrix_import_method_authority_commit_api.py::test_matrix_editor_session_composes_import_method_authority -q
py -m pytest tests/integration/test_matrix_editor_session_api.py -q
py -m py_compile backend/api/dependencies.py tests/integration/test_matrix_import_method_authority_commit_api.py
```

The later QA/readiness owner must record exact dependency versions, CWD, temp roots, commands,
counts, warnings, and failures. A test result from `D:\PythonProject\connlab` source is not clean
HEAD evidence.

## 5. Stage 3 - Exact Residual Inventory

This inventory describes the pre-Discovery `48`-entry snapshot. RELEASE_005 governance files
created afterward are not residuals.

### 5.1 Class A - Accepted/Post-Acceptance Governance Residuals

These `40` paths are docs/task status or evidence updates. They do not enter the seven-commit
push and require a separate docs-only reconciliation if the User later wants them committed.

Fee Child 1/2/3 and umbrella (`14`):

```text
docs/fee_default_fill_dependent_field_corrections_plan.md
docs/fee_rule_resolution_matrix_base_fee_policy_plan.md
docs/pricing_draft_pending_field_preservation_frontend_hydration_plan.md
docs/lane_evidence/FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS_planner.md
docs/lane_evidence/FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY_planner.md
docs/lane_evidence/PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION_planner.md
tasks/FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS.md
tasks/FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY.md
tasks/PRICING_DRAFT_PENDING_FIELD_PRESERVATION_FRONTEND_HYDRATION.md
docs/fee_default_fill_residual_package_reconciliation_plan.md
docs/lane_evidence/FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION_completion_reconciliation_planner.md
docs/lane_evidence/FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION_planner.md
docs/lane_evidence/FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION_reviewer.md
tasks/FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION.md
```

Older accepted TASK_362A governance (`5`):

```text
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_developer.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_integrator.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_qa.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_reviewer.md
tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md
```

TASK_364B/C completion governance (`13`):

```text
docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_package_re_gate_reconciliation_planner.md
docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_qa_pass_reconciliation_planner.md
docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_reconciliation_planner.md
docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_task364c_dependency_release_planner.md
docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_authorization_reconciliation_planner.md
docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_planner.md
docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_qa_pass_reconciliation_planner.md
docs/task_364b_project_point_profile_cr_coverage_authority_and_ui_plan.md
docs/task_364b_r1_inline_cr_table_corrective_plan.md
docs/task_364c_project_point_profile_cr_coverage_authority_baseline_package_plan.md
tasks/TASK_364B_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_AND_UI.md
tasks/TASK_364C_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_BASELINE_PACKAGE.md
docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_completion_reconciliation_planner.md
```

TASK_365B completion governance (`5`):

```text
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_planner.md
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_user_acceptance_reconciliation_planner.md
docs/task_365b_text_pdf_docx_matrix_extraction_parity_plan.md
tasks/TASK_365B_TEXT_PDF_DOCX_MATRIX_EXTRACTION_PARITY.md
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_completion_reconciliation_planner.md
```

Superseded TASK_366C composition evidence (`2`):

```text
docs/lane_evidence/TASK_366C_import-matrix-replace-method-authority-sync_developer.md
docs/lane_evidence/TASK_366C_import-matrix-replace-method-authority-sync_reviewer.md
```

Older accepted TASK_363D Planner checkpoint (`1`):

```text
docs/lane_evidence/TASK_363D_fee-pricing-draft-prior-defaults-attestation_planner.md
```

Recommendation: preserve untouched now. Later create one docs-only residual reconciliation,
deduplicate against accepted evidence, and package only after User approval and Reviewer gate.

### 5.2 Class B - Unaccepted Product/Test Residuals

Three paths contain substantive unaccepted tests and must not enter this push:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts
tests/unit/test_confirmed_matrix_fee_draft_service.py
tests/unit/test_spec_section_text_extractor.py
```

Ownership:

- `feeEvaluationPreviewModel.test.ts`: Fee Child 3/legacy hydration test residual. It adds
  manual-required LLCR Pending/blocker coverage outside the accepted Child 3 hunk. Route a
  future bounded test-only Discovery or ask Reviewer to prove accepted bounded coverage before
  proposing discard.
- `test_confirmed_matrix_fee_draft_service.py`: Fee Child 1 mixed legacy residual. The
  multi-Group Base Fee fixture/test was explicitly excluded from Child 1 packaging. Route a
  focused test-ownership audit; do not whole-file stage.
- `test_spec_section_text_extractor.py`: oversized legacy parser residual containing Damp Heat
  duplicate coverage plus TASK_365C Thermal Shock/Voltage Surge replay. The accepted parser
  package explicitly excluded this `51/0` hunk. Prefer Reviewer equivalence proof followed by
  User-approved discard, or a separate test-only package if coverage is uniquely required.

### 5.3 Class C - Cleanup/Discard Candidates

These four paths have no current approved package:

```text
tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py
docs/lane_evidence/TASK_364A_point-profile-editor-visual-alignment_developer.md
docs/task_364a_point_profile_editor_visual_alignment_plan.md
tasks/TASK_364A_POINT_PROFILE_EDITOR_VISUAL_ALIGNMENT.md
```

- The test diff is only one removed blank line and has no behavior. Recommend User-approved
  restore to HEAD in a future cleanup action.
- TASK_364A files are untracked historical governance for a lane not present in the accepted
  seven-commit chain. Preserve now; later User decides archive/package/delete after ownership
  audit. No product source is included in this snapshot.

### 5.4 Class D - Mixed Board

```text
docs/task_board.md
```

The worktree board contains valid historical completion additions mixed with stale TASK_366D
pending-implementation text. RELEASE_005 may change only:

- header/current task/proposed next fields;
- one TASK_366D accepted-status correction;
- one RELEASE_005 planned-only narrative;
- one TASK_366D row correction and one RELEASE_005 row.

Any future package must reconstruct those hunks from HEAD and must not stage the whole board.

## 6. Dependency And Ordering

1. Reviewer plan gate for RELEASE_005.
2. If passed, explicit User approval for a validation-only QA/readiness pass.
3. Clean committed-tree aggregate verification from exact HEAD.
4. Reviewer/QA push-readiness conclusion.
5. Separate User decision on residual cleanup/docs packaging.
6. Fresh remote-ref verification and separate explicit User push authorization.
7. Only then may a designated Integrator perform the exact push.

Residual cleanup is not a prerequisite for commit-object integrity, but no dirty file may be
used as validation evidence or included in a later commit without its own lane.

## 7. Rollback

This Discovery adds governance only. Rollback removes the RELEASE_005 task, plan, Planner
evidence, and exact board hunks. It never touches the seven accepted commits or any pre-existing
residual.

## 8. Current Stop

Historical closeout only. No Developer, QA, Integrator, cleanup, commit, or push is activated.
