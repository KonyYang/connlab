# TASK_361K Project Point Profile LLCR Fee Units Integration

## Status

Complete/accepted locally after Developer implementation, Reviewer implementation
gate, QA disposable smoke, and Integrator package isolation. Remote push was
intentionally not performed.

## Lane

`project-point-profile-llcr-fee-units-integration`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- TASK_361J is complete/accepted; no implementation lane was active when Discovery
  began.
- Current role: Integrator closeout completed after the passed QA gate.
- The user explicitly authorized this separate confirmed-consumer lane; the accepted
  package remains limited to its read-only Fee integration contract.

## Goal

Use the active confirmed Project Point Profile as the project-level default source of
LLCR readings per sample. A confirmed profile such as prefix `P` with expression
`1-4` contributes `4 readings/sample`; the Fee line then multiplies that value by the
current Confirmed Matrix group sample quantity. Preserve target-specific confirmed
Measurement Plan authority as the higher-priority Group-Step override and never count
both sources.

## Confirmed Formula

```text
LLCR readings_per_sample = active confirmed Project Point Profile points_per_sample
LLCR Units = LLCR readings_per_sample * current Confirmed Matrix group sample quantity
```

Examples:

- Point Profile `P / 1-4` -> `4 readings/sample`.
- Matrix group sample quantity `5` -> LLCR Units `20`.
- The existing LLCR price tier remains `1.5/reading` when readings/sample is `<=20`
  and `1/reading` when it is `>20`; TASK_361K does not change that rule.

Invalid or non-numeric group sample quantity remains `Confirm sample quantity` and
produces no Units/testing fee.

## Authority And Precedence Contract

Apply this precedence per LLCR Group-Row-Step identity:

1. A matched, included, usable target in the effective confirmed Measurement Plan is
   the highest-priority target-specific override. Its `readings_per_sample` is used.
2. When an independent Measurement Plan root is active, an omitted, excluded,
   impacted, unmatched, empty, needs-review, or corrupt target remains review-required.
   Project Point Profile must not bypass that existing TASK_361E safety gate.
3. When Measurement Plan status is `not_started` or explicitly `disabled`, the active
   confirmed Project Point Profile is the LLCR project default. For LLCR only, a usable
   profile must create a matched Fee quantity context directly from each parsed
   Confirmed Matrix LLCR token/line and its current group sample quantity. This path
   must not read, require, or fall back to `ConfirmedMatrixStepQuantity` or any legacy
   Matrix Step contact quantity, and absence of those records must not produce
   `Confirm Matrix Step quantity`.
4. If that profile is not started, disabled, stale, missing, or authority-corrupt,
   LLCR is review-required with no TASK_351 text, legacy Matrix Step quantity, draft,
   or arbitrary count fallback.
5. CR specified-current keeps its accepted target-specific Measurement Plan / Matrix
   Step behavior. Project Point Profile is not a CR default in this lane.
6. Non-LLCR Fee lines are unchanged.

Multiple tokens in one LLCR Fee line may receive the same profile default, but the
existing conservative equal-value check remains: the Fee calculation uses one common
readings/sample value and never sums the repeated default across Steps.

This LLCR-only construction rule does not weaken precedence. If an independent
Measurement Plan root is active, omitted, excluded, affected, unmatched, or corrupt
targets are typed review-required before profile selection. The direct profile context
is unavailable in those states. CR specified-current and all non-LLCR tokens continue
through their current context construction and may not consume this profile path.

## Confirmed Point Profile Consumer Contract

Future implementation should add a typed, read-only application adapter over the
existing Point Profile repository. It must read only the active confirmed revision and
return:

- status: `confirmed`, `not_started`, `disabled`, `stale`, or `authority_corrupt`;
- revision id, revision sequence, and persisted fingerprint;
- derived positive `readings_per_sample` from included confirmed category counts; and
- ordered category identity/prefix/expression lineage only as internal audit context.

Draft/editable revisions are never read. `disabled` is a reserved injected rollback
state, not a new Settings UI or public configuration feature. `stale` means the active
revision id/fingerprint changed during a pinned consumer read; it fails closed. Root
pointer mismatch, wrong revision state, malformed categories, fingerprint/count
inconsistency, or missing active revision is `authority_corrupt`.

The Fee field metadata source must identify `Confirmed Project Point Profile` and
include revision id/sequence/fingerprint in backend audit metadata without requiring a
frontend or API-client contract change.

## Production Composition Boundary

Every production construction of `ConfirmedMatrixFeeDraftService` that can feed Fee
preview, direct/subprocess export, required-form composition, or Matrix rebase default
promotion must receive the same typed Point Profile adapter. This prevents preview and
export/rebase paths from calculating different LLCR Units.

No confirmed pricing draft or manual operator override is silently rewritten when a
Point Profile is reconfirmed. A newly built Fee draft reads the latest confirmed
profile; saved Fee edits retain their existing explicit pricing-draft semantics.

## Future Authorized May Touch After Gates

- `backend/application/contact_point_profile_confirmed_consumer_adapter.py` (new)
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py` only for narrow internal
  authority lineage fields with backward-compatible defaults
- `backend/api/dependencies.py` only for read-only adapter composition
- `backend/infrastructure/office/fee_evaluation_export_child.py` only to compose the
  same read adapter in the child process; no workbook layout change
- `backend/application/matrix_fee_rebase_promotion_service.py` only for injected
  read-only profile composition when creating a new default Fee draft
- focused backend unit/integration tests listed in the plan
- TASK_361K task/plan/evidence and `docs/task_board.md`

## Authorized Implementation Scope

- Read-only confirmed Project Point Profile consumer adapter and lineage projection.
- LLCR-only direct profile context before legacy Step quantity lookup.
- Homogeneous selected readings/source propagation through existing Fee metadata:
  profile source includes revision sequence/id/fingerprint; existing legacy Matrix
  Step and exact confirmed Measurement Plan source values remain unchanged.
- Missing or divergent selected sources are typed review-required/no-write even when
  numeric readings agree.
- Consistent production composition for Fee preview, direct/subprocess export,
  required forms, and rebase-created defaults.
- Focused unit/integration tests using disposable SQLite and temporary roots only.

No public DTO/API shape or frontend/API-client change is authorized.

## Must Not Touch / Locked Paths

- No TASK_361I/J Point Profile schema, migration, model, parser/canonicalizer,
  repository writes, lifecycle commands, API commands, frontend editor, or summary UI.
- No Measurement Plan schema/repository/lifecycle/impact/confirmation semantic change.
- No Fee rule seed, matcher, price tier, unit price, base fee, discount, man-hour,
  manual edit, pricing draft, or Fee frontend behavior.
- No frontend runtime or `frontend/src/api/client.ts`.
- No TASK_360B/TASK_361D workbook projection/layout/artifact behavior; export-child
  composition may only ensure the existing Fee draft reads the same authority.
- No Generic Test Record, Report, StepInstance, Matrix parser/import, Matrix authority
  mutation, LTR/public drive, Office template redesign, real DB, real workbook, or
  real project/public-drive folder operation.
- No `.agents/**`, `docs/project_management/**`, release/settings cleanup, unrelated
  residual cleanup, staging, commit, or remote push in Planner/Reviewer gates.

## Acceptance Criteria

1. Confirmed profile `P / 1-4` exposes `4 readings/sample` to LLCR only.
2. With Matrix group sample quantity `5`, LLCR Units is `20`; unit price remains the
   existing `1.5/reading` tier.
3. A later confirmed profile `P / 1-6` makes a newly built LLCR draft use Units `30`.
4. An unconfirmed/draft profile never changes Fee output.
5. An exact included target-specific confirmed Measurement Plan value wins over the
   project profile and is not added to it.
6. Active-root omitted/excluded/impacted/corrupt target remains review-required and
   cannot fall back to the project profile.
7. Under Measurement Plan `not_started`/`disabled`, a usable confirmed profile builds
   LLCR Units successfully even when no `ConfirmedMatrixStepQuantity` exists; no
   `Confirm Matrix Step quantity` review reason is emitted.
8. Under Measurement Plan `not_started`/`disabled`, missing, disabled, stale, or
   corrupt Point Profile is review-required with no text/legacy/draft fallback.
9. Missing, zero, non-numeric, or otherwise invalid current Confirmed Matrix group
   sample quantity remains review-required (`Confirm sample quantity`) and produces no
   Units or write, even when the profile is usable.
10. CR specified-current and every non-LLCR Fee row are unchanged.
11. Fee field metadata identifies Point Profile revision lineage for calculated Units.
12. Preview, direct/subprocess export, required-form composition, and rebase-created
    default drafts cannot silently use different LLCR authority selection.
13. Tests use temporary SQLite only; the real project and real files remain untouched.

## Validation Gate

- Adapter tests: confirmed/not-started/disabled/stale/corrupt, draft isolation,
  fingerprint/count validation, reconfirm revision update, and read-only behavior.
- Fee unit/default-fill tests: `4 x sample quantity`, tier boundary, source metadata,
  target override precedence, no double count, `not_started` and `disabled` success
  with no legacy Step quantity, active-root omission no-profile-fallback, no fallback,
  multiple equal Step tokens, invalid sample quantity/no-write, CR and non-LLCR
  regression.
- API tests with disposable SQLite: profile confirm -> Fee GET, later local draft/no
  effect, reconfirm -> updated Units, missing/corrupt -> typed review-required.
- Composition/export/rebase tests prove all production Fee draft constructors receive
  the same adapter without changing workbook layout or saved manual edits.
- Existing TASK_351, TASK_357D, TASK_361E, TASK_361I/J, Fee export, and pricing draft
  suites pass as focused regressions.
- `py -m pytest`, `py -m py_compile`, diff/trailing/line-count/whitelist/
  forbidden-scope/no-real-mutation scans. No browser test is required for backend-only
  V1 because frontend/API response shape remains compatible.

## Merge Gate

Reviewer plan gate, explicit user approval for Developer planning-first, Developer
docs-only planning-first, Reviewer implementation-readiness, explicit implementation
approval, Developer implementation, Reviewer implementation gate, disposable API QA,
and Integrator package isolation are complete.

## Definition Of Ready

Satisfied and accepted. The formula, current sample source, authority precedence,
no-fallback policy, audit lineage, production composition points, file boundary,
tests, and exclusions were verified in the isolated package.

## Governance Gate Record

- Reviewer initial plan gate identified B1 and blocked.
- Planner B1 fix froze the LLCR-only direct context/no-legacy-Step-quantity contract.
- Reviewer plan re-gate passed and closed B1.
- User approved Developer planning-first only.
- Developer docs-only planning-first completed without product/test/DB/file changes.
- Reviewer implementation-readiness initially blocked on metadata source propagation;
  Developer completed the docs-only B1 planning fix.
- Reviewer implementation-readiness re-gate passed.
- User explicitly approved TASK_361K product implementation.
- Planner reconciliation authorizes only the bounded scope above; next legal role is
  Developer implementation.
- Developer completed the bounded implementation and focused disposable validation.
- Reviewer implementation gate passed with no product blocker.
- QA passed the disposable smoke; Integrator isolated the approved package and
  accepted the lane locally.

## Blocking Questions

None.
