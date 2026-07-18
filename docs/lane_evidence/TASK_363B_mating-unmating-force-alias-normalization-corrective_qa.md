# TASK_363B QA Evidence: Mating/Unmating Force Alias Normalization Corrective

Date: 2026-07-18

Role: QA / Smoke Owner

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Task: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

Gate result: `qa_pass` for the TASK_363B candidate, with one separately recorded
external API-regression residual.

## Scope And Environment

- All test databases were contained under `tmp\\task_363b_qa*`.
- The API smoke used the disposable SQLite root `tmp\\task_363b_api_smoke_rerun` and
  only called `GET /api/projects/P363B/confirmed-matrix/fee-draft` after seeding that
  disposable project and confirmed Matrix snapshot.
- No real database, project folder, workbook, public-drive path, generated output,
  product source, frontend/API client, staging, commit, or push was used.

## Candidate Boundary

- Product candidate: `backend/modules/fee_evaluation/fee_rule_matcher.py` only.
- It adds two anchored full-label canonicalizers before generic tokenization:
  base combined Mating/Unmating maps to `mating un mating force`; exact Single Pin
  combined form maps to `single pin mating force`.
- Candidate physical UTF-8 line counts: matcher `135`; alias test `115`; two-Group
  test `132`; all are below the 500-line hard limit.
- `fee_reviewed_extension_defaults.py`, r6 seed/extension/manifest, frontend/API
  client, and price/formula paths have no TASK_363B candidate hunk. The visible dirty
  `backend/application/confirmed_matrix_fee_draft_service.py` remains external and
  excluded.

## Core Disposable Regression

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363b_qa_core tests\unit\test_fee_rule_mating_unmating_alias_normalization.py tests\unit\test_confirmed_matrix_fee_draft_mating_unmating_units.py tests\unit\test_fee_rule_temperature_force_alias_safe_rebase.py tests\unit\test_fee_default_fill.py tests\unit\test_confirmed_matrix_fee_draft_service.py tests\unit\test_fee_evaluation_pricing_draft_persistence_service.py tests\unit\test_fee_evaluation_pricing_draft_v2_rebase.py tests\unit\test_fee_rule_transition_safe_rebase.py -q
```

Actual result: `160 passed in 2.97s`.

Validated behavior:

- `MATING /UNMATING FORCE`, slash/space/case variants, and accepted hyphenated base
  spelling resolve to Mechanical force with Unit Price `50`, unit label `sample`, and
  owning Group sample quantity only.
- Exact combined Single Pin variants remain Mechanical force `20/reading` and retain
  their existing missing-readings review path.
- Generic no-Force, Mating, Unmating, Insertion, Withdrawal, Latch, CPA, TPA, and
  Automotive negative/manual boundaries remain intact. Contact retention and Lateral
  Force remain `20/reading`.
- Missing or invalid owning sample quantity stays `review_required`, has no Units or
  Testing Fee, and retains the typed manual-review result.
- TASK_363A safe-rebase/default-fill/currentness regressions remain green.

## Disposable API Two-Group Smoke

QA artifact: `tmp\\task_363b_api_smoke.py`.

The temporary API snapshot used two Groups with sample quantities `5` and `9`, base
labels `MATING /UNMATING FORCE` and `Mating/Un-mating Force`, and divergent step
readings `100` and `200`.

```powershell
py tmp\task_363b_api_smoke.py
```

Actual result: passed.

`GET /api/projects/P363B/confirmed-matrix/fee-draft` returned:

| Group | Unit price | Unit label | Units | Testing fee |
|---|---:|---|---:|---:|
| `g1` | `50` | `sample` | `5` | `250` |
| `g2` | `50` | `sample` | `9` | `450` |

Both lines matched `fee_rule_mechanical_force` by exact alias. The divergent readings
did not multiply Units or cause cross-Group aggregation.

## Static And Package Checks

```powershell
py -m py_compile backend\modules\fee_evaluation\fee_rule_matcher.py
git diff --check -- backend\modules\fee_evaluation\fee_rule_matcher.py
Select-String -Pattern '[ \t]+$' <candidate paths>
git diff --cached --name-only
```

- Compilation passed. Diff and trailing-whitespace scans found no defect beyond
  established LF/CRLF notices.
- Staging index is empty.
- Candidate scan found no real database/folder, workbook/COM, public-drive/LTR,
  release/dist, frontend, API-client, seed, or manifest path/content.
- r6 seed/extension/manifest has no worktree diff.

## External API Regression Residual

An expanded read-only run also included the unrelated existing
`tests/integration/test_confirmed_matrix_fee_draft_api.py`:

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363b_qa <core suite plus tests\integration\test_confirmed_matrix_fee_draft_api.py> -q
```

Actual result: `1 failed, 162 passed`.

Failure: `test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units` expected
LLCR Units `"20"`; the current dirty worktree returned `None`.

This regression does not exercise either TASK_363B combined alias and is outside its
locked candidate boundary. The active worktree has external unaccepted changes in
`backend/application/confirmed_matrix_fee_draft_service.py` and the untracked
`backend/application/confirmed_matrix_fee_rule_resolution.py`; QA did not modify or
attribute a fix to TASK_363B. It remains an explicit external residual for its owning
lane to investigate, and was not packaged with TASK_363B.

## QA Disposition

`QA gate: pass`

TASK_363B's matcher-only corrective and two bounded tests pass their required
disposable service/API smoke and locked-scope checks. Recommend only `Integrator
packaging/readiness`, staging the matcher hunk, two new bounded tests, and TASK_363B
governance/evidence while excluding all external residuals. The LLCR API failure above
must remain visible for its external owner; it is not a TASK_363B Developer fix.
