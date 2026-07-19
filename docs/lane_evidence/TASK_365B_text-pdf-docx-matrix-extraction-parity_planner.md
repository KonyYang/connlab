# TASK_365B Planner Evidence

## Status

Superseded by the 2026-07-19 user-acceptance/package-scope reconciliation. TASK_365B
is user accepted and pending Integrator packaging/readiness; no new product work is
authorized.

Plan approved by the user on 2026-07-19 / Developer implementation authorized.

## Discovery Result

- User confirmed all supported text PDFs must behave like DOCX for Import Matrix,
  including all previously discussed extraction rules.
- PDF and DOCX already share the parser; the defect is the PDF neutral paragraph
  snapshot, not the family business rules.
- Read-only `GS-12-2268` evidence proves page-continuation loss, false `4.8` heading
  detection, missing Current Rating/MFG fields, and later cross-section leakage.
- One infrastructure rebuilder can restore parity without frontend, API, parser-rule,
  Fee, persistence, or authority changes.

## Boundary Result

TASK_365B may own only PDF page/paragraph normalization, its gateway delegation,
focused tests, and governance. Shared Matrix/MCR/Fee rules, DOCX behavior, real data,
OCR, new dependencies, and unrelated dirty-worktree changes are locked.

## Readiness

The lane has confirmed scope, a reproduced root cause, concrete May Touch / Must Not
Touch boundaries, deterministic acceptance cases, read-only real-sample evidence,
and an executable validation gate. User approval is recorded; Developer
implementation may proceed within those boundaries.
