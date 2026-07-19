# TASK_364B Developer Evidence

Date: 2026-07-18

Role: Developer

Status: `developer_implementation_complete / pending_reviewer_qa_user_acceptance`

TASK_ID: `TASK_364B_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_AND_UI`

Lane: `project-point-profile-cr-coverage-authority-and-ui`

## Current Phase / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- TASK_363B remains the board's separate active Fee lane.
- TASK_364B was explicitly approved with `批准 TASK_364B 实施`; its Point Profile
  backend/frontend paths are disjoint from TASK_363B's Fee matcher scope.
- Implementation stopped at project-level LLCR/CR Point Profile authority, atomic
  confirmation, Setup UI, and confirmed summary. No downstream consumer was opened.

## Implementation

- Added the additive
  `contact_point_profile_cr_category_selections` authority table. No rows means
  `follow_llcr`; one or more stable category-id rows means `custom`.
- Extended schema bootstrap, repository, V3 fingerprinting, lifecycle confirmation,
  read projections, typed API, and frontend client contracts for CR coverage.
- Direct Confirm issues or retains category ids, persists whole-category CR selection,
  and confirms one immutable Point Profile revision in the same transaction.
- Existing revisions with no selection rows read as `follow_llcr`; their persisted
  fingerprints and history are not rewritten.
- The Setup card now shows restrained inline `CR coverage` controls. Customize starts
  with current categories selected; later added rows start unselected; returning to
  LLCR follow clears custom selection. Category labels remain dynamic project data.
- Matrix summary displays the confirmed follow/custom CR policy without calculating
  Matrix-group sample totals or feeding any Fee/workbook consumer.

## TDD Evidence

- RED: four focused tests initially failed for the missing selection table, V3
  fingerprint arguments, custom lifecycle persistence, and frontend CR controls.
- GREEN: the minimal backend/frontend implementation made those focused tests pass.
- Completion protection was expanded for exact legacy three-table upgrade, malformed
  selection shape, default follow, custom-all, stable identity after rename, a later
  unselected row, return-to-follow, and follow/stale no-partial-write behavior.
- The expanded schema/lifecycle protection set passed `23/23` before the final suite.

## Fresh Validation

- Point Profile backend set: `46 passed`.
- Contact Measurement Plan plus Matrix workspace frontend regression: `12` files and
  `89 passed`.
- Frontend production build: passed. Vite's existing chunk-size advisory remains a
  non-blocking warning.
- `py_compile` passed for all changed TASK_364B Python modules.
- Scoped `git diff --check` passed; only repository LF/CRLF conversion notices were
  emitted.
- Production-path scan found no hard-coded HP/LP/High Power/Low Power policy and no
  `TODO` or `FIXME` marker.
- Changed feature/service files remain below their applicable hard limits. The shared
  `database.py` was already above the project line target; TASK_364B changes only its
  authorized Point Profile table-name registration and does not refactor that file.

## Browser Evidence

- A fresh localhost tab showed default `Same as LLCR` coverage and `30 points / sample`.
- `Customize CR` selected all three dynamic categories; locally deselecting one showed
  `2 categories` and `25 points / sample`.
- At `514x831`, the document had no horizontal overflow and the inline controls
  remained usable; the fresh tab reported no console errors.
- Browser smoke intentionally did not press Confirm, so no operator Point Profile
  business-authority write was performed during visual verification.

## Task Review Checklist

- Architecture: API remains typed and thin; application owns validation/transactions;
  infrastructure owns SQLite shape and persistence; React uses the API client/model.
- Scope: no Matrix-group totals, Measurement Plan target authority, Fee, workbook,
  Generic output, Office, LTR, parser, dependency, release, or TASK_363B change was
  made as part of this lane.
- Design: stable ids, derived mode, and V3 fingerprints preserve history and allow any
  current whole category without name heuristics.
- Runtime: temporary-SQLite tests, typed API regression, frontend tests/build, and
  disposable browser smoke passed.
- Quality: typed contracts and focused helpers are present; no unfinished marker or
  new dependency was added.

## Stop Point / Next Legal Role

TASK_364B Developer implementation is complete locally. The next legal gate is
focused Reviewer/QA and user acceptance. No Matrix-group CR total, Fee, workbook, or
other downstream CR-consumer task is activated automatically.

## Corrective Revision R1

Approval: `批准 TASK_364B R1 实施`

Status: `developer_r1_complete / pending_reviewer_qa_user_acceptance`

### Implementation

- Replaced the duplicated CR coverage section with one narrow checkbox cell on every
  category row. Visible columns are `Point category`, `Range`, `CR`, and action; the
  top `LLCR` heading and points-per-sample summary remain.
- Removed the separate `Customize CR` / `Use same as LLCR` frontend state and controls.
- Added rows start checked. All checked derives `follow_llcr`; any unchecked row
  derives `custom`; zero checked remains invalid.
- Preserved the existing Confirm command contract: follow sends false row flags and
  custom sends the visible row flags. No backend, API, storage, client DTO, or
  confirmed-summary change was made in R1.

### TDD And Validation

- Selector RED proved the previous empty-row default was false and the derived-mode
  selector was absent; GREEN passed `5/5`.
- Hook RED proved explicit mode state did not follow row toggles; GREEN passed `4/4`
  and covers custom, all-selected follow, new-row checked default, and command shape.
- Editor RED proved the inline CR column was absent; GREEN passed `7/7` and covers
  visible headers, no LLCR checkbox column, no duplicate section, and row toggling.
- Serial regression passed `12` test files and `91/91` tests.
- `npm run build` passed; the existing Vite chunk-size advisory remains.
- `git diff --check` passed with repository line-ending notices only. R1 production
  files contain no obsolete mode-button/CR-section selector and stay below applicable
  line limits.

### Browser Evidence And Open Recheck

- Effective in-app viewport was `723x831`: document `scrollWidth 708 <= clientWidth
  723`, table `scrollWidth == clientWidth == 531`, and no separate CR section existed.
- Page behavior confirmed: the three persisted rows started checked; Signal could be
  excluded; an added blank fourth row started checked; deleting it restored three
  rows; zero selected disabled Confirm; restoring all three re-enabled Confirm.
- Confirm was never pressed, so browser smoke did not write project authority.
- The browser backend did not honor the requested `514px` override. Its console also
  retained one Fast Refresh hook-order error whose signature exactly matches R1
  removing the sixth `useState` before the existing `useCallback`. Current source has
  unconditional hooks, fresh hook/component tests and build pass, and the page was
  interactive afterward. Focused Reviewer/QA must recheck an effective `514px` and a
  clean console from a fresh page session.

### Stop Point

R1 Developer work is complete locally. The next legal role is focused Reviewer/QA,
then user acceptance. No downstream CR totals or consumers are activated.
