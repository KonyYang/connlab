# TASK_365B Integrator Evidence

## Status

`integrator_accepted` on 2026-07-19. The controlled package was committed locally
only; remote push was intentionally not performed.

## Controlled Package

- The page-aware PDF paragraph rebuilder and its focused unit tests.
- Exact `PdfMatrixSourceGateway` imports, original page-text collection, rebuild
  delegation, tuple assignment, and replacement of superseded local helpers.
- Exact generated cross-page PDF regressions in the gateway, neutral parser parity,
  and preview API tests.
- TASK_365B governance/evidence and the precise board closeout hunk.

## Explicit Exclusions

- Accepted TASK_365A MFG and TASK_365C thermal/surge source or test changes.
- Shared parser and Fee production, Current Rating business-rule changes, API routes
  or DTOs, schema, frontend, seed, authority writes, source documents, real data,
  release output, and unrelated dirty worktree residuals.

## Validation

- Upstream Reviewer and QA gates: passed; combined regression evidence records
  `214 passed`, with the later accepted combined baseline at `276 passed`.
- Integrator contained rerun: `48 passed` across the rebuilder, PDF gateway, neutral
  parser parity, and preview API targets.
- `py_compile` passed for the rebuilder and PDF gateway.
- Staged diff, whitelist, forbidden-content, trailing-whitespace, physical-line,
  and no-real-mutation checks passed before commit.
