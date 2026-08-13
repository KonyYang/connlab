TASK_ID: TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY
ROLE: Developer
STATUS: ready_for_review
SUBJECT: 60068858e1216e21ff5977b934625bc59d2113a8
COMMIT: 60068858e1216e21ff5977b934625bc59d2113a8
ATTEMPT: 1
ACTION_ID: 5e1c54eb73cf18d23bec23a23980d1cdd675fa8315f7a7dcbda0477ce7e07165
PROMPT_SHA256: f2ac73f61fbee26bda69e6f5b7ca1915a5cfdd0bd9b98d908ba0da4f8b3e17dd
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:cross_frontend_backend

VALIDATION:
- source candidate and desktop picker unit: 17 passed
- source candidate API integration: 3 passed
- Matrix picker hook and Matrix Editor regression: 49 passed
- task-specific frontend shell assertion: 1 passed
- frontend production build: passed
- py_compile: passed
- git diff --check: passed
- full test_frontend_shell_files baseline: 27 pre-existing failures reproduced unchanged on primary; 135 passed before the task-specific assertion

SAFETY:
- Changed paths are confined to the approved implementation and test allowlist.
- No database, schema, persistence, Matrix authority, public-drive, or business-rule change.
- No project/source directory or file was created, copied, or mutated by the resolver.
- Browser upload fallback and legacy .doc conversion path remain available.
- No push, cleanup, reset, restore, stash, rebase, merge, or primary write.
