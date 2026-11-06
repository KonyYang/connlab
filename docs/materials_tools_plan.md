# Materials and independent planning tools

## Outcome
Replace Intake temporary-project creation with Save materials. Preserve existing Intake autosave and formal LTR registration. Tools owns a standalone Matrix editor and linked fee estimate without creating database projects or authority records.

## Boundaries
- Save original email, application and attachments into a configured materials root, with editable email-derived folder name and preview. Never overwrite existing directories/files. Do not clear or navigate away from Intake.
- Settings uses the existing external-resource configuration for the materials root; no new managed-material entity/schema.
- Reuse Matrix parsing/editing/export and fee rules through explicit standalone adapters. A browser session retains Matrix and fee edits across tool navigation; explicit exports retain longer-term work.
- Retire temporary-project creation/lifecycle UI. Preserve existing data and provide a read-only recovery entry to Tools for old temporary URLs. Formal projects retain their workflows.

## Verification
Isolated file-copy byte equality and conflict/path safety; Intake state preservation; resource configuration; full standalone Matrix/Fee editing and import/export with no project creation; existing formal regression; independent review and final QA including browser checks. No real business-file writes, push, or publication.

## Implemented seams
- `IntakeMaterialsService` receives repositories and a filesystem protocol. The adapter checks existing non-reparse roots, creates the child exclusively, and opens every output in exclusive mode. Partial failures retain files and identify the destination rather than risking deletion of concurrent user files.
- Tools has stateless Matrix preparation/export, shared fee calculation, configured-template Fee Form export/import, and read-only legacy recovery endpoints. The existing project calculator delegates to the same pure builder.
- Shared Matrix hooks receive standalone persistence/import/export/method-check adapters. Tools keeps browser-session state and reports storage failure. Project record/publication controls are hidden in Tools.
- Legacy pricing matches group/row/step identity, reports unmatched manual/inactive rows, and retains the complete original edit payload for download. No new schema or managed-material entity.

## Developer validation (2026-11-06)
- RED/GREEN: materials service missing module -> 7 initial cases passed; standalone Matrix initially stuck at project loading -> rendering passed; missing Tools fee calculator -> real LLCR price/point units passed.
- Materials service boundary suite: 11 passed (original bytes, existing-name refusal, path traversal/reserved names, Unicode/duplicate attachments, partial-copy retention, absent root/source, reparse rejection).
- Tools Matrix/Fee unit suite: 5 passed (real fee rules, duration and point inputs, stable identities, exact legacy pricing transfer, unmatched/manual/inactive and unselected-group recovery).
- Tools API integration: 4 passed. Actual repositories/configuration copy email+application and keep the entire SQLite dump unchanged; existing destination returns 409. Matrix XLSX export/read/prepare preserves fields with no DB writes. Fee XLSX download/import preserves edited price/units and the configured template bytes. Legacy read restores saved edits without changing any DB table.
- Intake/CompletionDock/initial standalone UI: 22 passed; includes dialog input focus, retained edited phone/quantity, no navigation/TMP creation or LTR action. Shared Matrix persistence plus standalone reopening: 11 passed. Tools Fee UI: 2 passed (manual edits retained on re-entry/Matrix change, late calculation ignored after unmount). Catalog: 4 passed, including hidden retained TMP and linked copy.
- Shared formal fee engine regression included in a 38-test passing batch. Existing frontend formal persistence lifecycle: 9 passing cases above.
- TypeScript build checked; final exact-state verification and independent review/QA evidence are recorded by the main task workflow.

## Acceptance and remaining verification
Independent Reviewer and QA run after the fixed developer commit. QA should exercise desktop browser layout/focus/Escape, Settings directory picker, Word/PDF/XLSX Matrix import and method-version resource errors, Matrix→Fee→Matrix navigation, Fee import comparison/download, legacy URL recovery and formal project smoke paths. Developer checks cover actual native XLSX roundtrip; Word/PDF/Office COM parsing continues through the established adapters and requires the configured runtime for interactive checks.

The Tools session is per browser tab, not a new managed project registry. Export before closing the browser for durable files. Original materials are copied unchanged; Intake field edits remain in existing Intake autosave rather than being silently rewritten into application files. A partially failed materials save requires checking the reported folder and choosing a new name. No real business file was overwritten, and no push or release was performed.
