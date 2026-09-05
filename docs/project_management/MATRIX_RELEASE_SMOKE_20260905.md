# Matrix release acceptance — 2026-09-05

Task: `TASK_MATRIX_RELEASE_SMOKE_20260905`.
Local build and isolated packaged-runtime acceptance complete; second-computer/operator acceptance remains pending.
The original release-delivery step changed no product code, schema, dependencies, existing release, real database or public-drive material.
The subsequent development-environment correction below changes frontend rendering only; the delivered ZIP is unchanged.

## Delivered artifact

- Release: `ConnLab_Web_202609051010_v0.1.0-matrix1`.
- Source commit: `c94eb2d64c49b4f993de1a8041aeb776fc51fa21`.
- Source identity is read mechanically from Git and embedded in `_internal/release_manifest.json`.
- Output directory: `C:/Users/White/Documents/Codex/ConnLab_Releases/ConnLab_Web_202609051010_v0.1.0-matrix1`.
- Portable ZIP: same path plus `.zip`; 55,176,725 bytes.
- ZIP SHA-256: `6ddab486ac23bd8ef5d95773fadc5564678495972741e38ffd88454883ad5329`.
- Server SHA-256: `0ea5133a75bbefdb20a3c70b85860ddca0b2edd85f0fdd5aa0cf61d6b14b642a`.
- All 1301 delivered files matched the built/tested folder byte-for-byte; ZIP CRC verification passed.
- Chinese operator checklist: `C:/Users/White/Documents/Codex/ConnLab_Releases/Matrix新版验收清单.md`.
- Build/acceptance artifacts: `C:/Users/White/Documents/Codex/2026-08-07/new-chat/matrix-release-20260905-final`.

## Build and checks

Reused the existing browser release script/spec in an immutable source snapshot with no source edits.
Selected only required source/resource paths, excluding tracked historical release binaries. Reused the existing
ConnLab Python 3.11.9 environment/PyInstaller 6.22.0 and frontend dependencies. The wrapper routed `py` to the
project interpreter and `npm` to `npm.cmd`; it preserved the source commit in the packaged manifest.
All build cleanup targets were absent or confined to the new scratch snapshot; existing release/build data was not removed.

The prior full QA code subject `707e89712e2d9ea801be258bab4a54b4a61024ce` is unchanged in implementation/tests.
The build used `-SkipTests` intentionally: it did not rerun that full gate (2565 Python / 482 frontend tests).
A fresh TypeScript/Vite build passed in 10.2 s; PyInstaller 110.9 s; release assembly 2.1 s.
Optional hidden-import warnings included tzdata and non-SQLite database drivers; these did not block the tested flows.

Actual new EXE acceptance, on loopback 8877 with synthetic data/config/template only:

- Health and production frontend routes passed, including deep-link Matrix loading.
- A real synthetic Word file parsed through `/api/test-plan/matrix-preview-from-path` and imported through
  `/api/projects/P1/matrix-import/commit`; no mocked backend or development server was used.
- UI edits corrected the parser-only sample's sequence gaps and supplied sample quantities using normal controls;
  business validation was not disabled. First-group/first-step description and requirement autosaved.
- The EXE was stopped/restarted before first Confirm: draft text survived, another group and another step stayed unchanged.
- UI Confirm created revision 1. Reopen retained text; actual generated Word XML contained the description only once,
  with the matching requirement. Matrix XLSX retained canonical shared-row items and group step strings.
- A second UI edit was saved but not confirmed. Active snapshot and formal Word output stayed unchanged.
  A deliberately stale confirmation returned HTTP 409 and preserved draft/authority. These checks also passed after EXE restart.
- A separate synthetic project exercised manual Matrix creation without import: save, reload, and UI Confirm passed.
- Support diagnostic ZIP contained the release manifest and isolated log after aligning the test harness's log override
  with the packaged logger's actual isolated path. No product logging implementation changed.
- Browser warning/error log was empty; request logs had no HTTP 500 or exception traceback.
- The delivered copy separately started with a fresh empty user directory on port 8878: health, app shell and empty
  project registry passed. This tests relocation/fresh startup, not real-old-database migration.
- Owned browser tab and test EXE processes were stopped. Existing operator installation/server was left untouched.

Review and QA were distinct focused passes by the same agent, not independent role agents. Review checked scope,
manifest/hash consistency, copied bytes, isolated paths, actual runtime evidence and stated limitations.

## Limitations and findings

- Windows file-selection dialog upload was not completed by browser automation. Import parser/commit were exercised
  through the packaged server's public path API; the UI import entry itself was inspected. The second-PC checklist explicitly
  requires the normal picker/upload path. Do not describe this as a fully automated end-to-end file-dialog test.
- No second computer, real operator database upgrade/rollback, actual lab templates, or exhaustive Office COM gate tested.
- The synthetic Word's first preview took 29,294 ms despite succeeding; import commit took 26 ms. Treat this as an
  observed remaining responsiveness issue, not a proven root cause or a broad performance pass. No unrelated fix added.
- First unconfirmed draft reopening displayed generic no-change/return wording although Confirm correctly created version 1;
  this is a copy-clarity observation, not a failed persistence result.
- An initial whole-repository archive unnecessarily included tracked old release binaries; only this task's archive processes
  were stopped and a scoped source archive was built instead. No original files deleted.
- Fixture setup initially reused a fixed Basic Information ID for two projects. After verifying the partial synthetic state,
  preserved the two projects and P1 information and generated only missing sample files. This was a harness issue, not an app defect.

## Next operator action

Copy/unzip the new package to a new folder on the second PC; back up its current data/config and stop its old service first.
Do not overwrite the old release or replace real data with this synthetic fixture. Follow the Chinese checklist, recording
the release identity, exact failed step, screenshot, timing and diagnostic ZIP if a problem occurs.

This task delivers the local accepted artifact and checklist; it does not claim a production deployment or second-PC signoff.

## Development-environment follow-up: legacy Workbench flash

User clarified that this is a bug at `http://localhost:5173/`, not feedback from the distributed release.
Environment/version transparency remains deferred. No release was rebuilt and no real project data was edited.

- Cause: Matrix and LTR identity arrive asynchronously. The shell selected `active_matrix` from the snapshot,
  while the layout additionally required an LTR number. A confirmed Matrix with an unresolved LTR therefore
  fell through to the obsolete Temporary planning cards until identity arrived.
- Fix: render the unified Matrix workspace when its authority snapshot exists, otherwise the unified no-Matrix
  workspace. Remove the old stage-banner/mode-tabs/temporary-promotion rendering branch and its local state.
  Keep registration gating on project-folder creation and preserve closed-project read-only status/actions.
- Implementation and regression test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  and its `.test.tsx`. Source subject: `45fc53609a289b5207133ecdcd1dedc557622ac3`.
- RED: the new public-UI regression reproduced the screenshot's Temporary planning region and old promotion
  cards with a confirmed snapshot and no LTR; 1 failed / 42 passed before the fix.
- GREEN: 43 focused layout tests passed. Focused review checked async identity, no-Matrix, closed-project,
  registration and folder guards; final QA on committed source passed 75 files / 483 frontend tests (16.97 s).
  TypeScript checks and Vite production build passed (Vite stage 1.02 s). No Python/API/schema changes.
- Browser: used the existing development tab, returned to Projects and opened DL-2026-08-008 through its
  real Open Workbench button. Matrix projection and unified actions rendered; browser warning/error log was empty.
  No real project mutations were performed. The millisecond flash was reproduced by the controlled UI test,
  not claimed as captured by browser snapshots.
- Diagnosis, implementation, focused review and QA were sequential passes by the same agent, not independent agents.
- Residual boundary: unused historical component definitions remain in their existing module, with no runtime
  callers; this fix removes their live entry path rather than doing unrelated repository-wide dead-code cleanup.
  The already-distributed ZIP does not contain this follow-up fix; include it in a future explicitly requested release.

## Development follow-up: initial Matrix step appearance

- User requested initial black step numbers instead of simulated execution-stage colors.
- Removed sequence-modulo status generation from `projectWorkbenchMatrixProjectionSelectors.ts`.
  Preview tokens now carry `not_started` until an actual execution-data integration is implemented.
  `workbench.css` renders this state with black text and the existing neutral background; selection outline remains.
  No backend execution records were changed and no execution feature was implemented.
- Regression in `ProjectWorkbenchMatrixProjectionPanel.test.tsx` selects steps 1–6 through public UI
  and checks the selected token's initial status. RED failed on step 2's fake `in_progress`; GREEN passed all 10 panel tests.
- Final source `b918aed60992d830b961f14d05a5bf6aa2d4e4fe`: 75 files / 484 tests passed with two workers
  (51.52 s); TypeScript and Vite build passed (Vite 1.01 s). Initial high-concurrency suite had one
  unrelated 256-category contact-measurement test timeout; its isolated run passed in a 1.26 s suite.
  The new test initially used unsupported Testing Library `exact` options; those were removed before final validation.
  No timeout or assertion was relaxed. Lower concurrency is a command-local validation choice, not a repository setting.
- Real development page: all 77 rendered step buttons computed to `rgb(0, 0, 0)` with neutral background.
  Clicking the user-selected step 4 retained black text and the selected outline.
- Standards review: no finding; minimal selector/style change, no new abstraction or dependency.
  Spec review: no finding; simulated statuses removed rather than merely hidden, step selection preserved.
  Review and QA were same-agent passes. Existing release ZIP remains unchanged.
