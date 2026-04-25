# Project Folder Template Design

## Folder Creation Principles

- Generate from external template.
- Provide preview before copy.
- Do not overwrite existing folders.
- Store generation record in SQLite.
- Copy original application form into request folder.

## Recommended Folder Structure

```text
{DL_NUMBER} {PROJECT_NO}/
  00_Request/
    attachments/
  01_LTR/
  02_Specifications/
    product_spec/
    standards/
    customer_requirements/
  03_Matrix/
  04_Test_Record/
  05_Raw_Data/
    LLCR/
    IR_DWV/
    Mechanical/
    Temperature_Rise/
  06_Images/
  07_Report/
    draft/
    review/
    released/
  08_Customer_Report/
  99_Archive/
```

## Placeholders

- `{DL_NUMBER}`
- `{PROJECT_NO}`
- `{PRODUCT_NAME}`
- `{REQUESTOR}`
- `{DATE}`
- `{BUSINESS_UNIT}`

## Conflict Strategy for MVP

If target folder exists, fail with clear message. Do not merge and do not overwrite.
