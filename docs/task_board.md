# ConnLab Task Board

> Status: classic permanent-role execution active; V1-Lite and Controlled Lane V2 are frozen read-only, V2 heartbeat remains `PAUSED`, and retained snapshots are preserved
> Last Updated: 2026-08-02
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF` is the sole WIP=`1` token owner in `gate_running/Reviewer` on lane `task-governance-active-context-deterministic-transition-and-event-handoff`.
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Next Serial Task: none. Orchestrator must reuse the exact existing lane and non-destructively fast-forward it from `e958ba37...` to `3e737616...`, then prove exact clean HEAD equality and obtain a fresh `ImplementationDispatch=ALLOW_DISPATCH`. Until those proofs pass, Developer is not authorized. Task B remains `planned_pending_user_approval` and cannot start without Task A acceptance plus separate User approval. The rejected umbrella remains permanently non-executable.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.execution-control",
  "version": 1,
  "wip_limit": 1,
  "execution_token_owner": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
  "execution_state": "gate_running",
  "active": {
    "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
    "lane": "task-governance-active-context-deterministic-transition-and-event-handoff",
    "role": "Reviewer",
    "branch": "lane/task-governance-active-context-deterministic-transition-and-event-handoff",
    "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-active-context-deterministic-transition-and-event-handoff",
    "base_sha": "15c3120a6d889e97d098c2cb9f8c8ef852d74f69",
    "head_sha": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
    "locked_paths": [
      "AGENTS.md",
      ".agents/skills/connlab-lane-orchestrator/SKILL.md",
      ".agents/skills/connlab-planner/SKILL.md",
      "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
      "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
      "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
      "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
      "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
      "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
      "docs/project_management/TASK_EXECUTION_SKILL.md",
      "docs/project_management/TASK_REVIEW_CHECKLIST.md",
      "scripts/run_task.ps1",
      "scripts/connlab_execution_transition.py",
      "scripts/connlab_execution_transition_proof.py",
      "scripts/connlab_active_context.py",
      "scripts/connlab_handoff_contract.py",
      "tests/unit/test_connlab_execution_transition.py",
      "tests/unit/test_connlab_execution_transition_proof.py",
      "tests/integration/test_connlab_execution_transition_recovery.py",
      "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
      "tests/unit/test_connlab_active_context.py",
      "tests/integration/test_connlab_board_closeout_maintenance.py",
      "tests/unit/test_connlab_handoff_contract.py",
      "tests/unit/test_connlab_active_context_governance.py",
      "tests/unit/test_execution_wip_and_quick_fix_governance.py",
      "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
      "tasks/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF.md",
      "docs/task_governance_active_context_deterministic_transition_and_event_handoff_plan.md",
      "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_*",
      "docs/task_board.md",
      "docs/archive/task_board_history/index.v1.jsonl",
      "docs/archive/task_board_history/generation-[0-9]{6}-[0-9a-f]{40}.md"
    ],
    "required_gates": [
      "Reviewer",
      "QA",
      "Integrator"
    ],
    "evidence": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@70e5c6a7606284e1fc55ac6b0497c6d9756b665f#1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
    "last_transition_id": "367e000d5a4c93e060039b5a3cfd4f1ad88ac096500a994c62d8bdea94399968",
    "scope_contract_ref": "tasks/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF.md@d7994d264db1d7314d916a9773c95722e9201958#828cb6152b0f1a30213bb54207533c5a12eca7c4ef20baa785399b936e50b29a",
    "may_touch_digest": "758076d1217b9d15d547c3bdcf1f66262611203a34c804252e96fbbc073215af",
    "locked_paths_digest": "93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c"
  },
  "queue": [],
  "paused": null,
  "quick_fix": null,
  "residuals": [
    {
      "task_id": "TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH",
      "residual_owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH_integrator.md"
    },
    {
      "task_id": "TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX",
      "residual_owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md"
    },
    {
      "task_id": "TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY",
      "residual_owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368E_matrix-import-optional-standard-version-fallback-and-copy-clarity_integrator.md"
    }
  ],
  "parallel_exception": null,
  "last_governance_commit": "3e73761673fd75de4e79028b0b8d0b89979bbd1a",
  "evidence": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@70e5c6a7606284e1fc55ac6b0497c6d9756b665f#1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
  "transition_metadata_bootstrap": {
    "schema": "connlab.transition-metadata-bootstrap",
    "version": 1,
    "purpose": "initialize frozen metadata during first atomic DEVELOPER_READY adoption",
    "single_use": true,
    "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
    "base_sha": "15c3120a6d889e97d098c2cb9f8c8ef852d74f69",
    "planning_primary_anchor": "49911ae626daf646836471246a223496dc7ea771",
    "authority_primary_head": "329c0343ea0e7f4d24d6fb7e2e986a094c304fd8",
    "source_board_sha256": "e5fe215766043dc2377554faa341edc762d2925817be8b82775a80dd7487b8ed",
    "source_payload_digest": "124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8",
    "durable_board_head": "3e73761673fd75de4e79028b0b8d0b89979bbd1a",
    "blocked_candidate_head": "aeb7709128361782800d2da5a473d730d48df652",
    "source_locked_paths_digest": "df114c309a21657d155401a591bb4a05b960ea9ef3854125713fe149509e2907",
    "expanded_locked_paths_digest": "93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c",
    "blocked_candidate_evidence_blob": "104387574e995f2b6caf4bf1ceacfab76a748c64",
    "blocked_candidate_evidence_sha256": "3d53242ba53f899bd9656e37e33508f6b74d57b711fd5926f39e1a4d67d2157c",
    "blocked_candidate_delta_digest": "18fac5e571c1f78c16b8bbf8f587b9488444ead1a1f8be8a92f8c9b4763a01c1",
    "scope_contract_ref": "tasks/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF.md@d7994d264db1d7314d916a9773c95722e9201958#828cb6152b0f1a30213bb54207533c5a12eca7c4ef20baa785399b936e50b29a",
    "plan_contract_ref": "docs/task_governance_active_context_deterministic_transition_and_event_handoff_plan.md@d7994d264db1d7314d916a9773c95722e9201958#022cbde17359a7a70304e1e55862e3071d70931624c41e58cb649268a6919e61",
    "blocked_candidate_evidence_ref": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@aeb7709128361782800d2da5a473d730d48df652#3d53242ba53f899bd9656e37e33508f6b74d57b711fd5926f39e1a4d67d2157c",
    "blocked_candidate_evidence_status": "ready_for_review",
    "candidate_lane_head": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
    "candidate_delta_digest": "2b245c5114b0c78da78ba62022f1a98f9ef9c633753c9cfc00f0e18a66e661b5",
    "may_touch_digest": "758076d1217b9d15d547c3bdcf1f66262611203a34c804252e96fbbc073215af",
    "expanded_locked_paths": [
      "AGENTS.md",
      ".agents/skills/connlab-lane-orchestrator/SKILL.md",
      ".agents/skills/connlab-planner/SKILL.md",
      "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
      "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
      "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
      "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
      "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
      "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
      "docs/project_management/TASK_EXECUTION_SKILL.md",
      "docs/project_management/TASK_REVIEW_CHECKLIST.md",
      "scripts/run_task.ps1",
      "scripts/connlab_execution_transition.py",
      "scripts/connlab_execution_transition_proof.py",
      "scripts/connlab_active_context.py",
      "scripts/connlab_handoff_contract.py",
      "tests/unit/test_connlab_execution_transition.py",
      "tests/unit/test_connlab_execution_transition_proof.py",
      "tests/integration/test_connlab_execution_transition_recovery.py",
      "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
      "tests/unit/test_connlab_active_context.py",
      "tests/integration/test_connlab_board_closeout_maintenance.py",
      "tests/unit/test_connlab_handoff_contract.py",
      "tests/unit/test_connlab_active_context_governance.py",
      "tests/unit/test_execution_wip_and_quick_fix_governance.py",
      "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
      "tasks/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF.md",
      "docs/task_governance_active_context_deterministic_transition_and_event_handoff_plan.md",
      "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_*",
      "docs/task_board.md",
      "docs/archive/task_board_history/index.v1.jsonl",
      "docs/archive/task_board_history/generation-[0-9]{6}-[0-9a-f]{40}.md"
    ],
    "retained_context_digest": "eaa4fed4a95df5a05b1629c1e15880253da3dd174d9e1b4693fe662d855f2775",
    "branch": "lane/task-governance-active-context-deterministic-transition-and-event-handoff",
    "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-active-context-deterministic-transition-and-event-handoff",
    "clean": true,
    "ancestry": [
      "base_to_durable",
      "durable_to_blocked",
      "blocked_to_candidate"
    ],
    "candidate_evidence_ref": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@70e5c6a7606284e1fc55ac6b0497c6d9756b665f#1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
    "candidate_evidence_blob": "e9d528a9c2b63b4a87dfcc6eaac74232942eeb54",
    "candidate_evidence_status": "ready_for_review",
    "bootstrap_id": "b1605205d969bd5a0110383ede944018786fb7a2c94e708076b72fc33ed4cfb3"
  },
  "last_transition": {
    "transition_id": "367e000d5a4c93e060039b5a3cfd4f1ad88ac096500a994c62d8bdea94399968",
    "plan_digest": "5ac92b5060cbde4d647c0d173f9773119bc18ed360de5dd7650f180b8edf2f96",
    "event": "DEVELOPER_READY",
    "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
    "lane": "task-governance-active-context-deterministic-transition-and-event-handoff",
    "primary_head": "329c0343ea0e7f4d24d6fb7e2e986a094c304fd8",
    "expected_board_head": "3e73761673fd75de4e79028b0b8d0b89979bbd1a",
    "candidate_lane_head": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
    "evidence_ref": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@70e5c6a7606284e1fc55ac6b0497c6d9756b665f#1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
    "evidence_status": "ready_for_review",
    "range_digest": "758076d1217b9d15d547c3bdcf1f66262611203a34c804252e96fbbc073215af",
    "from_state": "implementation_running",
    "from_role": "Developer",
    "to_state": "gate_running",
    "to_role": "Reviewer",
    "retained_context_digest": "eaa4fed4a95df5a05b1629c1e15880253da3dd174d9e1b4693fe662d855f2775",
    "bootstrap_id": "b1605205d969bd5a0110383ede944018786fb7a2c94e708076b72fc33ed4cfb3",
    "evidence_commit": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
    "evidence_blob_sha": "e9d528a9c2b63b4a87dfcc6eaac74232942eeb54",
    "evidence_sha256": "1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
    "helper_blob_sha": "8bfc2f981fa1b1bec4183382303e24bba6be8b3b",
    "lane_head": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
    "range_paths": [
      "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md",
      "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_legacy-bootstrap-attestation.v1.json",
      "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
      "scripts/connlab_active_context.py",
      "scripts/connlab_execution_transition.py",
      "scripts/connlab_execution_transition_proof.py",
      "scripts/connlab_task_a_legacy_bootstrap.py",
      "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
      "tests/integration/test_connlab_execution_transition_recovery.py",
      "tests/integration/test_connlab_task_a_legacy_bootstrap_migration.py",
      "tests/unit/test_connlab_execution_transition.py",
      "tests/unit/test_connlab_execution_transition_proof.py",
      "tests/unit/test_connlab_task_a_legacy_bootstrap.py"
    ]
  },
  "transition_history": [
    {
      "transition_id": "367e000d5a4c93e060039b5a3cfd4f1ad88ac096500a994c62d8bdea94399968",
      "plan_digest": "5ac92b5060cbde4d647c0d173f9773119bc18ed360de5dd7650f180b8edf2f96",
      "event": "DEVELOPER_READY",
      "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
      "lane": "task-governance-active-context-deterministic-transition-and-event-handoff",
      "primary_head": "329c0343ea0e7f4d24d6fb7e2e986a094c304fd8",
      "expected_board_head": "3e73761673fd75de4e79028b0b8d0b89979bbd1a",
      "candidate_lane_head": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
      "evidence_ref": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@70e5c6a7606284e1fc55ac6b0497c6d9756b665f#1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
      "evidence_status": "ready_for_review",
      "range_digest": "758076d1217b9d15d547c3bdcf1f66262611203a34c804252e96fbbc073215af",
      "from_state": "implementation_running",
      "from_role": "Developer",
      "to_state": "gate_running",
      "to_role": "Reviewer",
      "retained_context_digest": "eaa4fed4a95df5a05b1629c1e15880253da3dd174d9e1b4693fe662d855f2775",
      "bootstrap_id": "b1605205d969bd5a0110383ede944018786fb7a2c94e708076b72fc33ed4cfb3",
      "evidence_commit": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
      "evidence_blob_sha": "e9d528a9c2b63b4a87dfcc6eaac74232942eeb54",
      "evidence_sha256": "1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56",
      "helper_blob_sha": "8bfc2f981fa1b1bec4183382303e24bba6be8b3b",
      "lane_head": "70e5c6a7606284e1fc55ac6b0497c6d9756b665f",
      "range_paths": [
        "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_legacy-bootstrap-attestation.v1.json",
        "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
        "scripts/connlab_active_context.py",
        "scripts/connlab_execution_transition.py",
        "scripts/connlab_execution_transition_proof.py",
        "scripts/connlab_task_a_legacy_bootstrap.py",
        "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
        "tests/integration/test_connlab_execution_transition_recovery.py",
        "tests/integration/test_connlab_task_a_legacy_bootstrap_migration.py",
        "tests/unit/test_connlab_execution_transition.py",
        "tests/unit/test_connlab_execution_transition_proof.py",
        "tests/unit/test_connlab_task_a_legacy_bootstrap.py"
      ]
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

## Active Execution Model

- `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`: `approved_reconciliation_preparation`. The User approved the exact amendment at `3e73761673fd75de4e79028b0b8d0b89979bbd1a`; the conflict-free local merge `a42ca37e205127afd87d4cdc1d26ede53830522c`, exact frozen 26-path package, zero-write blocked migration, and absent archive/index/audit remain preserved. Task A retains the sole token in `implementation_running/Developer` with expected target/head `3e737616...`; the physical lane is still clean at `e958ba37...`. Orchestrator must fast-forward that existing lane non-destructively, prove exact clean target HEAD, and obtain fresh `ALLOW_DISPATCH` before Developer receives a capsule. No helper/test/attestation edit, merge, migration, Task B work, push, runtime, or cleanup is authorized by this preparation commit. Planner evidence is `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_planner.md`; blocked Integrator evidence remains immutable.
- `TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER`: `planned_pending_user_approval`, strict serial dependency on Task A local Integrator acceptance, and separate User approval required afterward. Planning-only Task B defines per-command evidence reuse, fail-closed full-regate triggers, deterministic Windows validation runner, committed baseline-debt ledger, final-full QA, Integrator differential validation, exact TASK_368E replay, >=40% Reviewer command reduction, and measured medium pilot. Planned lane is `lane/task-governance-regate-evidence-reuse-baseline-ledger-and-validation-runner` in sibling worktree `D:\PythonProject\connlab-worktrees\task-governance-regate-evidence-reuse-baseline-ledger-and-validation-runner`; neither exists nor is authorized.
- `TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF`: `superseded_by_split_plans`. It is retained only as a non-executable umbrella/audit trace and cannot be approved, queued, assigned a token, given a branch/worktree, or dispatched. Its responsibilities are owned by serial Tasks A and B above.
- `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE` is complete. Added the official workspace service settings DTO, backend naming planner, preview/create application service, UTF-8 `.connlab/manifest.json` gateway, SQLite workspace index, FastAPI routes `GET/POST /api/projects/{project_id}/official-workspace/...`, frontend API client wiring, and a minimal Workbench single-primary-action state for `Create local project workspace`. Review follow-up fixed TASK_316 closure issues: preview now returns `completed` when ConnLab workspace record, manifest, and real file-system paths match; backend DL resolution prefers latest registered LTR over legacy `project.project_no`; Workbench identity and official folder naming now use the same project identity resolver, with the current Project sample/product description first and LTR setup `Test Item` for the test description; application-form requested testing remains a folder-name fallback before `Qualification test`; completed existing workspace records now remain `completed` when current naming rules change, with naming drift reported as a warning for later repair instead of blocking the user back into create mode; Workbench now reads only ordinary Settings registry locations for TASK_316 (`Project default save location` as local workspace root, `Template folder` as template parent/root, and `Public Project locations` for future public-drive upload readiness), with no hidden `settings.official_workspace` fallback; the real template layout `Template/DL-XXXX-YY-ZZZ project/DL-XXXX-YY-ZZZ Title` is supported; Settings path saves always reactivate visible path rows so stale inactive resources cannot silently block Workbench; Package preview now treats a completed TASK_316 official workspace record as a ready project folder target when no legacy `ProjectFolderRecord` exists; missing workspace/template setup shows a Workbench blocker reminder without a shortcut button, raw backend path, or `workspace paths` operator prompt; sidebar Projects restores the current Workbench context after navigating to Settings or another top-level page, while the Workbench back button still returns to the project list. Existing safe `{DL_NUMBER}/` folders are adoptable/continuable; existing planned official folders without a matching ConnLab record still block create; manifest/file-system/index mismatch returns repairable inconsistency; `Public Project locations` is warning-only; template copy stages into ConnLab-owned temp and writes manifest/index last. Scope boundary held: no public drive upload, no request material collection, no Test Record/Fee/Customer Feedback generation changes, no Section 2 write-back, no execution evidence/StepInstance/report/AI/permissions/multi-user work. Validation: `py -m pytest tests/unit/test_config.py tests/unit/test_external_resource_service.py tests/integration/test_external_resource_api.py -q` (`23 passed`); `py -m pytest tests/unit/test_official_project_workspace_service.py tests/unit/test_official_project_workspace_naming.py tests/integration/test_official_project_workspace_api.py tests/integration/test_api_default_dependencies.py -q` (`20 passed`); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or official_workspace or task316"` (`4 passed, 133 deselected`); `cd frontend; npm test -- --run ProjectWorkbench officialWorkspace --watch=false` (`25 passed`, existing mocked-error stderr only); `cd frontend; npm run build` passed; browser smoke verified Settings only exposes `Public Project locations` and sidebar Projects restores to current Workbench; follow-up browser smoke verified project `2cd4b0e7ff6f4df99448c9ffdd78629f` no longer exposes raw template paths, `Configure workspace paths`, task IDs, or `Test description unavailable`, now shows the official workspace as completed, and Package preview no longer reports the stale project-folder blocker. Additional identity smoke verified `DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing` in Workbench and planned official folder path; workspace status smoke verified existing `D:\Test Project\DL-2026-05-011` no longer re-enters create-blocked mode after the naming rule correction. Next recommended step is TASK_317 task file and executable plan review before implementation.
- `TASK_304_NEW_PROJECT_LAB_PERFORMING_TESTS_CONFIRMATION` is complete. New Project `Project setup confirmation` now includes required `Lab Performing the Tests*` with `Dongguan` / `Valley Green` options and `Dongguan` default. The value persists as `project_setup.lab_performing_tests`, draft autosave/update rejects unsupported non-empty lab values, completion API/service validates the value, and fresh/already-confirmed-not-registered completion promotes it into latest `ApplicationForm.lab` before LTR commit. Already-registered/idempotent completion preserves frozen `ApplicationForm.lab`. LTR readiness consumes the promoted `ApplicationForm.lab`, and Word Section 2 write-back now recognizes the real label `Lab Performing the Tests:` for the existing `lab` field. Validation: `py -m pytest tests/unit/test_intake_case_review_service.py tests/integration/test_new_project_completion_api.py tests/unit/test_ltr_readiness_service.py tests/unit/test_word_document_section2_write_gateway.py -q` (`35 passed`); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "new_project or section2 or task304"` (`8 passed`); `cd frontend; npm run build` passed; browser smoke on `http://localhost:5173/intake` confirmed label, options, and default. The planned Vitest target command found no matching test files in the current frontend test layout, so the behavior is covered by static shell tests plus build/browser smoke.
- `TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN` is complete. Matrix Editor now includes a planned `Day` column, selected-group `Test Days` summary, and compact `Project Schedule` card with native date inputs. Row `day_expression` and root planned schedule fields persist through Matrix draft/session/confirmed authority, with lightweight SQLite ensure-column migration for existing schemas. Confirm Matrix validates selected-row day expressions, non-negative buffer days, and calendar-day date sufficiency while leaving draft save tolerant of transient planning edits. Validation: `py -m pytest tests/unit/test_database.py tests/unit/test_matrix_schedule_planning.py tests/unit/test_project_matrix_draft_repository.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_project_matrix_draft_persistence_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_matrix_revision_flow_service.py tests/unit/test_matrix_editor_session_service.py tests/unit/test_matrix_import_commit_service.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_authority_api.py tests/integration/test_matrix_to_test_record_smoke_flow_api.py -q` (`82 passed`); `cd frontend; npm test -- --run matrixSchedulePlanning MatrixEditorWorkspace --watch=false` (`24 passed`); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task284 or matrix_editor"` (`39 passed`); `cd frontend; npm run build` passed; `git diff --check` passed with CRLF warnings only. Scope boundary held: no actual execution dates, no StepInstance, no execution persistence, no Word `SECTION 2` writeback, no Test Record/report generation changes.
- `TASK_284 follow-up` (2026-06-03) is complete. `Pre-test buffer` is removed from the Matrix Editor `Project Schedule` card and confirmation/validation chain while keeping `pre_test_buffer_days` in backend/domain models and API payloads for compatibility. UI now requires only `Sample received`, `Planned start`, `Test complete`, `Post-test buffer`, `Estimated completion` and applies simpler date checks: planned start must be on/after sample received; complete must be at least + longest group days from planned start; completion estimate must include post-test buffer. Auto-fill now derives `Test complete` and `Estimated completion` from `Planned start`, and updates completion estimate whenever post-test buffer changes. `Confirm` no longer uses pre-test buffer as a planning constraint. Current UI payload sends `pre_test_buffer_days: null` to preserve compatibility. Validation: `cd frontend; npm test -- --run matrixSchedulePlanning MatrixSchedulePlanningCard MatrixEditorWorkspace --watch=false` (`31 passed`); `py -m pytest tests/unit/test_matrix_schedule_planning.py -q` (`17 passed`); `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task284 or matrix_editor"` (`39 passed`); `cd frontend; npm run build` passed; `git diff --check` passed with CRLF warnings only. Scope boundary held: backend compatibility path preserved, no StepInstance, no execution persistence, no report generation changes.
- `TASK_043` added no-write registration preview with deterministic proposed number, readiness field mapping, conflict reporting, and snapshot context
- `TASK_081_FRONTEND_LOOKUP_API_FIELD_RENDERER_WIRING` is proposed: frontend should consume `GET /api/lookups/intake-precheck`, remove hardcoded select arrays, and treat `post_testing_disposition` as the same backend-managed select implementation as the other Intake/Precheck lookup fields.
- `TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI` is proposed for the next controlled task: make sample rows editable, add compact edit/copy/delete actions, preserve at least one row, and persist sample row corrections before project confirmation.
- `TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE` is proposed for the next controlled task: run deterministic SECTION 1 precheck before Project creation and show clear blockers/warnings.
- `TASK_084_PRECHECK_FRONTEND_STRUCTURE_EXTRACTION` is proposed for the next controlled task: extract Precheck field config, sample config, issue summary, named components, and maintainable feature style/token rules into a `features/precheck` boundary while preserving behavior and the recent Intake/Precheck readability fixes.

## Immutable History

- Generation 000001: `docs/archive/task_board_history/generation-000001-5cb439a2bbffa8408b48aa9ecb2cd79a82efcf22.md` (exact pre-maintenance board bytes).
