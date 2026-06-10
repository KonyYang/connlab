# TASK_310A Matrix Editor Step Token Separator Hotfix Plan

Status: Complete. Implemented and validated on 2026-06-10.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_310A_MATRIX_EDITOR_STEP_TOKEN_SEPARATOR_HOTFIX` is complete; `TASK_311` still requires a separate task file, executable plan, and explicit approval before implementation.

## Why This Task Is Allowed Now

The user reported an active Matrix Editor parsing defect: in the step-cell editing area, `4，5` and `4 5` should represent two independent step tokens but are currently handled as one combined value or invalid whole token.

This task is allowed as a bounded hotfix because it only changes frontend Matrix Editor parsing semantics for separators. It does not implement or advance the next planned package-series task (`TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION`).

## Step 1: Task Understanding

Goal:

- Treat Chinese comma and whitespace between step numbers as step separators in Matrix Editor step cells.

Input data:

- Operator-entered step-cell text in Matrix Editor group columns, for example `4，5`, `4 5`, `1,2,3,4（1）`.

Output data:

- Parsed `ParsedStepToken[]` and `numbers[]` used by preview rows, validation guards, and Confirm Matrix enablement.

Modules involved:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- possibly `tests/unit/test_frontend_shell_files.py` for static guard coverage

Not allowed:

- Backend/API/domain/persistence changes.
- Matrix save/confirm contract changes.
- Customer Feedback, package publishing, report generation, StepInstance, evidence/image, AI, permission, multi-user, or server work.
- Broad refactor or redesign.

## Root-Cause Evidence

`parseStepTokens` currently:

- normalizes `（` and `）`;
- normalizes `，` to `,`;
- creates `normalizedForSplit` using newline, Chinese comma, and semicolon replacement;
- splits only on `,`;
- trims parts.

Whitespace is only trimmed around tokens, so `4 5` remains one part. Separator handling is also duplicated across `normalized` and `normalizedForSplit`, which makes the intended delimiter contract less explicit than it should be.

## Hypothesis

If `parseStepTokens` converts operator separators into one canonical comma before splitting, including whitespace that appears between complete step tokens, then `4，5` and `4 5` will produce independent tokens while existing extended tokens still parse.

## Step 2: Design

Data structure design:

- Keep existing `ParsedStepToken` unchanged:
  - `sequence: number`
  - `rawToken: string`
  - `suffixNote: string | null`

Function/signature design:

- Keep existing public local function signature:

```ts
function parseStepTokens(rawValue: string): {
  isValid: boolean;
  numbers: number[];
  tokens: ParsedStepToken[];
  errorMessage: string;
}
```

Implementation approach:

- Normalize full-width parentheses first.
- Normalize separator characters into commas:
  - English comma remains comma.
  - Chinese/full-width comma becomes comma.
  - newline and semicolon become comma.
- Treat whitespace as a separator only when it appears between token-shaped fragments. The conservative target is whitespace between a finished token marker and a following number, so existing suffix syntax such as `4(1)` and `6#` stays intact.
- Preserve the existing part-level regex for token validation:

```ts
/^(\d+)\s*(\((?:\d+|[a-zA-Z])\)|[*#])?$/
```

Expected concrete parsing:

- `4，5` -> `["4", "5"]`
- `4 5` -> `["4", "5"]`
- `4（1） 5` -> `["4(1)", "5"]`
- `6# 10*` -> `["6#", "10*"]`

Dependency relationship:

```text
MatrixEditorWorkspace UI input
  -> parseStepTokens
  -> validation sets + preview row builder
  -> Confirm Matrix disabled/enabled state
Confirmed Matrix authority cell values
  -> backend parse_step_tokens
  -> runtime projection / Workbench token buttons
```

No API or persistence contract changes.

## Step 3: File-Level Changes

Planned changes after approval:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Add failing tests first for `4，5` and `4 5` through the real rendered Matrix Editor flow.
  - Verify Confirm Matrix remains enabled when the resulting sequence is valid.
  - Verify step preview shows two independent step rows.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Update only `parseStepTokens` normalization/splitting logic.
  - Keep the `ParsedStepToken` model and error wiring unchanged.

- `backend/modules/test_plan/matrix_step_sequence_validation.py`
  - Update shared confirmed-output token splitting so `8，10` is not emitted as one Workbench token after confirmation.

- `tests/unit/test_matrix_step_sequence_validation.py`
  - Add backend parser regression coverage for full-width comma.

- `tests/unit/test_confirmed_matrix_runtime_projection_service.py`
  - Add Workbench projection regression coverage for confirmed `cell_value="8，10"`.

- `tests/unit/test_frontend_shell_files.py`
  - Add or update a lightweight guard for the explicit separator normalization contract if useful.

- `docs/task_board.md`
  - Update only after implementation and validation are complete.

## Step 4: TDD Plan

1. RED:
   - Add MatrixEditorWorkspace test case where the draft cell value is `1,2,3，4 5` or an equivalent valid sequence.
   - Confirm the current code fails because whitespace splitting does not produce independent tokens.

2. GREEN:
   - Update `parseStepTokens` separator normalization minimally.

3. REFACTOR:
   - Remove duplication in separator normalization if it improves clarity without changing behavior.

## Step 5: Validation Commands

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task230 or task310a"
```

Optional browser smoke after implementation if the local dev server is available:

- Open `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41/matrix-editor`.
- In the Matrix Editor step cell, enter `4，5` and verify the selected-group step preview shows separate steps.
- Repeat with `4 5`.

## Risks

- Whitespace can be meaningful inside the existing suffix regex, for example `4 (1)`. The implementation must avoid breaking existing tolerated spacing before suffix markers.
- Group continuity validation may still block inputs like only `4，5` if the group lacks steps `1,2,3`; that is correct existing behavior and not part of this hotfix.
- Confirmed Matrix consumers also depend on backend shared parsing; TASK_310A covers the runtime projection split for full-width comma without changing API or persistence contracts.

## Self-Check Before Implementation

- No API/domain/persistence changes planned.
- No future-scope package or Customer Feedback work planned.
- No broad UI redesign planned.
- Parser change is localized and test-first.

## Completion Notes

Implemented behavior:

- `4，5` means two steps: `4` and `5`;
- `4 5` means two steps: `4` and `5`;
- confirmed Matrix `8，10` means two Workbench tokens: `8` and `10`;
- existing extended tokens such as `4（1）`, `6#`, and `10*` remain valid.

Validation:

- `cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false` passed (`23 passed`).
- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task230 or task310a"` passed (`40 passed, 93 deselected`).
- `py -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_confirmed_matrix_runtime_projection_service.py -q` passed (`9 passed`).
- Read-only live API check against `http://localhost:5173/api/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/runtime-projection/confirmed-matrix-snapshot` showed separate Group 4 tokens `8` and `10`, with no merged raw token `8，10` in the filtered output.
