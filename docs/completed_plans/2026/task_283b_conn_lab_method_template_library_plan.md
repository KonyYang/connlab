# TASK_283B Implementation Plan - ConnLab Method Template Library

## 1. Task Identity

- Task: `TASK_283B_CONN_LAB_METHOD_TEMPLATE_LIBRARY`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Draft for review (no implementation yet)
- Execution mode: `superpowers:executing-plans` (serial, small, verifiable slices)

## 2. Why This Task Is Allowed Now

`TASK_283A` is complete and already improved deterministic section extraction. Current board sequence explicitly places `TASK_283B` as the next controlled follow-up for deterministic template fallback before historical library import (`TASK_283C`) and UX layer (`TASK_283D`).

## 3. Objective

Create an internal, deterministic Method Template Library used only as fallback/formatting support when section extraction is partial or missing. Keep extraction precedence clear:

1. Section extraction result (primary)
2. Template fallback (secondary)
3. Empty value + manual operator edit

## 4. Scope Control

### In Scope

1. Internal template data model (family, aliases, default/fallback fields, provenance).
2. Curated migration of approved rows from historical `template_data.py` concept into ConnLab-owned data files.
3. Deterministic alias matching and formatter rules.
4. Fallback integration in parser/extractor path without overriding confident extracted values.
5. Unit tests and minimal integration guard tests for precedence behavior.

### Out Of Scope

1. No template management UI.
2. No historical Test Report ingestion (belongs to `TASK_283C`).
3. No AI/LLM inference, semantic embedding, or fuzzy ranking.
4. No StepInstance/execution persistence/report/fee/evidence scope.
5. No database schema expansion unless explicitly required during review.

## 5. Current Constraints and Compatibility

1. Row-level `method`/`condition`/`requirement` already flows through Matrix/session/draft/authority path.
2. `TASK_283A` family-aware extraction exists and must remain primary.
3. Python file hard limit is 500 lines; any growth risk must be handled by helper-module split.

## 6. Proposed Design

### 6.1 Data Shape (Static, deterministic)

Add a small static template module under `backend/modules/test_plan/`:

- Canonical family key.
- Alias list (normalized tokens).
- Optional fallback method text.
- Optional fallback condition template.
- Optional fallback requirement template.
- Fallback policy flags per field (`method`, `condition`, `requirement`).
- Provenance note (for debug/test assertions only).

No runtime write path. Data is code-reviewed and test-covered.

### 6.2 Matching and Precedence

1. Normalize row test item (uppercase, punctuation collapse, whitespace collapse).
2. Match aliases deterministically against normalized test item.
3. Field-level fallback rule (hard contract):
   - Only fill empty row-level fields.
   - Any non-empty extracted field is immutable in this task and must not be overridden.
   - This task does not introduce `low-confidence` overwrite behavior.
4. Never overwrite user-edited values later in Matrix Editor (this task does not change editor save behavior).

### 6.3 Integration Point

Integrate fallback at row-detail assembly point in parser/extractor pipeline (where row `method/condition/requirement` are finalized), not in API layer and not in frontend.

### 6.4 Naming Coexistence Rule

- Keep existing step-level summary fields unchanged.
- Apply template fallback only to row-level `method`/`condition`/`requirement`.

### 6.5 TASK_283B Allowlist (Approved In This Round)

Only families listed below may receive template fallback in TASK_283B:

Visual fallback method is `EIA-364-18B` for TASK_283B because `B` is the current ConnLab lab-default revision for Visual Examination.

Revision suffixes are allowed in curated template defaults only when they represent an approved current lab convention. A future standard-version confirmation task may override this fallback value using a higher-priority source such as the shared-drive Excel standard list or a formal standard library.

| Family | Representative aliases (normalized) | Fallback `method` | Fallback `condition` | Fallback `requirement` | Field policy | Provenance note | Minimum test expectation |
|---|---|---|---|---|---|---|---|
| Visual | `visual examination`, `visual inspection`, `examination`, `inspection` | `EIA-364-18B` | `10x min magnification` | `No detrimental condition` | fill-empty-only | migrated from approved template concept + lab convention | alias hit fills empty M/C/R; non-empty extracted stays unchanged |
| LLCR | `llcr`, `low level contact resistance`, `low-level contact resistance` | `EIA-364-23` | none | none | fill-empty-only | approved family fallback | fills only missing method |
| MFG | `mfg`, `mixed flowing gas`, `mixed-flowing gas` | `EIA-364-65` | none | none | fill-empty-only | approved family fallback | fills only missing method |
| Durability | `durability`, `mechanical operation`, `mating durability`, `unmating durability` | `EIA-364-09` | none | none | fill-empty-only | approved family fallback | fills only missing method |
| Vibration | `vibration`, `random vibration`, `sinusoidal vibration` | `EIA-364-28` | none | none | fill-empty-only | approved family fallback | fills only missing method |
| Shock | `mechanical shock`, `shock` | `EIA-364-27` | none | none | fill-empty-only | approved family fallback | fills only missing method |

Out-of-allowlist families must not receive template fallback in TASK_283B.

## 7. File-Level Change Plan

Pre-step gate (must pass before functional edits):
1. Ensure `backend/modules/test_plan/product_spec_matrix_parser.py` is below AGENTS hard limit (`<500` lines). If not, first move helper logic to support modules.

Implementation steps:

1. Add: `backend/modules/test_plan/method_template_library.py`
2. Add: `backend/modules/test_plan/method_template_matcher.py`
3. Update: parser/extractor integration module(s) in `backend/modules/test_plan/`
4. Add/Update tests:
   - `tests/unit/test_method_template_library.py`
   - `tests/unit/test_product_spec_matrix_parser.py` (precedence + fallback cases)
   - small integration guard if needed in preview/session flow tests

Note: exact filenames can be adjusted during implementation review if line-limit or ownership needs differ.

## 8. Test Plan (Required)

1. Alias match deterministic cases:
   - Visual/Inspection variants
   - LLCR, MFG, Durability, Vibration/Shock representative aliases
2. Non-override guard:
   - Extracted non-empty value must not be replaced by template
3. Field-level fallback:
   - Missing method only -> fill method, keep other extracted fields
   - Missing condition/requirement -> fill per policy
   - Non-empty extracted field -> must not be overridden by template
4. Parser-level end-to-end row assertions through `parse_tables(...)`
5. Session/preview regression spot-check to ensure row MCR payload remains intact
6. Import-commit regression: ensure fallback values survive into sparse cells/draft payload (`tests/unit/test_matrix_import_commit_service.py`)
7. Smoke-chain regression: ensure downstream test-record smoke path is not broken (`tests/integration/test_matrix_to_test_record_smoke_flow_api.py`)

## 9. Risks and Mitigations

1. Risk: template overreach and accidental overwrite.
   - Mitigation: strict precedence tests and explicit field-level guard.
2. Risk: alias noise causing wrong family match.
   - Mitigation: normalized exact/controlled matching first; avoid broad fuzzy logic.
3. Risk: parser module line growth.
   - Mitigation: keep matching/fallback in dedicated helper modules.

## 10. Validation Commands (Implementation Phase)

1. `py -m pytest tests/unit/test_method_template_library.py tests/unit/test_product_spec_matrix_parser.py -q`
2. `py -m pytest tests/unit/test_matrix_editor_session_service.py tests/unit/test_source_matrix_persistence_service.py -q`
3. `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/integration/test_matrix_editor_session_api.py -q`
4. `py -m pytest tests/unit/test_matrix_import_commit_service.py -q`
5. `py -m pytest tests/integration/test_matrix_to_test_record_smoke_flow_api.py -q`
6. `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"`
7. `git diff --check`

## 11. Completion Criteria

Task can be marked complete only when:

1. Deterministic template fallback works for approved families.
2. Extracted values remain authoritative when present.
3. Matrix/session payloads keep row-level MCR intact.
4. All required tests pass.
5. `docs/task_board.md` and `docs/task_plan_index.md` are updated in the same completion turn.
