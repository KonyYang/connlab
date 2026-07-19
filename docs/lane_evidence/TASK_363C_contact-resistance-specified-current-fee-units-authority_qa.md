# TASK_363C QA Evidence

Date: 2026-07-19
Role: QA / Smoke Owner
Status: `qa_pass`

## Scope And Environment

- Validation used only pytest disposable roots under `tmp\\task_363c_qa_*` via
  `--basetemp`; no real `data/connlab.sqlite3`, user folder, workbook, public-drive,
  LTR, or output artifact path was opened or mutated.
- No product source or test was edited by QA. No staged files, commit, push, or
  packaging action was performed.
- This is a backend-only authority lane. No browser action was required to validate
  its API/service contract; the disposable API integration suites are the applicable
  smoke surface.

## Functional Validation

Commands run from repository root:

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363c_qa_cr tests\unit\test_confirmed_matrix_fee_cr_specified_current_authority.py tests\integration\test_confirmed_matrix_fee_cr_specified_current_api.py tests\integration\test_fee_pricing_draft_cr_measurement_plan_rebase.py tests\unit\test_fee_default_fill.py -q
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363c_qa_profile tests\unit\test_confirmed_matrix_fee_draft_profile_consumer.py -q
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363c_qa_attestation tests\unit\test_fee_pricing_draft_prior_defaults_attestation.py tests\unit\test_fee_pricing_draft_automatic_build_safety.py tests\unit\test_fee_rule_transition_safe_rebase_measurement_plan.py tests\integration\test_fee_pricing_draft_measurement_plan_rebase_attestation.py -q
```

Actual results:

- CR target-first authority, API, B4 production rebase path, and full default-fill:
  `96 passed in 7.47s`.
- Shared profile-consumer suite including the B6 `not_started` no-fallback node:
  `9 passed in 1.51s`.
- Accepted TASK_363D attestation/rebase preservation suite:
  `27 passed in 2.55s`.

The executed disposable tests prove:

- exact confirmed `cr_specified_current` target selection keeps Group/row/Step/
  suffix authority and uses owning Group quantity: `8 x 5 = 40` at
  `10/reading`; `12 x 3 = 36` at `5/reading`, with no cross-Group sum;
- missing/wrong target, unavailable/not-started authority, missing lineage, unsafe
  authority, and invalid owning quantity return review-required without automatic
  Unit Price, Units, or Testing Fee;
- no legacy generic Step quantity, prose/text, Point Profile, or LLCR fallback is
  used for specified-current CR;
- an attested V2 draft becomes `rebase_required` after a confirmed CR authority
  change; reviewed CAS rebase refreshes automatic CR Units/Testing Fee and reloads
  as `current_v2`, while compatible manual Unit Price and discount values remain;
- B6 now asserts the same fail-closed behavior for the shared `not_started` profile
  consumer node.

## Static And Package Checks

```powershell
py -m py_compile backend\application\confirmed_matrix_fee_cr_specified_current.py backend\application\confirmed_matrix_fee_draft_service.py backend\modules\fee_evaluation\fee_default_fill_models.py backend\modules\fee_evaluation\fee_reviewed_extension_defaults.py
git diff --check -- <TASK_363C candidate paths>
git diff --cached --name-only
```

- `py_compile` passed.
- `git diff --check` passed; only existing LF/CRLF normalization notices appeared.
- UTF-8 trailing-whitespace scan found no matches.
- Cached index was empty. `data/**` had no worktree change.
- Candidate/new Python physical line counts are below the 500-line hard limit:
  CR helper `129`, mixed Fee draft service `458`, models `98`, reviewed defaults
  `252`, authority test `303`, API test `63`, and V2 integration test `210`.
- No candidate diff was found in Fee seeds/manifest, frontend/API client, real-data
  paths, or the locked default-fill implementation modules.

## Isolation Decision

- `backend/application/confirmed_matrix_fee_draft_service.py` is mixed. Integrator
  must stage only the exact CR routing/typed-authority hunks, excluding external Base
  Fee and rule-resolution hunks.
- `tests/unit/test_fee_default_fill.py` is mixed and currently `803` physical lines
  versus `728` at `HEAD`. Only the two authorized B3 CR nodes are TASK_363C; their
  combined hunk is net three lines smaller. The unrelated added test hunks must not
  be staged with this lane.
- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py` contains only the
  B6 tests-only behavioral node for this lane and is `177` physical lines.
- Known external LLCR, TASK_364B, TASK_365A/TASK_365C, frontend, PDF, release, and
  other dirty-worktree residuals were observed but not validated, changed, or
  attributed to TASK_363C.

## QA Decision

`QA gate: pass`

Residual risk: package ownership must apply the exact-hunk isolation above; no
functional QA blocker remains. Recommended next role: **Integrator packaging/readiness**.
