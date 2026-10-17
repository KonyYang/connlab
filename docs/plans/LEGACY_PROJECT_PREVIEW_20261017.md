# Legacy project read-only batch preview

Task: `TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017`.
Starting product state: `246b589f`. The previous rejected intake implementation remains withdrawn.

## User outcome and exact boundary

Tools has one **导入旧项目** entry leading to `/tools/legacy-projects`.
The operator chooses a project or a parent containing many projects, previews discovered boundaries,
reviews identity conflicts, and selects rows for inspection. This increment has no import/registration
button, persistence, database dependency, source copy/move/rename, manifest write, or Office automation.
Original Delete/Trash/History and all existing Tools remain unchanged.

Manual folders, older macro-tool workspaces, and moved ConnLab workspaces are accepted as evidence.
Neither a supported manifest nor a current template nor a DL is required. Suggestions are derived
from folder/file names and bounded optional `manifest.json` / `application_data.json` identity hints.
This is not recovery of confirmed Matrix, Fee, LTR registration, lifecycle state, or report authority.

## Operator flow

1. Tools -> 导入旧项目 -> 选择目录. Add up to 20 independent locations; each may contain hundreds
   of projects. A collapsed manual path input is available when native folder selection is unavailable.
2. 开始预览 -> one table with selection, suggested number/name, folder, and check result.
   Clear rows are selected initially; conflicts remain unselected. Missing numbers are permitted.
3. Stop, retry, remove a root, return to Tools, clear selection, or select clear rows. No action writes
   projects. Changing roots invalidates old results; stopped/unmounted requests cannot revive them.

Duplicate recognition compares only this selected batch, not registered business data. Same physical
roots and overlapping selections are collapsed. Equal DL/source hints in distinct directories are
shown as review items, never merged. A workspace containing Source Book and an inner formal folder
is one project. Existing History, `.connlab` internals, redirected paths, Office lock files and generated
backup folders are not independently discovered as projects.

## Read and resource boundaries

- No `get_session`, `get_settings`, SQLAlchemy, or database initialization in preview routes/service.
- Filesystem IO stays in a read-only gateway; the application service owns grouping/conflicts.
- Up to 10,000 visited directories, depth 6, 2,000 entries per directory, and 64 KiB per optional
  metadata file. Partial results are explicitly marked; inaccessible roots do not block other roots.
- Do not follow symbolic links or Windows reparse points, including metadata ancestors.
- Only allowlisted identity hints leave the metadata reader. Internal source IDs are used for
  comparison and removed from the response. Duplicate explanations show at most five other paths.
- Stop aborts the browser request and suppresses late results. A running bounded server read may
  finish; no background job, persistent scan state, or server-side writer is created.
- This preview does not traverse and parse all Word/Excel/PDF contents or run macros. It intentionally
  does not claim universal folder recognition; ambiguous legacy layout rules need actual samples.

## Acceptance and actual development feedback

Public seams: application preview + actual HTTP route; React preview page + Tools entry/App routing.
Meaningful RED/GREEN: missing preview module -> first 2 tests pass; unnumbered wrapper and invalid-root
duplicate count -> reproduced 2 failures -> corrected; 12 copies exposed unbounded explanation output
-> bounded output/hidden IDs pass. Missing preview page and Tools/deep-link entry failed before implementation.

Affected Python feedback: **25 passed**, including main-app dependency overrides that fail on any
database/settings request, 320 temporary projects, parent/child grouping, duplicate identities,
mixed source numbers, missing roots, bad/oversized/redirected metadata and existing desktop picker tests.
One existing Starlette TestClient deprecation warning remains.
Affected frontend feedback before final review: **25 passed / 3 files** (preview, Tools, App).

Read-only real sample feedback uses `D:/Project Model`, `D:/ConnLabProjects`, and the old
`D:/Source/2/DL-2024-12-050 EK200 Connector Qualification Testing` folder. It found **36 projects:
30 ready / 6 review**, no truncation, and no duplicate ancestor/descendant project boundaries.
Mixed `DL-2026-07-013A` vs JSON `DL-2026-07-005`, distinct same-DL `DL-2026-09-001` records,
moved manifest paths and an unnumbered folder were all identified. A 2,747-entry inventory of names,
sizes and modification times plus hashes of the small metadata files read was unchanged before/after.
This is 36 real samples; the 320-project scale case uses disposable test fixtures.

Evidence directory: `C:/Users/White/AppData/Local/Temp/connlab-legacy-preview-20261017`.
`real-sample-preview.json` is feedback, not a substitute for the final frozen-state QA.

## Final verification requirement

Review the exact diff for Standards and Spec separately. On the frozen product state, run the affected
Python matrix, one complete default-worker frontend gate with sequential typecheck/build, and an
isolated browser check of Tools navigation, real preview, selection/conflicts, cancellation/retry,
return and narrow layout. Verify sample inventory again. Do not use the live business service for QA.
No push or publication. Reviews/QA by sequential passes of one agent must be reported as such.

## Focused review before QA

Standards: 0 remaining findings. Filesystem/GUI adapters own external reads and resources, application
grouping has no storage dependency, frontend requests stay in its API module, and existing Tools,
Project registry and schema files are not repurposed. Private source identities are not returned.

Spec: 0 remaining findings for this preview slice. No formal import endpoint/button or registry write
exists. Roots and results remain local session state. Existing samples provide concrete grouping,
same-DL, mismatched identity and moved-path cases. A usability correction derives a name from the
inner formal folder when an outer workspace is named only by DL; its regression was RED then GREEN.

The implementing agent performed these two focused passes separately; they are not independent
agent reviews. Final Developer feedback is 25 Python tests and 25 frontend tests in three files.
