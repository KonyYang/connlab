# TASK_034_ATTACHMENT_AWARE_PRECHECK_BRIDGE

## Status

done

## Goal

Pass registered supporting attachments into deterministic precheck context.

## Scope

- Make precheck aware of project `FileAsset` records created from intake packages.
- Use registered supporting attachments to evaluate “see attachment” style requested testing text.
- Keep deterministic rules only.
- Preserve existing precheck API behavior unless explicitly revised.

## Out Of Scope

- Parsing attachment contents.
- AI review.
- Matrix, report, or Excel ingestion.
- Frontend changes.
- Outlook inbox auto-scan.

## Required Implementation

- Add or adapt backend precheck context so registered project attachments can be considered.
- Add tests for requested-testing cases with and without supporting attachments.
- Run targeted precheck tests and the full backend suite.

## Validation

- Run targeted pytest coverage for attachment-aware precheck.
- Run full backend pytest suite before closing.
