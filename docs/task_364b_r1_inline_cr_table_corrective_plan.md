# TASK_364B R1 Inline CR Table Corrective Implementation Plan

Status: `complete / Integrator accepted`

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:test-driven-development` to implement this plan step-by-step. ConnLab
> task scope forbids subagent dispatch, staging, commits, or push for this corrective
> unless the user separately authorizes them.

**Goal:** Replace the separate CR coverage section with one compact row-level CR
checkbox column while preserving the accepted project-level Point Profile authority.

**Architecture:** This is a frontend-only corrective. The editor owns row checkbox
presentation, selectors derive `follow_llcr` when every row is selected and `custom`
when any row is excluded, and the existing hook serializes the unchanged API command.
Backend schema, persistence, fingerprinting, API DTOs, and confirmed summary remain
unchanged by R1. TASK_364C accepted that authority/API baseline at `b34f2c2c`; R1 may
proceed only after its client-plus-consumer package boundary passes Reviewer re-gate.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, feature-scoped CSS.

## Global Constraints

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Task: `TASK_364B_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_AND_UI`, corrective R1.
- Preserve project-wide whole-category CR authority and atomic Point Profile Confirm.
- Do not hard-code HP, LP, Signal, or any category-name policy.
- Do not touch backend, API contracts, Matrix-group totals, Measurement Plan target
  authority, Fee, workbooks, Generic outputs, Office, real DB/files, release, or
  dependencies.
- Do not stage, commit, push, or activate another task.

---

## 1. Discovery Gate

### Confirmed By User

- The separate CR coverage section consumes too much vertical space and is difficult
  to understand.
- CR selection belongs directly on each point-category row.
- The table displays `Point category`, `Range`, and `CR`; it does not display an LLCR
  checkbox column.
- The existing top `LLCR` heading and points-per-sample summary remain.
- Every newly added category starts with CR selected.
- When every row is selected, the command is normalized to `follow_llcr`; cancelling
  any row changes the command to `custom`.

### Confirmed By Repository Evidence

- `ProjectPointProfileEditor.tsx` currently duplicates category information in a
  second `CR coverage` section.
- `useProjectPointProfileModel.ts` currently stores a separate coverage-mode state and
  exposes `Customize CR` / `Use same as LLCR` actions.
- `ProjectPointProfileDraftCategory.cr_selected` already travels on the same row and
  the existing Confirm command already accepts `follow_llcr` or `custom`.
- Backend follow mode rejects active `cr_selected` flags; the existing serializer
  already sends all row flags as false when the derived mode is `follow_llcr`.
- Confirmed summary already renders the server-returned mode and needs no R1 change.

### Planner Decision

Use one derived mode with no hidden UI state:

```ts
export function projectPointProfileCrCoverageMode(
  rows: ProjectPointProfileDraftCategory[],
): ProjectPointProfileCrCoverageMode {
  return rows.length > 0 && rows.every((row) => Boolean(row.cr_selected))
    ? "follow_llcr"
    : "custom";
}
```

All selected has one visible and persisted meaning: follow LLCR. Any proper subset has
one visible and persisted meaning: custom. Zero selected remains invalid under the
candidate backend contract that TASK_364C must review and establish as an accepted
baseline.

## 2. Scope And File Map

### May Touch

- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
- `frontend/src/contact-measurement-plan.css`
- TASK_364B task/plan/Planner/Developer evidence and minimal `docs/task_board.md` state

### Locked

- All backend/storage/application/API Point Profile files
- `frontend/src/api/client.ts`
- `ContactMeasurementPlanSummaryCard.tsx` and its API semantics
- Matrix group/sample authority, Measurement Plan target authority, Fee, workbooks,
  Generic outputs, parser/import, LTR/public drive, Office, release/dist, dependencies
- TASK_363B history, unrelated worktree residuals, `.agents/**`,
  `docs/project_management/**`, real DB/files/folders, staging, commit, push

## 3. Interaction And Command Contract

The rendered columns are:

| Point category | Range | CR | Action |
|---|---|---|---|
| editable prefix | editable expression | checkbox | delete |

The action header continues to contain `Add row`. The separate `CR coverage` heading,
summary, checklist, `Customize CR`, and `Use same as LLCR` controls are removed.

State rules:

1. Hydrated follow revision: every row checked.
2. Hydrated custom revision: only `selected_category_ids` checked.
3. Add row: new row checked, regardless of current derived mode.
4. Delete row: mode is re-derived from remaining row flags.
5. Uncheck any row: derived mode is `custom`.
6. Recheck all rows: derived mode is `follow_llcr`.
7. Uncheck every row: validation blocks Confirm with the existing non-empty message.
8. Confirm in follow mode sends `cr_coverage_mode: "follow_llcr"` and false row flags,
   satisfying the accepted backend validation.
9. Confirm in custom mode sends `cr_coverage_mode: "custom"` and the visible row flags.

## 4. TDD Implementation Tasks

### Task 1: Derive Mode From Row Selection

**Files:**

- Modify: `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
- Modify: `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`

**Interfaces:**

- Produces:
  `projectPointProfileCrCoverageMode(rows) -> "follow_llcr" | "custom"`
- Changes: `emptyProjectPointProfileCategory()` returns `cr_selected: true`

- [ ] **Step 1: Add failing selector tests**

```ts
expect(emptyProjectPointProfileCategory().cr_selected).toBe(true);
expect(projectPointProfileCrCoverageMode(allSelectedRows)).toBe("follow_llcr");
expect(projectPointProfileCrCoverageMode(partialRows)).toBe("custom");
```

- [ ] **Step 2: Run the selector test in RED**

Run:

```text
npm test -- projectPointProfileSelectors.test.ts
```

Expected: fail because the empty row is currently unselected and the derived-mode
selector does not exist.

- [ ] **Step 3: Implement the exact pure selector and checked default**

Use the `projectPointProfileCrCoverageMode` implementation frozen in Section 1 and
change the empty row literal to:

```ts
return { category_id: null, prefix: "", point_expression: "", cr_selected: true };
```

- [ ] **Step 4: Run the selector test in GREEN**

Expected: focused selector file passes with zero failures.

### Task 2: Remove Hidden Mode State And Serialize The Derived Mode

**Files:**

- Modify: `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
- Modify: `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`

**Interfaces:**

- Consumes: `projectPointProfileCrCoverageMode(rows)`
- Preserves: existing `confirmProjectPointProfile(projectId, command)` API signature
- Removes from returned model: `customizeCr`, `useSameAsLlcr`
- Preserves: `setCrSelected(index, selected)`

- [ ] **Step 1: Add failing model tests**

Cover these exact assertions:

```ts
expect(result.current.rows.at(-1)?.cr_selected).toBe(true);
expect(result.current.crCoverageMode).toBe("follow_llcr");
act(() => result.current.setCrSelected(1, false));
expect(result.current.crCoverageMode).toBe("custom");
act(() => result.current.setCrSelected(1, true));
expect(result.current.crCoverageMode).toBe("follow_llcr");
```

Confirm tests must also assert that all-selected sends follow mode with all
`cr_selected: false`, while a proper subset sends custom mode with visible booleans.

- [ ] **Step 2: Run the model test in RED**

Run:

```text
npm test -- useProjectPointProfileModel.test.tsx
```

Expected: fail on the current explicit-mode state and unselected added row.

- [ ] **Step 3: Implement derived mode with minimal state removal**

Remove `useState<ProjectPointProfileCrCoverageMode>`, `setCrCoverageMode`,
`customizeCr`, and `useSameAsLlcr`. Derive the value from `rows`:

```ts
const crCoverageMode = useMemo(
  () => projectPointProfileCrCoverageMode(rows),
  [rows],
);
```

Hydration continues to mark row flags from the server's effective selected ids. The
existing Confirm mapping remains:

```ts
cr_selected: crCoverageMode === "custom" && Boolean(row.cr_selected)
```

- [ ] **Step 4: Run the model test in GREEN**

Expected: focused hook file passes with zero failures.

### Task 3: Move CR Checkboxes Into The Main Table

**Files:**

- Modify: `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
- Modify: `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`

**Interfaces:**

- Consumes: `model.rows[index].cr_selected`
- Calls: `model.setCrSelected(index, checked)`
- Keeps: `model.addCategory`, `model.removeCategory`, `model.confirm`

- [ ] **Step 1: Add failing component tests**

Assert:

- the column headers are `Point category`, `Range`, and `CR`;
- no `LLCR` column header exists;
- one accessible CR checkbox renders per row;
- toggling the Signal checkbox calls `setCrSelected(2, false)`;
- `CR coverage`, `Customize CR`, and `Use same as LLCR` are absent;
- the top heading `LLCR` and points/sample summary remain.

- [ ] **Step 2: Run the component test in RED**

Run:

```text
npm test -- ProjectPointProfileEditor.test.tsx
```

Expected: fail because the current component renders the separate CR section.

- [ ] **Step 3: Implement the compact table markup**

Use one checkbox cell in each existing row:

```tsx
<td className="project-point-profile-cr-cell">
  <input
    type="checkbox"
    aria-label={`Include ${row.prefix || `row ${index + 1}`} in CR`}
    checked={Boolean(row.cr_selected)}
    disabled={model.busy}
    onChange={(event) => model.setCrSelected(index, event.target.checked)}
  />
</td>
```

Remove the complete `section.project-point-profile-cr` subtree. Keep the existing
top header and footer actions.

- [ ] **Step 4: Run the component test in GREEN**

Expected: focused component file passes with zero failures.

### Task 4: Compact Responsive Styling And Regression

**Files:**

- Modify: `frontend/src/contact-measurement-plan.css`
- Read/run only: remaining Contact Measurement Plan and Matrix workspace tests

- [ ] **Step 1: Remove obsolete CR-section rules**

Delete only `.project-point-profile-cr*` selectors. Add a narrow centered CR column
and reuse the existing focus-visible checkbox vocabulary. Preserve the 600px editor
cap, textarea widths, delete button, and footer.

- [ ] **Step 2: Run the focused frontend regression**

Run:

```text
npm test -- src/features/contact-measurement-plan MatrixEditorWorkspace.test.tsx
```

Expected: all selected files pass with zero failures.

- [ ] **Step 3: Build the frontend**

Run:

```text
npm run build
```

Expected: TypeScript/Vite build exits `0`; the existing chunk-size advisory may remain.

- [ ] **Step 4: Run disposable browser smoke**

Verify desktop and `514x831`:

- top LLCR heading remains;
- columns are Point category / Range / CR / action only;
- no separate CR coverage section is present;
- an added row starts checked;
- unchecking any row produces a custom command state;
- rechecking all rows produces follow state;
- zero checked disables Confirm;
- no horizontal overflow, overlap, inaccessible checkbox, or console error.

Do not press Confirm against operator authority during visual-only smoke.

## 5. Validation And Review Gate

- Focused selector, hook, and editor RED/GREEN evidence.
- Contact Measurement Plan plus Matrix workspace frontend regression.
- `npm run build`.
- Scoped `git diff --check`, UTF-8/trailing-whitespace and line-count checks.
- Production scan: no hard-coded category names, no backend/API/summary changes, no
  obsolete `Customize CR` / `Use same as LLCR` / `.project-point-profile-cr` surface.
- Desktop and 514px disposable browser evidence.
- `docs/project_management/TASK_REVIEW_CHECKLIST.md` self-review.

Stop after TASK_364B R1. Reviewer/QA and user acceptance were separate gates and are
complete. Integrator found the accepted-baseline gap; the next role is Reviewer for
TASK_364C package-boundary gate. No automatic downstream product task or push is
authorized.

## 6. Approval Gate

Historical implementation approval was recorded on 2026-07-18 with
`批准 TASK_364B R1 实施`. Developer TDD, focused Reviewer/QA, and explicit user
acceptance are complete; current status is Integrator blocked pending TASK_364C.

Approval received:

```text
批准 TASK_364B R1 实施
```

## 7. Local Completion Evidence

- RED/GREEN completed for selector default/derived mode, hook command serialization,
  and the editor's inline CR column.
- Contact Measurement Plan plus Matrix workspace regression passed: `12` files,
  `91` tests.
- `npm run build` passed; the pre-existing Vite chunk-size advisory remains.
- Browser smoke confirmed the visible `Point category / Range / CR` table, no
  separate CR section, checked-by-default added row, zero-selection blocking, and
  restored all-selected state without pressing Confirm.
- The browser document width remained within the effective `723px` in-app viewport.
  The requested `514px` viewport override was not honored by the current in-app
  browser backend and remains a focused Reviewer/QA recheck.
- The console retained one Fast Refresh hook-signature error from changing the hook
  shape during HMR (`useState` removed before `useCallback`). Source inspection,
  fresh component/hook tests, build, and subsequent interaction found no conditional
  hook defect. Reviewer/QA must repeat the console check from a fresh page session.
- No backend, API contract, client DTO, confirmed summary, Matrix-group total, Fee,
  workbook, or other downstream consumer was changed by R1.
