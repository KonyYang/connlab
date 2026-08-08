# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING — QA Evidence

MODEL: gpt-5.6-terra
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: default_complex

## Result

`STATUS: pass`

Independent QA covered the exact reviewed subject
`ad7dac819268ae77781709b626aea4f624a7a740` and clean lane head
`d5e82f2ea6ab18c979540c226811c2a20978f48e`. The declared base
`3d0884e12cc39e7b416da75ab01aaffd36c6418c` is an ancestor of the reviewed
subject. The lane was clean before this evidence write.

## Scope and contract audit

- The implementation range changes only the three approved implementation paths; the Developer and
  Reviewer evidence files are the only pre-QA evidence additions. `docs/task_board.md`, runtime,
  integration suites, and all protected paths are unchanged.
- Submit rejects `kind` and uses the exact ten-category map; Approve requires `kind=planned` and the
  nine-category map that excludes `push_or_release`; Close uses no JSON and requires non-empty
  `DecisionRef`.
- Both governing documents require explicit complex-role model and effort dispatch, Terra-medium
  defaults, deterministic QA low eligibility, frozen-category Sol escalation, no Luna, role audit
  headers, and final `ACTUAL_MODEL_ROUTING` reconciliation.
- The direct simple path, recovery reuse/fail-closed behavior, and UI-smoke rule (only user-visible UI
  changes; documented load state or deterministic selectors; no `networkidle`) are preserved.

## Actual model routing audit

| Role | Model | Effort | Reason | Evidence/dispatch |
| --- | --- | --- | --- | --- |
| Developer | gpt-5.6-terra | medium | default_complex | Developer dispatch capsule and evidence header |
| Reviewer | gpt-5.6-terra | medium | default_complex | Reviewer dispatch capsule and evidence header |
| QA | gpt-5.6-terra | medium | default_complex | This QA dispatch and header |

No Luna route was used. The task changes operational orchestration guidance, so QA does not satisfy the
bounded documentation/copy-only low-effort exception.

## Validation

- `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q` — passed: 7 tests.
- `py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q` — exactly 9 failed, 8 passed. One failure is the stale V1
  `-ActivateNext` JSON-decoding test. The other eight copy the active task board into fixtures and then
  correctly receive `BLOCKED_ACTIVE_TASK_RUNNING`; the cutover assertion is a consequence of that same
  copied active board. No new or different failure class appeared.
- `git diff --check` — passed.

## Gate decision

QA passes the reviewed implementation. Integrator must add its explicit Terra/medium/default-complex
dispatch and evidence header, then reconcile Developer, Reviewer, QA, and Integrator in the required
`ACTUAL_MODEL_ROUTING` table.
