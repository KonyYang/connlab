# IR/DWV workbook golden comparison

## Gate status

**PASS — P1 recovery passed the User-approved acceptance contract.**

This is the writer gate only, not acceptance of the unimplemented P2/P3 application,
publication or browser workflows.

The User explicitly approved the revised acceptance contract on 2026-10-01: historical
results are the layout/style/merge/formula reference; dynamic business fields must match
current authoritative inputs, not historical execution values or erroneous group labels.
No unexplained formatting defect may pass the gate. The original failed comparison remains
below for traceability.

## Final P1 verification

- Independent Reviewer: no blocking code findings in the column-copy fix and regression tests.
- Developer RED/GREEN: four new public-seam column-width tests failed before the fix and
  passed after it. All 23 writer tests passed; an independent QA rerun also passed 23 tests.
- Independent QA generated a fresh workbook via the public writer: three groups, two
  blocks each, five samples, one `Odd&Even` pair. Compared 3,000 cells (A1:Y40 per sheet).
- All 390 current-input assertions passed. All 720 reserved measurement cells were blank;
  none of the 60 historical measured values were copied into the new blank record.
- Against the historical reference: **0 actual style, 0 merged-range, 0 formula and 0
  row-height differences**.
- Ten effective-width differences remain, all in manually adjusted historical second
  blocks: Group 1 W/X/Y; Group 2 V/W/X/Y; Group 3 W/X/Y. All six generated blocks instead
  match the first template prototype's actual styles, effective widths and static content
  exactly. This is the intentional template-driven copy behavior, not lost dimensions.
- Ninety historical non-measurement values differ: date/environment 20; identity/stage/
  remarks 8; Matrix raw conditions 60; personnel 2. The new record uses its supplied input,
  not historical execution readings, inconsistent capitalization or incorrect group labels.
- The template SHA256 was unchanged before/after generation:
  `e577747e7e18047e2e5d50062ef73d790d10312731c5c50f02862f15b093bafa`.
- Independent QA output (temporary evidence, not a business report):
  `C:/Users/White/AppData/Local/Temp/connlab-ir-dwv-p1-independent-qa-l21uaacn/independent-golden.xlsx`.
- Verified recoverable original-template backup:
  `D:/Source/Template/backup/IR&DWV Template_before_TASK_362_20261001.xlsx`.
  The original and historical result workbooks have not been changed.

Command: `C:/PythonEnvs/connlab/.venv/Scripts/python.exe -m pytest
tests/unit/test_ir_dwv_record_workbook_gateway.py -q` (independent QA: 23 passed).

## Recovery findings (2026-10-01)

- Reproduced the original comparison against the retained generated workbook below:
  90 non-measurement value differences and 60 measurement values intentionally blank.
- The original 96 style differences compare workbook-local style indices. Comparing actual
  font, fill, border, alignment, protection and number format instead gives **zero** differences
  across all three sheets, rows 1–40 and columns A–Y. Index differences are not formatting defects.
- Column copying has a real defect: Excel stores the template's B–J width in one dimension
  (`min=2`, `max=10`, `width=16.46484375`). Looking up only individual column letters loses
  that range for C–J. The same issue affected other grouped dimensions. The regression fix
  now resolves covering ranges, explicit overrides and real default widths.
- The original 34 dimension differences below are a historical raw-key comparison, not an
  effective-width comparison. Accessing absent `column_dimensions` entries creates default
  objects with width 13, whereas this template's actual `defaultColWidth` is 9. These counts
  must not be reused as the final formatting verdict.
- The historical second block is not a dimension-identical copy of the first block. The
  first block's K/L widths are 17.86328125/9, whereas the historical second block's X/Y
  widths are 12/12.59765625 in Group 1, with additional per-group manual adjustments.
  A template-first block copy therefore cannot eliminate every historical dimension
  difference. No per-project or per-group historical widths will be hardcoded to mask this.
- Value differences include historical per-block execution dates and environment readings,
  mixed `mated`/`Mated` capitalization, remarks after execution, and differing requestor text.
  The generated input supplies one project header and preserves the Matrix condition text.
- The reference itself contains inconsistent identity content: Group 1 cell O10 says Group 2,
  and Group 3 cells I11/V11 omit the product name. Copying those values into product logic
  would conflict with current Matrix/Basic Information authority.
- An independent Planner confirmed these classifications. The User explicitly accepted
  current-authority validation for dynamic fields. This does not waive genuine layout,
  style, merged-range or formula defects.
- The external template's Excel lock file was absent when recovery began. Neither the
  original template nor the historical results workbook has been changed during recovery.

The comparison table below retains the original failed evidence, not the final verification counts.

## Original comparison inputs

- Generated workbook: `D:\tmp\generated_ir_dwv_golden.xlsx`
- Historical reference: `C:\Users\White\Desktop\AI information\Projects\DL-2026-07-115 Custom Pwr 14P VH Qualification Testing\Test results\DL-2026-07-115 BTB 14P IR&DWV Results.xlsx`
- Case: three groups, two blocks per group, five samples, one measurement pair (`Odd&Even`).
- Measurement values in the generated blank record are intentionally empty.

## Original raw counts

- Measurement value differences: 60
- Other value differences: 90
- Workbook-local style array differences: 96 (semantic formatting differences: 0)
- Merged-range differences: 0
- Raw row/column dimension differences: 34 (not an effective-width verdict)

## Non-measurement value differences

| Sheet | Cell | Generated | Golden |
|---|---|---|---|
| Group 1 | O8 | 'Start Date:2026/08/18' | 'Start Date:2026/08/24' |
| Group 1 | X8 | 'Amb Temp: 25.7°C' | 'Amb Temp: 24.6°C' |
| Group 1 | O9 | 'Finish Date: 2026/08/18' | 'Finish Date: 2026/08/24' |
| Group 1 | X9 | 'Rel. Hum.:48.5%RH' | 'Rel. Hum.:45.7%RH' |
| Group 1 | O10 | 'Item/Process: Group 1  IR&DWV-After reseating' | 'Item/Process: Group 2  IR&DWV-after reseating' |
| Group 1 | B14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 1 | H14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 1 | O14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 1 | U14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 1 | B15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 1 | H15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 1 | O15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 1 | U15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 1 | B16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 1 | H16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 1 | O16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 1 | U16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 1 | B17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 1 | H17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 1 | O17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 1 | U17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 1 | B18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 1 | H18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |
| Group 1 | O18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 1 | U18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |
| Group 2 | B8 | 'Start Date:2026/08/18' | 'Start Date:2026/07/31' |
| Group 2 | K8 | 'Amb Temp: 25.7°C' | 'Amb Temp: 25°C' |
| Group 2 | O8 | 'Start Date:2026/08/18' | 'Start Date:2026/08/13' |
| Group 2 | X8 | 'Amb Temp: 25.7°C' | 'Amb Temp: 26.3°C' |
| Group 2 | B9 | 'Finish Date: 2026/08/18' | 'Finish Date: 2026/07/31' |
| Group 2 | K9 | 'Rel. Hum.:48.5%RH' | 'Rel. Hum.:46.5%RH' |
| Group 2 | O9 | 'Finish Date: 2026/08/18' | 'Finish Date: 2026/08/13' |
| Group 2 | X9 | 'Rel. Hum.:48.5%RH' | 'Rel. Hum.:46.9%RH' |
| Group 2 | I10 | 'Request  No.:  DL-2026-07-115' | 'Request  No.:   DL-2026-07-115' |
| Group 2 | O10 | 'Item/Process: Group 2  IR&DWV-After Humidity&Temp. cycling' | 'Item/Process: Group 2  IR&DWV-after Humidity&Temp. cycling' |
| Group 2 | B14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 2 | H14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 2 | O14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 2 | U14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 2 | B15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 2 | H15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 2 | O15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 2 | U15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 2 | B16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 2 | H16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 2 | O16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 2 | U16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 2 | B17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 2 | H17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 2 | O17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 2 | U17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 2 | B18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 2 | H18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |
| Group 2 | O18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 2 | U18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |
| Group 3 | B8 | 'Start Date:2026/08/18' | 'Start Date:2026/07/31' |
| Group 3 | K8 | 'Amb Temp: 25.7°C' | 'Amb Temp: 25°C' |
| Group 3 | O8 | 'Start Date:2026/08/18' | 'Start Date:2026/08/26' |
| Group 3 | X8 | 'Amb Temp: 25.7°C' | 'Amb Temp: 24.3°C' |
| Group 3 | B9 | 'Finish Date: 2026/08/18' | 'Finish Date: 2026/07/31' |
| Group 3 | K9 | 'Rel. Hum.:48.5%RH' | 'Rel. Hum.:46.5%RH' |
| Group 3 | O9 | 'Finish Date: 2026/08/18' | 'Finish Date: 2026/08/26' |
| Group 3 | X9 | 'Rel. Hum.:48.5%RH' | 'Rel. Hum.:49%RH' |
| Group 3 | O10 | 'Item/Process: Group 3  IR&DWV-After reseating' | 'Item/Process: Group 3  IR&DWV-after reseating' |
| Group 3 | B11 | 'Remarks:' | 'Remarks:The alarm function is normal, LC: Leakage Current' |
| Group 3 | I11 | 'Product Name: Custom Pwr 14P VH' | 'Product Name: ' |
| Group 3 | O11 | 'Remarks:' | 'Remarks:The alarm function is normal, LC: Leakage Current' |
| Group 3 | V11 | 'Product Name: Custom Pwr 14P VH' | 'Product Name: ' |
| Group 3 | K12 | 'Requestor:David Tao' | 'Requestor: David' |
| Group 3 | X12 | 'Requestor:David Tao' | 'Requestor: David' |
| Group 3 | B14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 3 | H14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 3 | O14 | '1. IR testing/ 1# 500VDC 2min. mated' | '1. IR testing/  1# 500VDC 2min. mated' |
| Group 3 | U14 | '6. DWV testing/ 1# 1500VDC 1min. Mated' | '6. DWV testing/  1# 1500VDC 1min. Mated' |
| Group 3 | B15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 3 | H15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 3 | O15 | '2. IR testing/ 2# 500VDC 2min. mated' | '2. IR testing/  2# 500VDC 2min. Mated' |
| Group 3 | U15 | '7. DWV testing/ 2# 1500VDC 1min. Mated' | '7. DWV testing/  2# 1500VDC 1min. Mated' |
| Group 3 | B16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 3 | H16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 3 | O16 | '3. IR testing/ 3# 500VDC 2min. mated' | '3. IR testing/  3# 500VDC 2min. Mated' |
| Group 3 | U16 | '8. DWV testing/ 3# 1500VDC 1min. Mated' | '8. DWV testing/  3# 1500VDC 1min. Mated' |
| Group 3 | B17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 3 | H17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 3 | O17 | '4. IR testing/ 4# 500VDC 2min. mated' | '4. IR testing/  4# 500VDC 2min. Mated' |
| Group 3 | U17 | '9. DWV testing/ 4# 1500VDC 1min. Mated' | '9. DWV testing/  4# 1500VDC 1min. Mated' |
| Group 3 | B18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 3 | H18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |
| Group 3 | O18 | '5. IR testing/ 5# 500VDC 2min. mated' | '5. IR testing/  5# 500VDC 2min. Mated' |
| Group 3 | U18 | '10. DWV testing/ 5# 1500VDC 1min. Mated' | '10. DWV testing/  5# 1500VDC 1min. Mated' |

## Original raw formatting comparison

- Style array differences: 96 (indices are workbook-local)
- Merged-range differences: 0
- Raw dimension differences: 34

### Original row/column dimension details

| Sheet | Dimension | Generated | Golden |
|---|---|---|---|
| Group 1 | column A | 13.0 | 14.46484375 |
| Group 1 | column AA | 13.0 | 16.46484375 |
| Group 1 | column AJ | 13.0 | 17.86328125 |
| Group 1 | column AK | 13.0 | 9.0 |
| Group 1 | column M | 13.0 | 14.46484375 |
| Group 1 | column N | 13.0 | 16.46484375 |
| Group 1 | column O | 16.46484375 | 13.0 |
| Group 1 | column W | 13.0 | 17.86328125 |
| Group 1 | column X | 17.86328125 | 12.0 |
| Group 1 | column Y | 9.0 | 12.59765625 |
| Group 1 | column Z | 13.0 | 14.46484375 |
| Group 2 | column A | 13.0 | 14.46484375 |
| Group 2 | column AA | 13.0 | 16.46484375 |
| Group 2 | column AJ | 13.0 | 17.86328125 |
| Group 2 | column AK | 13.0 | 9.0 |
| Group 2 | column M | 13.0 | 14.46484375 |
| Group 2 | column N | 13.0 | 16.46484375 |
| Group 2 | column O | 16.46484375 | 13.0 |
| Group 2 | column V | 13.0 | 14.59765625 |
| Group 2 | column W | 13.0 | 17.86328125 |
| Group 2 | column X | 17.86328125 | 11.265625 |
| Group 2 | column Y | 9.0 | 14.59765625 |
| Group 2 | column Z | 13.0 | 14.46484375 |
| Group 3 | column A | 13.0 | 14.46484375 |
| Group 3 | column AA | 13.0 | 16.46484375 |
| Group 3 | column AJ | 13.0 | 17.86328125 |
| Group 3 | column AK | 13.0 | 9.0 |
| Group 3 | column M | 13.0 | 14.46484375 |
| Group 3 | column N | 13.0 | 16.46484375 |
| Group 3 | column O | 16.46484375 | 13.0 |
| Group 3 | column W | 13.0 | 17.86328125 |
| Group 3 | column X | 17.86328125 | 12.0 |
| Group 3 | column Y | 9.0 | 13.0 |
| Group 3 | column Z | 13.0 | 14.46484375 |

## Registered template purification (2026-10-01)

The original external template was backed up and verified before replacement:

- Recoverable original: `D:/Source/Template/backup/IR&DWV Template_before_TASK_362_20261001.xlsx`.
- Original/backup SHA-256: `e577747e7e18047e2e5d50062ef73d790d10312731c5c50f02862f15b093bafa`.
- Purified registered asset: `D:/Source/Template/IR&DWV Template.xlsx`.
- Purified SHA-256: `2842de663c9cda612d5a3c749f305db95f8d800878f9f60265ffbb8534d80f9e`.
- The existing external-resource API registered `ir_dwv_record_template` as active and returned `validation_status=valid`.

The purified workbook retains one reusable prototype sheet. Independent checks confirmed
all prototype cell styles by semantic value, 40 merges, 40 row heights, 14 effective column
widths, static laboratory headers/footers and the statistical formulas. All 132 cells in
the prototype measurement area are blank; historical business headers, conditions and
equipment fields are cleared. The original fixture and historical result workbook were
not modified. Replacement used a uniquely owned staging file after rechecking the original
hash, backup hash and absence of the Excel lock file.

The writer continues clearing history regardless of template cleanliness. Purification is
not a prerequisite for preventing historical measurement leakage.

## P2/P3 review and final QA checkpoint (2026-10-01)

Independent review found and closed three defects: dirty-template historical calibration/
environment headers and duplicate footer at dynamic widths; semantic header styles at
1/3/7 samples; and an over-capacity preview incorrectly advertising readiness. The writer
now validates capacity before publication, clears historical fields independently of
template purification, and reconstructs dynamic headers from prototype semantic styles.
Independent delta review reported Standards 0 / Spec 0, seven focused checks passed,
and a separate five-sample/two-block semantic style comparison had zero differences.

Final independent QA executed the affected Python matrix (151 passed) plus shared
publication/recovery regressions (52 passed). Frontend validation passed 234 tests in
37 files; the opt-in Matrix profiling file/test was skipped because profiling was not enabled.
Production build failed: the new output kind is missing from the label mapping in
`ProjectWorkbenchCloseConfirmation.tsx`. Approval to include that file and its same-name
test was requested; no change to those files or passing build is claimed at this checkpoint.

Browser smoke was performed by the primary agent using a separate 8014/5174 runtime,
test database, template and project root. Independent QA verified the actual files:

- Draft download returned HTTP 200 and the exact downloaded file existed in Downloads.
- First official publication used confirmed Basic Information and Matrix fields; two
  blocks contained five samples and two measurement pairs, with all 240 measurement
  cells and 40 equipment/calibration cells blank and correct statistical formulas.
- Cancelling replacement left the synthetic measured file byte-identical, with no archive.
- Approved replacement archived the entire old file byte-identically under the existing
  LTR workspace `History/Test results` and published a new blank record to `Test results`.
- Missing pairs produced a persistent inline blocker; the temporary template lock also
  produced a visible blocker. Business reports and the original browser tab were not edited.

Screenshots and isolated artifacts remain under
`C:/Users/White/AppData/Local/Temp/connlab-ir-dwv-final-browser-qa-wmvh7kb2/`.
Browser download-event collection timed out, but the independent backend log, exact
downloaded file and UI success were checked; this timeout is not a generation failure.

## Remaining work and limitations at the initial QA checkpoint

- Obtain the bounded build-mapping scope approval, implement and independently review
  the label regression, then rerun affected frontend checks and the production build.
- Complete independent integration and record `ready_for_close`; this checkpoint is not delivery.
- More than 17 samples per block is explicitly blocked, not silently truncated or paginated.
- No confirmed project equipment selection or actual execution personnel/environment
  source exists yet; those fields stay blank with information diagnostics.
- No packaged release or installed-Office validation was run. This chain uses openpyxl,
  not Excel COM, and no full-repository test pass is claimed.

## User acceptance correction and build delta (2026-10-01)

The preceding build blocker is now closed: the User explicitly approved the close-label
component and its matching test. Developer reproduced the missing public label, fixed it,
and passed four focused tests. Independent Reviewer reported zero findings. Independent QA
then ran the two affected workbench files (72 tests passed) and, sequentially, TypeScript
and Vite production build (157 modules, exit 0). No repeated full test pass is claimed.

This does not complete the task: the User supplied a generated draft exposing a business
grouping error and clarified the intended record format. Read-only comparison established:

- Actual Group 2 has IR steps 2/5/8 and DWV steps 3/6/9, separated by Thermal Shock 4
  and Cyclic Temperature and Humidity 7. Equal-step-only grouping incorrectly produced
  six blocks; the intended output has three shared measurement-round blocks.
- The historical PDF table visually confirms consecutive IR/DWV pairs in Groups 1/2/3,
  each with two measurement rounds. The historical workbook shares both tests within
  each round; its measured values and incorrect copied group titles are not authority.
- The faulty supplied output has zero images. The current User-edited registered template
  has one top-right LOGO and explicit Instrument/Gage ID defaults. These must be retained
  in every generated block, including continuation sheets; no template replacement is needed.
- First read of the User-edited template had SHA256 `389c3fe570e1f5f8ec291d1987ba6a7dd06156eb95d79fb11f1855010b699e4a`.
  The backup remains the original `e577747e7e18047e2e5d50062ef73d790d10312731c5c50f02862f15b093bafa`.
  The purification SHA above records the earlier operation, not the User's current asset.
- Default physical slots are `max(5,N)`. Unused slots stay entirely blank; actual sample
  counts, Fee quantities and statistical ranges still use N. Conditions come from Matrix,
  not the template examples. Result-unit priority is being clarified with the User.

Independent Planner completed this correction plan; Developer's revised targeted
RED/GREEN, independent review, affected final QA and new generated-file/browser checks
are still pending. Earlier browser checks prove the shared publication safety sequence,
not correctness of this newly corrected round grouping or LOGO preservation.

The User then saved and closed Excel at 23:22. Read-only verification found no template
lock, a 22,997-byte asset with SHA256
`07cf9e81e11fca5c1fb5d94a291aaba6851c0e748563384ef814aa8c048ef7cf`, one LOGO,
the default instrument and DG-Q-0624, blank calibration dates and GΩ/nA units. The saved
hash supersedes the first-read hash for upcoming actual-asset validation; no source
template bytes were written by the revision implementation.

Round/template revision Developer targeted checks passed 59 cases; independent Reviewer
passed 20 risk-focused cases and reported zero actionable findings. Independent QA then
passed the four affected Python files (78 cases) and prepared an isolated pending Group 2
draft through real session APIs. The actual User template was copied only into the QA-owned
template path; source-before, copied asset and source-after hashes all matched `07cf9e81...`.

Before browser acceptance, direct validation of that actual asset revealed a previously
uncovered incompatibility: its IR statistics use four independent row merges (including
`C36:G36` and `C37:G37`) and MIN/MAX/AVERAGE/STDEV formulas, while validation required
the historical `C36:G37` merged slash region. The 78-case pass is not evidence of support
for this new asset. Browser acceptance was paused; Developer is adding support for both
real topology variants and template-derived statistics with actual-N ranges. The User
asset must not be edited to make the check pass. Independent review and affected final
QA must rerun on that fix before recording successful actual-asset generation.

## Actual saved-template acceptance delta (2026-10-02)

The statistics compatibility defect above was fixed without editing the User asset.
Developer recorded 10 newly failing topology checks before the fix and 13 passing
focused checks afterward. Independent Reviewer passed 13 focused checks and reported
Standards 0 / Spec 0. Independent final QA ran the affected writer/API files: 65 passed.
These overlapping test runs are not added to the earlier 78-case count.

The primary agent then exercised the actual UI on the isolated 5174/8014 runtime:
the full Group 2 draft has steps 1 through 10, and IR/DWV Form -> Download preview
returned a real file and a visible download-success message. Independent QA checked
the downloaded artifact against the backend output (identical SHA256
`6501128992b0f224b851ef3f1445938274aa286beb9dbc8355b753a666bca1d5`):
three shared rounds, three LOGOs, template equipment defaults, 24 statistical formulas,
correct statistical styles/merges and 360 blank measurement cells. The five-sample
count came from `5+5(d)`. The original registered template remained `07cf9e81...`;
synthetic old formal and archived files remained unchanged. Only owned validation
processes/listeners were stopped; the User's browser tab and services were preserved.

This is not complete expanded-sample acceptance. A further main-agent check found
that the N7 output translated a TwoCellAnchor into narrower sample columns while
keeping the same offsets. The PNG bytes remained identical but the LOGO's physical
width shrank. A bounded writer regression/fix and independent review/affected QA are
required. N5 download evidence remains valid; it does not prove N7 image geometry.
Result-unit priority also remains an unanswered business choice. No packaged-release
or installed-Excel rendering/recalculation pass is claimed.

### Expanded-sample LOGO correction and final affected QA

The width defect is now closed for the current saved template. The writer retains
the translated right marker and rebases only the left marker using the covered column
span; it does not change column widths, fonts, row heights or the image payload.
Developer recorded the N7 failure before the fix and passed 14 focused checks.
Independent Reviewer passed 10 focused checks with Standards 0 / Spec 0. Independent
final QA ran the complete affected writer unit/API integration files once: **71 passed**,
one existing deprecation warning, 36.54 seconds. Counts from overlapping earlier runs
are not added to this final result; unaffected frontend/build evidence is retained.

The actual source Normal font was independently checked as Song 11pt with an
eight-pixel maximum digit width at the examined 96-dpi font metric. Independent read-only
geometry checks of all nine LOGOs in current-template 3/5/7-sample outputs found
`1728000 x 1378626 EMU`, right gap `117468 EMU`, matching the source. N3/N5 relative
markers are unchanged; N7 uses left marker column 13 / offset 211932 and correctly
continues across two sheets. The same regression also checks the standard seven-pixel
metric. This is bounded validation of this asset, not a general font rasterizer or
native-Excel rendering claim. The source, synthetic prior formal record and archive
remain byte-identical. No new browser service, formal publication or external write
was performed for this geometry-only delta.

Reviewed/QA frozen bytes:

- Gateway: `4cbac63c67aa264e2b866e07ff03b8669f3c46e28ddcddf0e6fbc1d6f1ba7df5`.
- Writer tests: `a2fcfe5341a4676903e4aff6a90ddb5bd49c6384cc671f4a79759a678ed71c9f`.

The remaining business choice is result UNITS priority: retain the template's GΩ/nA,
or derive result units from Matrix requirements with template fallback. The async
question has not been answered; the preselected recommendation is not approval.
Task remains running, not committed, integrated, ready_for_close or closed. Final
integration/scope-manifest reconciliation will follow that decision. The source
template is not changed to force either answer.

### User unit decision and Matrix requirements output (2026-10-02)

The User explicitly approved retaining the registered template's result UNITS while
voltage, time and acceptance requirements come from the corresponding Matrix steps.
This resolves the previously pending business choice above. Requirement text does not
convert measurement values or replace GΩ/nA result units.

Final inspection found that per-side Matrix requirements and step overrides were
already projected but the writer left Remarks blank. A bounded writer correction now
adds `IR Requirement:` and `DWV Requirement:` to the existing Remarks field, omitting
the inactive side. It changes only wrapping and the shared Remarks row height; later
short or empty blocks cannot shrink the height required by an earlier block. Text
exceeding Excel's 32,767-character cell limit or the 409-point row budget fails
explicitly rather than silently truncating requirements.

Developer reproduced seven missing-Remarks failures before the fix, then passed the
seven cases and a final 31-case focused check. Final source-template 3/5/7-sample
outputs are retained under `connlab-ir-dwv-final-requirements-xniifnm0` in the owned
temporary directory. The main agent inspected a read-only rendering of the final
seven-sample conditions/Remarks region: both requirements and Matrix conditions are
visible, with seven IR and seven DWV sample rows. Rendering uses the bundled artifact
renderer, not installed Excel. Source-template SHA256 remains `07cf9e81...`.

Final frozen bytes for this additional delta:

- Gateway: `434ec58405808f60f9ce310a80a8d1320ec7c9ecd8c4140ce29f14b811465a01`.
- Writer tests: `2936bd91da5bd1fff3a5654f0dc7d4c61af76bbdcb352f3cf9df9374719bda6e`.

Independent Reviewer passed ten risk-focused checks with Standards 0 / Spec 0 and
independently inspected all nine final 3/5/7-sample form blocks: requirements and
overrides are complete, 72 statistics formulas are correct, LOGO anchors/payloads match
the preceding reviewed output, and measurement cells remain blank. The reviewer also
verified that the new text-limit failures occur while generating the temporary staged
file, before the existing publisher can archive or replace a business file.

Independent final QA ran the complete affected writer unit and IR/DWV API files:
**81 passed**, one existing deprecation warning, 43.28 seconds. Frozen hashes match.
Read-only actual-asset checks covered 18 per-side requirements, 90 Matrix condition
rows, 1,224 blank measurement cells, 72 statistics formulas with semantic styles,
and all nine LOGO rectangles/right margins. N7 continues correctly on two sheets;
the registered source, prior synthetic formal file and sole archive remain unchanged.
This final affected result supersedes the earlier 71-case result for changed writer
bytes; overlapping runs are not summed. Unchanged frontend/build and isolated
browser-flow evidence remains applicable, but is not a claim that native Excel,
packaged release, or this final Remarks delta was exercised in the browser.

Remaining bounded limitations: result units follow the registered template without
automatic conversion; more than 17 samples per block is explicitly blocked;
unavailable execution personnel/environment/calibration values remain blank;
Remarks height uses conservative wrapping estimates with explicit overflow errors.
No full-repository, packaged-release or installed-Excel rendering/recalculation pass
is claimed. Scope reconciliation and independent integration are the last governance
steps before the sole board writer records `ready_for_close`.

### Two-column separation acceptance revision (2026-10-02)

After the preceding delivery checkpoint, the User supplied a screenshot showing the
second and third same-sheet forms touching and requested the same two empty columns
between every adjacent form. The sole writer resumed this same task with `Revise`.
The earlier final 81-case result does not validate this subsequent layout change.

Independent revision planning retained three forms per five-slot sheet and the
existing expanded-sample capacity/continuation rules. Developer reproduced the
symptom through the public writer: `-k every_adjacent_record_table` returned two
failures (N3/N5) and one pass (N7), 2.53 seconds. In both failures the second form
ends at Y and the third starts at Z, leaving zero empty columns. The historical
five-slot origins `(2, 15, 26)` differ from the expanded layout's width-plus-two
spacing rule. The intended five-slot origins are now B/O/AB `(2, 15, 28)`, with
M/N and Z/AA as equal two-column gutters. Expanded layouts must still reject 18
samples rather than gaining capacity as an unintended effect of this correction.

Only the existing layout and writer tests changed. Registered template, formal
business files, authority selection and safe publication remain unchanged.
Developer's final focused GREEN passed 35 cases (41 deselected), 19.14 seconds.
The public writer now checks every same-sheet gap for exactly two blank columns,
without values, table borders or intersecting merges. It also verifies continuation
and preserves the existing 17-sample limit, explicitly rejecting 18 samples.

Frozen implementation SHA256:

- Layout: `f88a33c6e1796ce906d4d41181a7fa57bf7c3ecaa41c77c39ed8fbde2137ab6a`.
- Writer tests: `a67b9a135fd46512433360bbd9dc68ebf497a5768e3cce53b601b474466bb2dc`.
- Gateway remains `434ec58405808f60f9ce310a80a8d1320ec7c9ecd8c4140ce29f14b811465a01`.

Actual current-source outputs are retained under the owned temporary directory
`connlab-ir-dwv-final-spacing-z56xdufn`, named `matrix-spacing-{3,5,7}-samples.xlsx`.
Main inspected a read-only rendering of N5 `W1:AL14`: the second form ends at Y,
Z/AA are empty, and the third starts at AB. The rendering does not modify or export
the workbook and is not an installed-Excel rendering/printing claim. LOGO payload
and physical anchor preservation are checked separately in the actual OOXML.
Independent Reviewer passed seven focused spacing, continuation and 17/18-capacity
tests (69 deselected), 5.53 seconds, with Standards 0 / Spec 0. Read-only inspection
verified all nine actual blocks: 4,530 cell styles, 72 statistics formulas,
normalized merges, static fields, Units, blank data and LOGO payload/anchor geometry
remain correct. N3/N5 end at AL without a fixed print area clipping the third block;
N7 retains two blocks plus continuation. The source SHA256 remains unchanged.
The preceding requirements sample and this spacing sample use different synthetic
business inputs; conditions, requirements and stages were checked against each
sample's own inputs, not falsely reported as entirely identical business values.
Independent QA ran the complete affected writer unit and IR/DWV API files once on
these frozen bytes: **85 passed**, one existing deprecation warning, 117.13 seconds,
exit 0. This supersedes the preceding 81-case result for the subsequently changed
layout/tests; overlapping counts are not summed. QA independently verified all
same-sheet two-column gaps, N7 continuation, 17 supported/18 rejected, 72 statistics
formulas, 1,224 empty measurement cells, template GΩ/nA Units, nine LOGO physical
frames/right gaps, and immutable registered-source/prior synthetic official/archive
bytes. No UI/service restart or repeated unaffected frontend build was needed.
The owned QA evidence log is
`connlab-ir-dwv-final-browser-qa-wmvh7kb2/round-template-revision-qa.md` in Temp.
Native Excel rendering/printing and packaged-release execution remain untested.

### Sample-expanded third-round placement revision (2026-10-02)

User acceptance feedback: increasing Group 2 to six samples must keep its third
round at the right of `Group 2`, not move it prematurely to `Group 2 (2)`.
The sole writer resumed this same task. Independent Planner selected the smallest
compatible correction: three rounds per sheet for every supported sample count;
sample growth widens each block with two-column gutters, while a fourth round keeps
the existing continuation naming. The independent 17-sample limit remains in place.
This explicitly supersedes the old template-width-based capacity rule in D5.

Main reproduced through the actual requested Matrix Editor URL in a separate in-app
browser tab, without editing or confirming business Matrix data. `IR&DWV Form` ->
`Download preview` produced the owned browser-download token
`5651fad0b54742fe9651f16d5697fb01`: six IR/DWV sample IDs are present, but Group 2
has Initial at B10 and After Thermal Shock at Q10, with Final at B10 in a new
`Group 2 (2)`. A read-only assertion requiring only `Group 2` for its three rounds
failed with that exact sheet list. The attached older `e98d793...` file instead
has three five-slot forms and was left unchanged; it is not claimed as the six-sample
reproduction. Main viewed a read-only rendering of the actual six-sample Final form
and its current Matrix requirements/conditions before implementation.

The old layout exposes three five-slot origins but computes expanded capacity from
the template's fixed last column 37. Thus a six-sample block's width13 leaves only
two slots before that arbitrary boundary. Regression and final verification of the
correction must exercise the public writer and actual browser download, including
the rightmost form, gutters, formulas, LOGO, and unchanged group/source data.

Independent Developer's public-writer capacity RED: N6/N7 failed because a third
round moved to a continuation sheet; N3/N5 passed (2 failed, 2 passed, 76 deselected,
2.52 seconds). Adding N6 to the independent eight-pixel LOGO geometry check also
exposed a 9-pixel width error (1,813,725 versus source 1,728,000 EMU). The bounded
correction uses the approved Normal Song/SimSun 11pt font's verified eight-pixel
digit metric only for image-anchor column geometry; other fonts retain the existing
seven-pixel convention. Remarks, row heights, column widths and source fonts are
not changed. This is not a universal font rasterizer.

Final Developer targeted GREEN: 40 passed, 48 deselected, 99.67 seconds. Owned
current-source outputs are in `connlab-ir-dwv-three-rounds-z50vxbb1` (Temp), named
`matrix-three-rounds-{3,5,6,7}-samples.xlsx`. All have three rounds in one Group
sheet; N6 ends at AR44 and N7 at AX50. N6 gutters O/P and AD/AE, N7 gutters Q/R and
AH/AI are blank. All actual-source LOGOs preserve 1,728,000 x 1,378,626 EMU frames;
source SHA256 remains `07cf9e81e11fca5c1fb5d94a291aaba6851c0e748563384ef814aa8c048ef7cf`.
Final independent review, QA and browser GREEN are recorded below when complete.

Main repeated the real requested page's `IR&DWV Form` -> `Download preview` on
the frozen revised generator, still without changing or confirming business data.
The browser produced token `748f17fbd05d481fba879a66cbcec609`, SHA256
`c2763ae03d586b52784ea433fb0f569af9c4927ab6daae190c36025cbbf353ca`.
It contains only `Group 2` and `Group 6b`: Group 2's Initial, After Thermal Shock
and Final are at B10, Q10 and AF10, ending at AR. All 1,560 cells across those
three forms match the actual pre-fix download's values/styles after translating
the relocated formula coordinates. The two gutters remain empty, Group 6b is
unchanged and Group 2 has three LOGOs. The registered template hash is unchanged.
Main viewed a read-only rendering of AC10:AR23: two blank columns separate the
preceding form from Final, which has six IR and six DWV conditions/IDs and the
same Matrix requirements/Units. Neither rendering nor inspection exports or
modifies a workbook; this is not native Excel rendering or a printing claim.

Review caught an intermediate shared-helper boundary error: `_fill_remarks`
also used the column-width helper, so changing its default to eight pixels could
reduce Remarks row height. A public-writer RED with identical requirements/cell
fonts and differing Normal fonts proved Song11 incorrectly used 48.2 points
instead of the existing 70.3-point budget (1 failed, 1 passed, 88 deselected,
2.15 seconds). The correction is isolated to the two LOGO callers via a dedicated
wrapper; the Remarks helper retains its original seven-pixel default. This
supersedes the intermediate frozen generator and its claims about row-height
preservation, rather than treating their partial GREEN as final acceptance.

Final Developer targeted validation on this corrected boundary: **45 passed**,
45 deselected, 27.99 seconds; diff check passed. Final raw SHA256: layout
`dd207eb057ce26c4da6ffe9a12e2bc489b62f13da5567ad366e6924a4a4d020a`, gateway
`4c546011b877a06e4f3b997405defc35d5c0fb2ea8120cc485cad54e3c82c9a4`, writer tests
`d68c9589e21b32f1a7a751e8a306092caf9676d5c0e6d8052984f1814f73e3e6`.
Final actual-source outputs are in the new owned Temp directory
`connlab-ir-dwv-three-rounds-isolated-5sk149tn`, using the same N3/N5/N6/N7 filenames.
Old `z50vxbb1` outputs and browser `748f17...` remain diagnostic evidence, not the
final frozen validation. Final QA/review and a repeat actual browser download
must verify the corrected bytes.

Final Main browser GREEN on the corrected boundary produced token
`613fc50e52ce4cbc87372f075742641f`, SHA256
`b07a0268745d5c918ab065b77a0487a59539037e90cd9d3444123374605aed44`.
Only Group 2/Group 6b remain. B/Q/AF, both two-column gutters and three LOGOs are
verified. All 1,599 cells across the three Group 2 forms match the pre-fix values
and styles with formula-coordinate translation; Group 6b is unchanged. Remarks
row11 height is 136.6 points, exactly matching the pre-fix workbook. Main viewed
the final read-only AC10:AR23 rendering, not just the intermediate output. The
registered source hash remains 07cf9e81...; no business Matrix confirmation or
official-folder write occurred during this user-page smoke test.

Independent Reviewer passed the exact final frozen bytes: **19 passed**, 71
deselected, 11.84 seconds; Standards 0 / Spec 0. The shared-helper finding is
closed. Current-source N3/N5/N6/N7 artifacts preserve 12 LOGO payloads/physical
frames/right margins, 96 actual-sample statistics formulas, 1,512 blank measurement
cells and 652 blank gutter cells. N3/N5/N7 were compared to the earlier spacing
artifacts: 4,530 cell values, translated formulas and semantic styles remain the
same. Remarks heights match their own earlier synthetic inputs (114.5/114.5/114.5/
70.3 points). These synthetic values differ from the business preview's 136.6
points because the requirements differ; neither was silently equated. Source
hash and diff checks pass. Full final affected QA is recorded separately below.

Final independent QA ran the complete affected files once on the exact frozen
generator/tests:

`C:/PythonEnvs/connlab/.venv/Scripts/python.exe -m pytest tests/unit/test_ir_dwv_record_workbook_gateway.py tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py -q -p no:cacheprovider`

**99 passed**, one existing deprecation warning, 53.84 seconds, exit 0. This
supersedes the preceding 85-case result for the changed implementation/tests;
overlapping counts are not added. Independent current-source N3/N5/N6/N7 checks
cover three-round sheets, fourth-round continuation, two-column gutters, 17/18
pre-write bounds, 96 statistics formulas, styles/merges, blank measurement cells,
Units, LOGO physical frames and the preserved Remarks budget. Frozen implementation
and registered-source hashes match the values above.

QA independently compared final business preview token `613fc50...` to pre-fix
`5651fad...`: 1,599 Group 2 cell values, translated formulas and semantic styles
match. Group 2 has B/Q/AF, three LOGOs and unchanged 136.6-point Remarks; Group 6b
correctly keeps its original two rounds at B/O, two LOGOs and unchanged 92.4-point
Remarks. A preliminary diagnostic applied Group 2's round/height assumptions to
Group 6b; this was corrected in the QA script, not treated as a product failure
or used to change the valid generator. The final browser artifact hash is b07a026...
as recorded above. No native Excel rendering/printing, packaged release execution
or full-repository test claim is made for this revision. The frontend and safe
publication chain were unchanged; their earlier valid evidence is retained.
