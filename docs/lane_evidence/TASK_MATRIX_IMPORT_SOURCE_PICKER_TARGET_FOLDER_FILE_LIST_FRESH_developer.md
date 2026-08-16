# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH Developer Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH
ROLE: Developer
STATUS: blocked
SUBJECT: 1798d0377347459a78478b9a10e3c2f2a23327e4
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: 02a14ac9be19ea59782ca4b53c3f646bbb2672ee156ac4dff2f4ac01149d7551
ATTEMPT: 1
NEXT: User
BLOCKER: DEVELOPER_BLOCKED

## Implementation

- Bounded child commit: `1798d0377347459a78478b9a10e3c2f2a23327e4`.
- Changed exactly the approved service and two backend test paths.
- Added streamed read-only SHA-256 fingerprinting, before/after descriptor checks, opaque fingerprint
  binding, equal-length same-name replacement rejection, and source read-only regressions.
- No endpoint, frontend production byte, persistence, schema, parser, Matrix authority or external file
  was changed.

## TDD and focused validation

- Retained diagnostic with `-x -vv`: 23 passed; the historical failure did not reproduce.
- New stale-replacement RED failed because no not-found error was raised.
- Replacement and read-only nodes: 2 passed after the fix.
- Candidate service/API set: 15 passed.
- Candidate/API/preview set: 26 passed.

## Authoritative manifest blocker

- Manifest SHA-256: `f7e9a8779b724390c61bb970332dfa986315fb6430ef711634224512911f9eb9`.
- Board SHA-256: `98cae47fcd5e781d502fd8b5410afee68568d6520e068356b3114ab3d149ceb9`.
- Overall code: `BLOCKED_VALIDATION_FAILED`; duration: 5547 ms.
- First check `source-folder-candidate-contract` exited 1 in 5428 ms.
- stdout SHA-256: `d4e05d53bfff11158ceaa9662654c1e5e8c6ec006f728ea06cb274d2297ffcb3`.
- stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- The authoritative runner exposed no failing pytest node or assertion; remaining checks were not run.
- No retry or post-manifest product/test change occurred.

## Git and safety

- Task branch/worktree is clean at the exact subject; retained start remains its ancestor.
- Base-to-subject diff remains exactly the frozen 12 product/test paths.
- Primary was clean at the durable invocation state.
- Ignored smoke fixtures only were prepared; Vite and Chrome were stopped.
- No push, cleanup, archive, retire, reset, restore, stash, rebase, cherry-pick, force update or resource
  deletion occurred.
