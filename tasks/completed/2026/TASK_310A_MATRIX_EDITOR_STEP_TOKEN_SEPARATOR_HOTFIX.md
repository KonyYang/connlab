# TASK_310A_MATRIX_EDITOR_STEP_TOKEN_SEPARATOR_HOTFIX

Status: Complete. Implemented and validated on 2026-06-10.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed Now

The user reported a current Matrix Editor bug on `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41/matrix-editor`: step-cell input such as `4，5` or `4 5` is treated as one step token instead of two independent steps.

This is a bounded Matrix Editor hotfix. It does not advance Customer Feedback, package publishing, report generation, execution persistence, AI review, permissions, server deployment, or any future StepInstance scope.

## Root Cause

`frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` parses step tokens in `parseStepTokens`.

Current behavior:

- full-width parentheses are normalized;
- Chinese comma `，` is normalized to English comma;
- splitting only happens on English comma, newline, and semicolon;
- spaces are trimmed around parts but not treated as separators.

As a result:

- `4，5` can be normalized late enough to stay vulnerable to inconsistent handling at the split boundary;
- `4 5` is parsed as one part and then treated as an invalid or single whole token rather than two step tokens.

## Goal

Make Matrix Editor step-cell parsing treat common operator separators as independent step-token separators:

- English comma: `4,5`
- Chinese/full-width comma: `4，5`
- semicolon: `4;5`
- newline: `4\n5`
- whitespace between numeric step tokens: `4 5`

The parser must preserve existing extended token support:

- `3(a)`
- `4(1)`
- full-width parentheses such as `4（1）`
- `6#`
- `10*`

## In Scope

- Add focused frontend test coverage for Chinese comma and whitespace-separated step tokens.
- Update `parseStepTokens` separator normalization in `MatrixEditorWorkspace.tsx`.
- Update backend shared `parse_step_tokens` separator handling so confirmed Matrix runtime projection also splits full-width comma tokens after Confirm Matrix.
- Keep existing validation and group sequence rules.
- Update static shell guard if needed.
- Run targeted frontend tests and build.
- Update `docs/task_board.md` only after implementation is approved and completed.

## Out Of Scope

- No API/domain/persistence changes.
- No Matrix save/confirm contract change.
- No Test Record, Fee Evaluation, Customer Feedback, Approval Package, public-drive, or folder behavior changes.
- No StepInstance, execution record, evidence/image, report generation, AI review, permission, multi-user, or LAN/server work.
- No broad Matrix Editor decomposition or UI redesign.

## Acceptance Criteria

- In a selected Matrix group, entering `4，5` yields step preview rows for step `4` and step `5`.
- Entering `4 5` yields step preview rows for step `4` and step `5`.
- After Confirm Matrix, confirmed Matrix runtime projection parses `8，10` as separate Workbench tokens `8` and `10`.
- Existing valid input such as `1,2,3,4（1）` remains valid.
- Existing invalid token checks still reject unsupported characters.
- Existing group continuity/duplicate checks still run after token splitting.
- Confirm Matrix is not blocked for valid Chinese-comma or whitespace-separated step cells when the resulting group sequence is otherwise valid.

## Required Validation

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

## Stop Point

After this hotfix is implemented and validated, stop. Do not proceed to TASK_311 or any other task without a separate task file, executable plan review, and explicit approval.

## Validation

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

Result: `23 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task230 or task310a"
```

Result: `40 passed, 93 deselected`.

```powershell
py -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_confirmed_matrix_runtime_projection_service.py -q
```

Result: `9 passed`.

Read-only live API check:

```powershell
Invoke-RestMethod -Uri 'http://localhost:5173/api/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/runtime-projection/confirmed-matrix-snapshot'
```

Result: current project runtime projection returns separate Group 4 tokens `8` and `10`; no merged raw token `8，10` was observed in the filtered token output.
