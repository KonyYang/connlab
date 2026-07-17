# TASK_363A QA Evidence

Date: 2026-07-17

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`
Lane: `fee-rule-temperature-and-force-alias-safe-rebase`
Role: QA / Smoke Owner
Gate result: `qa_pass`

## Scope And Environment

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- QA used disposable pytest and manifest roots only: `tmp/task_363a_qa_pytest` and `tmp/task_363a_qa_manifest`.
- No real SQLite database, user file, workbook, public-drive/LTR path, Fee UI/API-client, product output, staging, commit, or push action occurred.
- Governance residual: `docs/task_board.md` still presents the earlier pending-Developer wording. Current Developer/Reviewer evidence and this explicit delegation describe the implemented candidate and QA gate. QA did not alter the locked board.

## Executed Validation

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363a_qa_pytest tests\unit\test_fee_rule_transition_safe_rebase.py tests\unit\test_fee_rule_temperature_force_alias_safe_rebase.py tests\unit\test_fee_evaluation_pricing_draft_persistence_service.py tests\unit\test_fee_evaluation_pricing_draft_v2_rebase.py tests\unit\test_fee_default_fill.py tests\unit\test_fee_rule_seed_loader.py tests\integration\test_fee_evaluation_pricing_draft_compatibility_api.py tests\integration\test_confirmed_matrix_fee_draft_api.py tests\integration\test_confirmed_matrix_fee_evaluation_export_api.py -q
```

Actual result: `148 passed in 7.50s`.

```powershell
cd frontend
npm run build
```

Actual result: passed. The existing Vite chunk-size warning remained non-blocking.

```powershell
py -m py_compile <TASK_363A touched application, route, matcher, seed-loader, and transition modules>
git diff --check
```

Actual result: compilation passed. Diff check reported no whitespace error; only established LF/CRLF normalization notices. Targeted candidate trailing-whitespace scan found no matches. Candidate Python physical line counts are below the 500-line hard limit; the largest checked file is `459` lines.

## Functional Smoke Findings

- `Temperature life`, punctuation-normalized and whitespace-normalized variants resolve to `fee_rule_high_temperature_life`; explicit `48 hours` produced `15 / per hour / 48`.
- `Lateral Force`, `contact retention force`, `Single Pin Mating Force`, and `Single Pin Unmating Force` resolve to `fee_rule_mechanical_force`; structured readings yielded `20 / per reading / 30`.
- Generic `Mating Force`, `Unmating Force`, `Insertion Force`, `Withdrawal Force`, and Latch variants did not receive the `50 / per sample` fallback. Only exact normalized `Mating/Un-mating Force` retains the reviewed exception.
- `CPA force`, `TPA force`, and `Automotive mechanical force` retained the Automotive mechanical rule and `review_required` manual/Pending behavior.
- Active manifest selects `fee_rules_v2026_07_17_r6`. The accepted `fee_rules_v2026_07_16_r5` remained independently loadable with the same source hash; disposable manifest selections resolved r6 then r5 without modifying repository seed files.
- V2 transition tests verified changed/missing Point Profile or Measurement Plan lineage, invalid prior-default fingerprint, and row-identity mismatch return `blocked` with no saved snapshot. A valid r5-to-r6 rebase preserved manual Unit Price `999` while refreshing automatic Units from `3` to `9`.
- Existing load/Cancel, CAS/stale, current-V2, automatic-default fingerprint, and ordered row identity regressions remained in the disposable suite.

## Scope And Residual Checks

- Diff-only candidate scan found no real database/folder, public-drive/LTR, COM, or workbook-path addition.
- Current frontend Fee page/model modifications, TASK_362A evidence/task files, all
  `backend/api/dependencies.py` content except the later Planner-approved exact
  `_build_fee_evaluation_pricing_draft_service` composition hunk, r5 line-ending
  residuals, release/dist output, and unrelated task-board hunks are external to the
  TASK_363A package and must remain excluded.
- The r5 seed/extension dirty two-line worktree normalization remains an external immutable baseline residual; TASK_363A uses new r6 seed/extension plus the manifest activation only.

## QA Disposition

`QA gate: pass`

No product blocker found. Recommend `Integrator packaging/readiness`, staging only the reconciled TASK_363A candidate and isolating all listed external residuals.

---

## QA Package-Isolation Re-Gate

Date: 2026-07-17
Gate result: `qa_pass`

### Accepted Baseline

- Re-gate used `HEAD` `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`.
- The accepted TASK_362A baseline repair commit contains only the two r5 seed-identity changes and its repair evidence.
- `fee_rules_v2026_07_16.json` and `fee_rule_extensions_v2026_07_16.json` have no working-tree diff against `HEAD`; they are not in the TASK_363A candidate.
- The staging index is empty.

### Revalidation

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363a_qa_isolation tests\unit\test_fee_rule_temperature_force_alias_safe_rebase.py tests\unit\test_fee_rule_transition_safe_rebase.py tests\unit\test_fee_rule_seed_loader.py -q
```

Actual result: `47 passed in 3.14s`.

- The accepted r5 library is used for prior-default reconstruction. The r6 transition verifies the prior automatic-default fingerprint and ordered row identities before using current defaults.
- Missing or changed Point Profile/Measurement Plan lineage, prior fingerprint mismatch, and row-identity mismatch returned typed `blocked` with no saved snapshot. A safe transition preserved manual Unit Price while refreshing automatic Units.
- Exact Temperature/force aliases, the sole exact `Mating/Un-mating Force` `50/per sample` exception, and CPA/TPA/Automotive manual behavior remained covered by the isolation suite.
- Focused `py_compile` passed. `git diff --check` reported only established LF/CRLF notices; trailing-whitespace scan was clean. All checked candidate Python modules remain below 500 physical lines; largest is 459.

### Candidate Isolation

- Candidate whitelist contains the 25 scoped backend/seed/test paths plus TASK_363A
  docs and one hunk-level exception in `backend/api/dependencies.py`. The exception is
  limited to `_build_fee_evaluation_pricing_draft_service`: local Measurement Plan
  adapter construction, reuse for automatic defaults, and
  `measurement_plan_provider` injection. It includes r6 seed/extension and manifest
  activation, not the accepted r5 baseline pair.
- The earlier `459`-line maximum applies to the bounded candidate modules checked by
  QA. `dependencies.py` is a pre-existing oversized composition root; its separately
  audited exception totals `6` additions / `4` deletions, net `+2` (`1958 -> 1960`
  under the corrected checked-out UTF-8 physical-line convention),
  with no business logic. Any other hunk remains excluded.
- No candidate hunk adds frontend/Test Points UI, release/dist, real database/file, workbook, public-drive/LTR, or COM path behavior.
- Outside the whitelist, current tracked residuals include every other
  `backend/api/dependencies.py` hunk/content, TASK_362A governance files, unrelated
  `docs/task_board.md` hunks, and existing Fee frontend test/model files. They remain
  excluded. Untracked `dist_release/**` is also excluded.

### Re-Gate Disposition

`QA package-isolation gate: pass`

This QA pass remains valid product evidence, but its original whole-file exclusion is
superseded by the Planner package-boundary reconciliation. Recommend Reviewer
package-boundary re-gate, then QA/Integrator package isolation using the exact hunk
whitelist while excluding the accepted r5 baseline commit and every listed residual.

---

## QA Exact-Hunk Package-Boundary Re-Gate

Date: 2026-07-18

Gate result: `qa_blocked` (source-of-truth package-boundary metadata mismatch; no
product behavior failure found).

### Scope Under Test

This re-gate replaces the earlier whole-file exclusion with the approved exact-hunk
whitelist for `backend/api/dependencies.py` only. The expected logical composition is
inside `_build_fee_evaluation_pricing_draft_service`:

1. construct the existing confirmed Measurement Plan adapter once;
2. reuse it for `ConfirmedMatrixFeeDraftService`; and
3. pass it to `FeeEvaluationPricingDraftPersistenceService` as
   `measurement_plan_provider`.

### Exact-Hunk Audit

Commands:

```powershell
git diff --numstat -- backend/api/dependencies.py
git diff --unified=10 -- backend/api/dependencies.py
git diff --unified=0 -- backend/api/dependencies.py
git show HEAD:backend/api/dependencies.py | Measure-Object -Line
(Get-Content backend/api/dependencies.py -Encoding UTF8 | Measure-Object -Line).Lines
```

Observed facts:

- `git diff --numstat` is exactly `6` additions and `4` deletions (net `+2`).
- Default-context diff has one logical composition hunk. Zero-context diff represents
  it as the expected three fragments, all within the same function: adapter local,
  reuse in automatic defaults, and `measurement_plan_provider` injection.
- No import, branch, validation, transformation, persistence operation, authority
  decision, or other function is changed in this file.
- `HEAD` has `1958` physical lines and the worktree has `1960` physical lines under
  the checked-out UTF-8 command convention, including blanks.
- Planner subsequently corrected the task/plan/evidence metadata to this source fact;
  the earlier `2214 -> 2216` assertion is superseded.

The `6/4` hunk content and its function boundary match the approval, but the stated
physical line-count invariant does not match the actual repository. QA cannot certify
the package boundary while the task/plan/evidence fact is contradictory.

### Disposable Regression And Safety Validation

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_363a_qa_exact_hunk tests\unit\test_fee_rule_transition_safe_rebase.py tests\unit\test_fee_rule_temperature_force_alias_safe_rebase.py tests\unit\test_fee_evaluation_pricing_draft_persistence_service.py tests\unit\test_fee_evaluation_pricing_draft_v2_rebase.py tests\unit\test_fee_default_fill.py tests\unit\test_fee_rule_seed_loader.py tests\integration\test_fee_evaluation_pricing_draft_compatibility_api.py tests\integration\test_confirmed_matrix_fee_draft_api.py tests\integration\test_confirmed_matrix_fee_evaluation_export_api.py -q
```

Actual result: `148 passed in 6.31s` using the contained `tmp\task_363a_qa_exact_hunk`
root.

- Missing or changed Point Profile / Measurement Plan lineage returned typed `blocked`
  with no saved snapshot in the transition regression coverage.
- A normal r5-to-r6 safe rebase preserved the manual Unit Price while refreshing the
  automatic Units. The suite also retained alias, manifest, CAS/currentness, and
  export regressions.
- The exact production composition now passes the same confirmed Measurement Plan
  adapter to both automatic-default and persistence source-context consumers. The
  receiving persistence service already uses `measurement_plan_provider` for lineage.

Additional checks:

```powershell
py -m py_compile <dependencies and TASK_363A backend modules>
git diff --check -- <TASK_363A candidate backend paths>
Select-String -Pattern '[ \t]+$' <candidate paths>
git diff --name-only -- <accepted r5 seed pair>
git diff --cached --name-only
```

- Compilation passed. Diff and trailing-whitespace checks found no defect; only
  established LF/CRLF normalization notices were emitted.
- No r5 seed-pair working-tree diff exists; the index is empty.
- Diff-only candidate additions contained no real database/folder, public-drive/LTR,
  workbook/COM, release/dist, or frontend path.
- All external TASK_362A governance, TASK_361L/LTR/frontend/Test Points, board, and
  `dist_release/**` residuals remain excluded.

### Required Resolution And Disposition

`QA package-boundary/isolation gate: blocked checkpoint; metadata correction recorded`

Planner corrected the false `2214 -> 2216` physical-line assertion in the TASK_363A
task/plan/reconciliation evidence to `1958 -> 1960`; no Developer product fix was
indicated or performed. Next route is Reviewer package-boundary metadata re-gate,
followed by QA re-gate before Integrator packaging.

---

## QA Metadata And Package-Isolation Re-Gate

Date: 2026-07-18

Gate result: `qa_pass`

### Frozen Metadata Recheck

```powershell
git show HEAD:backend/api/dependencies.py | Measure-Object -Line
(Get-Content backend/api/dependencies.py -Encoding UTF8 | Measure-Object -Line).Lines
git hash-object backend/api/dependencies.py
git diff --numstat -- backend/api/dependencies.py
git diff --unified=0 -- backend/api/dependencies.py
git diff --cached --name-only
```

Actual result:

- Checked-out UTF-8 physical lines including blanks: `HEAD 1958`, worktree `1960`.
- Git blob hash: `916da2dce7d6e1b39994e2117d54792beb39716e`.
- Numstat: `6` additions / `4` deletions, net `+2`.
- The zero-context diff contains the three authorized fragments, all in
  `_build_fee_evaluation_pricing_draft_service`: local Measurement Plan adapter,
  automatic-default reuse, and `measurement_plan_provider` injection.
- The staging index is empty. No other `dependencies.py` function or composition
  hunk is present.

TASK, plan, Planner/reconciliation/package-boundary evidence, Reviewer evidence, this
QA evidence, and board now consistently use `1958 -> 1960`. The prior `2214 -> 2216`
value is explicitly superseded historical audit context only.

### Whitelist And Regression Disposition

- Whole-file exclusion is replaced by the exact hunk whitelist above; every other
  `backend/api/dependencies.py` hunk/content remains excluded.
- The prior contained `148 passed` backend/API suite remains valid because this
  metadata pass made no product-code change. It covers typed blocked/no-write for
  missing or changed Measurement Plan lineage and safe r5-to-r6 manual-field
  preservation.
- `py_compile` for composition, persistence, and rebase modules passed. Diff-check
  and trailing-whitespace scans found no defect beyond established LF/CRLF notices.
- Candidate additions contain no real database/folder, workbook/COM, public-drive/LTR,
  release/dist, or frontend path. The accepted r5 seed pair has no worktree diff;
  TASK_362A/TASK_361L/LTR/frontend/Test Points/board/release residuals remain outside
  the package.

### QA Disposition

`QA metadata/package-isolation gate: pass`

Recommend only `TASK_363A Integrator final packaging re-gate`. Integrator must stage
the reconciled TASK_363A whitelist and only the exact approved
`backend/api/dependencies.py` fragments; do not stage the whole file or any listed
external residual.
