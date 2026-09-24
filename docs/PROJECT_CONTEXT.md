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

For Intake requests with a manually specified full DL, preview the public workbook before completion.
An exact existing number presents its current row beside the proposed replacement for confirmation.
An absent associated suffix (for example, `DL-2026-09-002A`) is eligible only when its base row exists;
show that base row read-only beside the proposed new row, then append the suffix as a separate row in
the base number's annual sheet. Revalidate the confirmed target/base state under the workbook write
transaction; a missing base, duplicate target, or stale row blocks the write. An associated append
never replaces the base row.

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

### Independent Project Schedule

- `Confirm schedule` confirms the three schedule dates and post-test buffer independently of
  `Confirm Matrix` and Basic Information confirmation. It validates its own required ISO dates,
  chronology and buffer; sample receipt and calculated Matrix days are reference/defaulting inputs.
- Upstream Basic/Matrix references on a schedule revision are optional provenance, not prerequisites.
  Later upstream changes do not revoke an explicitly confirmed schedule. Output consumers read that
  revision; the legacy Matrix-date fallback remains only when no independent revision exists.
- Matrix confirmation validates Matrix rows, groups, quantities and Day expressions, not legacy
  schedule completeness. Loading a saved draft preserves its rows, order and cleared text; a source
  preview may supply review metadata and excluded-group context, never reinsert deleted test rows.
- Existing schedule tables migrate transactionally to nullable lineage with history and constraints
  preserved. Operator databases and external project outputs must not be replaced to deploy this fix.

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
- The normal project-folder entry creates a missing folder, opens a healthy indexed folder, or links
  an existing same-project folder by repairing only its `.connlab` identity manifest and local SQLite
  binding. Linking never copies, renames, deletes, tree-hashes, or rewrites operator business files.
  Ordinary additions, edits, deletions, and file locks inside the official project folder do not change
  project identity; identity comes from the immutable `project_id`, registered DL number, configured
  workspace boundary, and manifest. Symlinks, junctions, reparse points, unreadable/foreign manifests,
  or identity changes during linking fail closed. The legacy Create action never mutates an adoptable
  existing folder and instead directs the operator to Link existing folder. Linking does not require
  the configured template source to remain reachable; template validation is deferred to a later
  create/rebuild operation. A manifest that changes to a different reviewed official-folder identity,
  even for the same project and DL number, wins the race and is preserved while linking fails closed.
  Retained SQLite paths are rechecked against the configured workspace boundary and expected child
  layout before they are treated as completed; no path below any project workspace may be reused as
  a generation template.
- Rebuild is a separate advanced operation. New rebuilds only offer `Backup and Rebuild`, which moves
  the reviewed inner business folder to `LTR/History/Folders/<old name + timestamp>` before creating
  a fresh folder. The LTR root, `Source Book`, and other root-level files remain in place. New operations
  cannot select legacy incremental continuation or delete/overwrite rebuild; already-persisted legacy
  journals may still resume those historical choices so interrupted releases remain recoverable.
  Ordinary preview and linking do not hash the business tree; only the explicit rebuild preview binds
  approval to current target contents. History names use the original folder name plus its local
  last-modification timestamp (`yyyyMMddHHmmss`), with collision suffixes.
- New official project folders use the latest confirmed Basic Information product description and
  test item, with existing Project/LTR/application-form fallbacks when absent. The registered LTR
  remains the DL-number authority. Unconfirmed Basic drafts never name official folders. The inner
  folder's descriptive name is mutable, not project identity. A confirmed name change offers an
  explicit, identity-checked in-place rename and updates live indexed paths. A uniquely identified
  manual rename offers explicit rebind while retaining the custom name or adopting the confirmed
  name. Retaining a custom name requires an explicit, reviewed in-place update to refresh outputs;
  it is never silently converted into a whole-folder rebuild. Manual rebind requires a previously
  recorded stable folder identity; older manifests without that proof require manual review.
  Foreign or unreadable manifests, multiple active DL-prefixed folders, redirected paths, and
  changed preview context fail closed; historical operation snapshots are not rewritten.
- Include file, operation, and external-context details in actionable errors without exposing local
  paths unnecessarily in the UI.
- Project-folder required-form work files use an operation-isolated `data_dir/stage/<operation_id>`
  root; durable journal hashes, locks and recovery locations remain unchanged. Customer Feedback uses
  extended Windows paths throughout its filesystem/openpyxl boundary, including UNC inputs, rather
  than requiring a machine-wide long-path policy change. Returned/indexed paths keep their normal form.

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
