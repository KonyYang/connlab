# TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP QA Evidence

TASK_ID: TASK_LTR_WORKBOOK_PUBLIC_DEFAULT_ADMIN_CONFIG_BOOTSTRAP
ROLE: QA
STATUS: pass
SUBJECT: 503a471a47cd69180822a6e3963c133a4fb68e81
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ACTION_ID: 4d899f39640b40097f698e165757fdaa787a793f03419f27a4dd6eff9d537060
ATTEMPT: 1
NEXT: Integrator
BLOCKER: none

## Authority And Identity

- Board remained at raw SHA-256 `5d5604521518b8a9e4deadd945f5d0ba729854475d9f5e9fed39504aa3f5a65b`, `running/qa`, QA attempt 1 and callback pending.
- Durable action, attempt, host and exact subject reconcile with the board and dispatch capsule.
- Actual route reconciles with the committed structured route and dispatch capsule: `gpt-5.6-sol / medium / risk:authority`. The board invocation independently proves ACTION_ID, ROLE and ATTEMPT; it intentionally does not persist model fields.
- Plan raw SHA-256: `2146474d4de6e197003023307b2cb3470300c6c018ba9d44ca757b48f49aa1f6`.
- Planner evidence raw SHA-256: `7bc2ab530762c026ce09b9151153110fed0b27ad3985450266919ea2f8e3ca5d`.
- Developer evidence raw SHA-256: `d7aa27a6b46b5e5dbcef81ed3823a5ed6a40f181e9e7868bcbacd3f43e76525d`.
- Reviewer evidence raw SHA-256: `564a4c60d758c89048d2e7a6d60c5338bebb5dfa61c19d79daa4be4f5058f7d9`.
- Developer and Reviewer evidence are single-parent, evidence-only commits whose parent boards contain their exact durable invocation identities; neither evidence commit is in subject ancestry.

## Complete QA Validation

- Current primary `--from-board` manifest authority validation passed.
- The exact unchanged manifest object was transported to the clean task worktree.
- Complete frozen QA manifest executed once on exact subject and returned `ALLOW_VALIDATION`.
- Subject before/after: `503a471a47cd69180822a6e3963c133a4fb68e81`.
- Total duration: 1445 ms.
- `config-bootstrap-authority`: passed, 576 ms.
- `packaged-path-and-release`: passed, 720 ms.
- `config-bootstrap-compile`: passed, 75 ms.
- An initial `--manifest` argv transport supplied JSON where the supported interface required a file path; it returned `BLOCKED_MANIFEST_INVALID` before starting any check. Board, HEAD and clean facts were proved unchanged, then the supported byte-equivalent file transport was used. No test matrix was duplicated.

## Scope And Semantic Audit

- Subject is the exact single-parent child of base `e51a674b68ca1b4d1fe193b5e10903b361ae3660`.
- Changed paths are exactly the approved five: `backend/shared/config.py`, `connlab.admin.example.toml`, `tests/unit/test_config.py`, `tests/unit/test_desktop_packaged_runtime_paths.py`, `tests/unit/test_desktop_release_scripts.py`.
- `backend/desktop/runtime_paths.py`, `scripts/build_windows_desktop_release.ps1` and `scripts/build_windows_browser_release.ps1` are byte-identical to base.
- `git diff --check` passed.
- Controlled Python sizes remain below 500 lines: config 417, config tests 459, packaged-path tests 160, release-script tests 195.
- Template and deterministic bootstrap bytes contain the approved public `DGLAB` default.
- Bootstrap uses a unique same-directory complete temporary file, flush/fsync and exclusive non-overwriting publication.
- Concurrent creation preserves the winner and leaves no partial/truncated destination.
- Existing custom, blank, malformed and unreadable files are not repaired, rewritten or overwritten.
- Explicit environment presence, including an empty string, remains higher priority; `connlab.local.toml` password remains inert.
- Errors are operation-specific, path-bearing and redact underlying sensitive detail without alternate-location fallback.
- Packaged tests isolate the ProgramData target and prove development, local and example files are not copied or modified.

## Safety

- Primary and task worktree remained clean; task HEAD remained the exact subject.
- Tests used only synthetic temporary roots.
- No real ProgramData, development administrator configuration, local user configuration, public drive, workbook, installed release or deployed configuration was accessed or mutated.
- No board, implementation, evidence, ref or external configuration was modified by QA.
- No push, cleanup, archive, retire, reset, restore, stash, rebase, cherry-pick, force update, resource move or deletion occurred.
