# V1-Lite Task-Scoped Thread Label / Short-Title Governance Reconciliation

## Ownership

- Owner: `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD｜Controller`
- Disposition: independent governance reconciliation
- Product task relationship: explicitly excluded from
  `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD` implementation and lane diff
- Authorization: user explicitly identified the five paths below as legacy V1-Lite
  `thread_label` / compact native-title governance and authorized an exact-path local commit
- Remote disposition: local only; no push

## Authorized Governance Paths

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `AGENTS.md`
3. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
4. `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
5. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`

This evidence file is the only additional path in the reconciliation package.

## Diff Review

The four governance documents consistently establish:

- a bundle-owned, business-readable `thread_label`;
- compact native display titles using
  `<thread_label>｜主控/规划/开发/评审/测试/集成`;
- continued use of the complete formal `TASK_ID` in durable governance, prompts, and callbacks;
- exact native thread IDs, rather than title search, as routing authority.

The bounded governance test validates those contracts. Its previous empty-manifest assertion was
operational-state dependent and failed while a legitimate task bundle was active. The assertion
was narrowed to the durable routing schema (`state`, task identity, and `thread_label`) without
changing the active manifest or any product behavior.

## Validation

- Command:
  `py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q`
- Initial result: `1 failed, 2 passed`; the failure required the active routing manifest to be
  empty while this task bundle was legitimately active.
- Corrected result: `3 passed in 0.05s`.
- Diff scope: only the five user-authorized governance paths plus this evidence file.
- Package commit: the local commit containing this evidence.

## Safety / Non-Goals

- No product implementation file is included.
- No `TASK_BROWSER_RELEASE_FRONTEND_FRESHNESS_AND_INSTANCE_GUARD` implementation worktree content
  is included.
- No V2 registry, heartbeat, pilot, corrective, or test path is changed.
- No stash, deletion, cleanup, fetch, push, or remote mutation is performed.
- Staging and commit use exact paths only.
