# TASK_351 Fee Evaluation Auto Default Fill Implementation Reconciliation Evidence

Task: `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL`
Lane: `fee-evaluation-auto-default-fill`
Role: Planner
Status: implementation authorized - pending Developer implementation
Date: 2026-07-05

## Scope

Minimal Planner source-of-truth reconciliation after Reviewer implementation-readiness passed and the user explicitly approved `TASK_351` reconciliation plus Developer implementation.

This pass updates governance/planning documents only. It does not modify product code, backend, frontend, tests, API client, fee seed JSON, real workbook/public-drive/folder data, release artifacts, `.agents/**`, or `docs/project_management/**`.

## Required Reads

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL.md`
- `docs/task_351_fee_evaluation_auto_default_fill_plan.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_developer.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_reconciliation_planner.md`
- Current `git status --short`

## Reconciled Fact Chain

1. Planner created and updated TASK_351 as a planned formal Fee Evaluation auto default-fill lane.
2. Reviewer plan gate passed.
3. User approved Developer planning-first.
4. Developer planning-first completed and updated TASK_351 plan/evidence only.
5. Reviewer implementation-readiness passed.
6. User explicitly approved `TASK_351` reconciliation and Developer implementation.
7. This Planner pass updates repository source-of-truth so TASK_351 is implementation authorized / pending Developer implementation.

## Files Updated

- `docs/task_board.md`
- `tasks/TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL.md`
- `docs/task_351_fee_evaluation_auto_default_fill_plan.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_planner.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_implementation_reconciliation_planner.md`

## Implementation Authorization Scope

Authorized:

- Fee Evaluation auto default-fill for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and review-required/manual confirmation metadata.
- Use user-confirmed V1 rules plus existing seed JSON.
- Keep `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` as template authority reference only; no runtime `.xls` ingestion.
- Add or refine backend rule/default-fill logic and compact frontend review/editability display only within TASK_351 May Touch.
- Preserve operator manual review and correction before Fee confirmation/export.

Key authorized rules:

- Sample preparation: Man-hour `0.5`, Unit Price `50`, Unit Type `per sample`, Units from Matrix group sample quantity, Discount `100%`.
- Visual Examination / Examination of Product: Man-hour `0.5`, Unit Price `10`, Unit Type `per photo`, Units `3`, Discount `100%`.
- LLCR / Contact Resistance (Low Level): `per reading`, `<=20 readings/specimen` -> `1.5/reading`, `>20` -> `1/reading`; total readings only when derivable, otherwise review-required.
- Durability: `per cycle`; Units = sample quantity * cycles; `<=50 cycles/specimen` -> `2/cycle`, `50~250` -> `1/cycle`, `>250` -> `0.5/cycle`; Base Fee manual unless clear.
- High temperature Life / Pre-High temperature Life: Unit Price `15`, `per hour`, Units from explicit hours.
- Thermal Shock: Unit Price `30`, `per hour`, Units from explicit hours.
- Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance: Unit Price `25`, `per hour`, Units from explicit hours.
- MFG / Mixed Flowing Gas: default Class IIA, Unit Price `1000`, `per day`, Units from explicit days; Discount manual unless clear.
- Vibration / Random Vibration: Unit Price `300`, `per hour`.
- Microsecond discontinuity: Unit Price `300`, `per time`, Units `1`.
- Mechanical Shock: Unit Price `30`, `per time`; unclear Units require manual confirmation.
- Mating/Un-mating Force / force family: Unit Price `50`, `per sample`, Units from Matrix group sample quantity; Base Fee manual unless clear.
- CR / Contact Resistance, Specified Current: `per reading`; Unit Price by Unit Price Reference tier only with enough facts, otherwise review-required.
- Report preparation / Report: Man-hour `4`, Unit Price `600`, `per report`, Units `1`, Discount `100%`.
- Temperature Rise / T-rise: `<=240A` -> `500/specimen`; `>240A and <=500A` -> `600/specimen`; `>500A and <=1000A` -> `700/specimen`; `>1000A and <=2000A` -> `800/specimen`; Unit Type `per sample`; Units from Matrix group sample quantity; Man-hour `4`; Base Fee `500` with review-required/manual confirmation. `300A` defaults to `600/specimen`, not the manual sample `500`.

## Scope Locks Preserved

- No runtime external `.xls` parsing.
- No real workbook, public-drive, folder, LTR workbook, or user data mutation.
- No Matrix parser/import or Confirmed Matrix authority changes.
- No Fee workbook template redesign except regression checks.
- No schema change unless separately justified and re-gated.
- No StepInstance, Report generation, AI, permissions, LAN/server, multi-user, release/settings/basic-information residual cleanup.
- No `.agents/**` or `docs/project_management/**` changes.

## Expected Validation For Developer Implementation

- Focused backend rule/default-fill tests.
- Focused frontend review-required display/editability tests.
- Seed JSON validation.
- `npm run build`.
- `git diff --check`.
- trailing whitespace scan.
- forbidden-scope/status scans.

## External Residuals Excluded

Current workspace includes unrelated New Project, Settings/LTR, release/packaging, desktop release, and `temp_agents_stash.md` residuals. They are not part of TASK_351 and must not be packaged with this lane.

## Validation

Checks run:

- `git diff --check -- docs/task_board.md tasks/TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL.md docs/task_351_fee_evaluation_auto_default_fill_plan.md docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_planner.md docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_implementation_reconciliation_planner.md`
  - Passed with existing LF/CRLF warning on `docs/task_board.md` only.
- trailing whitespace scan on touched TASK_351 docs/board/evidence
  - No matches.
- targeted status for TASK_351 docs/evidence plus `backend`, `frontend`, and `tests`
  - Confirms this Planner pass updated only TASK_351 governance docs/evidence/board.
  - Existing unrelated New Project, Settings/LTR, release/packaging, desktop release, and test residuals remain dirty and excluded.

## Next Role

Recommended next role: Developer implementation pass.
