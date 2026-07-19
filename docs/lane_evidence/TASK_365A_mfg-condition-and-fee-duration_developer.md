# TASK_365A Developer Evidence

## Status

Developer implementation complete locally on 2026-07-19 / focused Reviewer and
QA review plus user acceptance pending.

## Implemented Contract

- MFG source facts are normalized to
  `Class IIA; unmated 224 hours; mated 112 hours`.
- Both label-before-duration and duration-before-label hour forms are supported.
- Ambiguous or conflicting phase values are omitted from Matrix Condition and do
  not become Fee authority.
- The existing Class IIA Fee rule converts the complete labeled phase pair with
  exact Decimal arithmetic: `(224 + 112) / 24 = 14` days.
- The resulting Fee values are Unit Price `1000`, Unit Type `day`, Units `14`,
  Base Fee `0`, Discount `0`, and Testing Fee `14000`.
- Missing Class IIA or either phase remains review-required with Units and Testing
  Fee Pending. Existing explicit `14 days` behavior is preserved.

## TDD Evidence

- Initial red run failed during collection because the two approved helper modules
  did not yet exist.
- First implementation run produced five focused failures and exposed cross-phase
  numeric capture; phase matching was tightened before acceptance.
- Final focused parser/Fee/draft suite: `89 passed`.
- Adjacent product-spec parser and Fee default-fill suite: `100 passed`.
- `py_compile` passed for all four touched production modules.
- `git diff --check` passed; only existing Windows LF-to-CRLF notices were emitted.

## Review Checklist

- Architecture: pure helper modules; no UI, API, persistence, Office, or authority
  write dependency added.
- Scope: only approved MFG parser/Fee calls, tests, and governance were changed.
- Design: exact Decimal conversion; fail-closed incomplete/conflicting inputs;
  no hard-coded file path or Class IIIA generalization.
- Runtime: canonical example returns the expected Condition and `14` days.
- Quality: new production files are 62 and 62 lines, typed, documented, and contain
  no TODO/FIXME, broad exception, or absolute path.

## Isolation Notes

The worktree contains unrelated in-progress changes in shared files. TASK_365A owns
only the narrow MFG import/dispatch hunks in `spec_section_text_extractor.py` and
`fee_default_fill.py`, its two new helper modules, focused tests, and governance
documents. No unrelated change was reverted, staged, or absorbed.

The live project Matrix was not re-imported or mutated during validation. Existing
confirmed Matrix rows therefore remain unchanged until the operator performs the
normal future import/confirmation workflow.
