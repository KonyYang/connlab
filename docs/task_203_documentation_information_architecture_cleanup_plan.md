# TASK_203 Documentation Information Architecture Cleanup Plan

Last Updated: 2026-05-16
Status: Slice A, Slice B, Slice C, and Slice D approved and executed

## 1. Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
none; TASK_202 complete, pending next controlled task
```

Why this plan is allowed now:

- The user requested repository-wide Markdown cleanup and alignment.
- `AGENTS.md` requires a reviewed plan before broad file edits.
- This is not runtime feature work, so it must not implement backend, frontend, API, DB, runtime, or UI behavior.
- This cleanup is justified as repository maintainability and source-of-truth repair after TASK_194-TASK_202.

## 2. Task Goal

Clean up ConnLab Markdown documentation so future tasks can find current truth quickly without being misled by historical MVP/phase documents.

The task should:

- identify canonical documents
- mark or archive historical documents
- align stale phase/API/domain wording
- reduce root-level Markdown clutter
- keep `tasks/` as the task execution archive
- preserve task history unless a file is clearly duplicate/generated/superseded
- avoid breaking `docs/task_board.md`, governance tests, or existing task references

## 3. Inventory Summary

Project-related Markdown files, excluding `node_modules`, `tmp/codex-runtime-home`, and generated cache directories:

- Root Markdown: 10 files
- `docs/`: 116 files
- `tasks/`: 203 files
- `test_by_third/`: 6 files
- `prompts/`: 2 files
- `checklists/`: 1 file
- `.workbuddy/`: 1 memory file
- `local/`: 1 prompt file

Main observation:

The repository has enough information, but current and historical documents are mixed at the same level. The highest-risk files are not wrong because they exist; they are risky because they look current when they are historical.

## 4. Current Problems

### 4.1 Canonical source-of-truth is implicit

Current truth is spread across:

- `AGENTS.md`
- `docs/task_board.md`
- `PRODUCT.md`
- `README.md`
- `docs/runtime_governance_freeze_rule.md`
- TASK_194-TASK_202 docs and tasks

There is no `docs/README.md` that explains what to read first and what is historical.

### 4.2 MVP documents are stale but still top-level under `docs/`

Examples:

- `docs/01_MVP_SCOPE.md`
- `docs/03_DOMAIN_MODEL.md`
- `docs/04_API_CONTRACTS.md`
- `docs/07_FUTURE_EXTENSION_MAP.md`

These are valuable history, but they no longer fully represent the active system. In particular:

- `docs/04_API_CONTRACTS.md` is still MVP-level and does not cover the current route surface.
- `docs/03_DOMAIN_MODEL.md` is MVP-centered and does not reflect current Matrix/output/runtime projection additions.
- `docs/07_FUTURE_EXTENSION_MAP.md` risks treating already-started Matrix execution direction as future-only.

### 4.3 Plan documents dominate `docs/`

`docs/task_XXX_*_plan.md` files are useful review history, but they crowd out canonical docs. Moving or indexing them must be done carefully because `docs/task_board.md` references many plan paths.

### 4.4 Root Markdown contains mixed roles

Root should only contain immediately useful project entry/control docs. Current root includes:

- active controls: `AGENTS.md`, `README.md`, `PRODUCT.md`, `DESIGN.md`, task skills
- historical/packaged material: `docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md`
- support guides: `ConnLab_Auto_Code_Skill_User_Guide.md`, `AUTO_FIX_SKILL.md`

`docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md` contains an addendum but also older packed content and mojibake. It should not remain a primary-looking root source of truth.

### 4.5 External AI / old modification notes are mixed with current docs

`docs/archive/external_ai/` and some modification logs are useful as history, but should be clearly archived.

### 4.6 Task board is overloaded

`docs/task_board.md` is authoritative but now also contains a very long historical changelog. It should remain authoritative, but its historical mass may eventually move into an archive file after tests are checked.

## 5. Proposed Target Structure

Target structure should be conservative and path-safe:

```text
docs/
  README.md                         # documentation map and read-order
  task_board.md                     # current task source of truth
  runtime_governance_freeze_rule.md # active runtime governance rule

  current/
    product_and_stage.md            # compact current product/stage summary
    architecture.md                 # current architecture summary
    domain_model.md                 # current domain model summary
    api_surface.md                  # current API inventory snapshot

  runtime/
    matrix_execution_phase_principles.md
    project_workbench_runtime_console_information_architecture.md
    step_centric_domain_foundation.md
    interactive_step_token_read_model_projection_foundation.md
    runtime_projection_service_and_read_model_boundary.md
    first_runtime_implementation_slice_planning.md

  frontend/
    frontend_architecture_rules.md
    frontend_smoke_checklist.md
    manual_frontend_smoke.md

  validation/
    phase*_validation*.md
    smoken_result.md

  archive/
    legacy_mvp/
    historical_plans/
    task_plans/
    external_ai/
    session_notes/
```

This target does not require moving `tasks/`. Task files are the task archive and should remain stable.

## 6. Proposed Actions

### 6.1 Safe first-pass actions

These can be implemented with low risk:

1. Create `docs/README.md` as the canonical documentation map.
2. Create `docs/archive/README.md` explaining archive semantics.
3. Add archive/status headers to historical docs that should not be treated as current truth.
4. Update `README.md` so it points to the current read order:
   - `AGENTS.md`
   - `docs/task_board.md`
   - `docs/runtime_governance_freeze_rule.md`
   - `PRODUCT.md`
   - `docs/README.md`
5. Update `docs/04_API_CONTRACTS.md` into a current API surface snapshot or rename its title to make MVP status explicit before a fuller generated inventory is added.
6. Update `docs/03_DOMAIN_MODEL.md` to state that the MVP model is historical and point to Matrix/runtime additions.
7. Keep `tasks/` in place.

### 6.2 Move/archive actions requiring reference updates

These should be done only with path reference checks:

1. Move `docs/archive/external_ai/` to:

   ```text
   docs/archive/external_ai/
   ```

2. Move root historical packed blueprint:

   ```text
   docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md
   -> docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md
   ```

   Add a short root placeholder only if needed; otherwise update references to point to `AGENTS.md` and `docs/task_board.md`.

3. Move old phase-wide plans to:

   ```text
   docs/archive/historical_plans/
   ```

   Candidate files:

   - `ConnLab_Phase5_Workbench_UX_Plan.md`
   - `ConnLab_Phase6_Implementation_Plan.md`
   - `ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md`
   - `ConnLab_Phase7_TASK043_044_Patch_And_TASK045_Execution_Guide_v3_OfficeFacade_COM.md`
   - `phase_2_business_plan.md`

4. Move task plan files only if references are updated:

   ```text
   docs/task_XXX_*_plan.md
   -> docs/archive/task_plans/task_XXX_*_plan.md
   ```

   This is high-volume and should be either automated with validation or deferred.

### 6.3 Delete candidates

Deletion should be conservative. Candidate deletion requires confirmation:

- exact duplicate logs where one copy exists in both active docs and archive
- obsolete draft-only files with no unique content after consolidation
- generated cache/readme files under cache directories, if they are tracked

Do not delete:

- `tasks/TASK_*.md`
- `docs/task_board.md`
- runtime governance/foundation docs
- validation summaries
- docs referenced by active tests

## 7. Canonical Document Alignment

### 7.1 README

Update to make README an entry point, not a full truth source. It should state:

- current baseline
- next runtime direction
- current read order
- where to find docs index
- where API snapshot lives

### 7.2 PRODUCT

`PRODUCT.md` is already mostly aligned. No large rewrite needed.

### 7.3 AGENTS

`AGENTS.md` remains top control. Avoid moving it. Encoding/mojibake display should not be mass-fixed unless a separate encoding task confirms actual file encoding and downstream parser behavior.

### 7.4 API contracts

`docs/04_API_CONTRACTS.md` must stop presenting itself as complete API truth. Recommended update:

- rename title to "API Surface Snapshot"
- include current route groups from `backend/api/routes_*.py`
- keep MVP examples as historical examples only

### 7.5 Domain model

`docs/03_DOMAIN_MODEL.md` should be changed from "MVP Domain Model" to "Domain Model Snapshot" and explicitly include:

- historical MVP objects
- current Matrix foundation objects
- current output ledger objects
- runtime projection read-model objects
- future execution objects not yet implemented

### 7.6 Future extension map

`docs/07_FUTURE_EXTENSION_MAP.md` should be updated so Matrix-driven execution is not shown as generic future scope. It is now the approved next direction, but StepInstance persistence/runtime engines remain future controlled work.

## 8. Proposed Implementation Slices

Because this is broad repository cleanup, do it in slices rather than one large move.

### Slice A: Index and status alignment

Files changed:

- add `docs/README.md`
- add `docs/archive/README.md`
- update `README.md`
- update `docs/03_DOMAIN_MODEL.md`
- update `docs/04_API_CONTRACTS.md`
- update `docs/07_FUTURE_EXTENSION_MAP.md`

No file moves in Slice A except creating archive directory README.

Validation:

- static board tests
- route inventory check for API doc
- grep/select-string check for old current-source claims

### Slice B: Low-risk archive moves

Status: executed after user approval.

Files moved:

- `docs/archive/external_ai/*` to `docs/archive/external_ai/`
- old phase-level plan files to `docs/archive/historical_plans/`
- root `docs/archive/legacy_blueprints/ConnLab_Master_Blueprint.md` to archive only if references are updated

Validation:

- `git diff --name-status`
- path reference search for moved filenames
- static board tests

### Slice C: Task plan archive decision

Status: executed after user approval.

Options:

1. Keep `docs/task_XXX_*_plan.md` in place and index them.
2. Move to `docs/archive/task_plans/` and update `docs/task_board.md` references.

Decision: keep in place for now, because task board references are extensive and historical path stability is useful.

### Slice D: Task board slimming

Status: executed after user approval.  
`docs/task_board.md` remains source of truth and static board-state tests remain active.

Possible later approach:

- keep top current-state section in `docs/task_board.md`
- move older completion notes into `docs/archive/task_board_history_2026-05-16.md`
- update tests accordingly

## 9. Risks

- Moving many docs can break historical task-board links.
- Renaming canonical files can confuse future AI agents if `AGENTS.md` references old names.
- API documentation can drift again unless it is generated or route-inventory based.
- Encoding/mojibake should not be mass-fixed blindly because it may change many files without improving source-of-truth clarity.

## 10. Validation Plan

Run after implementation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Also run path/reference checks:

```powershell
Select-String -Path README.md,AGENTS.md,PRODUCT.md,docs\*.md -Pattern "ConnLab_Master_Blueprint.md","Other_AI_Modified","04_API_CONTRACTS","03_DOMAIN_MODEL"
```

For API doc alignment:

```powershell
Select-String -Path backend\api\*.py -Pattern "@router\.|@app\."
```

## 11. Stop Condition

Slice A and Slice B may be executed after user approval.

TASK_203 slices are complete. Any further documentation restructuring needs a new approved task.
