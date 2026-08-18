# TASK_289 Fee Template Testing Prices Layout Optimization Plan

## Goal

Optimize `D:/Source/Template/Testing Fee Evaluation-Even.xls` sheet `Testing Prices` for normal 100% editing and A4 portrait multi-page printing, while preserving the original workbook and preparing the layout for later Matrix-driven A-column group and C-column `Test item` filling.

## Design

- Use Excel COM only, because the source is `.xls` and must preserve formulas, merge areas, page setup, and workbook compatibility.
- Open the original template read-only and save optimized copies:
  - `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.qa.xls`
  - `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`
- Modify only `Testing Prices`; keep `Unit Price Reference` unchanged.
- Do not implement Matrix auto-fill or any fee calculation in this task.

## Layout Rules

- Page setup:
  - A4 portrait.
  - Fit to 1 page wide.
  - Do not fit to 1 page tall.
  - Use moderate margins instead of zero margins.
- Visible sheet:
  - Save workbook view at 100%.
  - Use compact typography: title 11pt, headers/details 9pt.
  - Reduce rows 1-12 from oversized 36.5 heights to compact working heights.
  - Reduce A-I widths for portrait print while leaving C as the widest text column.
- Future fill contract:
  - A column is group label merge area.
  - C column is Matrix `Test item`.
  - B/D/E/F/G/H/I remain available for later spend time, unit, price, discount, and fee work.

## Verification

- Confirm original template hash stays unchanged.
- Confirm optimized copy has both `Testing Prices` and `Unit Price Reference`.
- Confirm `Testing Prices` has `UsedRange=A1:I12`, `PrintArea=A1:I12`, A4 portrait, fit-wide only, and no fit-tall compression.
- Confirm key formulas remain unchanged.
- Confirm generated PDF preview exists.

## Accepted Formal Baseline

After initial generation, the user manually adjusted `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls` and accepted it as the formal optimized template baseline.

Baseline characteristics:

- SHA256: `ED1E73C68F87E51F34CED4202A0C2C02FC47056F7BC5444A9043BD4DDC73BE4E`
- `Testing Prices` `UsedRange` / `PrintArea`: `A1:I12`
- `A4 = Group`
- `C7 = Report preparation`
- Totals and signature area occupy rows 9-12.
