# Phase 7 Folder Evidence Placement

## Real Folder Shape Observed

The local template and generated sample were inspected read-only during
`TASK_047`.

Template root:

- `DL-XXXX-YY-ZZZ/`
- `DL-XXXX-YY-ZZZ/DL-XXXX-YY-ZZZ Title/`
- `DL-XXXX-YY-ZZZ/DL-XXXX-YY-ZZZ Title/E-mail/`
- `DL-XXXX-YY-ZZZ/DL-XXXX-YY-ZZZ Title/Photos/`
- `DL-XXXX-YY-ZZZ/DL-XXXX-YY-ZZZ Title/Submitted Material/`
- `DL-XXXX-YY-ZZZ/DL-XXXX-YY-ZZZ Title/Test results/`
- `DL-XXXX-YY-ZZZ/Source Book/`

Real generated sample:

- project root is named by DL number
- the primary evidence folder is the child folder whose name starts with the DL
  number and includes the project title
- original `.msg` files are stored under `E-mail`
- request materials and specifications are stored under `Submitted Material`
- photos are stored under `Photos`
- raw test/source material remains separate from intake evidence

## Placement Rules

ConnLab places project evidence under the primary title folder when it can be
detected. If the title folder is missing, ConnLab previews targets under the
project folder root and returns a warning.

| Evidence | Target |
| --- | --- |
| Original Outlook `.msg` | `E-mail/` |
| Selected application form | `Submitted Material/` |
| Supporting attachments | `Submitted Material/` |
| Specifications and drawings | `Submitted Material/Specifications/` |
| Photos and images | `Photos/` |
| LTR readiness/preview/commit evidence | `Submitted Material/LTR Evidence/` |
| Corrected or revised evidence | `Submitted Material/Corrections/` |

## Safety Rules

- Preview runs before copying.
- Source files must exist before execution.
- Existing target files are never overwritten.
- Duplicate target paths in the same plan block execution.
- Corrected evidence is copied to `Corrections`; older evidence is not deleted.
- This task does not mutate the external LTR workbook and does not execute LTR
  renumbering or folder rename operations.
