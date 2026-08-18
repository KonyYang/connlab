# ConnLab Engineering Brief

## Product Definition

ConnLab is an offline Windows-first connector laboratory project workbench. Its first version supports project creation from an application form, deterministic precheck, LTR tracking, and project folder generation.

## Why ConnLab Exists

The old system grew from small tools: LTR application, folder creation, Matrix, test records, report initialization, equipment updates, fee sheets, customer report conversion, and later report updates. The result was functional but scattered. ConnLab prevents the same failure by making Project the center and keeping every feature attached to a lifecycle stage.

## MVP Lifecycle

```text
Import application form
  -> Parse fields
  -> Run Precheck
  -> Confirm project metadata
  -> Register LTR number
  -> Preview project folder generation
  -> Generate folder from template
```

## Future Lifecycle

```text
Application / email / customer request
  -> Precheck
  -> Standard/spec confirmation
  -> MatrixPlan
  -> TestRecord
  -> TestResult from Excel/raw data
  -> TestAsset image management
  -> LabReport dataset
  -> ReportAudit
  -> Word/PDF export
```

## Design Red Lines

- Do not implement future features in MVP tasks.
- Do not create a feature-button collection UI.
- Do not let Word/Excel become the primary data model.
- Do not place business rules in UI or API route bodies.
