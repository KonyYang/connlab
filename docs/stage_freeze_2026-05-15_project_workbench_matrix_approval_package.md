# ConnLab Stage Freeze (2026-05-15)

## Freeze Statement

As of 2026-05-15, ConnLab is no longer in the original early MVP-only stage.

Current practical stage is:

`Project Workbench / Matrix / Approval Package`

This freeze records implemented baseline capabilities and scope boundaries for subsequent controlled tasks.

## Implemented Baseline (Frozen)

1. New Project intake/precheck with structured draft and duplicate-handling workflow.
2. LTR registration path aligned to workbook authority and completion orchestration.
3. Project Workbench as post-confirmation work surface.
4. Matrix test-plan draft lifecycle:
   - source preview/import path;
   - draft persistence;
   - reviewed authority and candidate editing semantics;
   - authority workspace UI surface.
5. Section 2 preview and controlled write-back pipeline.
6. Test-record/fee dataset preview and controlled document generation.
7. Approval package preview/execute flow with project-folder placement rules.
8. Output version ledger/status for downstream stale/fresh checks.

## Deferred/Excluded At This Freeze

1. AI review and autonomous decisioning.
2. Full report-generation/audit workflow beyond current approval-package pipeline.
3. Multi-user permissions and LAN/server deployment model.
4. Non-`.docx` Matrix parsing expansion (`.doc`/PDF as full supported import path).

## Governance Rule For Next Tasks

- Do not rewrite core architecture for cleanup only.
- Keep evolution task-driven through `docs/task_board.md`.
- Any stage escalation beyond this freeze requires a new explicit board/task activation.

