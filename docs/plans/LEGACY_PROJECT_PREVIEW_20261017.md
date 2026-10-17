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

Initial frozen subject `ab9983b3` passed the affected Python gate (25) and the complete default-worker
frontend gate (961 passed / 1 existing skip, 29.30s), plus sequential typecheck/build (187 modules,
1.60s). Actual browser preview showed the expected 36 rows / 30 selected / 6 review and 18px aligned
checkboxes without desktop document overflow. Visual inspection then found native secondary-button
styling and a duplicated page title. These two presentation issues were corrected locally, followed
by 25 affected frontend tests passing again. The complete frontend gate and browser checks must
therefore be repeated on the final UI bytes; the unchanged Python inputs retain their passing gate.

## Final acceptance — 2026-10-17

Frozen executable subject: `ba07214bdb3cee7fcc8269e45f5e0afa69468d9d`. Worktree clean.

- Complete default-worker frontend: **961 passed / 1 existing profiling skip**, 103 files passed /
  1 skipped, **41.39s**. `tsc -b` and sequential Vite build passed, **187 modules / 1.18s**.
- Affected Python: **25 passed**, 20.28s during the first frozen gate; all backend/test inputs remain
  byte-identical at the final subject. No unrelated complete backend or Office gate was repeated.
- Final isolated UI used a byte-verified 38-file copy of the final build at `127.0.0.1:18766`, with
  every mutable setting under the task's Temp root and external LTR disabled. No live 5173/8000
  service was accessed. Tools navigation, 36 real rows / 30 selected / 6 review, overlapping-root
  collapse, clear/reselect/manual selection, mocked-503 failure + real retry, stop, and return passed.
- Desktop 1440x1000 and narrow 514x900 have no document horizontal overflow; narrow table scroll is
  local. Checkboxes measure 18px. The final screenshot has one page heading and consistent actions.
- Native picker cancel/selected responses were simulated at its HTTP boundary; the operating-system
  dialog itself was not clicked by automation. Manual directory entry was exercised end to end.
- First separated slow-request harness expired before its Stop click; this harness failure is
  retained. The replacement atomic controlled-delay sequence passed with three roots retained,
  no result table after stopping, and no late result. No product code changed for the harness.
- Console contains exactly one expected resource error from the deliberate mocked 503, with no
  application exceptions or warnings. It is not represented as a zero-error run.
- All **2,747** source inventory entries and read metadata hashes still match their pre-final-UI
  baseline. Browser and owned backend process tree stopped; port 18766 closed.

Final machine evidence: `qa-final-result.json` in the Temp evidence directory above. Final logs are
`qa-frontend-final.log`, `qa-python-ab9983b3.log`; screenshots and DOM evidence are in
`output/playwright/`. Sequential Developer/Reviewer/QA/Integrator passes are all by the same agent.
No formal import, business-data/source mutation, push or publication occurred.

## Tools card copy follow-up (2026-10-17)

User feedback changes only the Tools entry card: heading `Legacy Project Files`, action
`Import Legacy Projects`. Its former gray paragraph is now an English native button hover tooltip:
`Preview existing project folders in batches. Original files and folder structure remain unchanged.`
The preview page and read-only behavior are unchanged.

After the final code/test edits, targeted Vitest validation passed: **22 tests / 2 files**
(`ToolsPage.test.tsx`, `App.test.tsx`). Same-agent focused diff review found no scope or behavior
regression. The native tooltip uses the browser's `title` behavior; no separate visual UI run was
performed for this copy-only follow-up. Earlier full frontend, Python, and isolated UI results above
describe the prior executable subject; no full matrix was repeated for this bounded copy change.
No business data, original project directory, push, or publication is involved.

## Preview page copy follow-up (2026-10-17)

User requested the same English and hover-help treatment for `/tools/legacy-projects`.
The page title, controls, table labels, states, generated diagnostics and native picker title now use
English. Folder-selection guidance and limits are on the related controls' native `title` tooltips;
read-only guidance is on Start Preview and batch-only comparison scope is on Select Clear Projects.
Counts, conflicts, errors and incomplete-result alerts remain directly visible. Source folder names
and project names remain as supplied; detection, selection and cancellation behavior is unchanged.

- Final targeted frontend: **25 passed / 3 files**. First attempt had three failures because a literal
  replacement stopped before updating the preview test; corrected test labels and rerun passed.
- Final affected Python: **14 passed**. Initial sandbox run failed at fixture setup because pytest
  could not create temporary directories; the identical command passed with the required boundary.
- TypeScript and sequential Vite production build passed, **187 modules / 1.74s**.
- Same-agent Standards review: **0 findings**. Spec review: **0 findings**. Scope contains only this
  feature's display strings, helper placement, matching tests and this record; no data logic changed.
- Existing browser at 598x804 shows the English shared heading, Back to Tools, Choose Folder,
  collapsed manual-path entry and Start Preview, with no persistent gray paragraphs. Manual entry
  expanded and collapsed successfully; accessibility Help exposes the English tooltips. Screenshot:
  `legacy-preview-english.png` in the Temp evidence directory above. No folder was submitted or API
  preview started.
- Browser check covers the initial/manual-entry layout; result/error behavior is covered by targeted
  tests. No complete frontend matrix or real-sample scan repeated for this bounded copy follow-up.

No business database, original directory, push or publication was modified.

## Exact changed paths (excluding task board)

- `backend/api/main.py`
- `backend/api/routes_tools_legacy_projects.py`
- `backend/application/legacy_project_preview_service.py`
- `backend/infrastructure/files/legacy_project_preview_gateway.py`
- `backend/infrastructure/files/windows_path_picker.py`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`
- `frontend/src/api/legacyProjects.ts`
- `frontend/src/features/legacy-projects/LegacyProjectPreview.tsx`
- `frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx`
- `frontend/src/features/legacy-projects/legacy-project-preview.css`
- `frontend/src/pages/ToolsPage.tsx`
- `frontend/src/pages/ToolsPage.test.tsx`
- `tests/unit/test_legacy_project_preview.py`
- `tests/integration/test_tools_legacy_projects_api.py`
- `docs/plans/LEGACY_PROJECT_PREVIEW_20261017.md`
