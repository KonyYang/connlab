# TASK_364B TASK_364C Dependency Release Reconciliation

Date: 2026-07-19

Role: Planner / package owner

Status: `QA package passed / pending Integrator packaging/readiness`

## Accepted Dependency

TASK_364C accepted the CR coverage backend/API/storage authority baseline in local
commit `b34f2c2cbcc3b27266b480d6ff76a604f06be452`. Its Reviewer, QA, and Integrator
gates passed. Remote push was intentionally not performed.

## Proposed Review Package

The narrow TASK_364B package candidate is:

1. `frontend/src/api/client.ts`: exact 11 additions only;
2. the seven previously accepted R1 paths/hunks: selectors + test, model hook + test,
   editor + test, and `contact-measurement-plan.css`;
3. `ContactMeasurementPlanSummaryCard.test.tsx`: only the single fixture addition
   `cr_coverage: { mode: "custom", selected_category_ids: ["ppc-1"], points_per_sample: 4 }`.

Expected source numstat is 355 additions / 23 deletions. Reviewer must reproduce it
from accepted HEAD plus exact hunks. The full SummaryCard test diff is not eligible:
its other 8 additions / 2 deletions and `ContactMeasurementPlanSummaryCard.tsx` belong
to external summary work and remain excluded.

## Gates And Locks

- Reviewer verifies exact hunk ownership, required-field compatibility, and isolated
  frontend build/typecheck.
- If Reviewer passes, QA revalidates the isolated frontend package and accepted R1
  behavior; only then may Integrator retry TASK_364B.
- No backend/API/schema change, optional client fields, SummaryCard production change,
  downstream authority/consumer change, real DB/file access, or external residual
  absorption.
- No staging, commit, push, or automatic new product lane.

Reviewer and QA passed the exact package boundary. Next legal role: Integrator
packaging/readiness for TASK_364B.
