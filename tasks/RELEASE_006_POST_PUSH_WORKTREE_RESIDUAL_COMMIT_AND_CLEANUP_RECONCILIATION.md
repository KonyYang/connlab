# RELEASE_006 Post-Push Worktree Residual Commit And Cleanup Reconciliation

Date: 2026-07-25
Status: Child A scope corrected / pending Reviewer package-scope re-gate
Lane: `post-push-worktree-residual-commit-and-cleanup-reconciliation`
Role: Planner Discovery
Implementation authorization: Child A docs-only package only
Cleanup authorization: none
Commit authorization: none
Push authorization: none

## 1. Goal

Reconcile the post-push dirty worktree through separate, reviewable children so
that the eventual final gate can prove:

```text
git status --short
```

is empty, the index is empty, every retained change is owned by a controlled
local commit, and every discarded/restored path has an explicit reviewed User
decision.

This is a non-atomic governance umbrella. It is not authorization to stage all
residuals, create one catch-all commit, restore files, delete untracked files,
or push.

## 2. Current Source Facts

- `master` and `origin/master` both resolve to
  `580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5`.
- `origin/master...HEAD` is `0/0`.
- The index is empty.
- The pre-RELEASE_006 worktree contains exactly `52` status entries:
  `37` tracked and `15` untracked.
- RELEASE_005 classified its pre-Discovery `48` entries as:
  - Class A accepted/post-acceptance governance: `40`;
  - Class B unaccepted substantive tests: `3`;
  - Class C cleanup/discard candidates: `4`;
  - Class D mixed board: `1`.
- RELEASE_005 then added four untracked governance files: task, plan, Planner
  evidence, and Reviewer evidence.
- No RELEASE_005 QA evidence file exists; the prior QA activity was
  validation-only.

## 3. Ordered Children

### Child A - Accepted Governance Docs Closeout

Proposed ID:
`RELEASE_006A_ACCEPTED_GOVERNANCE_DOCS_CLOSEOUT`

Purpose:

- audit and deduplicate the Class A `40` governance paths;
- audit the four RELEASE_005 governance files;
- reconstruct only the accepted/push-complete/current-task board hunks from
  `HEAD`, never stage the mixed board as a whole;
- separate retained evidence from stale/duplicate discard candidates;
- after Reviewer approval and explicit User package authorization, allow a
  designated Integrator to create one local docs-only commit containing only
  the retained governance whitelist.

Child A does not own product code, tests, cleanup operations, or remote push.

### Child B - Test Residual Ownership Audit

Proposed ID:
`RELEASE_006B_TEST_RESIDUAL_OWNERSHIP_AUDIT`

Read-only audit scope:

1. `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
   (`114/0`);
2. `tests/unit/test_confirmed_matrix_fee_draft_service.py` (`38/13`);
3. `tests/unit/test_spec_section_text_extractor.py` (`51/0`).

For each exact hunk, compare its assertions with committed accepted bounded
coverage. Classify each hunk as:

- unique required coverage, which must become its own narrow tests-only lane;
  or
- duplicate/stale coverage, which becomes an exact discard candidate and
  remains untouched until explicit User confirmation.

No whole-file stage or product change is permitted.

### Child C - Cleanup Candidate Decisions

Proposed ID:
`RELEASE_006C_WORKTREE_CLEANUP_CANDIDATE_DECISIONS`

Decision scope:

- exact one-blank-line deletion in
  `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py`;
- three untracked TASK_364A governance files:
  - `tasks/TASK_364A_POINT_PROFILE_EDITOR_VISUAL_ALIGNMENT.md`;
  - `docs/task_364a_point_profile_editor_visual_alignment_plan.md`;
  - `docs/lane_evidence/TASK_364A_point-profile-editor-visual-alignment_developer.md`.

The blank-line hunk is a restore candidate. The TASK_364A files require an
archive/package/delete decision. Reviewer must first confirm the exact list.
Restore or delete then requires explicit User approval. Permanent deletion
requires the User to use the exact text `discard`.

### Final Clean Gate

The final gate runs only after Children A, B, and C have no unresolved entries.
It verifies:

- exact `HEAD` and `origin/master`;
- ahead/behind;
- empty index;
- empty `git status --short`;
- no tracked or untracked residual;
- commit-level and aggregate `git diff --check`;
- the focused tests required by every retained local commit;
- no real-data or generated-output mutation.

Any new remote push requires a separate fresh-ref check and explicit User push
authorization.

## 4. Child A Candidate Whitelist

Child A may inspect the exact `40` Class A paths frozen by RELEASE_005 and the
following four RELEASE_005 files:

```text
tasks/RELEASE_005_ACCEPTED_COMMIT_CHAIN_PUSH_READINESS_AND_RESIDUAL_RECONCILIATION.md
docs/release_005_accepted_commit_chain_push_readiness_and_residual_reconciliation_plan.md
docs/lane_evidence/RELEASE_005_accepted-commit-chain-push-readiness-and-residual-reconciliation_planner.md
docs/lane_evidence/RELEASE_005_accepted-commit-chain-push-readiness-and-residual-reconciliation_reviewer.md
```

The exact Class A list is copied into the RELEASE_006 plan and Planner evidence.
Candidate membership is not package authorization. Child A must produce a
smaller retained whitelist and a separate stale/duplicate decision list.

The only future board hunk owners are:

- top `Status`, `Current Active Task`, and `Proposed Next Task` lines;
- RELEASE_005 and RELEASE_006 Active Execution Model bullets;
- RELEASE_005 and RELEASE_006 Active Lanes rows.

All other `docs/task_board.md` content is locked.

## 5. Must Not Touch

- any product code;
- any test outside a separately approved tests-only child;
- any whole mixed file;
- schema, database, API client, frontend product code, seeds, manifests;
- real databases, public-drive files, attachments, source workbooks, or
  generated artifacts;
- `dist_release/**`;
- accepted commit contents;
- remote refs;
- unknown residuals outside the exact `52`-entry snapshot plus this lane's
  governance files.

## 6. Prohibited Git And Cleanup Operations

- `git add -A`;
- whole-file staging of mixed paths;
- `git reset`, `git clean`, `git checkout`, `git restore`, or `stash`;
- `git gc`, `git prune`, or object deletion;
- deletion or overwrite of user files;
- any commit or push in Planner/Reviewer Discovery;
- automatic remote push at any later gate.

## 7. Validation Contract

Planner/Reviewer governance validation:

```powershell
git rev-parse HEAD
git rev-parse origin/master
git rev-list --left-right --count origin/master...HEAD
git status --porcelain=v1 -uall
git diff --cached --name-only
git diff --check -- <RELEASE_006 governance paths and exact board hunk>
```

Use UTF-8 reads and a trailing-whitespace scan. Verify that no product or test
path changed during this Discovery.

## 8. Stop Point

Route only to Reviewer Child A package-scope re-gate.

Do not route Developer, QA, cleanup, or push. After Child A closeout, each later
child still requires the exact User authorization specified
above.
