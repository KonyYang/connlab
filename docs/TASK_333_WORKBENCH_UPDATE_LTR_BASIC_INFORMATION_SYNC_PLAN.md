# TASK_333 Workbench Update LTR Basic Information Sync Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_332_OFFICIAL_OUTPUT_HEADERS_CONSUME_BASIC_INFORMATION` is currently planned and awaiting explicit approval on `docs/task_board.md`.

This `TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC` plan is a later candidate task requested by the user. It must not be implemented until the user explicitly approves this task and the board sequencing is updated.

## Goal

Make the Workbench `Basic Information` card `Update LTR` button update the public-drive LTR registration workbook configured in setup by using the existing post-registration LTR workbook Basic Information sync preview/commit API.

## Existing Behavior

### Setup Workbook Path

The setup page `LTR registration workbook` path is the existing external resource path used by the backend LTR workbook transaction gateway.

Relevant existing files:

- `frontend/src/features/settings/settingsResourceConfig.ts`
- `backend/shared/config.py`
- `backend/application/external_resource_service.py`
- `backend/desktop/path_picker_api.py`
- `backend/infrastructure/files/windows_path_picker.py`
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`

No new workbook path source is needed for this task. The `Update LTR` flow should use the same configured path indirectly through the existing backend dependency wiring.

### Initial LTR Application

Initial LTR application is handled by the New Project completion path.

Relevant existing files:

- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/ltr_excel_authority_adapter.py`
- `backend/api/routes_ltr_workbook.py`

This path writes an initial registration row and can create or register a local LTR record. It is not the correct path for `Update LTR` because the Workbench button must update an existing row, not request a number or append a row.

### Existing Backend Sync API

`TASK_331` already added the backend workflow this frontend task should reuse.

Relevant existing files:

- `backend/api/routes_ltr_workbook_basic_information_sync.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

Existing routes:

- `GET /api/projects/{project_id}/ltr-workbook/basic-information-sync/preview`
- `POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/commit`

Existing backend guarantees:

- Preview opens the workbook read-only.
- Preview returns `status="ready"` or `status="blocked"`.
- Preview locates the existing row with `find_ltr_number()`.
- Commit validates Basic Information version and source-signature hash from preview.
- Commit uses a locked transaction and backup.
- Commit writes only the existing row.
- Commit never appends a row and never creates a new LTR record.

## Product Decision

`Update LTR` belongs in the Project Workbench `Basic Information` card, below the folder action card, because the operation refreshes project-level LTR metadata from confirmed Basic Information after the operator returns to Workbench.

The Basic Information page itself is not the right place because confirming Basic Information navigates back to Workbench, and the LTR workbook update is a separate public-drive write operation that needs preview and confirmation.

## UX Flow

1. The Workbench `Basic Information` card always shows `Update LTR`.
2. If Basic Information is not confirmed, `Update LTR` is disabled with a nearby title/disabled reason.
3. If Basic Information is confirmed, clicking `Update LTR` calls the preview API.
4. While preview loads, the card shows a compact in-card loading state.
5. If preview is blocked, the card shows the blocker text and no commit action.
6. If preview is ready, the card shows:
   - LTR number
   - workbook path
   - target sheet
   - target row
   - Basic Information version
   - a compact list/table of target row values to be written
7. The operator confirms from the in-card preview.
8. Commit uses the preview version/hash.
9. On success, the card shows the sheet, row, and backup path.
10. If Basic Information changed after preview, show `Basic Information changed after preview. Refresh before updating LTR.`
11. If workbook lock fails, show a workbook-lock message telling the operator to close or retry after the workbook is free.

Use an inline card expansion instead of a modal. This follows ConnLab's product principle: preview before write, state before action, and workflow before isolated tools.

## Data Flow

```text
Workbench Basic Information card
  -> frontend API client preview function
  -> GET /api/projects/{project_id}/ltr-workbook/basic-information-sync/preview
  -> backend reads latest registered local LTR
  -> backend reads latest confirmed Basic Information
  -> backend opens configured LTR workbook path read-only
  -> backend finds existing row by LTR number
  -> frontend displays preview
  -> operator confirms
  -> frontend API client commit function
  -> POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/commit
  -> backend revalidates version/hash
  -> backend locks workbook, creates backup, writes existing row, saves
```

## API Contract To Add In Frontend

Modify `frontend/src/api/client.ts`.

Add types:

```ts
export type LtrWorkbookBasicInformationSyncColumn = {
  column: string;
  field_name: string;
  value: unknown;
};

export type LtrWorkbookBasicInformationSyncPreview = {
  status: "ready" | "blocked";
  project_id: string;
  ltr_number: string;
  workbook_path: string | null;
  target_sheet: string | null;
  target_row: number | null;
  columns: LtrWorkbookBasicInformationSyncColumn[];
  confirmed_basic_information_version: number | null;
  confirmed_basic_information_source_signature_hash: string | null;
  blockers: string[];
  warnings: string[];
};

export type LtrWorkbookBasicInformationSyncCommitInput = {
  operator_confirmed: boolean;
  preview_acknowledged: boolean;
  expected_confirmed_basic_information_version: number;
  expected_confirmed_basic_information_source_signature_hash: string;
};

export type LtrWorkbookBasicInformationSyncCommit = {
  project_id: string;
  ltr_number: string;
  workbook_path: string;
  backup_path: string;
  sheet_name: string;
  row_number: number;
  confirmed_basic_information_version: number;
  confirmed_basic_information_source_signature_hash: string;
};
```

Add functions:

```ts
export function previewLtrWorkbookBasicInformationSync(
  projectId: string
): Promise<LtrWorkbookBasicInformationSyncPreview> {
  return requestJson<LtrWorkbookBasicInformationSyncPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/basic-information-sync/preview`
  );
}

export function commitLtrWorkbookBasicInformationSync(
  projectId: string,
  input: LtrWorkbookBasicInformationSyncCommitInput
): Promise<LtrWorkbookBasicInformationSyncCommit> {
  return requestJson<LtrWorkbookBasicInformationSyncCommit>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/basic-information-sync/commit`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}
```

## Frontend Component Design

Modify `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`.

Add props:

```ts
type ProjectBasicInformationSummaryCardProps = {
  projectId: string;
  basicInformation: ProjectBasicInformationResponse | null;
  loading: boolean;
  error: string | null;
};
```

Add local state:

```ts
const [ltrPreview, setLtrPreview] =
  useState<LtrWorkbookBasicInformationSyncPreview | null>(null);
const [ltrPreviewLoading, setLtrPreviewLoading] = useState(false);
const [ltrCommitLoading, setLtrCommitLoading] = useState(false);
const [ltrSyncMessage, setLtrSyncMessage] = useState<string | null>(null);
const [ltrSyncError, setLtrSyncError] = useState<string | null>(null);
```

Add preview handler:

```ts
async function handlePreviewLtrSync(): Promise<void> {
  if (!canUpdateLtr) {
    return;
  }
  setLtrPreviewLoading(true);
  setLtrSyncError(null);
  setLtrSyncMessage(null);
  try {
    const preview = await previewLtrWorkbookBasicInformationSync(projectId);
    setLtrPreview(preview);
  } catch (error) {
    setLtrSyncError(getLtrSyncOperatorMessage(error, "preview"));
  } finally {
    setLtrPreviewLoading(false);
  }
}
```

Add commit handler:

```ts
async function handleCommitLtrSync(): Promise<void> {
  if (
    !ltrPreview ||
    ltrPreview.status !== "ready" ||
    ltrPreview.confirmed_basic_information_version === null ||
    !ltrPreview.confirmed_basic_information_source_signature_hash
  ) {
    return;
  }
  setLtrCommitLoading(true);
  setLtrSyncError(null);
  try {
    const result = await commitLtrWorkbookBasicInformationSync(projectId, {
      operator_confirmed: true,
      preview_acknowledged: true,
      expected_confirmed_basic_information_version:
        ltrPreview.confirmed_basic_information_version,
      expected_confirmed_basic_information_source_signature_hash:
        ltrPreview.confirmed_basic_information_source_signature_hash
    });
    setLtrSyncMessage(
      `LTR workbook updated: ${result.sheet_name} row ${result.row_number}. Backup: ${result.backup_path}`
    );
    setLtrPreview(null);
  } catch (error) {
    setLtrSyncError(getLtrSyncOperatorMessage(error, "commit"));
  } finally {
    setLtrCommitLoading(false);
  }
}
```

Add a small frontend error mapper rather than passing `error.message` through directly:

```ts
function getLtrSyncOperatorMessage(error: unknown, action: "preview" | "commit"): string {
  const message = error instanceof Error ? error.message : "";
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes("changed after preview") || lowerMessage.includes("stale")) {
    return "Basic Information changed after preview. Refresh before updating LTR.";
  }

  if (
    lowerMessage.includes("lock") ||
    lowerMessage.includes("permission") ||
    lowerMessage.includes("being used")
  ) {
    return "The LTR workbook appears to be open or locked. Close it and retry.";
  }

  if (lowerMessage.includes("not found")) {
    return "The registered LTR row was not found in the configured workbook.";
  }

  return action === "preview"
    ? "Unable to preview the LTR workbook update."
    : "Unable to update the LTR workbook.";
}
```

Render an inline preview surface below the card actions:

- Blocked preview: show blockers.
- Ready preview: show workbook context and a compact table of target row values to be written.
- Commit button label: `Confirm LTR update`.
- Secondary action: `Cancel`.

The card must not show raw Python stack traces, backend object names, or raw technical API messages. Use the frontend error mapper above for stale preview, workbook lock/permission, missing row, and generic preview/commit failures. Returned backend business blockers can be shown as-is when they are already operator-facing.

## Parent Wiring

Modify the Workbench component that renders the card:

- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`

Pass the current `projectId` into `ProjectBasicInformationSummaryCard`.

Update tests that instantiate the card directly:

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

## Styling

Modify `frontend/src/workbench.css`.

Add styles for:

- `.runtime-console-ltr-sync-preview`
- `.runtime-console-ltr-sync-context`
- `.runtime-console-ltr-sync-columns`
- `.runtime-console-ltr-sync-error`
- `.runtime-console-ltr-sync-message`

Rules:

- Keep the preview inside the Basic Information card.
- Use the existing form/button vocabulary.
- Avoid modal-first behavior.
- Use a compact table/list because this is operational metadata, not a marketing surface.

## Test Plan

### Frontend API Client

Add or extend tests if this repository has direct API-client test coverage. If no API-client unit test exists, cover calls through component mocks.

Expected assertions:

- Preview calls `/api/projects/P1/ltr-workbook/basic-information-sync/preview`.
- Commit posts expected version/hash.

### Summary Card Unit Tests

Modify `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`.

Add tests:

1. `Update LTR` remains visible but disabled without confirmed Basic Information.
2. Clicking enabled `Update LTR` renders ready preview context.
3. Ready preview commit sends:
   - `operator_confirmed: true`
   - `preview_acknowledged: true`
   - expected Basic Information version from preview
   - expected Basic Information source hash from preview
4. Blocked preview displays blockers and does not render commit action.
5. Successful commit displays sheet, row, and backup path.
6. Commit error displays actionable error text.

### Workbench Integration Tests

Modify `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`.

Add or update tests:

- Basic Information card receives `projectId` and clicking `Update LTR` can preview from Workbench.
- The card remains below Folder Action as currently required.

### Backend Regression Tests

Run existing TASK_331 backend tests:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
```

No backend test changes are expected unless frontend work uncovers an existing DTO mismatch.

## Validation Commands

After implementation approval:

```powershell
cd frontend; npm test -- --run ProjectBasicInformation ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
git diff --check
```

## Risks

- Workbook may be open or locked by another user. Existing backend maps this to conflict, frontend must show a retry/close-workbook message.
- Basic Information may change after preview. Existing backend rejects stale context; frontend must ask the operator to preview again.
- The existing preview returns target row values to be written for all write columns, not a true old-vs-new diff. If users need before/after comparison later, that should be a separate backend enhancement task.
- `TASK_332` is currently planned on the board. `TASK_333` must not be implemented until explicitly approved and sequenced.

## Review Checklist

- Scope does not call initial LTR registration.
- Scope does not append workbook rows.
- Scope does not directly manipulate Office files from frontend or API route bodies.
- Scope uses existing setup workbook path through backend dependencies.
- Scope keeps preview before write.
- Scope keeps Workbench card placement and disabled-state behavior.

## Stop Point

Stop after this plan is reviewed. Do not implement until the user explicitly approves `TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC`.
