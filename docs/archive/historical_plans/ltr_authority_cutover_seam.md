# LTR Authority Cutover Seam

## Current mode (Phase 10E)

- Official LTR number authority: configured external workbook flow.
- Commit path: `NewProjectCompletionService` -> `LtrAuthorityPort` -> `ExcelWorkbookLtrAuthorityAdapter` -> `LtrWorkbookWriteCommitService`.
- Local SQLite `LtrRecord` role: structured local copy after successful authority commit; not the official authority source while Excel mode is active.

## Why this seam exists

`NewProjectCompletionService` and API orchestration should speak in authority terms, not workbook/COM details. This keeps high-level workflow stable when authority changes.

## Future server cutover

When server authority is available:

1. Implement a new adapter that satisfies `LtrAuthorityPort` (for example `ServerLtrAuthorityAdapter`).
2. Change dependency wiring in `get_ltr_authority_service`.
3. Keep `NewProjectCompletionService` and route contracts unchanged.
4. Preserve local SQLite behavior as needed (mirror/cache/audit) under explicit policy.

No UI route should import workbook transaction gateway or COM classes directly.
