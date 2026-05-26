# TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS

## Status

Complete. Implemented and validated on 2026-05-26.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current task status: `TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS` complete
- Allowed reason: `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` is complete, `docs/task_board.md` set TASK_275 as the active planned task, and user approved implementation after plan review.

## Source Inputs

Primary source:

- User smoke-test feedback on Project Workbench after TASK_274.
- User-provided reference image showing a Matrix table with bottom rows for sample size, estimated completion, and status.

Relevant project rules:

- `$impeccable` product register.
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

## Objective

Refocus Project Workbench information hierarchy so the first screen answers what lab users actually need during execution:

```text
Which groups are not started, in progress, passed, or failed?
Which failed items need attention?
Which output materials are prepared or pending?
Which Matrix steps belong to each group?
```

This is a frontend UI information-hierarchy task. It must not add backend data models, StepInstance persistence, real completion-date calculation, real fee calculation, image/evidence upload, or new output generation behavior.

## User Problems

1. Top project header repeats status that is already implied by the project number and LTR number.
2. `LTR Number Registered` badge is not useful on the Workbench first screen.
3. `Edit Matrix Definition` appears as a global top action, but Matrix editing belongs near the main Matrix surface.
4. `Refresh` is unclear and not meaningful for the user.
5. `Project readiness status` takes too much vertical space and repeats facts such as created project, LTR registered, and Matrix authority.
6. `Open Setup Manager` is unclear.
7. Workbench should instead show project setup and output-material preparation: project folder, source materials, Test Record, fee estimate, sample images, and approval package readiness.
8. Step Workspace `Matrix` action should move to the main Matrix area.
9. Step Workspace `Record` action should move to the setup/output-materials area for future Test Record workflow placement.
10. `Recent activity` is useful for investigation but should not be permanently visible on the normal first screen.
11. `Fee estimate` should show total estimated fee, not spent and remaining amounts.
12. Matrix status categories are too many. The user wants only four visible states: not started, in progress, pass, failed.
13. Matrix table currently includes `Seq` and `Section`, which add detail without helping first-screen execution scanning.
14. Group headers include sample quantity, which distracts from group identity.
15. Sample quantity should move to bottom rows under the Matrix table.
16. Estimated completion date and group status rows should be present as placeholders for future real execution data.

## Scope

In scope:

- Simplify Workbench top header:
  - remove the `LTR Number Registered` badge from the title area.
  - show project identity with `DL-*` or temporary project identifier plus product name and test description when available.
  - remove or hide unclear top actions `Refresh` and `Edit Matrix Definition`.
- Move Matrix edit/open action into the main Matrix section.
- Replace the large `Project readiness status` strip with a smaller `Project setup / Output materials` area.
- In setup/output area, keep only business-relevant preparation/output entries:
  - Project folder
  - Source materials
  - Test Record
  - Fee estimate
  - Sample images
  - Approval package
- Keep output-material actions as disabled placeholders unless already implemented.
- Move future `Record` entry to setup/output area as disabled or placeholder.
- Hide `Recent activity` from the default first-screen card layout and expose it only through an investigation/history affordance.
- Simplify `Fee estimate` to total estimated fee only.
- Simplify top/bottom metrics to group-oriented progress and failed-item attention.
- Simplify Matrix status tones to four visible categories:
  - not started
  - in progress
  - pass
  - failed
- Remove `Seq` and `Section` columns from the Matrix projection table.
- Keep only `Test item` plus group columns in the main Matrix projection table.
- Remove sample quantity from group headers.
- Add bottom Matrix rows:
  - `Sample sizes` using existing sample quantity expressions.
  - `Estimated completion date` placeholder per group.
  - `Status` placeholder per group.
- Keep estimated overall completion out of scope unless a simple non-invasive placeholder row is feasible without awkward colspan behavior.
- Update frontend tests and static guards.
- Update task and board status after implementation.

Out of scope:

- Backend/API/domain/storage changes.
- New projection DTOs.
- StepInstance or execution persistence.
- Real group progress computation beyond existing projection placeholder data.
- Real estimated completion-date calculation.
- Real project total completion-date calculation.
- Real fee calculation by test item, sample quantity, or test time.
- Real sample image upload.
- Real Test Record workflow activation.
- Real Recent Activity modal implementation if it requires new state/storage; a disabled or lightweight local placeholder is acceptable.
- Report, fee, AI, equipment, permission, approval workflow implementation.
- Full Workbench redesign outside the specific hierarchy and Matrix table cleanup.

## Expected File Changes

Likely modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.test.ts` if present or added by implementation
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS.md`

Likely no backend files should be modified.

## UI / UX Requirements

- ConnLab register: `product`.
- Physical scene: a lab engineer on an offline Windows workstation is checking daily execution progress and should see group progress and failed items faster than setup metadata.
- Matrix table should feel like an execution map, not an audit dashboard.
- Use the existing restrained ConnLab visual system.
- Do not add extra decorative cards.
- Do not show duplicate status counts in top and bottom regions.
- Do not show future features as active actions.
- Do not make users interpret implementation terms such as projection DTO, authority history, or backend status.

## Behavioral Requirements

### Header

- Show the project identifier and product/test description compactly.
- Remove `LTR Number Registered` from the header.
- Remove top-level `Refresh`.
- Remove top-level `Edit Matrix Definition`; place Matrix editing/opening near the Matrix section.

### Setup / Output Materials

- Replace readiness status cards with a smaller output-materials section.
- Do not display created project or LTR registered as separate cards.
- Do not display Matrix Authority as a readiness card.
- Include Test Record and fee estimate as output/preparation concepts without activating future workflow.

### Matrix Projection

- Render columns:

```text
Test item | Group 1 | Group 2 | ...
```

- Do not render `Seq`.
- Do not render `Section`.
- Do not show sample quantity in group headers.
- Show only four status categories in the legend and token styling:

```text
Not started
In progress
Pass
Failed
```

- Map existing review/retest tones into one of the four visible categories, preferably `in progress` unless the existing token is failed.
- Add bottom rows:

```text
Sample sizes | <existing sample quantity per group>
Estimated completion date | <placeholder per group>
Status | <placeholder per group>
```

### Bottom Area

- Hide or remove default `Recent activity` card from the always-visible bottom layout.
- Keep a lightweight history/activity entry only as a secondary affordance.
- Simplify fee area to total estimated fee only.
- Fee total in this task must use placeholder wording, not a hard-coded numeric estimate value.
- Remove spent and remaining values.

## Acceptance Criteria

- Header no longer displays `LTR Number Registered` as a badge.
- Header does not show unclear `Refresh` or global `Edit Matrix Definition` buttons.
- Matrix action is available near the main Matrix section.
- Readiness strip no longer shows `Created project`, `LTR Number registered`, or `Matrix Authority` cards.
- Workbench contains a smaller setup/output-materials area with Project folder, Source materials, Test Record, Fee estimate, Sample images, and Approval package entries.
- Step Workspace no longer contains `Matrix` and `Record` controls.
- Recent activity is not shown as a persistent large bottom card.
- Fee estimate displays total estimated fee only.
- Fee estimate does not present a hard-coded numeric total in this task scope.
- Matrix table does not render `Seq` or `Section` columns.
- Matrix group headers do not show sample quantity.
- Matrix table includes `Sample sizes`, `Estimated completion date`, and `Status` bottom rows.
- Matrix legend and visible token states are limited to four categories: Not started, In progress, Pass, Failed.
- No backend/API/domain/storage changes are introduced.
- No StepInstance, execution persistence, evidence upload, report, fee-calculation, AI, equipment, permission, or approval scope is introduced.
- Relevant frontend tests, static guards, and build pass.

## Validation Plan

Required commands after implementation:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task275 or task274 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Manual browser smoke validation:

```text
Open Workbench.
Confirm header is compact and does not show LTR Number Registered badge.
Confirm Refresh and top Edit Matrix Definition are gone.
Confirm setup/output area is smaller and output-material focused.
Confirm Matrix action sits near Matrix projection.
Confirm Matrix table has no Seq or Section columns.
Confirm group headers do not show sample quantities.
Confirm bottom Matrix rows show Sample sizes, Estimated completion date, and Status.
Confirm status legend has only Not started, In progress, Pass, Failed.
Confirm Recent activity is not a persistent bottom card.
Confirm Fee estimate shows total only.
```

## Risks

- Removing top controls may make Matrix editing harder to discover unless the Matrix section gets a clear local action.
- Hiding Recent Activity reduces passive traceability; keep a clear secondary affordance for investigation.
- Status simplification may hide review/retest nuance. This is acceptable for first-screen clarity, but detailed states can return later inside Step Workspace.
- Bottom Matrix rows add height; implementation must keep the table scannable.
- Placeholder completion and status rows must be clearly non-final so users do not mistake them for real calculated data.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a scoped frontend information-architecture refocus using existing React components, selectors, CSS, and tests. The task requires careful UI hierarchy judgment, conservative removal/hiding of redundant elements, and clear static guards, but does not require new backend architecture or data-model design.
