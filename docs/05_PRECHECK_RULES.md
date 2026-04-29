# Precheck Rules v1

## Rule Format

Each rule returns zero or more PrecheckIssue objects.

```text
rule_id
category
level
field
condition
message
suggestion
```

## Form Rules

### FORM-001 Form number

Expected: `E-3718`.

If missing or different, create WARNING or ERROR depending configuration.

### FORM-002 Form revision

Expected: `Rev H`.

### FORM-003 Reference document

Expected: non-empty if form footer includes reference doc field.

## Requestor Rules

Required:

- Requested By
- Date
- Email
- Business Unit
- Mfg. Site

Phone is warning if missing.

Project # is optional application metadata. It may be parsed and stored when present, but it must not block precheck or project continuation.

## Sample Rules

Required per non-empty sample row:

- Product Name
- Part Number / Revision
- Traceability / Manufacturing Lot Info
- Contact Base Material
- Contact Plating
- Housing Material
- Quantity

Quantity with symbols like `+`, `/`, or free text should create WARNING to confirm interpretation.

## Testing Description Rules

- Empty Description of Requested Testing -> ERROR.
- Text such as “see attachment”, “依附件”, “per attached” without registered attachment -> WARNING.
- Applicable Specifications empty -> WARNING.

## Subcontract Rule

Extract Yes/No. Missing -> WARNING.

## Lab Section Rules

Required before folder generation if workflow policy requires:

- Lab Performing the Tests
- Lab Personnel Assigned
- Date Lab Received Samples
- Estimated Completion Date
- Condition of Samples when Received

Estimated Completion Date may be missing during early precheck, but must be flagged.
