# Child 2 External Fee-Rebase Residual Reconciliation

Date: 2026-07-24
Role: Planner
Status: `stale_fixture_context_pending_reviewer_tests_only_scope_confirmation`
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`

## Exact Failure

`tests/integration/test_matrix_editor_session_api.py::test_matrix_editor_session_autosave_restore_confirm_and_discard`

The autosave response is current, but its pending Fee-rebase summary has
`preserved_count=0` while the fixture asserts at least one preserved row.

## Read-Only Root Cause

The fixture helper `_seed_previous_pricing_draft()` persists the source pricing
draft with `fee_rule_version_id="fee_rules_v2026_06_03"`. The same test later
queries promotion under that obsolete id.

Matrix Editor derives its pending-rebase and promotion context from
`load_active_fee_rule_library().version.version_id`, which is accepted active
`fee_rules_v2026_07_17_r6`. The repository performs exact
project/Matrix/revision/rule-version lookup. It correctly finds no source draft
for the r6 command and therefore reports zero preserved rows.

The rebase service and source-row producer are unchanged in the current
worktree. TASK_366B Developer/Reviewer/Integrator evidence already recorded
this exact failure as an external Fee residual before Child 2 and before the
TASK_366C composition issue.

## Disposable Proof

Planner loaded the test source in memory, replaced only both occurrences of
`fee_rules_v2026_06_03` with `fee_rules_v2026_07_17_r6`, and executed the exact
test against a temporary directory. Result:

`fixture_context_probe=passed`

No repository file was changed by the probe.

## Ownership Decision

Classification: stale integration fixture context.

It is not:

- a Child 2 typed-duration product defect;
- a TASK_366C composition defect;
- a Matrix/Fee rebase algorithm defect;
- a reason to permit cross-version fallback.

TASK_361L/TASK_363D require exact current context, attestation, provenance,
fingerprints, CAS/no-write, and reviewed rebase. Changing production to find an
old rule-version draft would weaken those accepted contracts.

## Preservation Contract

- `preserved_count` counts source Fee rows matched to target Matrix rows by
  stable rebase identity under the exact current Matrix/revision/rule context.
- It does not count preserved manual fields.
- A context mismatch correctly yields no source match and no fallback.
- In an exact context, current automatic defaults remain authoritative; only
  proven compatible manual provenance survives.
- Testing Fee is derived from final safe values.
- Fingerprint/currentness/CAS mismatch remains blocked/no-write; load and Cancel
  remain zero-write.

## Proposed Tests-Only Scope

Pending Reviewer confirmation, May Touch would be only:

`tests/integration/test_matrix_editor_session_api.py`

Exact hunk:

1. Replace the obsolete rule-version literal inside
   `_seed_previous_pricing_draft()`.
2. Replace the same obsolete literal in the promoted-draft repository lookup
   within the exact failing node.

Both replacements use accepted active `fee_rules_v2026_07_17_r6`. The change is
line-neutral; the file remains `1107` blank-inclusive physical lines.

No assertion, fixture pricing value, manual note, summary, product code, rebase
key, provenance, CAS, API shape, or fallback change is allowed.

## Validation Gate

- exact lifecycle node;
- full `tests/integration/test_matrix_editor_session_api.py`;
- Matrix Fee draft/pending/promotion rebase unit modules;
- TASK_361L/TASK_363D V2 contract, prior-default attestation, and safe-rebase
  focused modules;
- diff/trailing/line-count/no-product-hunk/no-real-data/staging checks.

Child 2 product code is locked and passed. TASK_366C is read-only. Child 3 and
the umbrella remain blocked.

Next legal role: Reviewer tests-only scope confirmation. Developer is not yet
authorized for this fixture migration.
