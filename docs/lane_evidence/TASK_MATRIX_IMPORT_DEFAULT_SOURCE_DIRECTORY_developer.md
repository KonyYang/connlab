TASK_ID: TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY
ROLE: Developer
STATUS: developer_blocked
SUBJECT: 60068858e1216e21ff5977b934625bc59d2113a8
COMMIT: 60068858e1216e21ff5977b934625bc59d2113a8
ATTEMPT: 2
ACTION_ID: b078cf89f9e462edb2a74a981d2708acc8f87e655bb073586e0dcc3474fabb48
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:cross_frontend_backend

BLOCKER_CODE: BLOCKED_SCOPE_REQUIRED
BLOCKER_STAGE: development
BLOCKER_FINDINGS: Reviewer R1 requires the local-path reloadImportPreview request to preserve page number, table-on-page index, and table-text query exactly like the upload branch.
MISSING_PATHS:
- backend/api/routes_project_test_plan.py
- tests/integration/test_project_test_plan_preview_api.py
BLOCKER_REASON: MatrixPreviewFromPathCommand already supports the locator fields, but the current path API request schema exposes only source_path and project_id, and the route constructs the command without locator values. Frontend-only changes would be ignored by the backend and would not truthfully fix R1.

ZERO_WRITE_FACTS:
- Candidate was clean at 5c30adf890f879789b3cbb9696968f4c21a75d2d before this evidence-only record.
- No implementation or test file was modified.
- No validation was rerun because the required production contract path is outside the approved scope.
- No primary or board write, push, cleanup, reset, restore, stash, rebase, merge, or destructive action occurred.

NEXT: User scope decision through the production Personal Serial V2 workflow.
