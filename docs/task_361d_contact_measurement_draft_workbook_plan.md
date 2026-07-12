# TASK_361D Contact Measurement Draft Workbook Plan

## Status

Complete / Integrator accepted on 2026-07-12. Developer implementation,
Reviewer implementation re-gate, QA smoke gate, and controlled Integrator package
isolation passed. Remote push was intentionally not performed.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Active task: TASK_361D accepted/complete.
- Role: Integrator packaging/readiness closeout.
- TASK_361A/B/C are accepted, and TASK_361C established the dedicated setup
  workspace where draft outputs can be mounted without reopening Matrix UI scope.

### Confirmed By User

- Draft and needs-review Measurement Plans may preview and generate LLCR/CR draft
  workbooks before plan or Matrix confirmation.
- Every output must clearly identify draft/review status, Matrix revision, plan
  revision, fingerprint, and generated time.
- TASK_360B confirmed output remains unchanged and formal consumer migration remains
  TASK_361E.
- Use macro-free openpyxl and managed artifacts. No VBA/XLSM/COM, public-drive/LTR,
  or real-file mutation.
- Preview-first, stale protection, blockers, cleanup, download containment, and no
  empty workbook are mandatory.

### Confirmed By Repository Evidence

- TASK_361B persists independent revisions, target/family snapshots, Matrix binding,
  revision fingerprints, and impact/review state.
- TASK_361C exposes current editable revision/fingerprint and readable Group-Step
  context in a dedicated setup workspace.
- TASK_360B supplies deterministic LLCR/CR expansion, code-owned macro-free
  `LLCR_CR_RECORD_LAYOUT_V1`, preview fingerprint generation, contained artifact
  lookup, and typed preview/generate/download patterns.
- TASK_360B is hard-bound to the active Confirmed Matrix and its current output lacks
  draft labels and independent plan metadata. Reusing its endpoint would misstate
  authority.
- The accepted contract reserved `TASK_361D_CONTACT_MEASUREMENT_DRAFT_WORKBOOK`; the
  id and lane are not formally occupied elsewhere.

### Planner Inference And Decisions

- Use a separate draft route, projection, generation service, artifact root, manifest,
  filename, and frontend model. Share only pure expansion/layout primitives with
  TASK_360B and require confirmed-path regression tests.
- No schema is required. The artifact lifecycle is local managed-file state with a
  strict JSON sidecar, not business authority.
- `needs_review` generation is allowed only when review impacts exist but all included
  targets remain structurally valid and non-empty. Structural target errors block the
  whole draft workbook rather than silently creating a partial file.
- Retain 10 owned artifact/manifest pairs per project. This gives bounded local
  history without a new settings or database surface.
- The setup workspace owns an inline output section. The Matrix Editor retains the
  separate TASK_360B confirmed compatibility row.

### Not Yet Confirmed

None that blocks plan review. Retention count, route naming, and helper extraction are
explicit V1 planning decisions for Reviewer scrutiny, not implementation approval.

## Data Flow

```text
current editable Measurement Plan revision
  -> revision/target/family/impact read projection
  -> deterministic LLCR/CR draft projection
  -> no-write preview + preview fingerprint
  -> explicit generate with matching fingerprint
  -> macro-free workbook to app-owned temp path
  -> atomic publish + JSON manifest + bounded cleanup
  -> contained latest/download metadata
```

No step promotes or confirms Measurement Plan or Matrix authority.

## Status And Generation Matrix

| Preview status | Conditions | Label | Generate |
|---|---|---|---|
| `ready` | Current editable revision, non-empty, all included targets valid, no open review impact | `DRAFT` | allowed with matching fingerprint |
| `review_required` | Current editable revision, non-empty, all included targets valid, open review impact exists | `NEEDS REVIEW` | allowed with matching fingerprint |
| `blocked` | stale revision, invalid lineage/binding/count/prefix/readings, or any included structural blocker | none | prohibited |
| `empty` | no included eligible LLCR/CR section or no rows | none | prohibited |

Preview fingerprint is null for `blocked` and `empty`. Generation always recomputes
the projection and returns `409` for a changed source or review state.

## API And DTO Design

The task file lists the exact routes. The preview DTO includes:

- `output_class = measurement_plan_draft`;
- `output_label = DRAFT | NEEDS REVIEW | null`;
- project, plan revision id/sequence/state/fingerprint;
- source Matrix id/revision and Matrix binding fingerprint;
- status, preview fingerprint, section/row counts, sections, diagnostics;
- `generate_allowed` derived by backend.

Generate accepts only `preview_fingerprint`. The response includes the same source
metadata plus artifact id, filename, generated UTC time, and contained download URL.
Latest returns only the most recent complete manifest for that project. Download uses
project id plus strict artifact id. There is no path parameter or authority override.

## Workbook Layout And Labels

- Extract one neutral pure row-expansion primitive and one code-owned workbook layout
  primitive so confirmed and draft adapters cannot diverge on contact rows/formulas.
- Preserve TASK_360B sheet names and measurement columns where practical.
- Draft summary A1 and every record-sheet banner use the output label.
- Summary metadata includes Matrix source, plan source, both fingerprints, generated
  UTC time, layout version, review count, and draft-only disclaimer.
- Record sections retain Group, Step, sample, contact id/label, Initial/After/Final,
  Result, Remarks, and guarded statistics formulas.
- No workbook is created from an empty or structurally blocked projection.

## Artifact Lifecycle

- Dedicated root and strict filename from the task contract.
- Prepare one owned temporary path, write/close workbook, atomically replace final
  `.xlsx`, then atomically publish sidecar manifest.
- On failure, remove only temporary/partial files created by that operation.
- Resolve and download only complete manifest-backed artifacts contained under the
  exact project directory.
- After successful publication retain newest 10 complete pairs. Remove older pairs
  only when both names satisfy the owned contract; leave unknown files untouched.
- Generated draft artifacts are local derived outputs, never authority records.

## UI Boundary

Register: product. Physical context: a lab engineer reviews a dense setup workspace
on a daytime Windows workstation and must distinguish review material from formal
records without opening a modal.

- Add one compact inline draft-output section after target setup/review controls.
- Use status text plus restrained semantic color; never rely on color alone.
- Show only concise metadata and diagnostics. Keep detailed row preview in the
  existing operational table pattern, not nested cards.
- Preview, Generate, and Download are distinct commands. Disable conflicting plan
  commands while generating and restore focus after completion/error.
- The TASK_360B Matrix-only compatibility row remains unchanged and is not copied
  into this workspace as a confirmed action.

## Exact File Boundary

The task file is authoritative for the complete future May Touch list. New code is
confined to draft projection/preview/generation, shared pure expansion/layout
primitives, a separate artifact store/route, typed client, one setup-workspace panel
and model, scoped CSS, and focused tests.

Existing confirmed projection/gateway files may change only to delegate to shared
primitives without output, API, filename, fingerprint, or artifact behavior changes.

## Locked Scope

- TASK_361B schema/repository writes/lifecycle/classifier/commands and plan/Matrix
  confirmation semantics.
- TASK_360B confirmed endpoint, source, fingerprint, artifact path/name, client, and
  Matrix compatibility behavior.
- TASK_361E Fee/formal workbook/other confirmed-consumer migration.
- Generic Test Record, Matrix persistence/parser/import, Fee rules, Basic Information,
  StepInstance, Report, LTR/public drive, real files, VBA/XLSM/COM, release/settings,
  `.agents/**`, `docs/project_management/**`, external residuals, commit/push.

## Validation Gate

1. Pure projection tests cover ordering, expansion, status matrix, review impacts,
   all structural blockers, no partial/empty output, and deterministic fingerprint.
2. Temp-dir gateway/store tests inspect labels/metadata/formulas, atomic cleanup,
   strict containment, latest manifest, retention 10, unknown-file safety, and no
   macro payload.
3. Service/API tests prove current-editable-revision ownership, stale `409`, typed
   responses, no authority mutation, and no arbitrary path.
4. Frontend tests cover inline lifecycle, labels, busy/focus states, visible blockers,
   latest/download, stale recovery, and no confirmed endpoint substitution.
5. TASK_360B confirmed output/API/client and TASK_361B/C lifecycle/workspace regression
   suites pass unchanged.
6. Focused pytest/npm tests, build, Python compile, diff/trailing/forbidden-scope and
   no-real-mutation scans pass; browser smoke uses controlled data only.

## Merge Gate

Complete. Reviewer plan/readiness gates, user approvals, Developer implementation,
Reviewer implementation re-gate, QA smoke gate, and Integrator package isolation
passed. The accepted package isolates all parser/TASK_360Q-R-S and other external
residuals and preserves TASK_360B confirmed behavior while adding TASK_361D
draft-workbook output only.

## Dependencies And Parallelism

1. TASK_361A/B/C: complete/accepted prerequisites.
2. TASK_361D: current planned lane; serial owner of draft workbook outputs and setup
   workspace draft-output controls.
3. TASK_361E: serial after TASK_361C/D acceptance; owns formal consumer migration and
   must not reinterpret draft artifacts as confirmed authority.

## Definition Of Ready

Satisfied and closed for TASK_361D. No blocking findings remain. Source, statuses,
fingerprint, artifacts, UX, tests, validation, and package isolation were accepted
for this draft-workbook lane only.

---

## Developer Planning-First Refinement

### Authorization Checkpoint

This refinement follows the recorded Reviewer plan pass, user-approved Developer
planning-first, docs-only planning-first completion, Reviewer implementation-readiness
pass, and explicit user approval for reconciliation plus Developer implementation.
Planner reconciliation now aligns the board, task, plan, and evidence for the
Developer implementation pass within the exact authorized scope.

### Exact Source and Status Algorithm

1. The preview service accepts `project_id` and `revision_id`, then reads the current
   editable revision from the existing TASK_361B authority read boundary. The supplied
   revision must equal that current editable revision. It never falls back to a
   confirmed plan, the active Confirmed Matrix, or a previous draft artifact.
2. The service reads persisted revision, target, family, Matrix-binding, and open
   impact snapshots only. It does not use unsaved browser state or mutate authority.
3. Eligible material is included LLCR or CR specified-current targets. Excluded,
   ineligible, and zero-count families are omitted under the existing TASK_360B
   deterministic expansion rules. A positive whole-number sample quantity and each
   included family count are required; included-family sums must equal the persisted
   readings-per-sample fact.
4. Any current-revision mismatch, missing binding/lineage, malformed included target,
   non-integral value, prefix collision in the same Group-Step record section, or
   readings mismatch produces `blocked`. It produces neither preview fingerprint nor
   artifact and generation is not attempted.
5. No materialized eligible record section produces `empty`, likewise without a
   fingerprint or artifact. A non-empty structural projection with an open review
   impact is `review_required` and labelled `NEEDS REVIEW`; otherwise it is `ready`
   and labelled `DRAFT`. Both valid non-empty states are generateable.

### Fingerprint and Managed Artifact Contract

- Define one canonical draft projection serializer shared by preview and generation.
  It includes `draft-workbook:v1`, layout version, project id, editable revision id/
  sequence/state/fingerprint, source Matrix id/revision and binding fingerprint,
  normalized sections/families/diagnostics, status, and visible output label.
- Generate recomputes this projection before preparing any output path. A missing or
  unequal preview fingerprint is a typed stale `409`; it must create no directory,
  workbook, manifest, or latest-pointer update.
- The draft artifact manifest is a strict JSON document containing `artifact_id`,
  `project_id`, `output_class`, `output_label`, `layout_version`, `file_name`,
  `generated_at_utc`, plan and Matrix source metadata/fingerprints, preview
  fingerprint, status, section/row/review counts, and a manifest format version.
  It is derived local output metadata, never plan authority.
- Store pairs only below
  `settings.data_dir/generated_contact_measurement_draft_workbooks/<safe-project>/`.
  The filename follows the task contract and the manifest name is derived only from
  that owned filename. A `latest.json` pointer stores only artifact id and manifest
  format/version, and is updated after a complete manifest is published.
- Writer flow: reserve a strict owned id, write macro-free `.xlsx` to an app-owned
  temporary file in the project directory, close/validate it, atomically publish the
  workbook, atomically publish the manifest, then atomically update `latest.json`.
  A failed write removes only temporary or incomplete files named by the active
  reservation. Failure never deletes a previously complete pair.
- Download and latest lookup resolve `project_id` plus a strict hexadecimal artifact
  id through a contained manifest. They reject traversal, missing/mismatched
  manifest/file/project data, and never receive a client path. Post-publication
  cleanup retains the latest ten valid owned pairs. It leaves unknown files and
  malformed pairs untouched; cleanup failure is recorded as a concise warning, not a
  reason to report a successfully published workbook as absent.

### Reuse Boundary and Workbook Layout

- Extract only a pure contact-family expansion primitive from TASK_360B. It accepts
  an already-authorized projection input and returns deterministic record rows plus
  structural diagnostics. It contains no confirmed-Matrix lookup, artifact path,
  API, or write behavior.
- Extract a code-owned macro-free `openpyxl` layout primitive that accepts explicit
  output metadata and record rows. TASK_360B delegates with its current confirmed
  label/metadata unchanged; TASK_361D supplies draft metadata. Neither lane calls
  the other lane's API, artifact store, or route.
- Draft summary and all LLCR/CR record sheets receive a high-visibility textual
  `DRAFT` or `NEEDS REVIEW` banner, source Matrix revision, plan revision, abbreviated
  fingerprint, generated UTC time, layout version, and review count. The workbook
  never says confirmed, formal, or Test Record. Existing fixed sheets, blocks,
  manual-entry cells, and guarded formulas are reused without VBA/XLSM/COM.

### API and Setup Workspace Boundary

- Add the four task-defined draft-only routes on a dedicated router. Preview and
  generate bind only to project plus revision id; generate receives only
  `preview_fingerprint`; latest/download take contained ids only. Responses carry
  typed status, label, source metadata, diagnostics, counts, fingerprint, and
  artifact metadata/download URL where applicable.
- The API maps current-source or fingerprint divergence to a typed stale `409` and
  maps `blocked`/`empty` to business-readable typed preview results rather than a
  partial output. Routes coordinate application services only; no route or frontend
  code opens Office or manipulates artifact paths.
- `useDraftMeasurementPlanWorkbookModel` owns preview, generated-artifact and busy
  state. Its panel is a single inline operational section in the dedicated setup
  workspace, after target/review work and before the existing actions. It displays
  current plan/Matrix revision, status label, fingerprint abbreviation, counts,
  concise diagnostics, Preview, Generate, and Download. It clears stale preview
  state after source changes and requires an explicit new preview before generate.
- A draft-workbook busy state disables draft preview/generate/download and conflicting
  plan command buttons while retaining the workspace route and readable feedback.
  The panel uses no modal, nested card, raw filesystem path, or artificial progress.
  TASK_360B's Matrix-only confirmed compatibility row is neither moved nor reused.

### Exact Future Package and Isolation

May Touch remains restricted to the task's listed draft projection/preview/generation
services, shared pure expansion/layout extraction, draft store/router/dependency/main
wiring, typed client, one setup-workspace panel/model/styles/tests, focused backend/
frontend tests, and TASK_361D governance/evidence. New modules must stay below the
AGENTS Python hard limit and split projection, generation, artifact store, and layout
responsibilities rather than growing confirmed services.

Must Not Touch remains all TASK_361B authority schema/repository/lifecycle/commands,
Matrix confirmation/persistence, TASK_360B confirmed routes/client/artifact behavior,
TASK_361E formal-consumer migration, generic Test Record, Fee, parser/import,
Basic Information, StepInstance/Report, LTR/public-drive, real files, VBA/XLSM/COM,
settings/release cleanup, `.agents/**`, and `docs/project_management/**`. Existing
parser and TASK_360Q/R/S dirty residuals must be excluded at hunk/package level.

### Focused Validation Detail

- Temp-SQLite/service fixtures: current editable revision only, ready versus
  needs-review versus blocked versus empty, no-confirmed fallback, canonical
  fingerprint equality, stale source/review state rejection, and no authority writes.
- Temp-directory artifact tests: strict project/id containment, atomic success and
  rollback cleanup, manifest consistency, latest pointer, missing artifact behavior,
  traversal rejection, ten-pair retention, unknown-file preservation, and cleanup
  warning behavior.
- Workbook tests: summary and record-sheet `DRAFT`/`NEEDS REVIEW` labels, complete
  metadata, fixed sheets/blocks/formulas, positive-integer expansion, zero omission,
  no rounding, prefix collision blocking, and no macro payload.
- API/client/UI tests: typed preview/generate/latest/download, stale `409`, blocked/
  empty no-write states, busy locking, action focus/status recovery, no confirmed
  endpoint substitution, and no TASK_360B visual or contract change.
- Merge checks: TASK_360B preview/generate/download regression, TASK_361B/C authority
  and workspace regressions, focused pytest/npm/build/compile, line count, diff,
  UTF-8 trailing whitespace, dependency, forbidden-scope, no-real-mutation, and
  candidate-package isolation scans. Browser smoke uses only a controlled temporary
  project/artifact root.
