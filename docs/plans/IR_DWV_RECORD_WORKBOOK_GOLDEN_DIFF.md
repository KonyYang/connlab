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
