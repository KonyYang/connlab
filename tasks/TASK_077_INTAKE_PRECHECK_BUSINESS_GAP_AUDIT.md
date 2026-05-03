# TASK_077_INTAKE_PRECHECK_BUSINESS_GAP_AUDIT

## Status

done

## Goal

Audit the current real-business Intake and Precheck UI/backend flow before any broad redesign or functional completion work.

## Why This Task Is Allowed Now

- Current board state has no active implementation task after `TASK_076`.
- The user explicitly approved auditing Intake and Precheck before broad UI completion.
- This task is documentation-only and does not activate Phase 10B.
- The audit stays inside MVP intake/precheck scope.

## Scope

- Review current Intake and Precheck frontend pages.
- Review related frontend API DTOs and client calls.
- Review backend intake package, selected form, case review, manual intake, confirmation, parser, and precheck logic.
- Identify mismatches between UI controls, backend contracts, parser output, persisted records, and MVP business rules.
- Produce a controlled fix sequence for later tasks.
- Document what business information the user should provide to complete the next implementation tasks safely.

## Out Of Scope

- No frontend code refactor.
- No backend behavior changes.
- No field implementation.
- No route or API contract changes.
- No copied-workbook LTR write hardening.
- No Outlook inbox auto-scan or email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope feature.

## Design Notes

- Use `docs/frontend_architecture_rules.md` as the frontend boundary rule.
- Treat route pages as current evidence, not as the target structure.
- Separate issues into UI layout, frontend state, backend contract, parser, persistence, and business-policy gaps.
- Recommend small implementation tasks rather than one large broad rewrite.

## Completion Notes

- Added `docs/intake_precheck_business_gap_audit.md`.
- Added a documentation regression test for the audit and task board state.
- Updated `docs/task_board.md` with the audit completion and next recommended task.
- No runtime code was changed.

## Validation Result

- `py -m pytest tests\unit\test_intake_precheck_business_gap_audit.py -q`: `2 passed`

## Stop Condition

Stop after audit documentation and board sync. Do not proceed into Intake/Precheck implementation, frontend refactor, or Phase 10B without explicit user approval.

