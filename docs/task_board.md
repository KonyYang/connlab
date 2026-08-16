# ConnLab Task Board

> Status Authority: Read `state` and `active` in the machine control block below; dynamic task status is not duplicated in human prose.
> Last Updated: 2026-08-14
> Current Source Of Truth: `docs/task_board.md`
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Execution Rule: WIP=1; occupied submissions wait with zero writes, while idle submissions classify into direct simple work or the automatic approved complex role chain.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.personal-serial-control",
  "version": 2,
  "mode": "personal_serial",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP",
    "summary": "Bootstrap an entirely absent administrator LTR workbook config with the public DGLAB default using exclusive atomic publication while preserving existing files, precedence, development and packaged paths, and all workbook/public-drive boundaries.",
    "kind": "planned",
    "classification": "complex",
    "phase": "integration",
    "scope_contract": {
      "may_touch": [
        "backend/shared/config.py",
        "connlab.admin.example.toml",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tasks/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP.md",
        "docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 13,
      "classification_reason": "Planned/complex because application startup gains administrator-authority persistence and controlled external filesystem mutation, changes a public business default, requires race-safe exclusive publication, and needs independent Reviewer, QA, and Integrator verification.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_config.py -q",
        "py -m pytest tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py -q",
        "py -m py_compile backend/shared/config.py tests/unit/test_config.py tests/unit/test_desktop_packaged_runtime_paths.py tests/unit/test_desktop_release_scripts.py",
        "Verify the exact task diff contains only the five approved implementation/test paths and passes git diff --check.",
        "Verify tests use only repository/disposable temporary roots and do not access or mutate real ProgramData, development administrator config, public drives, workbooks, installed releases, or user configuration.",
        "Verify existing administrator files are byte-preserved, concurrent first loads publish one complete file, environment presence including blank stays highest precedence, local password remains inert, and filesystem failures are actionable without fallback.",
        "Verify runtime_paths.py and both release scripts remain byte-unchanged while packaged path selection and example-only release shipping remain covered by tests."
      ],
      "forbidden_categories": {
        "api_contract": false,
        "database": false,
        "schema_or_migration": false,
        "persistence": true,
        "authority": true,
        "public_drive_workflow": false,
        "business_rule_semantics": true,
        "destructive_action": false,
        "external_mutation": true
      }
    },
    "plan_ref": "docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md@1ca021a61f556c9e3f8e195f02fb0dd36b603dfa#2146474d4de6e197003023307b2cb3470300c6c018ba9d44ca757b48f49aa1f6",
    "approval_ref": "批准",
    "activation_parent_sha": "e51a674b68ca1b4d1fe193b5e10903b361ae3660",
    "activated_at": "2026-08-16T02:52:24Z",
    "updated_at": "2026-08-16T03:18:56Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-ltr-workbook-public-default-admin-config-bootstrap",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-ltr-workbook-public-default-admin-config-bootstrap",
      "base_sha": "e51a674b68ca1b4d1fe193b5e10903b361ae3660",
      "head_sha": "e51a674b68ca1b4d1fe193b5e10903b361ae3660",
      "integration_target": "master",
      "worktree_lifecycle": "integration_ready",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "adf495e3a2fc5193bf2bde94b703a872b20550cad20c8fdbf3b435a4289ac036",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_public_default_bootstrap_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-16T02:53:38Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "ff17be341b801d16b85293183fdfd9b9c1478aa07a334ac40afb1f8ffc26d057",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_public_default_bootstrap_host",
          "host_id": "/root/ltr_public_default_bootstrap_host",
          "status": "started",
          "recorded_at": "2026-08-16T03:27:20Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "5e0a6d00185acdad6d862c60095e09dd894bca6901c4b34d2f4acc04683a3a9b",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_public_default_bootstrap_reviewer",
          "host_id": "/root/ltr_public_default_bootstrap_host",
          "status": "started",
          "recorded_at": "2026-08-16T03:41:28Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "4d899f39640b40097f698e165757fdaa787a793f03419f27a4dd6eff9d537060",
          "role": "QA",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_public_default_bootstrap_qa",
          "host_id": "/root/ltr_public_default_bootstrap_host",
          "status": "started",
          "recorded_at": "2026-08-16T03:53:33Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "5f0510ed9f01951c5a58c6e1ae2398d90f3aa9f9caf9a1a98bef9301af5bdb58",
          "role": "Integrator",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_public_default_bootstrap_integrator",
          "host_id": "/root/ltr_public_default_bootstrap_host",
          "status": "started",
          "recorded_at": "2026-08-16T04:05:07Z"
        }
      ],
      "host_thread_id": "/root/ltr_public_default_bootstrap_host",
      "host_id": "/root/ltr_public_default_bootstrap_host",
      "approved_code_paths": [
        "backend/shared/config.py",
        "connlab.admin.example.toml",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tasks/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP.md",
        "docs/task_ltr_workbook_public_default_admin_config_bootstrap_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "503a471a47cd69180822a6e3963c133a4fb68e81",
      "reviewer_subject_commit": "503a471a47cd69180822a6e3963c133a4fb68e81",
      "qa_subject_commit": "503a471a47cd69180822a6e3963c133a4fb68e81",
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_planner.md@1ca021a61f556c9e3f8e195f02fb0dd36b603dfa#7bc2ab530762c026ce09b9151153110fed0b27ad3985450266919ea2f8e3ca5d",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_developer.md@f733dbd33ca68530600f3f6019da6f7f511512ce#d7aa27a6b46b5e5dbcef81ed3823a5ed6a40f181e9e7868bcbacd3f43e76525d",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_reviewer.md@536f957aa941f156e78f562e71fee1e44452fdf7#564a4c60d758c89048d2e7a6d60c5338bebb5dfa61c19d79daa4be4f5058f7d9",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_qa.md@3d26a4460ea30d25cbcf2b3d653255dd7047dafb#97a70036d69b6dec204d7e6fefe16ce83219434d0579f005c074c6244445ae97",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP_integrator.md@93771222ce61d0b70cba9590a7db9a233397f1d7#58d540912b6c17ea602ef12d39b64d83c2f0edff34e7900b812d054385b0d628"
      ],
      "blocker_history": [],
      "pending_callback": null,
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null,
      "timing_facts": {
        "host": {
          "started_at": "2026-08-16T03:19:45Z",
          "completed_at": "2026-08-16T03:25:52Z"
        },
        "roles": [
          {
            "role": "Planner",
            "attempt": 1,
            "started_at": "2026-08-16T02:53:04Z",
            "completed_at": null
          },
          {
            "role": "Developer",
            "attempt": 1,
            "started_at": "2026-08-16T03:26:58Z",
            "completed_at": "2026-08-16T11:39:50+08:00"
          },
          {
            "role": "Reviewer",
            "attempt": 1,
            "started_at": "2026-08-16T03:40:55Z",
            "completed_at": "2026-08-16T11:48:52+08:00"
          },
          {
            "role": "QA",
            "attempt": 1,
            "started_at": "2026-08-16T03:52:33Z",
            "completed_at": "2026-08-16T12:02:23+08:00"
          },
          {
            "role": "Integrator",
            "attempt": 1,
            "started_at": "2026-08-16T04:04:01Z",
            "completed_at": "2026-08-16T12:13:30+08:00"
          }
        ],
        "integration_completed_at": null
      },
      "execution_routes": {
        "Developer": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:authority"
        },
        "Integrator": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:authority"
        },
        "QA": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:authority"
        },
        "Reviewer": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:authority"
        }
      },
      "validation_manifest": {
        "schema": "connlab.validation-manifest",
        "version": 1,
        "task_id": "TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP",
        "checks": [
          {
            "id": "config-bootstrap-authority",
            "kind": "targeted",
            "run_for": [
              "Developer",
              "Reviewer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-m",
              "pytest",
              "tests/unit/test_config.py",
              "-q"
            ],
            "timeout_seconds": 600,
            "permission": "pytest_temp",
            "required": true
          },
          {
            "id": "packaged-path-and-release",
            "kind": "full",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-m",
              "pytest",
              "tests/unit/test_desktop_packaged_runtime_paths.py",
              "tests/unit/test_desktop_release_scripts.py",
              "-q"
            ],
            "timeout_seconds": 600,
            "permission": "pytest_temp",
            "required": true
          },
          {
            "id": "config-bootstrap-compile",
            "kind": "static",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-m",
              "py_compile",
              "backend/shared/config.py",
              "tests/unit/test_config.py",
              "tests/unit/test_desktop_packaged_runtime_paths.py",
              "tests/unit/test_desktop_release_scripts.py"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          }
        ]
      }
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN",
    "disposition": "retained",
    "decision_ref": "关闭",
    "integration_commit": "e56f3ef78168d9541f7e21b402e0feac3d041aaf",
    "integrator_evidence_ref": "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md@b3507acc2cc444f6ec7e6c1a71900bcbd9a83e0c#edfc81750dc5dad81b68906e4e01c745a53d7d93b37ffe6e79a1903ad7d52cf8",
    "retained_resources": {
      "thread_id": "/root/ltr_admin_runtime_config_host",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-ltr-workbook-admin-runtime-config",
      "branch": "codex/task-ltr-workbook-admin-runtime-config",
      "head_sha": "ff01fb1d725c98fb58a3e343cf241076853e8cfa"
    },
    "closed_at": "2026-08-16T01:13:03Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
      "status": "cancelled",
      "owner": "User / manual governance",
      "disposition": "retain clean Task-A lane and all evidence; no automatic adoption, merge, rewrite, deletion, or role dispatch",
      "evidence": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md@85e71dfa212c57c26527fad42eaf00a83b19c935#f1ca9341149d567958d837c18932e25ddee1ad47189266d0de73a03540e6de3a",
      "branch": "lane/task-governance-active-context-deterministic-transition-and-event-handoff",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-active-context-deterministic-transition-and-event-handoff",
      "head": "85e71dfa212c57c26527fad42eaf00a83b19c935"
    },
    {
      "task_id": "TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH_integrator.md",
      "branch": "lane/task-governance-wip1-and-proportionate-quick-fix-fast-path",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-wip1-and-proportionate-quick-fix-fast-path",
      "head": "600bbf2d8d6b7884fed6a3af4e46f56cce3fe3a3"
    },
    {
      "task_id": "TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md",
      "branch": "lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix",
      "head": "45f345f49c43eece139245b00048c74e8c83f73b"
    },
    {
      "task_id": "TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368E_matrix-import-optional-standard-version-fallback-and-copy-clarity_integrator.md",
      "branch": "lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity",
      "head": "c9a61bcb701178c1042d99ca8011d138e0420330"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

## Active Work

- The machine control block is the sole current-status authority. Read its `state` and `active`
  fields before submitting, continuing, reviewing, or closing work.
- This section intentionally contains no dynamic task identity or idle/running claim.

## Queue

- Version-2 queue compatibility fields are inert and have no daily operation entry. Submission
  availability is determined only by the machine control block's `state` and `active` fields.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.
- `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING` auxiliary reconciliation/proof resources are retained. After the first subsequent real task completes and the User closes it, report `CLEANUP_READY` and request explicit cleanup authorization.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
