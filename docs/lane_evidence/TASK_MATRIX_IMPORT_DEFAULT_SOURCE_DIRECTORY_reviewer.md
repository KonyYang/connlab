TASK_ID: TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY
ROLE: Reviewer
STATUS: reviewer_blocked
SUBJECT: 60068858e1216e21ff5977b934625bc59d2113a8
COMMIT: 60068858e1216e21ff5977b934625bc59d2113a8
ATTEMPT: 1
ACTION_ID: 647064def7ec5d47ab9513d2ebaf944314510ffda1f4ab921bb0fe3450ca4fc3
PROMPT_SHA256: 0454783f849cacb865e453d99332bea19fb2058d5a3204a4ddcc9577f9c1f268
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:cross_frontend_backend

FINDINGS:
- R1 (blocking): the desktop local-path flow does not preserve the existing locator recalibration contract. `reloadImportPreview` receives parsed page, table, and keyword values, but its `importSourcePath` branch calls `previewProjectTestPlanMatrixFromPath` with only `source_path` and `project_id`. Consequently the operator can enter locator controls and trigger reparse while those values are silently ignored. This conflicts with Plan 3.3, which requires both import paths to share existing preview behavior, and is not covered by a local-path Workspace regression.
- R2 (blocking): the approved `MatrixEditorWorkspace.test.tsx` path is unchanged. The Plan explicitly requires executable Workspace regressions for local-path preview, browser upload fallback, read-only state, and cancel/no mutation. The four hook tests prove only picker choice classification; they do not prove Workspace orchestration or state safety. A bounded fix must add these regressions and correct R1 without expanding approved scope.

VALIDATION:
- commit topology: implementation subject is a direct child of base; Developer evidence is the evidence-only direct child of subject
- exact implementation scope: 14 changed paths, all within the approved 16-path allowlist
- source candidate and desktop picker unit: 17 passed
- source candidate API integration: 3 passed
- Matrix picker hook and Matrix Editor existing suite: 49 passed
- frontend production build: passed (existing chunk-size warning only)
- py_compile: passed
- git diff --check: passed
- full `tests/unit/test_frontend_shell_files.py` on subject: 27 failed, 136 passed
- full `tests/unit/test_frontend_shell_files.py` on primary: the same 27 tests failed, 135 passed; the reported failures are baseline drift, not this subject's regression

SAFETY:
- Review was read-only except for this fixed Reviewer evidence path.
- No product, test, board, primary, branch, worktree lifecycle, or retained-resource mutation was performed.
- No push, cleanup, reset, restore, stash, rebase, merge, or integration action was performed.

HASH_RECONCILIATION:
- The authoritative evidence reference must use the committed Git blob bytes; the earlier reported digest was computed from working-tree bytes after line-ending conversion and is superseded by this evidence-only child.
