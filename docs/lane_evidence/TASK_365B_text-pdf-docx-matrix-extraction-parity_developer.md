# TASK_365B Developer Evidence

## Status

Developer implementation complete locally on 2026-07-19 / focused Reviewer and
QA review plus user acceptance pending.

## Implemented Contract

- Text-PDF page boundaries remain available while logical specification sections
  are rebuilt into the existing Word-like paragraph contract.
- Text before the first valid heading on the next page is appended to the active
  section, allowing continuation facts to reach the unchanged shared parser.
- Explicit Clause/Section/paragraph references, backward section numbers, and
  inline decimal measurements such as `19.5 N` do not open false sections.
- Dense single-line PDF extraction retains the prior inline-heading compatibility.
- Existing table normalization, continuation merge, locator metadata, raw-text
  behavior, PDF blockers, and the DOCX path remain unchanged.

## TDD Evidence

- The first red run failed because the approved page-aware helper did not exist.
- Generated helper tests then exposed unsectioned-page merging and were corrected
  without adding business-family rules.
- The real-sample reproduction exposed `19.5 N` as a false forward section. A new
  red unit/gateway fixture reproduced the loss of later 7.x/8.x headings before the
  Gateway was narrowed to retain original page text for logical reconstruction.
- PDF/DOCX-equivalent paragraph fixtures now produce equal Method, Condition,
  Requirement, and extraction-status tuples through `ProductSpecMatrixParser`.
- A generated cross-page PDF API regression returns MFG Method `EIA-364-65` and
  Condition `Class IIA; unmated 224 hours; mated 112 hours`.
- Final focused suite: `98 passed`.
- `py_compile` and scoped `git diff --check` passed; Windows LF/CRLF notices only.

## Read-Only Real PDF Smoke

- `GS-12-2186`: supported, page `9`/table `2`, `11` groups, `24` rows.
- `GS-12-2268`: supported, page `11`/table `2`, `15` groups, `28` rows.
- `GS-12-1507`: supported, page `8`/table `2`, `10` groups, `26` rows.
- `GS-12-1941`: supported, page `11`/table `2`, `11` groups, `23` rows.
- `GS-12-2268` Current Rating 6.4 Method is `EIA-364-70`.
- `GS-12-2268` MFG 8.2 retains Method `EIA-364-65`, canonical Class IIA
  224h/112h Condition, and its own Requirement.
- `GS-12-2268` 8.9 retains its own 85C/85%RH/1000h source condition; neighboring
  8.x Requirement/Condition fragments are not substituted for it.

## Review Checklist

- Architecture: one pure infrastructure helper and narrow Gateway delegation;
  shared parser production logic remains locked.
- Scope: no frontend, API route/DTO, application behavior, schema, persistence,
  Office/Word, Fee, authority, OCR, AI, dependency, or real-data change.
- Design: page-aware source normalization only; ambiguous facts remain available to
  the shared parser and are not invented by the PDF layer.
- Quality: new production file is below 300 lines, the Gateway remains below 500,
  functions are typed/documented, and no TODO/FIXME or absolute path was added.

## Isolation Notes

The shared worktree contains unrelated task changes. TASK_365B owns only the new
PDF paragraph rebuilder, narrow PDF Gateway delegation, focused test additions, and
its governance documents. No unrelated change was reverted, staged, or absorbed.

All external PDF inputs were read-only. The live project Matrix was not imported,
confirmed, or otherwise mutated during validation.
