# TASK_234 Matrix Editor Requirement Split Rules Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_234_MATRIX_EDITOR_REQUIREMENT_SPLIT_RULES`
- Allowed now: user explicitly requested deterministic requirement split behavior.

## Goal

Enhance Step preview Requirement defaults for repeated special-family steps by splitting matrix requirement into staged parts.

## Rule Design (Deterministic)

Input source:

- Matrix row `requirement` raw text
- special-family grouping from TASK_233 (LLCR/IR/DWV/mating aliases)

Parsing strategy:

1. Normalize line breaks to spaces.
2. Attempt split by first `;` into `head` and `tail`.
3. Validate `head` starts with `Initial` (case-insensitive).
4. Validate `tail` starts with `After` / `After test` / `After ...:`.
5. Strip the leading `After...` label from tail and keep the technical content.

Default output:

- single matching step: unchanged matrix requirement
- multiple matching steps:
  - first -> `head` (`Initial ...`)
  - remaining -> stripped tail content
- if parser cannot confidently split -> unchanged matrix requirement

Override precedence:

- `stepOutputOverrides[key].requirement` always wins over generated default.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- add requirement split helper
- apply staged default requirement mapping in family-group loop (alongside description rules)
- keep fallback conservative

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_234 static assertions for:
  - split helper presence
  - initial/after parsing markers
  - override precedence kept

## Risks

- Requirement text formats vary; parser must be conservative to avoid wrong truncation.
- Mixed punctuation (`;`, `:`, unicode symbols) may appear; keep normalization light and fallback-to-original default.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task234 or task233 or matrix_editor"
```

## Out Of Scope

- backend authoritative requirement parser
- full grammar/semantic parser for all requirement styles
- persistence/API save changes
