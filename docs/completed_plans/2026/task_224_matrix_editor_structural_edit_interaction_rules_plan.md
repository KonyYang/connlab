# TASK_224 Matrix Editor Structural Edit Interaction Rules Plan

## Purpose

Define how Matrix Editor should expose structural editing for test item rows and group columns while protecting the fixed Matrix frame.

This is a design and implementation-boundary plan only. It does not authorize coding.

## Current Governance

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: none. `TASK_223` Matrix Editor grid local fix is complete.

Allowed now because the user requested the next controlled Matrix Editor interaction design task, and the requested work is frontend design only with no backend/API/domain changes.

## Recommended Interaction Model

Use a combined interaction model:

- Row action rail for row actions.
- Group header dropdown for group-column actions.
- Top toolbar for global append and undo.
- Contextual action bar for selected row/group actions.
- Right-click menu later as an optional accelerator, not MVP primary.

This gives discoverability for non-programmer lab operators while preserving efficient table workflows for repeated edits.

## Analysis By Candidate Trigger

### A. Right-click menu

Recommendation: not primary for MVP.

Use it later as an accelerator that mirrors visible commands.

Pros:

- Familiar to many Windows users.
- Efficient for experienced spreadsheet users.
- Keeps visible UI quieter.

Cons:

- Low discoverability.
- Higher training cost.
- Browser context-menu conflicts are possible.
- Less reliable for accessibility and touchpad use.
- Dangerous if destructive commands are hidden but available.

### B. Row hover action area

Recommendation: primary for row operations.

Use a narrow row-control rail outside the data columns. Show actions on hover or selection.

Pros:

- Spatially tied to the affected row.
- Easy to discover after one hover.
- Avoids putting row buttons inside every editable cell.
- Does not compromise fixed first five data columns.

Risk:

- Hover-only affordance can be missed.

Mitigation:

- Also show selected-row actions in contextual action bar.

### C. Group header dropdown

Recommendation: primary for group column operations.

Group structure belongs to the group header, not body cells.

Pros:

- Strong mapping between command and target column.
- Keeps fixed columns clearly protected.
- Scales with many groups.

Risk:

- Small dropdown targets can be hard to use.

Mitigation:

- Use a visible compact trigger in group headers and mirror actions in contextual action bar after group selection.

### D. Top toolbar buttons

Recommendation: limited global role.

Use toolbar for `Add test item`, `Add group`, and `Undo`.

Pros:

- Highly discoverable.
- Good for append operations without selection.
- Good location for recovery.

Cons:

- Poor for target-specific actions like move left/right or insert around current row.
- Can become a generic command dump.

### E. Contextual action bar

Recommendation: secondary primary layer.

Use it after row or group selection to show target-specific commands with labels.

Pros:

- Discoverable and explicit.
- Reduces right-click dependency.
- Explains protected areas and disabled actions.

Cons:

- Requires clear selection state.

Mitigation:

- Keep selection states simple: cell, row, group.

### F. Combined approach

Recommendation: use combined approach.

Reason:

- Matrix Editor is a controlled enterprise table, not a pure spreadsheet.
- Operators need visible controls for confidence and low training cost.
- Experienced users can later gain right-click and keyboard accelerators without changing the core model.

## Fixed Area Protection

Header row is protected:

- no move
- no copy
- no delete
- no insert before

First five columns are protected structurally:

- no move
- no copy
- no delete
- no insert before
- cell content remains editable

Minimum structure:

- at least one content row
- at least one group column

## Visual Hint Strategy

Use operational cues only, not decorative polish.

Header row:

- sticky header
- stronger header state
- no action menu
- optional lock indicator in row-control rail header

Fixed first five columns:

- no column dropdown
- subtle divider after `Requirement`
- protected-state tooltip or contextual message

Editable cells:

- normal edit focus indicator
- no structural command icons inside the cells

## Forbidden Operation Handling

Use two layers:

- UI affordance layer: hide impossible commands, disable contextually invalid commands.
- Command guard layer: block every invalid structural mutation even if triggered programmatically.

Guard result shape for implementation:

```ts
type MatrixCommandGuardResult = {
  allowed: boolean;
  reason?: string;
};
```

Reason examples:

- `Header row is fixed`
- `Definition columns are fixed`
- `At least one test item row is required`
- `At least one group column is required`
- `Cannot insert before fixed definition columns`

## MVP Minimal Implementation

MVP should implement:

- row-control rail for body rows
- group header dropdown for group columns
- toolbar `Add test item`
- toolbar `Add group`
- toolbar `Undo`
- single row selection and single group selection
- command guard helpers
- disabled reasons
- one-step or short-stack local undo

MVP should not implement:

- backend persistence
- API contract changes
- matrix domain model changes
- multi-select
- drag reorder
- right-click menu
- keyboard shortcuts
- audit trail
- StepInstance or execution persistence

## Undo Decision

Undo is recommended in MVP as lightweight local undo for structural commands.

Scope:

- add row
- duplicate row
- delete row
- move row
- add group
- duplicate group
- delete group
- move group
- insert row/group

Do not implement server history or audit trail in MVP.

## Model Fit

`GPT-5.3-codex` with `medium` reasoning is suitable.

The future implementation is a bounded frontend interaction slice: local state, command guards, selection UI, and CSS. It does not require backend/API/domain changes.

## Review Questions

Before implementation approval, confirm:

- Should MVP include one-step undo or a short undo stack?
- Should row action rail be always visible or hover/selection visible?
- Should right-click be deferred entirely, or included as a mirrored optional accelerator?
