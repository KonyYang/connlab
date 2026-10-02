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

### Project Schedule in Matrix Editor

- Project Schedule fields are edited in Matrix Editor and confirmed through its single `Confirm Matrix`
  action. Post-test buffer, planned start, test completion and estimated completion are Matrix draft
  fields: changing only these fields still creates a new confirmed Matrix version. Confirm Matrix
  validates the three required ISO dates, their order and the buffer before publication. Calculated
  Matrix days can suggest dates; the sample-received date remains Basic Information authority.
- Independently confirmed Project Schedule revisions from older releases remain readable as migration
  evidence, but no new independent revision is created. When a historical confirmed revision differs
  from Matrix dates, the editor prefills its actual confirmed dates into empty Matrix draft date fields;
  nonempty saved draft fields and an intentionally blank zero-day buffer remain untouched. The older
  values are shown for review before the operator uses `Confirm Matrix`. Publication checks the
  historical revision and supersedes it atomically. Until then, formal outputs are blocked instead of
  silently using older Matrix dates or deleting newer historical work.
- Formal outputs read planned dates and buffer from the confirmed Matrix, and sample receipt from Basic
  Information. A missing Basic sample-received date remains an output-level blocker, not a Matrix
  confirmation blocker. Incomplete confirmed Matrix history remains readable but cannot produce
  date-dependent outputs. The retired Project Schedule write API cannot publish a second date authority.
- Loading a saved Matrix draft preserves its rows, order and cleared text; a source preview may supply
  review metadata and excluded-group context, never reinsert deleted test rows. Existing schedule
  tables and external project outputs are not replaced to deploy this change.

### Test points in Matrix Editor

- LLCR/CR project point IDs are shared by all Matrix steps and edited in the Matrix Editor draft.
  They become authority only through `Confirm Matrix`, together with the rest of the Matrix. New
  Group/step point subsets are no longer supported. Existing confirmed versions retain their saved
  subsets for historical reading and projections; an old draft with subsets must be explicitly
  switched to project-wide points before another Matrix confirmation, never cleared on load.
- Older independently confirmed point profiles remain readable as migration evidence. Only explicit
  IDs with a matching count may prefill the Matrix editor for review; count-only suggestions must not
  become authoritative point IDs. The retired independent Setup confirmation cannot publish a second
  authority. Fee and LLCR/CR record projections prefer the confirmed Matrix point plan; older
  projects without one can still read their existing point-profile authority for compatibility.
  That read-only fallback does not guess IDs or publish a new independent point authority.
- A workbook downloaded from an unconfirmed Matrix editor is a draft preview, not a formal test record.
  IR and DWV share optional measurement-pair text in the same Matrix draft (`electrical_point_pairs`).
  One compact text box sits beside `IR / DWV test points`, without a separate count label, categories,
  Group/step settings or coverage lists. Commas, Chinese commas, semicolons, Chinese semicolons,
  ideographic commas and line breaks separate pairs; empty entries are ignored. Pair operators such
  as `&`, `and` and `-` belong to the label, never split endpoints. For example,
  `Odd&Even，P1&P2, P1 and S2；PE-HOUSING` is four readings per sample. Text is retained for reopening;
  the backend derives the count (at most 8192 pairs and 65536 characters) rather than trusting a
  client-supplied count. Blank text clears electrical points; separator-only text is invalid.
  Existing separate numeric JSON fields remain readable for compatibility, with no label guessing or
  writes on load. Numeric-only editor input retains legacy count behavior. Unequal legacy counts
  require an explicit shared value before another editor confirmation. New pair text takes precedence
  over legacy counts, including an explicit clear. Each pair means one reading, not two connector
  pins or a sample number.
  The shared count applies to all selected IR/DWV steps, becomes authority only with `Confirm Matrix`,
  and populates the existing confirmed Step quantity snapshot. Fee consumes samples × points (the first quantity in `5+5(d)`),
  never live Matrix draft values. Clearing a previously confirmed electrical count restores quantity
  review; newly added steps inherit the configured count, removed/unselected steps do not contribute.
  LLCR/CR IDs and their compatibility fingerprints remain independent of these electrical counts.
  Historical JSON profiles without electrical settings remain readable without migration.
  Measurement pairs are entered and reviewed manually in Matrix Editor, then become authority through
  `Confirm Matrix`. Automatic extraction from specifications is not part of the required workflow.
- IR/DWV blank-record workbook generation is implemented through `IR&DWV Form` in Matrix Editor,
  using the configured Excel template and Matrix groups, sample quantities, measurement pairs,
  conditions and requirements. IR and DWV share each round's form; measured results remain blank.
  The writer uses `openpyxl`, not Excel COM.
- LLCR/CR and IR/DWV form actions in Matrix Editor first check whether the current on-screen Matrix
  matches the confirmed authority. Unconfirmed edits stay in a browser-downloaded preview; a verified confirmed
  Matrix may publish into its `Test results` folder. A same-name formal form requires explicit approval
  to preserve the old file under local `History/Test results` before saving a new blank form. No
  measured form is silently overwritten, and changed files or interrupted publication fail closed.
  IR/DWV files use the registered LTR plus `IR&DWV Record.xlsx`; unconfirmed downloads add
  the ` draft` suffix. A confirmed Matrix without an available official folder downloads the
  confirmed name, while internal download artifacts retain unique task-owned paths.
- If a CR fee row combines steps with different selected point counts, Matrix confirmation remains
  available, but that fee line requires human review rather than pricing from only the first step.
- An approved Create folder operation generates LLCR/CR blank workbooks in the official `Test results`
  folder only for confirmed Matrix steps with explicit point IDs. Missing point coverage skips the
  corresponding optional form with a warning; other projection or path failures block publication.
  The preview binds the target and any existing file's hash and filesystem identity. In an approved
  in-place update, an unchanged same-name file is moved without replacement to the local
  `History/Test results` before the new blank form is published without overwriting. Interrupted
  moves and output registration are journaled and fail closed if an operator changes either file.
  Whole-folder Backup and Rebuild instead retains the former business folder under `History/Folders`.
- Historical Matrix rows identified as LLCR/CR only by their structured contact plan are recognized
  for formal form generation, even when the test-item label is nonstandard. Their saved historical
  point subsets remain readable; new Matrix versions use the project-wide point IDs.

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
  a fresh folder from the configured template and latest confirmed authorities; old business files
  and subfolders stay in History and are never copied into the replacement. The new folder name follows
  the latest confirmed Basic Information, even when the archived folder had an older description.
  The LTR root, `Source Book`, and other root-level files remain in place. New operations
  cannot select legacy incremental continuation or delete/overwrite rebuild; already-persisted legacy
  journals may still resume those historical choices so interrupted releases remain recoverable.
  Ordinary preview and linking do not hash the business tree. New explicit archive/rebuild approval
  binds the sole active folder's filesystem identity and manifest, not its file bytes, descendant
  names, or descendant structure; historical content-bound journals retain their original recovery
  rules. If a retained manifest records the folder's filesystem identity, it must match before
  archival; older manifests without that field still require the indexed same-project/DL path and
  sole active folder; a missing or unreadable manifest blocks the new archive flow. Registered FileAsset
  sources inside the archive folder block generation before moving it. A new active sibling after the
  old folder moves blocks recovery. History names use the
  original folder name plus its local
  last-modification timestamp (`yyyyMMddHHmmss`), with collision suffixes.
- New official project folders use the latest confirmed Basic Information product description and
  test item, with existing Project/LTR/application-form fallbacks when absent. The registered LTR
  remains the DL-number authority. Unconfirmed Basic drafts never name official folders. The inner
  folder's descriptive name is mutable, not project identity. A confirmed name change offers an
  explicit, identity-checked in-place rename and updates live indexed paths. A uniquely identified
  manual rename offers explicit rebind while retaining the custom name or adopting the confirmed
  name. When an indexed folder already exists, the Workbench Create folder action instead offers a
  reviewed whole-folder archive/rebuild in that indexed LTR workspace; a changed default save root
  cannot move the new folder elsewhere. A previously queued relocation with no recorded move may
  be superseded only after folder and manifest identity are rechecked; a moved relocation still
  requires its own recovery. Manual rebind requires a previously
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
