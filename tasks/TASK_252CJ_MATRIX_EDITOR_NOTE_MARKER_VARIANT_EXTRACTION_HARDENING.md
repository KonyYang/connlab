# TASK_252CJ_MATRIX_EDITOR_NOTE_MARKER_VARIANT_EXTRACTION_HARDENING

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CJ_MATRIX_EDITOR_NOTE_MARKER_VARIANT_EXTRACTION_HARDENING`

## Why This Task Is Allowed Now

- `docs/task_board.md` currently shows no active task and requires explicit user approval before opening the next controlled Matrix Editor task.
- User explicitly approved opening a controlled task to harden note extraction and step mapping for marker variants.
- Scope is bounded to parser/API preview note extraction behavior already established by `TASK_252CH`, without adding new runtime domain objects.

## Model Fit Assessment

`GPT-5.3-codex` with `high` reasoning is suitable.

Reason:

- Needs deterministic parser enhancement with strict backward compatibility for existing marker-note linkage.
- Requires careful edge-case handling for marker prefixes while avoiding false positives in normal business text.

## Objective

Harden Matrix note extraction so marker-prefixed notes with real-world formatting variants are captured and mapped to Step preview notes correctly, including notes whose body content is document-number/path-like text (for example: `C:\...\Rev7.doc`).

## Scope

Allowed:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- Related unit/integration tests for parser and matrix preview API mapping
- Task/plan/board documentation updates required by governance

Forbidden:

- New import file formats or OCR/AI parsing
- Matrix domain/persistence redesign
- Frontend layout redesign beyond existing note card behavior
- Runtime execution model expansion

## Acceptance Criteria

1. Existing supported marker note formats remain valid:
   - `(a) text`
   - `* text`
   - `# text`
2. New marker prefix variants are parsed deterministically:
   - `a) text`
   - `A) text`
   - `（a）text`
   - `a. text`
   - `Note (a): text`
3. Note body can include file/document strings (including Windows path-like tokens) and is preserved as note text payload.
4. Step token marker linkage remains exact:
   - `3(a)` / `10(a)` map to marker `a`
   - `6#` / `5*` map to `#` / `*`
5. `Step Notes` / `Item/Section Notes` / `Samples Notes` card origins remain separated as established by `TASK_252CH`.
6. No regression on existing `.docx` samples validated in `TASK_252CH`.

## Validation

Backend targeted:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

Frontend safety check (no intended UI changes, ensure shell stays stable):

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor and notes"
```
