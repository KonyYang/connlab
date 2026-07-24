# QA Evidence - FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS

Date: 2026-07-24

Role: QA / Smoke Owner

Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`

Lane: `fee-default-fill-dependent-field-corrections`

## Gate Result

`qa_pass`

The final Child 2 implementation and its two line-neutral fixture-context
corrections passed the disposable backend/API and frontend payload validation.
No production code, test source, real database, workbook, public-drive file,
or generated business artifact was changed by QA.

## Environment And Safety Boundary

- Repository: `D:\PythonProject\connlab`
- Checked-out HEAD: `c5d91c36`
- Backend validation used pytest's disposable SQLite/temp fixtures only.
- Frontend validation used Vitest/build only; no browser route or real service
  was started.
- `git status --short -- data dist_release frontend/dist` was empty before the
  evidence write. The staged index was empty.
- QA did not read or write `data/connlab.sqlite3`, public-drive roots, LTR
  workbooks, attachments, or generated business outputs.

## Executed Validation

| Command | Result | Coverage |
| --- | --- | --- |
| `py -m pytest` over the nine bounded Child 2 duration-authority unit/API/publication modules | 38 passed | Structured source/import/edit to draft, first/revision Confirm publication, replacement/session signature, additive disposable schema bootstrap, typed duration fee authority, explicit-hour rules, no disallowed fallback, and V2 rebase no-write paths. |
| `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py tests/integration/test_matrix_editor_session_api.py -q` | 53 passed | Matrix session persistence/replacement plus reviewed rebase, strict r6 context, CAS and manual-field preservation. |
| V2 persistence/contract/repository/attestation/rebase/Measurement Plan/CR/API regression set | 45 passed | Currentness, attestation, stale-CAS no-overwrite, safe reviewed rebase, and confirmed-version lineage. |
| `py -m pytest` over the accepted TASK_366C eight-module import/replace/replay/authority gate | 29 passed | Child 2 remains compatible with the accepted Matrix import method-authority composition. |
| `py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q` | 113 passed | Child 1 Base Fee policy remains read-only; Long-term high temperature zone load and Salt Spray authorized paths, rejected aliases, legacy per-hour families, Temperature & Humidity guard, CR/LLCR boundaries, and manual-field protections regress correctly. |
| `py -m pytest tests/integration/test_matrix_typed_duration_authority_round_trip_api.py tests/integration/test_matrix_duration_authority_publication_api.py -q` | 7 passed | Disposable additive duration schema bootstrap and first/revision/source-replacement API publication round trips. |
| `npm test -- MatrixEditorWorkspace.durationAuthority --run` | 1 file / 2 passed | Non-visual duration-authority seed/save/confirm payload preservation. |
| `npm run build` in `frontend` | passed | TypeScript build passed. Only the existing Vite chunk-size warning was emitted. |
| `py -m py_compile` over 42 authorized backend candidate modules plus nine new bounded Python tests | passed | Candidate imports/compile health. |

## Behavioural Conclusion

- Typed duration authority is exercised through source/draft/confirmed
  snapshots and Matrix Editor session payloads. The passing bounded tests
  cover first confirmation, revision carry-forward, source replacement,
  canonical signature/stale handling, and confirmed Fee same-build use.
- Confirm Matrix remains the publication boundary. Missing, invalid, stale,
  conflicting, multiple, or wrong-row authority paths are covered by the
  bounded no-write/manual-review regressions; legacy condition/requirement/day
  text, legacy Step/readings, Point Profile, LLCR/CR, and other-row/group
  fallback are not accepted authority.
- Base Fee remains the accepted Child 1 read-only policy. Testing Fee only
  derives from safe dependencies, while manual price/units/type/discount and
  compatible fields remain preserved by the V2/rebase regressions.
- The expected duration-specific outcomes are covered by the passing suite:
  approved Long-term high temperature zone load is `15/per hour` with
  normalized-hour units; Salt Spray follows its approved typed path; rejected
  aliases remain manual/review-required.

## Static And Package Checks

- Candidate `git diff --check`: passed; only existing LF/CRLF normalization
  notices were emitted.
- UTF-8 trailing-whitespace scan of the 51 backend/test candidates: no
  matches.
- All checked new/split Python candidate modules and all nine bounded tests
  are below the 500 physical-line limit. Largest checked modules: payload
  builder 474, session signature 451, line builder 390.
- No staged files. No `data`, `dist_release`, or `frontend/dist` changes.
- The frontend diff contains typed DTO additions and the non-visual Matrix
  Editor payload mapping only; no new control/copy/layout/inference behavior
  was found.

## Package Isolation

The current worktree includes external changes that must not be packaged as
this lane, including `backend/api/dependencies.py`, Fee Evaluation frontend
residuals, TASK_366C composition files, and unrelated board/docs/task files.

The two mixed legacy test files are hunk-isolated and must be staged by hunk,
not by whole file:

- `tests/integration/test_matrix_editor_session_api.py`: exactly two
  `fee_rules_v2026_06_03` to `fee_rules_v2026_07_17_r6` literal replacements
  in the autosave/restore/confirm/discard fixture.
- `tests/unit/test_matrix_fee_rebase_promotion_service.py`: exactly two of the
  same literal replacements in the soft-removed-row restore fixture.

Both hunk sets are line-neutral (`2 additions / 2 deletions` per file) and
their enclosing module tests passed. Integrator must stage only the approved
Child 2 domain/storage/repository/application/API transport, type-only client,
non-visual Matrix payload, bounded test/evidence paths, and these exact hunks.
Child 1 is read-only; Child 3 and the umbrella remain blocked and excluded.

## Residual Risk

No blocking product finding. This was an automated/disposable QA gate; no
browser visual smoke was required by the non-visual frontend contract. The
only packaging risk is the dirty mixed worktree, mitigated by strict
path-and-hunk staging.

## Recommended Next Role

Integrator packaging/readiness, with the package-isolation constraints above.
