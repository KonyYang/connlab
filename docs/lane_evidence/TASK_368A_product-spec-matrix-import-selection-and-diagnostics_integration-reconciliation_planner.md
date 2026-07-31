# TASK_368A Integration Reconciliation Planner Evidence

Date: 2026-07-31
Task: `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Role: ConnLab｜总计划者 Planner
Status: `integration_reconciliation_approved`
Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Discovery Gate

Current active task/lane:

- `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
- `task-368a-product-spec-matrix-import-quick-fix`
- current repository state before this reconciliation: `integration_blocked`

Why Planner is allowed:

- The authorized Integrator merge stopped on one shared governance evidence path, cleanly aborted,
  and assigned the conflict to Planner/User reconciliation.
- This is not a new task, lane, product behavior, validation contract, or merge attempt.
- The existing user Goal authorizes the TASK_368A role chain through local Integrator acceptance.
  `AGENTS.md` section 18.12 covers ordinary evidence reconciliation and local governance commits
  inside that unchanged Goal envelope.

User goal restatement:

TASK_368A must retain its reviewed and QA-passed nine-path lane package while resolving the one
primary/lane Quick Fixer evidence conflict without losing dispatch history. Planner must decide
the exact authoritative evidence content and return the unchanged lane to Integrator. Planner
must not merge, alter product/test behavior, touch the independent browser-release checkpoint,
push, or mark TASK_368A complete.

Evidence read:

- `AGENTS.md`
- `docs/task_board.md`, including its current header, TASK_368A execution summary, and active-lane
  row
- `tasks/TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX.md`
- `docs/task_368a_product_spec_matrix_import_selection_and_diagnostics_quick_fix_plan.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- primary and lane versions of the TASK_368A Quick Fixer evidence
- lane Reviewer and QA evidence
- primary Integrator evidence
- browser-release cancelled-closeout evidence
- Git commit ancestry, exact path lists, blob identities, three-way diff, and read-only
  `merge-tree` output

Confirmed by user:

- TASK_368A is already authorized through the normal local role chain to Integrator acceptance.
- This dispatch authorizes exact governance reconciliation and an exact-path local checkpoint,
  but forbids Planner from merging or changing product/test scope.
- A new user decision is required only if material dispatch facts are missing, product/test or
  acceptance semantics must change, or destructive/remote action is required.

Confirmed by repository evidence:

- Primary is clean on `master` at
  `37d6010fa57921f02b3f646761f7ad2dce1fe183` with no `MERGE_HEAD`.
- The lane is clean at
  `826e0a232982153eb00b6fc379892c4611a872e1`.
- The exact merge-base remains
  `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`.
- The lane package contains exactly nine authorized paths: six product/test paths plus Quick
  Fixer, Reviewer, and QA evidence.
- Reviewed HEAD `78dcce7d50d09dd396a6dc5d15b2c24e743bdd1f` and Reviewer evidence commit
  `3c5e4a91373f882c7178b3a0e071e3778be1fd0a` are ancestors of lane/QA HEAD.
- Reviewer status is `reviewer_pass`; QA status is `qa_pass`.
- Read-only `git merge-tree` reports ordinary merges/additions for the other eight lane paths and
  one `changed in both` conflict at:
  `docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_quick-fixer.md`.
- Three-way blob identities for that path are:
  - base: `1e8b67b7932c8455702432875f99c91a053f74e7`
  - primary dispatch successor from `a55e4f22`:
    `c03c6263a00d110bca74ecce66fc4a1cfa473ef9`
  - lane chronological successor at `826e0a23`:
    `eff7f9f2c50621ebcc53515b932287225ba8db7a`
- The lane blob retains the dispatch authorization, diagnosis, ownership, branch, worktree, base,
  and clean-start facts, then records the actual implementation checkpoint, TDD, validation,
  Reviewer fix pass, and read-only real-DOCX smoke.
- No TASK_368A product/test/evidence path has been integrated. No merged-tree validation, push,
  publication, service restart, or worktree retirement has occurred.
- The cancelled browser-release checkpoint
  `0bf56ea09ba1a1baedd5ce982d0b47d73d1889df` remains an independent `retain` item owned by
  permanent Orchestrator governance/User decision.

Inferred by Planner:

- The lane Quick Fixer evidence blob is the lossless chronological successor of the primary
  dispatch placeholder, not a competing product or acceptance decision.
- Selecting that exact lane blob is safer than hand-combining prose because it preserves the
  reviewed/QA-observed evidence byte-for-byte.

Not yet confirmed:

- The outcome of the next Integrator merge and merged-tree validation is not yet known. This is
  intentionally the next Integrator gate and does not block Planner reconciliation.
- No unknown affects evidence ownership, product/test scope, acceptance semantics, or the exact
  conflict resolution.

Planning risk:

- A manual prose merge could omit dispatch provenance, alter reviewed evidence, or leave a hybrid
  status that was never reviewed.
- Treating the superseded pending fields as an unknown discard could incorrectly demand a new
  task or user decision.
- Treating QA history as merged-tree validation could produce a false acceptance claim.

Decision:

- Continue without a new user approval.
- Existing Goal authority is sufficient for this exact evidence reconciliation and local
  governance checkpoint.
- No replacement task or lane is created.

## Exact Reconciliation Authority

At the next authorized merge attempt, the final content for the conflict path must be the exact
blob from lane HEAD `826e0a232982153eb00b6fc379892c4611a872e1`:

```text
docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_quick-fixer.md
blob eff7f9f2c50621ebcc53515b932287225ba8db7a
```

The lane blob is authoritative because it is the chronological successor reviewed at
`78dcce7d...` and carried unchanged into QA HEAD `826e0a23...`.

### Primary Dispatch Fact Preservation

| Primary `a55e4f22` fact | Preservation in authoritative lane blob |
|---|---|
| User start instruction | Retained verbatim under `Authorization`. |
| Quick Fixer fast-path rationale | Retained under `Authorization`. |
| Four-product-file stop boundary | Retained under `Authorization`. |
| Correct Matrix, split header, false Revision Record, singular `Page`, score trigger, locator gap, diagnostic gap, and `24 passed` baseline | All eight facts retained under `Discovery Evidence`. |
| Product/test ownership, board ownership, browser-release/V2 isolation, and real-file read-only rule | All four facts retained under `Ownership`. |
| Lane branch and sibling worktree | Retained under `Worktree`. |
| Base `6c16cbcb...` | Retained as `Base commit`. |
| Clean branch/HEAD/worktree/index at dispatch | Retained as `Dispatch verification`. |
| `Quick Fixer checkpoint: pending` | Replaced by actual implementation checkpoint `a3d77c78...`. |
| Required RED, changed paths, GREEN validation, full checkpoint, clean proof, residuals, and next role | Fulfilled by `TDD Record`, `Changed Paths`, `Validation`, `Residuals And Handoff`, and `Reviewer Blocking Fix Pass`. |
| Allowed stop status list | Fulfilled by the actual `ready_for_review` status. |

The primary values `approved_ready_for_quick_fixer_dispatch`, `Quick Fixer checkpoint: pending`,
and the prospective required-record instructions are classified `stale/superseded`. They are not
unknown residuals and do not authorize deletion or alteration of any other evidence.

## Integrator Execution Gate

Integrator may retry the already authorized local non-fast-forward merge only after re-reading
this evidence and fresh repository state. Integrator must:

1. verify primary is clean, has no `MERGE_HEAD`, and contains this governance checkpoint;
2. verify the lane remains clean at exact HEAD `826e0a232982153eb00b6fc379892c4611a872e1`;
3. verify the merge-base remains `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`;
4. verify Reviewer/QA ancestry and statuses remain unchanged;
5. if the same single path conflicts, resolve only that path to the exact lane blob
   `eff7f9f2c50621ebcc53515b932287225ba8db7a`;
6. verify the staged conflict path resolves to that blob, for example by checking its index blob
   identity, before completing the merge;
7. verify the merged candidate contains the complete nine-path lane package and does not alter
   lane product/test, Reviewer evidence, or QA evidence;
8. run the original task merged-tree validation: `31` backend regressions, exact Python
   compilation, `45` focused frontend tests, and frontend build;
9. update Integrator evidence/task/board and mark acceptance only if all merge and validation
   gates pass.

No cherry-pick, partial product-only integration, new conflict prose, product/test edit, push,
publication, localhost restart, destructive cleanup, branch deletion, or worktree retirement is
authorized by this Planner decision. The browser-release cancelled retained branch, worktree,
checkpoint, and evidence are completely independent and must not be touched.

## Handoff

- Planner status: `integration_reconciliation_approved`
- TASK_368A remains unintegrated and not accepted.
- Next legal role: permanent Integrator.
- Blocker: none for the exact evidence reconciliation; Integrator must still complete the merge
  and merged-tree validation gates.
