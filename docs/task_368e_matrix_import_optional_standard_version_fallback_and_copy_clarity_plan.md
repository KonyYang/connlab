# TASK_368E Matrix Import Optional Standard Version Fallback And Copy Clarity Plan

Status: `qa_dispatch_ready`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: TASK_368E. It retains the durable execution token under schema state
`gate_running`; the exact branch/worktree are clean at Reviewer-pass evidence HEAD
`77fe429eea59d2908c2f57d9243e8fd893488ad5`, and mandatory QA dispatch is ready.

## Approval And Activation Record

- User approval date: 2026-08-01.
- Approved planning checkpoint:
  `5dff98af9d0f93770962a9a672d7610d0cef4936`.
- Approval covers the exact task/plan and automatic role progression through local Integrator
  acceptance after controlled activation.
- The approved route remains `Developer -> Reviewer -> QA -> Integrator`; every gate is
  mandatory because this is QF-4.
- WIP remains `1`; TASK_368E is the sole token owner, while the queue is empty and paused task,
  Quick Fix, and parallel exception are null. The exact TASK_368E branch/worktree is registered
  clean at the recorded base/HEAD.
- Orchestrator created and verified the exact isolated branch/worktree, and the authorized Developer
  implementation handoff is complete. No push, restart, release build, real-data/file mutation,
  destructive cleanup, or changes to retained/cancelled/frozen lanes are authorized.

## 1. Discovery Gate

### Confirmed by User

- The Settings label must express the business meaning “standard version file path”.
- Matrix Import Replace must not remain blocked merely because the Standard version file is
  absent, unconfigured, inactive, or unavailable.
- The operator may choose/set a Standard version file path or choose `Skip for now`.
- Skip must immediately complete Replace, preserve imported Method content, and create an
  editable Matrix draft; configuration is never mandatory.
- The reminder must be clear and non-red and direct the operator to existing
  `Standard Method versions` for later updates.
- A safely readable configured resource keeps existing automatic synchronization.
- Existing Preview/Apply is retained and Confirm Matrix remains the sole publication boundary.
- No automatic path configuration, development-DB copy, Standard-workbook write, or public-drive
  authority change is allowed.

The direct User update requesting the choose-or-skip window is later than an earlier
“warning-only/no-window” interpretation. Permanent Orchestrator explicitly re-read that update,
rescinded its interim no-window correction, and confirmed choose-or-skip as the controlling UX.

### Confirmed by Repository Evidence

- Primary was clean on `master@7b2be466b283d53f88b93d365ed21f15269fa5a5`; the read-only execution gate returned
  `ALLOW_INSPECT`, state `complete`, token owner `null`, empty queue, and no active/paused/Quick
  Fix/parallel task.
- TASK_366B owns Settings Standard worksheet configuration and the saved-draft
  `Standard Method versions` Preview/Apply flow.
- TASK_366C deliberately made every source-level Standard authority failure a `422` zero-write
  blocker and added strict import-context reuse.
- `MatrixImportMethodAuthorityResolver._load_resource()` rejects absent/inactive resources;
  `resolve()` wraps catalog failures; the commit service and route map them to `422` before writes.
- Current summary/client DTO metadata is non-null and status is limited to
  `synchronized | review_required`.
- Matrix Editor applies a returned draft and closes the import dialog on `201`, but currently has
  only green success and generic red error presentation.
- Settings currently labels the row `Standard record Excel`; its input derives
  `${row.label} path`, so a label-only edit would create `path path` accessibility copy.
- Existing resource list/save/validate clients and the Windows desktop path-picker bridge can be
  reused. No new settings endpoint or picker implementation is required.
- XLSX/XLS reader errors and cause chains permit a positive availability allowlist without
  changing Office gateway code.

### Planner Inference

- This is QF-4, not a copy-only Quick Fix: it changes an accepted authority, transaction, API,
  and frontend flow across layers.
- Backend must remain the classifier. Initial Replace uses the safe default
  `prompt_if_unavailable`; only a typed availability result opens the choice dialog, before writes.
- `Skip for now` supplies a narrowly typed retry policy. Backend rechecks current facts; it may
  preserve source only if the failure is still on the availability allowlist.
- Choosing a file is explicit user configuration: invoke the existing desktop picker, save and
  validate through existing APIs, then retry normal Replace. Cancel does nothing and keeps the
  choice visible.
- Integrity, format, worksheet, header, catalog, cleanup, and unknown failures never expose or
  honor Skip; they remain fail-closed.
- Fallback needs its own versioned audit context while configured-success v1 remains compatible.

### Not Yet Confirmed

- Exact implementation test totals.
- Whether a safe disposable live browser fixture is available to QA.
- Developer/Reviewer/QA/Integrator evidence, because implementation has not started.

These unknowns do not change scope, behavior, ownership, acceptance, or gate order. Definition of
Ready was satisfied for User review; approval and sole token remain recorded, Reviewer re-gate
passed, and mandatory QA is next.

### Continue Or Stop

Continue with mandatory QA against exact reviewed ancestry. Stop and return to Developer/Planner
on any B1 recurrence, positive-path regression, scope drift, transaction/reuse/accessibility/build
failure, real-resource access, or non-baseline unexplained failure.

## 2. User Flow And Exact Copy

### Settings

- Visible row label: `Standard version file path`.
- Standard path input accessible name/title: `Standard version file path` exactly; never
  `Standard version file path path`.
- `Standard record sheet`, Browse, validation, blur/Enter save, and all other resource rows remain
  unchanged.

### Replace: configured and safe

The current single-call Replace path remains: synchronize safe versions, apply returned editable
draft, close the import dialog, and render the existing green count summary.

### Replace: availability choice

1. Initial Replace preflight detects a positively classified availability state before any source,
   snapshot, draft, or context write.
2. API returns one typed action-required detail. Matrix Editor does not show a red error; it opens
   an accessible decision dialog titled `Standard version file unavailable`.
3. Dialog body:
   `Choose a Standard version file, or skip for now and keep the original Method values.`
4. Primary action: `Choose file` (desktop picker available) or `Set file path` (same semantic
   action if the final component convention uses a path field). The implementation must lock one
   visible label; this plan chooses `Choose file`.
5. Secondary safe action: `Skip for now`.
6. `Choose file` opens only the existing native Standard resource picker. Cancel performs no write
   and returns focus to the dialog. A selected path is explicitly saved active and validated via
   existing resource APIs, preserving the existing configured worksheet; validation success
   retries normal Replace. Validation failure stays in the dialog with actionable inline text.
7. `Skip for now` immediately retries with the explicit preserve-source policy. If availability is
   still eligible, Replace returns `201`, applies the draft, closes both dialogs, and shows the
   non-red warning. It never navigates to Settings or forces configuration.

Exact post-skip warning:

`Standard version file unavailable. Original Method values were kept. You can update them later in Standard Method versions.`

The choice dialog uses `role="dialog"`, `aria-modal="true"`, labelled title/description, focus
entry/return, Escape equivalent to closing the decision without committing, and reachable keyboard
actions. The post-skip warning uses amber/non-danger styling, `role="status"`, and
`aria-live="polite"`; it is not an alert.

## 3. Availability And Integrity Boundary

Classification must use exception types and bounded cause-chain evidence, never broad message
matching or `except Exception => fallback`.

| State | Private reason code | Initial result | Skip result |
| --- | --- | --- | --- |
| no resource record | `standard_version_not_configured` | typed action required, zero-write | fallback success |
| resource inactive | `standard_version_inactive` | typed action required, zero-write | fallback success |
| path absent/not a file | `standard_version_file_missing` | typed action required, zero-write | fallback success |
| explicit not-found/access-denied/share/network/sharing availability cause | `standard_version_file_unavailable` | typed action required, zero-write | fallback success |
| Excel COM runtime unavailable for `.xls` | `standard_version_runtime_unavailable` | typed action required, zero-write | fallback success |

Only explicit `FileNotFoundError`, `PermissionError`, `LegacyExcelComUnavailableError`, and a
documented Windows availability-code allowlist reached through `__cause__`/`__context__` may enter
the filesystem/runtime rows. Unknown errors fail closed.

These states remain `422` zero-write and must not expose or accept Skip:

- unsupported extension/workbook type;
- corrupt XLSX ZIP/XML/missing internal parts;
- legacy open/read failure without an explicit availability cause;
- missing, ambiguous, or wrong configured worksheet;
- invalid/missing header/layout or no nonblank Standard-code rows;
- returned catalog path or matched worksheet mismatch;
- oversized/invalid COM range, invalid value shape, or cleanup failure;
- malformed/unverifiable persisted authority context or any unknown exception.

Individually malformed/non-EIA catalog cells keep accepted TASK_366B/C row-level outcomes when the
workbook is structurally valid. They neither authorize fallback nor create a new source blocker.

## 4. Request, Action-Required Detail, And Response

Add one backward-compatible request field:

```text
standard_version_unavailable_action:
  prompt_if_unavailable | preserve_imported_methods
default = prompt_if_unavailable
```

The frontend sends the default on initial/choose-retry and
`preserve_imported_methods` only after `Skip for now`. The server never trusts the field alone; it
re-resolves resource/read facts on every request. The preserve value cannot suppress a configured
integrity failure. Existing callers omitting the field receive the safe prompt behavior.

Typed action-required HTTP detail (recommended `409`, matching the existing no-write conflict
family) is:

```text
code = matrix_import_standard_version_action_required
reason_code = one private availability code
message = Standard version file unavailable.
```

It contains no path or OS exception text. It is distinct from generic `422` errors and is consumed
through a typed client predicate, not text matching.

Successful response evolution:

```text
method_authority_sync.status:
  synchronized | review_required | source_preserved
standard_resource_id: string | null
effective_worksheet_name: string | null
catalog_fingerprint: string | null
context_fingerprint: string (required)
warning: null | {
  code: standard_version_unavailable
  message: <exact locked post-skip warning>
}
rows[]: existing shape; fallback rows use source_preserved/no-apply values
```

Configured success returns `warning=null` and non-null authority metadata as before. Public warning
code is stable/coarse; private context keeps the specific reason.

## 5. Source Preservation And Audit Context

Fallback does not run catalog proposals or claim synchronization. Every ordered imported row has:

- exact imported `current_method` and `resulting_method`, including blank/unicode/punctuation;
- `status="source_preserved"`;
- `matched_standard_code=null`, `source_row_number=null`, `applied=false`.

Selected Groups, group/cell values, source import/snapshot IDs, stable row identity, source locator,
payload, selected-group, root/row, result, and editable-draft lineage remain unchanged.

Persist a private canonical `matrix-import-method-fallback:v1` context in the existing
`method_sync_context_json`:

```text
schema, mode=replace_import
project_id, source_import_id, source_snapshot_id, project_matrix_draft_id
task261_commit_fingerprint, source_locator_fingerprint, payload_fingerprint
selected_group_fingerprint, source_root_fingerprint, source_row_fingerprint
authority_status=source_preserved, fallback_reason_code
standard_resource_id?, standard_resource_path?, effective_worksheet_name?
catalog_fingerprint=null
pre_method_fingerprint, proposal_fingerprint, post_method_fingerprint
result_fingerprint, context_identity_fingerprint, applied_at, row_results[]
```

Known resource metadata is recorded; unknown authority facts are JSON `null`, never fabricated.
Pre/post Method fingerprints must match. Proposal fingerprint covers ordered preservation decisions.
Configured success continues to write/read `matrix-import-method-sync:v1`; no migration or rewrite
of accepted contexts is allowed.

## 6. Reuse And Transaction Semantics

- Initial action-required response is before every persistence call and is zero-write.
- Choose/save/validate changes only the explicitly selected external-resource registry record via
  existing services; it never opens the Standard workbook for write.
- Skip retry enters the same nested source/draft transaction and read-verification sequence as
  configured success.
- Any persistence/readback failure rolls back the full import aggregate.
- Exact replay under identical fallback facts may return `reused` only after full lineage,
  context, child-count, Method, and result-fingerprint verification.
- Changed resource/availability reason, newly readable authority, edited draft, changed import
  facts, malformed context, or partial aggregate remains `409` zero-write. If authority becomes
  available later, use existing `Standard Method versions`; Replace does not silently rewrite an
  earlier import.
- Confirmed Matrix tables are never written by Replace.

## 7. File-Level Implementation Plan

1. Add RED unit tests in
   `tests/unit/test_task_368e_matrix_import_optional_standard_fallback.py` for the action-required
   allowlist, preserve retry, exact Methods, context/fingerprints, and integrity exclusions.
2. Update `matrix_import_method_authority.py` with a narrow availability classifier, typed
   action-required result/error, fallback builder, nullable/warning summary, and dual-context
   verification. Keep configured-success logic intact.
3. Add RED integration tests in
   `tests/integration/test_task_368e_matrix_import_optional_standard_fallback_api.py` for request
   default, typed action detail, skip success, transaction, reuse, 409/422 boundaries, and counts.
4. Make only narrow command/commit/route changes for the action enum, error mapping, and response.
5. Update `client.ts` types plus a typed action-required detail predicate. Reuse existing resource
   list/save/validate functions; add no endpoint.
6. Create `MatrixImportStandardVersionChoiceDialog.tsx` as a declarative accessible component and
   a bounded test. It owns no API calls.
7. Create `useMatrixImportStandardVersionChoice.ts` for picker/save/validate/retry state and a
   bounded test. It reuses `pathPickerBridge.ts` read-only and reports cancel/validation safely.
8. Compose the hook/dialog in `MatrixEditorWorkspace.tsx`; add a bounded integration-style
   component test proving action-required -> choose/skip flows, modal close, returned draft, and
   warning. Add warning/dialog CSS only.
9. Update Settings config/panel and bounded test for exact visible/accessibility copy; update only
   the old static assertion in `test_frontend_shell_files.py`.
10. Run focused plus read-only compatibility suites before every gate.

## 8. Exact May Touch

### Backend product

- `backend/application/matrix_import_method_authority.py`
- `backend/application/matrix_import_commit_service.py`
- `backend/api/routes_matrix_import_commit.py`

### Frontend product

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- new `frontend/src/features/matrix-editor/MatrixImportStandardVersionChoiceDialog.tsx`
- new `frontend/src/features/matrix-editor/useMatrixImportStandardVersionChoice.ts`
- `frontend/src/features/settings/settingsResourceConfig.ts`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- `frontend/src/workbench.css`

### Bounded tests

- new `tests/unit/test_task_368e_matrix_import_optional_standard_fallback.py`
- new `tests/integration/test_task_368e_matrix_import_optional_standard_fallback_api.py`
- new `frontend/src/features/matrix-editor/MatrixImportStandardVersionChoiceDialog.test.tsx`
- new `frontend/src/features/matrix-editor/useMatrixImportStandardVersionChoice.test.tsx`
- new `frontend/src/features/matrix-editor/MatrixImportOptionalStandardFallback.test.tsx`
- `frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx`
- `tests/unit/test_frontend_shell_files.py`

### Governance/evidence

- TASK_368E task/plan/role evidence and bounded board gate updates.

## 9. Must Not Touch And Locked Dependencies

Every unlisted path is locked, especially:

- `MatrixMethodVersionSyncPanel.tsx`, its existing hook, parser/catalog/layout, Office gateways and
  facade;
- external-resource backend service/routes, Settings page, desktop picker bridge implementation,
  dependencies/main;
- persistence repositories/models/schema/migrations;
- Matrix session/Confirm Matrix, confirmed authority, Test Record, Fee, Report, outputs;
- AGENTS, protocols/skills/scripts, execution schema, bundle/registry;
- real DB/files/public drive, release/package/dependencies/lockfiles;
- existing lanes/worktrees and push/restart/destructive actions.

If classification cannot be implemented without an Office gateway or external-resource backend
change, stop for Planner/User scope reconciliation.

## 10. Validation Matrix

Minimum deterministic coverage:

1. valid configured XLSX retains current synchronization/non-null metadata;
2. valid configured XLS with fake COM retains current behavior;
3. absent resource initial request returns typed action-required and zero writes;
4. inactive resource does the same;
5. absent file does the same;
6. explicit filesystem availability cause does the same;
7. COM-runtime-unavailable does the same;
8. skip retry for each allowed state returns `201 source_preserved`;
9. fallback preserves blank/nonblank/unicode Methods, selected Groups/cells, and lineage exactly;
10. fallback context has nullable metadata, equal Method fingerprints, stable identity, ordered
    rows, and no false synchronization;
11. same-fallback replay is read-verified and does not increase aggregate counts;
12. changed/newly-readable resource, edited draft, and changed context remain `409` zero-write;
13. injected post-source/post-draft failures roll back all import writes;
14. corrupt XLSX is `422` zero-write and cannot skip;
15. unsupported format is `422` zero-write and cannot skip;
16. wrong/missing/ambiguous sheet is `422` zero-write and cannot skip;
17. invalid header/empty catalog/path mismatch/range/cleanup/unknown error is `422` zero-write;
18. action detail/request/response nullability matches Python and TypeScript;
19. frontend typed action opens accessible non-red choice dialog, not generic error;
20. `Choose file` cancel writes nothing and keeps the decision recoverable;
21. explicit choose saves/validates existing Standard resource only, preserves worksheet, then
    retries normal Replace;
22. validation failure stays actionable and does not commit Matrix import;
23. `Skip for now` immediately completes Replace, closes dialogs, applies draft, and shows exact
    amber polite warning;
24. configured frontend success remains green with existing counts;
25. Settings label/input name are exact with no duplicate `path`; sheet label remains unchanged;
26. existing Standard Method versions Preview/Apply tests pass unchanged;
27. Matrix session, Confirm Matrix, source persistence, TASK_366B parser/sync, TASK_366C API/reuse,
    and group-selection regressions pass read-only;
28. pycompile, pytest, Vitest, frontend build, line-count/diff/allowlist/no-real-data/no-workbook-
    write checks pass.

QA uses disposable SQLite/XLSX/fake-COM resources. No deterministic test opens operator files.

## 11. Reviewer, QA, And Integrator Gates

### Reviewer

- Review clean base..HEAD only.
- Prove the positive availability allowlist and negative integrity cases.
- Review action-required/skip authorization, dual context schemas, reuse, transaction, nullability.
- Inspect accessible dialog/focus, exact copy, non-danger warning, and absence of forced config.
- Confirm existing Preview/Apply and Confirm Matrix remain unchanged.

### QA (mandatory)

- Run all 28 validation categories with disposable resources.
- Cover XLSX and fake-COM XLS availability/integrity.
- Run frontend/build and safe desktop/514 px smoke when a disposable fixture exists.
- Verify choice and skip are keyboard reachable, warning is not red, and screen-reader semantics
  are correct.
- Prove real DB/Excel/PDF/public-drive files were neither read nor changed.

### Integrator

- Require clean Developer checkpoint, Reviewer pass, QA pass, exact ancestry/path allowlist.
- Merge locally only after fresh gate and rerun merged-tree validations.
- Record residuals and clean states; do not push/publish/restart/release-build/retire worktrees.

## 12. Compatibility, Rollback, And Risks

Request evolution is optional/defaulted; configured-success response remains semantically intact.
Fallback adds nullable metadata only with `source_preserved`. Existing v1 contexts remain readable.

Rollback removes choice/fallback handling and restores old authority blocking. Already created
fallback drafts remain truthful editable drafts with source Methods and versioned audit context;
rollback must not delete/rewrite them, settings, confirmed Matrices, or workbooks.

Key risks are broad exception fallback, bypassing integrity through skip, reuse drift, partial
resource-save/import state, nullable DTO mismatch, inaccessible dialog focus, red warning styling,
and accidental Settings/Preview/Apply refactor. Positive classification, server recheck, separate
context, bounded components/tests, and mandatory gates mitigate them.

## 13. Implementation Order And Stop Conditions

1. Completed: User approved the exact task/plan at the recorded planning checkpoint.
2. Completed: production-root `Inspect` returned `ALLOW_INSPECT`, `StartTask` returned
   `ALLOW_START`, and the first CreateWorktree check correctly returned `BLOCKED_TOKEN_OWNED`
   while token-null; no topology changed.
3. Completed: Orchestrator's timed Create command produced the exact registered branch/worktree at
   `e226bf1e54db4de54eb2366e96895999ce54652d`; worktree/index are clean. Do not rerun Create.
4. Completed: Developer implementation checkpoint is `9cd39e2dc5e8b50f23fd3e3202913a96019d4999`;
   clean final evidence HEAD is `bb9734830b41c3a86c1cd5542d34a0832cd990d4`, with the exact
   17 locked product/test paths plus Developer evidence.
5. Completed with blocker: Reviewer independently confirmed the two baseline debts but found B1 at
   evidence HEAD `68a337678dfaa35fbfac987c36027c605d3e0668`: cleanup integrity can be downgraded
   to availability through a nested allowlisted cause.
6. Completed: Developer fix checkpoint `1882c1b04937f0c576ddd2350407edc91b990217`
   and final evidence HEAD `f924c33deb92be269150085c9e8982f152d3b809` change exactly the
   authority classifier, bounded unit/API tests, and Developer evidence.
7. Completed: Reviewer independently re-gated B1, positive/integrity behavior, frozen regressions,
   exact scope, and the 499-line authority constraint; Reviewer pass evidence HEAD is
   `77fe429eea59d2908c2f57d9243e8fd893488ad5`.
8. Current: mandatory QA executes the full 28-category validation matrix and passes or returns
   failures to Developer/Planner.
9. Integrator accepts locally only reviewed/QA ancestry and records residuals.
10. Stop after local acceptance; no push or next-task activation.

## 14. Planned Lane

- Lane: `task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Branch: `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
- Planning base: `7b2be466b283d53f88b93d365ed21f15269fa5a5`
- Worktree creation base/initial HEAD: `e226bf1e54db4de54eb2366e96895999ce54652d`
- WIP: `1`; parallel exception: none.

The exact TASK_368E branch/worktree is clean at Reviewer-pass evidence HEAD
`77fe429eea59d2908c2f57d9243e8fd893488ad5`. TASK_368E remains the sole token owner with role QA
and no parallel exception; base remains `e226bf1e54db4de54eb2366e96895999ce54652d`.

## 15. Definition Of Ready

Definition of Ready, existing User approval, and Reviewer pass cover mandatory QA execution.
Goal, copy, choose/skip behavior, availability/integrity boundary, audit/reuse/API/transaction
design, exact paths, tests, rollback, lane identity, and mandatory gates remain unchanged. QA must
use disposable resources and verify the full frozen acceptance before Integrator.

## 16. Next Legal Role

Mandatory QA, dispatched by Orchestrator against exact reviewed ancestry. Planner does not edit the
lane or implementation paths from this pass.
