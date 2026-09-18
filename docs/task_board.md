# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "idle",
  "active": null,
  "last_closed": {
    "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
    "tier": "standard",
    "subject": "Add fee summary acceptance contract fixtures and cross-stack tests",
    "summary": "Pinned frontend/backend fee-summary derivation to shared golden samples from docs/fee_confirmation_contract.md without changing business formulas. Backend 20/20, frontend model 10/10, frontend page 2/2 acceptance tests pass.",
    "disposition": "completed",
    "decision_ref": "User approved adjusted scope on 2026-09-18: contract.md authoritative, JSON as shared acceptance samples, numeric equivalence assertions, report-only on drift.",
    "closed_at": "2026-09-18T03:01:50.000000Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_ENVIRONMENT_DEBT_CLEANUP

**Tier:** standard  
**Discovered during:** TASK_361A acceptance run on 2026-09-18  
**Goal:** Make the backend pytest suite runnable to completion inside the current agent/WorkBuddy session.

**Observed blockers:**

1. **Managed Python 3.13.12 lacks tkinter.** `backend/api/dependencies.py:367` ultimately imports `windows_path_picker.py`, which does a top-level `from tkinter import ...`. Running `pytest tests` with the managed Python fails at collection for ~109 test files (`ModuleNotFoundError: tkinter`). Current workaround: use `C:/Python313/python.exe` for full-suite runs.
2. **WorkBuddy safe-delete hook intercepts test cleanup.** The sitecustomize.py injected by the agent runtime raises `SystemExit(1)` once per-turn deletions exceed threshold 50. Tests that use `path.unlink()` or `shutil.rmtree()` (e.g. `test_config.py`, `test_database.py`, `test_packaging_notes.py`) hit `SAFE_DELETE_BULK_CONFIRM_REQUIRED`. This makes even targeted runs fail after the threshold is reached, and single-file reruns fail with a higher count because temp dirs accumulate.
3. **Office COM crashes during matrix-preview integration tests.** `tests/integration/test_project_test_plan_preview_api.py:63` triggers Word COM calls that crash with Windows fatal exception `0x800706be` / `0x800706ba` inside `word_document_gateway.py`. This aborts the process rather than producing a normal test failure.

**Proposed remediation directions:**

- Add `tkinter` to the managed Python venv (or switch backend test runs to system Python with tkinter).
- Configure pytest `--basetemp D:/PythonProject/connlab/tmp/pytest-tmp` and, if the safe-delete hook allows, scope temp cleanup outside the bulk-delete threshold. Alternatively, run the suite in an environment where the hook is not injected.
- Isolate COM-dependent integration tests behind an `office` or `com` pytest marker and skip them in the standard CI/agent run unless an Office instance is confirmed healthy.

**Acceptance criteria:** `pytest tests -q` passes to completion (or cleanly skips COM tests) without manual intervention, using the project's documented Python runtime.
