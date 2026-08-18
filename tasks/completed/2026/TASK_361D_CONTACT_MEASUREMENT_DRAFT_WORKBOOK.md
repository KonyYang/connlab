# TASK_361D Contact Measurement Draft Workbook

## Status

Complete / Integrator accepted on 2026-07-12. Developer implementation,
Reviewer implementation re-gate, QA smoke gate, and controlled Integrator package
isolation passed. Remote push was intentionally not performed.

## Lane

`contact-measurement-draft-workbook`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Integrator packaging/readiness closeout.
- TASK_361A/B/C are complete/accepted. TASK_361C was accepted in local commit
  `5d754bb1`; remote was not pushed.
- The accepted contract reserves TASK_361D for draft Measurement Plan workbook
  outputs and leaves confirmed-consumer migration to TASK_361E.
- Why allowed: Reviewer implementation gate and QA gate passed, and the package is
  limited to the TASK_361D draft-workbook projection, artifact, API/client, inline
  workspace UI, tests, docs/evidence, and board closeout.

## Goal

Add preview-first LLCR/CR specialized workbook outputs from the current independent
Measurement Plan editable revision. A draft or needs-review output must be visibly
and mechanically distinct from the existing TASK_360B confirmed-Matrix workbook.
The setup workspace may preview, generate, and download the draft artifact without
confirming the Measurement Plan or Matrix.

## Source And Authority Contract

1. The source is the project's current `editable_revision_id` from TASK_361B. The
   requested revision id must still be the current editable revision at preview and
   generation time.
2. The projection reads only the persisted revision snapshot, its target/family
   snapshots, revision fingerprint, Matrix binding, and impact/review state.
3. A confirmed Measurement Plan or active Confirmed Matrix is not silently used as
   fallback for this draft endpoint.
4. Draft workbook output is review material only. It is never an authority source
   for Fee, formal specialized workbooks, generic Test Record, Report, or Matrix.
5. TASK_360B remains the unchanged confirmed-Matrix-only compatibility path until
   TASK_361E separately migrates formal consumers.

## Deterministic Projection And Status

- Reuse the accepted TASK_360B family expansion and fixed layout rules: included
  LLCR/CR targets only; positive whole-number sample quantity and family counts;
  zero-count family omitted; no decimal rounding; normalized prefix uniqueness per
  Group-Step record section; readings per sample equals included family count sum.
- `ready`: current editable revision, non-empty valid sections, and no open
  review-required impact. Generation is allowed with output label `DRAFT`.
- `review_required`: current editable revision has open review-required impacts,
  but every included target is structurally valid and at least one record section
  exists. Generation is allowed with output label `NEEDS REVIEW`.
- `blocked`: stale/non-current revision, missing lineage or Matrix binding, malformed
  included target, invalid count, prefix collision, readings mismatch, or another
  structural diagnostic. No generation and no workbook file.
- `empty`: no included eligible LLCR/CR target or no materialized rows. No generation
  and no workbook file.
- No partial workbook is generated when any included target is structurally blocked.
  Excluded targets do not block generation.
- A preview fingerprint exists only for structurally valid, non-empty `ready` or
  `review_required` projections.

## Preview Fingerprint

The fingerprint must include at least:

- output contract and layout version;
- project id, editable Measurement Plan revision id/sequence/state;
- revision fingerprint and Matrix binding fingerprint;
- source/base Matrix id and revision;
- normalized projected sections and diagnostics;
- output label (`DRAFT` or `NEEDS REVIEW`).

Generate recomputes the projection and compares the full fingerprint. A changed
revision, review state, target/family value, Matrix binding, or layout version returns
a typed stale `409` and writes nothing.

## Workbook And Artifact Contract

- Use macro-free `.xlsx` and the code-owned `LLCR_CR_RECORD_LAYOUT_V1` structure via
  a shared infrastructure layout primitive. No external template is introduced.
- Summary and every record sheet must visibly show `DRAFT` or `NEEDS REVIEW`.
- Workbook metadata must include project id, source Matrix id/revision, Measurement
  Plan revision id/sequence/state/fingerprint, preview fingerprint, generated UTC
  time, layout version, and review diagnostics/count.
- Draft files use a separate root:
  `settings.data_dir/generated_contact_measurement_draft_workbooks/<project>/`.
- Filename contract:
  `<project>_contact_measurement_<DRAFT|NEEDS_REVIEW>_m<matrix_revision>_p<plan_sequence>_<fingerprint12>_<artifact_id>.xlsx`.
- A sidecar manifest records the same metadata and exact project/artifact binding.
  Download resolves by project and strict artifact id, never by arbitrary path.
- Write to an app-owned temporary file, atomically publish the `.xlsx`, then publish
  the manifest. Failure removes temporary/partial app-owned files.
- Retain the latest 10 complete artifact/manifest pairs per project. Cleanup runs
  only after successful publication and deletes only files matching this store's
  strict owned naming and manifest contract. Unknown files are never deleted.
- The latest complete draft artifact metadata may be read by the setup workspace.
  It remains visibly draft-only and cannot be shown as a formal output.

## Planned API Boundary

- `POST /api/projects/{project_id}/contact-measurement-plan/revisions/{revision_id}/draft-workbook/preview`
- `POST /api/projects/{project_id}/contact-measurement-plan/revisions/{revision_id}/draft-workbook/generate`
  with `preview_fingerprint`
- `GET /api/projects/{project_id}/contact-measurement-plan/draft-workbook/artifacts/latest`
- `GET /api/projects/{project_id}/contact-measurement-plan/draft-workbook/files/{artifact_id}`

Responses are typed and include source/output class, review label, Matrix and plan
revision metadata, generated time where applicable, row/section counts, diagnostics,
fingerprint, artifact id, filename, and contained download URL. No arbitrary source
path, output path, or client-supplied authority id is accepted.

## Future May Touch After Separate Authorization

Backend application:

- `backend/application/llcr_cr_record_projection_core.py` (new shared pure expansion
  primitive)
- `backend/application/confirmed_matrix_llcr_cr_record_projection.py` only to
  delegate to the shared primitive with unchanged TASK_360B behavior
- `backend/application/draft_measurement_plan_workbook_projection.py`
- `backend/application/draft_measurement_plan_workbook_preview_service.py`
- `backend/application/draft_measurement_plan_workbook_generation_service.py`

Backend infrastructure/API:

- `backend/infrastructure/office/llcr_cr_record_workbook_layout.py` (new shared
  code-owned layout primitive)
- `backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py`
  only for behavior-preserving delegation and confirmed-output regression
- `backend/infrastructure/office/draft_measurement_plan_workbook_gateway.py`
- `backend/infrastructure/files/draft_measurement_plan_workbook_artifact_store.py`
- `backend/api/routes_contact_measurement_plan_draft_workbook.py`
- `backend/api/dependencies.py` only for draft read/generation/store composition
- `backend/api/main.py` only to register the draft router

Frontend:

- `frontend/src/api/client.ts` for typed draft-workbook DTO/helpers only
- `frontend/src/features/contact-measurement-plan/DraftMeasurementPlanWorkbookPanel.tsx`
- `frontend/src/features/contact-measurement-plan/DraftMeasurementPlanWorkbookPanel.test.tsx`
- `frontend/src/features/contact-measurement-plan/useDraftMeasurementPlanWorkbookModel.ts`
- `frontend/src/features/contact-measurement-plan/useDraftMeasurementPlanWorkbookModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.test.tsx`
- `frontend/src/contact-measurement-plan.css` for scoped inline output layout only

Focused tests:

- `tests/unit/test_draft_measurement_plan_workbook_projection.py`
- `tests/unit/test_draft_measurement_plan_workbook_generation_service.py`
- `tests/unit/test_draft_measurement_plan_workbook_artifact_store.py`
- `tests/unit/test_draft_measurement_plan_workbook_gateway.py`
- existing TASK_360B focused unit tests only for unchanged regression
- `tests/integration/test_contact_measurement_plan_draft_workbook_api.py`
- TASK_361D task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No schema, migration, model, repository write, lifecycle, bootstrap, impact
  classifier, identity, command, or confirmation-semantic changes.
- No TASK_360B confirmed route/service/generation/artifact/client/Matrix compatibility
  behavior change. Shared primitive extraction must be behavior preserving.
- No TASK_361E Fee/formal specialized-workbook/other confirmed-consumer migration.
- No generic Test Record, Matrix confirmation or persistence, Matrix parser/import,
  Fee rules/default fill, Basic Information, StepInstance, Report, Folder Actions,
  LTR/public drive, real workbook/folder mutation, VBA/XLSM/COM, release/settings
  cleanup, or unrelated refactor.
- `.agents/**`, `docs/project_management/**`, remote push, destructive git actions,
  and external residuals remain locked.

## UX Acceptance Criteria

1. The dedicated setup workspace contains one compact inline draft-output section,
   not a modal and not a nested card.
2. Preview is available only for a current editable Measurement Plan revision and
   writes no file.
3. The section shows source Matrix revision, plan revision, fingerprint abbreviation,
   row/section counts, and a clear `DRAFT` or `NEEDS REVIEW` label.
4. `ready` and structurally valid `review_required` previews may generate; blocked,
   stale, and empty previews cannot.
5. Generate requires the exact preview fingerprint. Busy state disables preview,
   generate, download, and conflicting plan commands to prevent duplicate work.
6. Errors and review diagnostics remain inline and business-readable. The workspace
   stays open for correction and re-preview.
7. Generated filename, download action, API metadata, workbook summary, and record
   sheets all identify the artifact as draft/review material.
8. The existing TASK_360B Matrix-only confirmed compatibility row remains unchanged
   and visually distinct from the setup-workspace draft output.

## Validation Gate

- Projection unit tests cover `ready`, `review_required`, `blocked`, `empty`, family
  expansion, zero omission, no rounding, prefix collision, readings sum, missing
  lineage, and deterministic ordering/fingerprint.
- Generation tests prove stale fingerprint and changed review state write nothing;
  valid draft/needs-review writes exactly one contained artifact.
- Gateway tests inspect labels and all required metadata on summary and record sheets,
  fixed layout/formulas, no VBA payload, and no empty workbook.
- Artifact tests use temporary directories for containment, strict ids, atomic
  cleanup, sidecar consistency, latest metadata, retention 10, unknown-file safety,
  and project isolation.
- API tests cover typed preview/generate/latest/download, stale `409`, blocked/empty
  responses, no arbitrary path, and no mutation of authority rows or real files.
- Frontend tests cover inline preview, labels, blockers, stale refresh, generate,
  latest/download, busy locking, and no TASK_360B endpoint substitution.
- Regression runs TASK_360B confirmed preview/generate/download and TASK_361B/C
  authority/workspace suites unchanged.
- Focused `py -m pytest`, focused `npm test`, `npm run build`, Python compile,
  diff/trailing/forbidden-scope/no-real-mutation scans, and controlled browser smoke
  pass.

## Merge Gate

Complete. Reviewer plan/readiness gates, user approvals, Developer implementation,
Reviewer implementation re-gate, QA temp-dir/browser smoke, and Integrator package
isolation passed. The accepted package excludes TASK_361E, TASK_360B semantic
changes, authority storage/lifecycle, parser/TASK_360Q-R-S residuals, real files,
VBA/XLSM/COM, LTR/public drive, `.agents/**`, `docs/project_management/**`, and
unrelated changes.

## Definition Of Ready

Satisfied and closed for TASK_361D. The lane is accepted as a draft-workbook output
lane only. Acceptance does not authorize TASK_360B confirmed-behavior changes,
TASK_361E formal consumer migration, Fee, schema/lifecycle/authority semantics,
VBA/XLSM/COM, LTR/public drive, real files, or external residual cleanup.

## Blocking Questions

None for Developer implementation within the authorized scope.
