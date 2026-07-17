# TASK_363A Developer Implementation Evidence

Date: 2026-07-17

Role: Developer

Status: `developer_bounded_fix_complete / pending_reviewer_implementation_re_gate`

TASK_ID: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Implementation Scope

Implementation stayed limited to exact Temperature/force aliases, safe immutable seed
activation, reviewed V2 pricing-draft rebase, and the frozen negative/manual paths.
No frontend/API client, schema, real database/file, stage, commit, or push action was
performed. Existing TASK_362A/TASK_361L and release/dist residuals remain excluded.

## Repository Facts Re-read

- The active manifest selects the immutable `fee_rules_v2026_07_17.json` (r6); the
  previous r5 seed remains available for safe prior-default reconstruction.
- `fee_rule_matcher.py` normalizes text, checks exact aliases, then performs generic
  token-subset matching; the new mechanical/Automotive policy must fence only those
  families from the generic stage.
- `fee_reviewed_extension_defaults.py` contains the current broad mechanical-force
  `50/per sample` branch and already has explicit duration/readings helpers that can
  be reused.
- `fee_rule_seed_compiler.py` compiles a reference snapshot plus reviewed extension;
  activation is selected by the manifest. Accepted r5 artifacts are not editable.
- TASK_361L V2 source context, provenance, CAS, and current-V2 guards are the
  compatibility boundary. The transition needs a read-only old-seed lookup and
  prior-default reconstruction before reviewed save.

## Frozen Decisions

- Exact normalized positives: `Temperature life`; `Lateral Force`; `contact retention
  force`; `Single Pin Mating Force`; `Single Pin Unmating Force`.
- Positive Temperature life uses `15/hour` and explicit hours; missing/conflicting
  hours is Pending/review-required.
- The four force aliases use `20/reading` and existing explicit/structured readings;
  missing readings are Pending/review-required.
- Only exact normalized `Mating/Un-mating Force` retains `50/per sample`. Generic
  Mating/Unmating, Insertion, Withdrawal, and Latch variants never inherit it.
- CPA/TPA/Automotive mechanical force remains exact manual-review/Pending.
- Rebase refreshes only proven system Pending/blank values and proven system zero;
  ambiguous zero or provenance blocks. Manual Unit Price, Units, Unit Type, Base Fee,
  Discount, Spend Time, Notes, and other manual fields survive. Testing Fee is
  recalculated.
- Load/Cancel is zero-write; reviewed save uses TASK_361L CAS/current-V2; stale,
  unknown-seed, V1, changed-lineage, row-mismatch, or mixed-provenance inputs fail
  closed.

## Implemented File-Level Sequence

1. Added `fee_rule_extensions_v2026_07_17.json` and compiled
   `fee_rules_v2026_07_17.json` from the existing reviewed snapshot. The accepted r5
   files remain available and the manifest is the only activation switch.
2. Added exact aliases and blocked mechanical/Automotive token-subset fallback while
   retaining unrelated generic matching.
3. Restricted the 50/sample branch to normalized exact `Mating/Un-mating Force`;
   generic Mating/Unmating/Insertion/Withdrawal/Latch uses no sample fallback, and
   CPA/TPA/Automotive remains review-required.
4. Added provenance-aware rebase field selection, bundled prior-seed validation,
   latest V2 read-only candidate loading, and a sub-500-line transition helper. CAS,
   current-V2 and zero-write load/Cancel boundaries remain in the existing service.
5. B1/B2 bounded fix: the transition helper now rebuilds defaults with the immutable
   saved seed, attests the saved automatic-default fingerprint and ordered row
   identities, and compares Matrix, Point Profile, and Measurement Plan lineage before
   any reviewed rebase. Missing or divergent attestation returns typed `blocked` with
   no persistence call. Production composition injects the confirmed Measurement Plan
   read adapter into the V2 source context; its deterministic target projection is
   fingerprinted for lineage checks.

## Future May Touch / Locks

May Touch is limited to the exact seed/manifest, matcher/alias policy, reviewed
extension defaults, narrow application transition helper, named TASK_361L V2 helpers,
dependency composition if necessary, focused backend tests, and TASK_363A docs.
Frontend/API DTO/client, Fee UI, formulas outside the frozen aliases, schema/storage,
Matrix/Point Profile/Measurement Plan, workbook/Required Forms, Generic outputs,
parser/import, LTR/public drive, real DB/files, TASK_362A-C/release residuals,
`.agents/**`, `docs/project_management/**`, and remote push are locked.

## Validation Results

Focused backend and compatibility tests passed: `254 passed` across matcher,
default-fill, seed/extension loader, pricing-draft V2 rebase/persistence/repository,
Confirmed Matrix Fee, pricing-draft API, compatibility API, export API, and Confirmed
Fee lineage suites. The dedicated TASK_363A alias/default tests cover positive aliases,
normalization, negative force families, Automotive manual review, explicit hours,
reading quantities, r5 retention, and manifest activation. The new
`tests/unit/test_fee_rule_transition_safe_rebase.py` has six passing regressions for
changed/missing Point Profile or Measurement Plan lineage, prior fingerprint mismatch,
prior row identity mismatch, and successful rebase preserving an explicitly manual
Unit Price while refreshing automatic Units.

`py_compile` passed; `npm run build` passed with the existing Vite chunk-size warning;
JSON/manifest parse passed; UTF-8 trailing whitespace scan passed; `git diff --check`
returned no whitespace errors and only the repository's existing LF/CRLF warnings.
Physical UTF-8 line counts are within the Python hard limit: persistence service 477,
transition helper 173, confirmed Matrix Fee service 499, and the new transition test
235 lines. Forbidden locked-path/no-real-data scan was clean; no real DB/file was
opened or modified.

## Developer Gate

The bounded B1/B2 fix is complete within the authorized boundary. Recommend Reviewer
implementation re-gate next; do not route QA or Integrator from this pass.
