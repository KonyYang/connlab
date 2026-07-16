# TASK_362C Force and Mating Defaults QA Evidence

Status: qa_pass
Date: 2026-07-17
Role: QA

## Automated Verification

Command:

`py -m pytest tests/unit/test_spec_section_text_extractor.py tests/unit/test_mcr_text_normalizer.py tests/unit/test_product_spec_matrix_parser.py -q`

Result: `114 passed in 0.26s`.

Additional gates:

- `py -m py_compile backend/modules/test_plan/spec_section_text_extractor.py`
- scoped `git diff --check`

Both completed with exit code 0. PowerShell reported only existing Git CRLF
conversion warnings.

## Coverage

QA covers specialized and generic Force rows, numeric and missing speeds,
label-only speed text, explicit mating/un-mating without `force`, mating-only
and un-mating-only exclusions, missing Requirement, numeric Requirements,
`No damage`, specialized composite Condition preservation, and non-Force
parser regression paths.

No real specification, database, workbook, or project data was mutated.
