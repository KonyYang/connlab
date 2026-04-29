# Phase 7 Validation Summary

Date: 2026-04-29

Status: Phase 7 complete. No later phase is active until the user explicitly approves the next scope.

## Scope Closed

Phase 7 covered the controlled real intake-to-registration path:

- real `.msg` and `.docx` baseline documentation
- parser calibration for real-style application forms
- LTR readiness catalog, number rules, readiness API, preview, local commit, Excel COM write boundary, and renumber planning
- project folder evidence placement
- lifecycle guards
- exception workflows
- read-only lookup surfaces for project, sample, and testing condition/method review

Phase 7 did not implement Matrix, Test Record, Report, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or email sending.

## Validation Results

Latest full backend regression:

- Command: `py -m pytest -q`
- Result: `203 passed`

Latest static diff check:

- Command: `git diff --check`
- Result: passed with line-ending warnings only

Frontend build:

- Not rerun for `TASK_051` because this task made no frontend or UX-copy changes.
- Existing Phase 5/6 validation records include successful `npm run build` runs.

Real sample validation evidence:

- `.msg` baseline: 4 local real samples were readable by the current gateway; originals remain outside Git.
- `.docx` baseline and calibration: 2 real forms were used for safe parser coverage probes; generated real-style fixtures now cover footer form/revision, request fields, requested testing, sample rows, and lab section behavior.
- LTR workbook layout: the decrypted local `.xls` reference was opened read-only through Excel COM; annual sheets `2020`-`2026`, A:Q registration columns, and DL column D were confirmed. No save or write was attempted.

## Workbook Write Mode

The external LTR workbook write path is implemented only as a guarded OfficeFacade/Excel COM boundary.

- Write mode is disabled by default.
- Workbook path and password are configuration-driven.
- The expected default password may be configured as `DGLAB`, but the implementation must not hard-code that value.
- Missing or invalid workbook access must not create a local registered state.
- Normal LTR allocation is intentionally deferred to the Excel write session after reading the current workbook state.
- `TASK_051` did not mutate any real workbook.

## Manual Smoke Checklist

Before using the Phase 7 path operationally, run this checklist on a local copy of real files:

1. Import a `.msg` package and confirm source metadata and attachments are preserved.
2. Review no-form and multi-form package exception outcomes.
3. Select each valid application form and confirm a separate review case/draft is created.
4. Confirm a case with required missing information and verify project creation is blocked with actionable missing fields.
5. Confirm a complete case and verify Project, ApplicationForm, SampleInfo, FileAsset, and IntakeCase linkage.
6. Run LTR readiness and verify missing fields block registration preview.
7. Run LTR preview and verify no workbook write occurs.
8. Run local LTR commit only after operator confirmation and verify audit notes.
9. If workbook write is explicitly enabled in config, use a copied workbook first and verify Excel is released after success or failure.
10. Run folder preview/generation and verify existing target conflicts are blocked.
11. Run evidence placement preview/execution and verify no source files are overwritten.
12. Try invalid lifecycle actions and verify the API blocks them with business-readable messages.
13. Use project lookup, sample summary, and testing summary endpoints to confirm operators can review structured records before downstream work.

## Known Limits

- Browser-based manual frontend smoke was not executed by Codex during `TASK_051`.
- PyWebView packaging and full installer creation remain future work.
- Real `.msg`, `.docx`, and `.xls` samples remain local and uncommitted.
- External workbook write requires explicit configuration and should first be verified against a workbook copy.
- Lookup surfaces are backend/API only in Phase 7; no new frontend lookup panel was added.
- Report generation, Matrix planning, AI review, permissions, LAN deployment, Outlook inbox auto-scan, and email sending remain out of scope.

## Next Recommendation

Stop after Phase 7. The next phase should be activated only after explicit user approval.

Recommended next-phase candidates:

- Phase 8A: frontend/operator workflow wiring for the Phase 7 backend routes, using the project-wide `$impeccable` UI rule.
- Phase 8B: operational hardening for controlled LTR workbook write on copied workbooks, including manual recovery guidance.

Do not activate either candidate automatically.
