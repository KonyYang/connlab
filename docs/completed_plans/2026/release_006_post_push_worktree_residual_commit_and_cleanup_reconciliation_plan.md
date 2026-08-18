# RELEASE_006 Post-Push Worktree Residual Commit And Cleanup Reconciliation Plan

Date: 2026-07-25
Status: Child A scope corrected / pending Reviewer package-scope re-gate
Task: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Lane: `post-push-worktree-residual-commit-and-cleanup-reconciliation`
Implementation authorization: Child A docs-only package only
Cleanup authorization: none
Commit authorization: none
Push authorization: none

## 1. Discovery Gate

### Current Phase / Active Task / Role

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled
  foundation`.
- Active task: RELEASE_006 Child A package-scope reconciliation.
- Role: Planner.
- Why allowed: the accepted seven-commit chain is already present on
  `origin/master`, and the User explicitly requested a separate Discovery for
  the remaining dirty worktree without authorizing staging, cleanup, commit,
  or push.

### Confirmed By User

- The eventual target is an empty `git status --short` and empty index.
- Every retained change must enter a controlled local commit.
- The `52` entries must not be packed into one atomic commit.
- Class A governance, Class B tests, and Class C cleanup decisions must pass
  separate gates in that order.
- Restore/delete/clean actions require Reviewer-confirmed exact lists and
  explicit User authorization.
- Permanent deletion requires the exact User text `discard`.
- Any future push requires a separate fresh-ref check and explicit User push
  approval.

### Confirmed By Repository Evidence

- `HEAD` and `origin/master` are both
  `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- `origin/master...HEAD` is `0/0`; the accepted chain has already been pushed.
- Index is empty.
- `git status --porcelain=v1 -uall` has `52` entries: `37` tracked and `15`
  untracked.
- RELEASE_005 Reviewer evidence passed its plan gate and confirmed the original
  exhaustive `40/3/4/1` residual classification.
- The four additional untracked entries are exactly RELEASE_005 task, plan,
  Planner evidence, and Reviewer evidence.
- No RELEASE_005 QA evidence file is present.
- Current Class B numstat is exactly `114/0`, `38/13`, and `51/0`.
- The Class C test hunk is exactly one removed blank line (`0/1`).
- The three TASK_364A files have no accepted commit history. Accepted HEAD
  references them only as unaccepted residuals in prior Discovery evidence.

### Inferred By Planner

- Child A can produce a docs-only commit only after it distinguishes unique
  historical evidence from stale duplicates; candidate membership alone is
  not enough to retain a file.
- Class B may resolve to more than one tests-only child because Fee frontend,
  Fee backend, and parser coverage have different accepted owners.
- Child C should use hunk-level restore for the blank-line deletion if the User
  authorizes it, while TASK_364A needs a distinct archive/package/delete
  decision.

### Not Yet Confirmed

- Which Class A candidate files are uniquely valuable after deduplication.
- Which Class B hunks add unique coverage rather than duplicate accepted
  bounded suites.
- Whether the User wants TASK_364A archived, packaged, or permanently
  discarded.

These unknowns do not block a planned-only umbrella. They do block every
commit, restore, deletion, and final clean claim.

### Discovery Decision

Reviewer Child A audit passed and the User authorized only the exact Child A
docs-only package. Child B/C execution remains unauthorized.

## 2. Baseline Snapshot

```text
HEAD:          580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
origin/master: 580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right:    0/0
index:         empty
status:        52 = 37 tracked + 15 untracked
```

RELEASE_005's pre-Discovery snapshot:

```text
Class A: 40 accepted/post-acceptance governance paths
Class B:  3 unaccepted substantive test paths
Class C:  4 cleanup/discard candidates
Class D:  1 mixed board
```

RELEASE_005 adds four governance paths after that snapshot.

## 3. Non-Atomic Dependency Order

```text
Reviewer plan gate
  -> User chooses/authorizes Child A audit
  -> Child A Reviewer package gate
  -> User authorizes exact retained docs package
  -> Integrator creates local docs-only commit
  -> User authorizes Child B read-only audit
  -> Reviewer classifies each exact test hunk
  -> separate tests-only lane(s) or explicit discard decisions
  -> Child C Reviewer exact cleanup-list gate
  -> User exact restore/archive/package/discard decisions
  -> authorized cleanup/package actions
  -> final clean gate
  -> separate fresh-ref push decision if new local commits exist
```

No later step is implied by approval of an earlier step.

## 4. Child A - Accepted Governance Docs Closeout

### 4.1 Candidate Class A Paths

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

TASK_362A (`5`):

```text
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_developer.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_integrator.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_qa.md
docs/lane_evidence/TASK_362A_complete-fee-reference-base-seed_reviewer.md
tasks/TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED.md
```

TASK_364B/C (`13`):

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

TASK_365B (`5`):

```text
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_planner.md
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_user_acceptance_reconciliation_planner.md
docs/task_365b_text_pdf_docx_matrix_extraction_parity_plan.md
tasks/TASK_365B_TEXT_PDF_DOCX_MATRIX_EXTRACTION_PARITY.md
docs/lane_evidence/TASK_365B_text-pdf-docx-matrix-extraction-parity_completion_reconciliation_planner.md
```

TASK_366C (`2`):

```text
docs/lane_evidence/TASK_366C_import-matrix-replace-method-authority-sync_developer.md
docs/lane_evidence/TASK_366C_import-matrix-replace-method-authority-sync_reviewer.md
```

TASK_363D (`1`):

```text
docs/lane_evidence/TASK_363D_fee-pricing-draft-prior-defaults-attestation_planner.md
```

RELEASE_005 (`4`):

```text
tasks/RELEASE_005_ACCEPTED_COMMIT_CHAIN_PUSH_READINESS_AND_RESIDUAL_RECONCILIATION.md
docs/release_005_accepted_commit_chain_push_readiness_and_residual_reconciliation_plan.md
docs/lane_evidence/RELEASE_005_accepted-commit-chain-push-readiness-and-residual-reconciliation_planner.md
docs/lane_evidence/RELEASE_005_accepted-commit-chain-push-readiness-and-residual-reconciliation_reviewer.md
```

### 4.2 Audit Output

Child A must publish:

1. an exact retained file/hunk whitelist;
2. an exact stale/duplicate candidate list;
3. source-of-truth corrections limited to accepted commit IDs, push-complete
   facts, superseded pending states, and next-task status;
4. a no-product/no-test package diff;
5. a local commit message proposal.

No candidate is staged merely because it appears above.

### 4.3 Mixed Board Boundary

Use `git show HEAD:docs/task_board.md` as the baseline. Only these hunk owners
may be reconstructed:

- top `Status`, `Current Active Task`, and `Proposed Next Task`;
- RELEASE_005 and RELEASE_006 Active Execution Model bullets;
- RELEASE_005 and RELEASE_006 Active Lanes rows.

Do not stage the board as a whole. Do not rewrite older task summaries or rows.

### 4.4 Child A Validation

- exact retained whitelist;
- no product/test paths;
- current accepted commit IDs and remote push state;
- UTF-8 trailing clean;
- `git diff --check`;
- hunk-level board diff;
- empty index before authorized packaging;
- Reviewer package gate before User authorization;
- local commit only; no push.

## 5. Child B - Test Residual Ownership Audit

### 5.1 Frontend Fee Preview Test (`114/0`)

Exact hunks:

- additional blocker assertion in the existing manually-required row test;
- new `keeps saved manual-required LLCR price and units pending` test.

Likely owner: accepted Child 3 hydration/currentness behavior, but the hunk was
not in its accepted package.

Required comparison:

- accepted Child 3 bounded hydration tests;
- accepted compatibility API/currentness coverage;
- current public wrapper compatibility tests;
- whether LLCR Pending and blocker behavior is already asserted with equivalent
  source metadata.

If unique, create a frontend tests-only lane with hunk-level staging and
focused Vitest/build. If duplicate, request exact User `discard` authorization.

### 5.2 Confirmed Matrix Fee Draft Service Test (`38/13`)

Exact hunks:

- one multi-Group Base Fee zero integration test;
- `group_count` fixture parameter;
- tuple construction generalized for groups and cells.

Likely owner: accepted Child 1 general Base Fee fallback, not Child 2 or Child
3.

Required comparison:

- accepted bounded Base Fee policy tests;
- accepted rule-resolution and draft-service integration tests;
- proof that single-Group and multi-Group use identical precedence without
  `matrix_group_count` authority.

If the service-level assertion is unique, create a narrow backend tests-only
lane. If equivalent accepted coverage exists, request exact User `discard`
authorization. Never stage the oversized/mixed test file as a whole.

### 5.3 Spec Section Extractor Test (`51/0`)

Exact hunks:

- Long-term damp heat extraction;
- TASK_365C Thermal Shock extraction replay;
- TASK_365C Voltage surge extraction replay.

Likely owners:

- accepted Damp Heat parser package for the first hunk;
- accepted TASK_365C for the latter two.

Required comparison:

- accepted bounded Damp Heat parser/dispatch tests;
- accepted Thermal Shock and Voltage Surge tests;
- whether integration through `extract_row_details` is uniquely absent.

The old module is oversized and remains read-only. Unique coverage must move to
new bounded test modules; duplicate coverage becomes an exact discard
candidate. The `51/0` mixed hunk may not be staged.

### 5.4 Child B Stop Point

Child B is read-only Discovery. It may produce governance evidence only. Each
unique test package requires its own Reviewer gate and explicit User tests-only
authorization. Each discard requires Reviewer confirmation and exact User
`discard` text.

## 6. Child C - Cleanup Candidate Decisions

### 6.1 Blank-Line Restore Candidate

Path:

```text
tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py
```

The current diff removes one blank line and changes no behavior. Recommend an
exact hunk restore only after Reviewer confirms the hunk and the User explicitly
authorizes restore. No whole-file restore is allowed.

### 6.2 TASK_364A Governance Candidates

Paths:

```text
tasks/TASK_364A_POINT_PROFILE_EDITOR_VISUAL_ALIGNMENT.md
docs/task_364a_point_profile_editor_visual_alignment_plan.md
docs/lane_evidence/TASK_364A_point-profile-editor-visual-alignment_developer.md
```

Repository evidence:

- no accepted commit contains these files;
- accepted HEAD mentions them only in prior residual Discovery evidence;
- they are not current accepted task evidence.

Future mutually exclusive decisions:

- archive/package through a dedicated TASK_364A governance/package lane;
- retain temporarily as unresolved;
- permanently delete after Reviewer confirmation and exact User `discard`.

No deletion occurs in this umbrella.

## 7. Final Clean Gate

Prerequisites:

- Child A has a committed retained docs package or an explicit no-package
  outcome;
- every Child B hunk is committed through a tests-only lane or explicitly
  discarded;
- every Child C item has completed its approved restore/archive/package/discard
  action;
- no child leaves pending generated files or staging.

Checks:

```powershell
git rev-parse HEAD
git rev-parse origin/master
git rev-list --left-right --count origin/master...HEAD
git status --short
git diff --cached --name-only
git diff --check
git log --oneline origin/master..HEAD
```

Run focused tests declared by each retained commit from committed source.
Record tracked/untracked counts as zero. A clean worktree does not itself
authorize remote push.

If local commits exist, a later push gate must:

- fetch/read remote refs without changing local source;
- prove the expected remote ancestor;
- name the exact ref range;
- obtain explicit User push approval;
- push only that approved range.

## 8. Rollback

This Discovery adds only RELEASE_006 governance and exact board planned-only
hunks. Rollback of the plan removes only those additions after approval. It
does not touch the existing `52` entries.

Every future child rollback is package-specific and must never use whole-tree
reset/clean/restore.

## 9. Current Stop

Route Reviewer Child A package-scope re-gate only. Developer, QA, cleanup, commit beyond
this exact docs package, and push remain unauthorized.
