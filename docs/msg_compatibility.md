# Outlook `.msg` Compatibility Notes

## Current Status

TASK_027C adds compatibility probing but does not claim full real Outlook `.msg` support yet.

Current repository state:

- Three real `.msg` samples are available under `tests/fixtures/msg_samples/` in the local workspace.
- Fixture-style `.msg` files used by unit tests are supported.
- The current OLE/MAPI reader successfully imports all available real `.msg` samples in this workspace.

## Supported In Current Code

- Preserve `.msg` source files under controlled intake storage.
- Read simple metadata from supported fixture-style `.msg` inputs.
- Read metadata from supported OLE-based Outlook `.msg` inputs without Outlook COM.
- Extract fixture-style attachments into an `attachments` directory.
- Extract supported OLE/MAPI file attachments into an `attachments` directory.
- Return clear unsupported results when metadata or attachment extraction fails.
- Preserve copied source files when parsing fails after source import.

## Not Yet Supported

- Full coverage for every Outlook `.msg` variant.
- Embedded message recursion and unusual attachment property variants.
- Outlook COM automation.
- Outlook inbox scanning.
- Email sending or message mutation.
- Project creation, intake persistence, or UI.

## Compatibility Probe Result Vocabulary

- `supported`: the sample imported, metadata was read, and attachment extraction completed.
- `unsupported`: the sample was present but the current parser could not safely read it.
- `blocked_missing_fixtures`: no real `.msg` sample is available to validate.

## Local Real Sample Validation

Latest local validation:

- real samples found: 3
- compatibility probe result: all available samples classified as `supported`
- Outlook COM required: no
- email content printed during validation: no
- project/intake database rows created: no

This is a positive local compatibility signal, not a guarantee that all customer `.msg` variants are supported.

## Required Next Evidence

Before relying on real `.msg` intake broadly, keep adding representative exported Outlook `.msg` samples that match actual lab request emails.

The sample should include:

- subject
- sender
- body preview
- at least one Word application form attachment
- optionally one PDF specification and one image/signature attachment

TASK_027C intentionally stops at compatibility classification. It does not add a third-party `.msg` parser dependency or Outlook COM automation.
