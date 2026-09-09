# ConnLab Project Context

Status: current engineering context. Read the relevant section only; inspect code for exact behavior.

## Product and authority

ConnLab is an offline, Windows-first workbench for an electronic connector laboratory. Project is the
lifecycle and traceability container. Matrix is the authoritative map of what must be tested. Test
records, reports, fee evaluation, and approval packages are derived outputs.

The current foundation is Project Workbench / Matrix / Approval Package, moving toward Matrix-driven
laboratory execution. Do not revive the old `TestFlowManager` design or implement future execution
concepts merely because archived plans describe them.

Existing public-drive LTR workbooks and approved Word/Excel templates retain the authority assigned by
their implemented workflow. SQLite is a local cache, automation aid, and migration backup. Any
authority cutover must be an explicit task with migration and recovery behavior.

## Domain ownership

- **Project** owns lifecycle identity and traceability.
- **Matrix** owns confirmed test intent, grouping, methods, conditions, samples, and execution mapping.
- **Application/Precheck** own intake facts and the first quality gate.
- **LTR and project-folder workflows** operate downstream of a confirmed Project.
- **Runtime projections and UI models** are derived views, not identity.
- **Test records, reports, fee drafts, and approval packages** consume confirmed authority; they do not
  redefine it.
- **Word/Excel/PDF/email files** are external inputs, outputs, or configured authorities, not a reason
  to store the domain as untyped strings.

When ownership is unclear, trace the current entry point, persisted record, write path, and consumers.
Do not use a dated snapshot as a substitute for the code.

### Project closure and registry location

- Business lifecycle and registry location are independent. A closed project is still a normal
  record; a project in the recycle bin (`trash`) or retained history (`history`) keeps its lifecycle.
- The immutable internal `project_id` identifies the retained aggregate. A displayed DL number does
  not identify a unique database record and must never be used as a replacement or deletion key.
- Registry moves retain Matrix, fee and output records, LTR associations and ownership, and external
  files. Conflict-aware restore can move the current records into history; it never overwrites them.
- Normal lists, selectors, counts and work queues exclude hidden records. Read-only inspection and
  audit can still resolve them; ordinary writes require restoration first.
- Registry transitions and business writes share the project-generation lock. A queued or running
  generation prevents a registry move; transitions revalidate all conflicts in one transaction.
- New closure actions require an explicit reason; only Other requires a note. Output exceptions are
  reminders, and reopening is separate from restoring a hidden record.
- [Management behavior and acceptance](project_registry_management.md) defines this boundary.

### Matrix draft lifecycle

- A Project has at most one editable Matrix working draft (`status = draft`).
- Imported working drafts can autosave before the first confirmation. Saving does not establish
  confirmed authority; first confirmation reuses the imported draft and preserves source lineage.
- Registry Matrix confirmation is derived from active confirmed authority, not legacy Project status;
  it does not imply that all prerequisites for test execution are satisfied.
- Confirming a Matrix archives its source draft as `superseded`; confirmed authority keeps that
  lineage record and its immutable confirmed snapshot.
- Startup reconciliation may physically remove only stale draft aggregates that are not referenced by
  any confirmed Matrix version. Source-import snapshots and confirmed Matrix history remain intact.
- Archived drafts are read-only and cannot be reactivated by a stale save request.
- Step Description / Requirement edits are draft content scoped to group, row, step sequence and
  suffix. Saving leaves active authority unchanged; successful Confirm copies selected-group values
  into a new immutable version. Failed confirmation retains the saved draft and prior authority.
- An excluded group keeps its text in the working draft. Null inherits defaults; an explicit empty
  string clears that step's text. Description does not change the canonical test-item classification.
- Manual Matrix drafts can autosave without importing a file; first save establishes reusable manual
  source lineage. Original methods are preserved when no external Standard catalog is available.

## Architecture seams

```text
React frontend -> FastAPI routes -> application modules -> domain/interfaces
                                                        ^
                                                        |
                                             infrastructure adapters
```

- `backend/domain`: pure concepts and invariants.
- `backend/application`: use cases and orchestration through interfaces.
- `backend/infrastructure`: persistence, files, Office, processes, and platform adapters.
- `backend/modules`: cohesive bounded implementations.
- `backend/api`: thin transport and typed Pydantic v2 responses.
- `backend/shared`: only genuinely shared primitives.

Domain must not depend on API, UI, SQLAlchemy, Office, or concrete infrastructure. Routes and UI
handlers coordinate rather than absorb business rules. Prefer an existing deep module and public seam
over a new pass-through layer. Introduce an adapter seam only when behavior actually varies.

## Windows, files, and Office

- Keep Word/Excel/Outlook access behind infrastructure gateways or the existing Office facade.
- Prefer offline parsers such as `python-docx` and `openpyxl`; isolate `pywin32`/COM details.
- Release COM objects, file handles, temporary resources, and child processes deterministically.
- Keep blocking Office and filesystem work off the UI thread.
- Test development and packaged path resolution when resources or configuration change.
- Never overwrite an authoritative workbook or existing project folder without the explicit conflict
  and recovery policy authorized by the task.
- Include file, operation, and external-context details in actionable errors without exposing local
  paths unnecessarily in the UI.

## Technical baseline

- Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, and pytest.
- React and TypeScript frontend with centralized typed API access.
- Windows and Microsoft Office integration where the workflow requires it.

Exact routes, DTOs, tables, and state shapes change frequently. Inspect `backend/api`, application
modules, migrations/models, frontend API types, and tests rather than maintaining a duplicate route or
schema catalog here.

## Change heuristics

- Preserve implemented business behavior and compatibility unless the request changes it.
- Prefer the smallest coherent behavioral change and reuse current seams.
- Do not introduce dependencies, generic workflow engines, future-scope abstractions, duplicate state
  channels, or framework migrations without a current demonstrated need.
- For structure changes, first establish a practical regression seam, then move responsibility without
  mixing unrelated behavior changes.
