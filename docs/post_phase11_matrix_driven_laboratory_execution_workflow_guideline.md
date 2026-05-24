# ConnLab Post-Phase-11 Matrix-Driven Laboratory Execution Workflow Guideline

> Suggested file path:
>
> `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`

## 0. Why This Document Exists

Phase 11 has completed the controlled foundation smoke flow:

```text
Matrix Authority
→ Group Selection
→ ProjectMatrixDraft
→ ConfirmedMatrix
→ TestRecordPreview smoke flow
```

The repository task board records:

```text
TASK_261 complete
TASK_262 complete
TASK_262A complete
TASK_262B complete
TASK_263 complete
TASK_264 complete
TASK_265 complete
Current Active Task: none
```

Therefore, this document is **not a Phase 11 implementation plan**.

This document is a **post-Phase-11 task planning and workflow refinement guideline** for the next product direction:

```text
Matrix-driven Laboratory Execution Phase
```

The next work should not restart Matrix Authority architecture. The next work should convert the validated smoke flow into a practical laboratory operator workflow.

---

# 1. Current Repository Baseline

## 1.1 Completed Foundation

The following chain has been validated:

```text
Import Matrix preview
→ Select execution groups
→ Persist complete SourceMatrix
→ Create selected-only ProjectMatrixDraft
→ Save/edit draft
→ Confirm active ConfirmedMatrix
→ Consume ConfirmedMatrix in Test Record preview
```

Key completed capabilities:

- Full SourceMatrix lineage is preserved.
- ProjectMatrixDraft contains selected groups only.
- ConfirmedMatrix is the downstream authority.
- Test Record preview consumes active ConfirmedMatrix only.
- Unselected groups remain in SourceMatrix but do not appear in draft, confirmed matrix, or preview.
- No fee/report/equipment/StepInstance/execution persistence scope was introduced.

## 1.2 Current Product Direction

README currently describes the next product direction as:

```text
Matrix-driven Laboratory Execution Phase
```

This is the correct naming direction.

Recommended document and task naming should avoid:

```text
phase11_workflow_refinement...
```

because Phase 11 is already complete and that name can mislead future planning.

Use names like:

```text
post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md
matrix_driven_lab_execution_workflow_guideline.md
matrix_to_test_record_workflow_refinement_plan.md
```

---

# 2. Product Identity After Phase 11

ConnLab should now be treated as:

# Matrix-driven Test Record Authoring & Execution Cockpit

It is not primarily:

- a generic workflow engine
- an MES replacement
- an AI recommendation system
- a report engine
- a permission system
- a runtime orchestration system

The practical business chain is:

```text
Source Matrix
    ↓
Group Selection
    ↓
Confirmed Matrix Authority
    ↓
Generate Test Record Draft
    ↓
Lab Execution
    ↓
Evidence / Data Upload
    ↓
Review
```

The central business object is:

```text
Test Record
```

The Matrix is the authority map that drives Test Record creation and execution navigation.

---

# 3. Real Laboratory Workflow To Preserve

The software workflow must follow the real laboratory workflow:

```text
S1. Open product specification
S2. Find Matrix table
S3. Confirm required test groups
S4. Search old Excel/Word project records
S5. Copy old record if available, otherwise copy the standard template
S6. Modify or fill steps
S7. Fill Test items, Test Method, Test conditions, Remarks
S8. Print and submit with paper application package for review
S9. Execute tests and manually fill remaining blank fields
S10. Upload test data or images
S11. Review
```

System goal:

```text
Reduce memory-based manual work.
Reduce repeated Word editing.
Reduce missing groups/steps.
Reduce wrong sample quantity.
Reduce forgotten remarks.
Reduce use of wrong old records.
```

---

# 4. Highest-Risk User Errors

Future task planning should prioritize error prevention in this order:

## 4.1 Highest Risk

```text
Missing selected group steps
```

If a required group or group step is missed, the generated Test Record is incomplete.

## 4.2 High Risk

```text
Wrong sample quantity
```

Sample quantity is group-level execution authority and must remain visible.

## 4.3 High Risk

```text
Missing remarks / requirements
```

Notes, markers, section notes, and step remarks must not disappear from the operator workflow.

## 4.4 Medium Risk

```text
Wrong product description, specification, method, condition, or old Test Record version
```

This is important, but not the first post-Phase-11 implementation priority unless it blocks Record generation.

---

# 5. Core Architecture Boundaries

## 5.1 Matrix Workspace

Matrix Workspace owns:

```text
Authority editing
```

Responsibilities:

- Import/load matrix
- Preview source matrix
- Select matrix candidate
- Select execution groups
- Create/load ProjectMatrixDraft
- Edit draft
- Save draft
- Confirm active ConfirmedMatrix
- Create and confirm lightweight revision draft

Matrix Workspace must not own:

- Test Record authoring UI
- Record export
- fee evaluation
- report generation
- runtime evidence collection
- structured measurement persistence

## 5.2 Project Workbench

Project Workbench owns:

```text
Downstream execution and record workspace
```

Responsibilities:

- Consume active ConfirmedMatrix
- Show matrix table projection
- Navigate group/step execution nodes
- Generate Test Record draft
- Attach evidence/data/images in later phases
- Support review continuity in later phases

Project Workbench must not directly mutate Matrix authority.

## 5.3 ConfirmedMatrix

ConfirmedMatrix remains:

```text
Current approved authority
```

Current lifecycle policy:

- Lightweight before project execution starts.
- Can be overwritten or reconfirmed without heavy approval.
- After testing begins, every authority change must leave a traceable record.

Do not introduce heavy permissions or approval workflow in the next tasks.

---

# 6. Major UX Problem To Solve Next

The current system has validated the data chain, but the operator workflow is still mentally discontinuous.

Main discontinuities:

```text
Import preview popup
→ Group selection mode
→ Draft editor
→ Confirm actions
→ Project Workbench preview
```

User confusion points:

- If the matrix table is wrong, how does the user go back and choose another table?
- If groups were selected incorrectly, how does the user return to group selection without re-importing?
- Why are Save, Create revision draft, and Confirm revision all in the same editor area?
- After confirmation, why does Project Workbench show group cards instead of a matrix-style execution projection?
- Why does Record still feel like a smoke preview instead of a real Word Test Record output?

The next phase should solve these workflow problems, not add unrelated backend systems.

---

# 7. Matrix Workspace Post-Phase-11 Direction

## 7.1 Replace Popup Thinking With Persistent Import Session

The biggest design correction:

```text
Import preview should no longer be treated as a throwaway popup.
```

It should behave like a persistent import/session workspace.

Recommended mental model:

```text
Matrix Import Session
```

Contains:

- uploaded source document
- detected matrix candidates
- current selected matrix candidate
- preview page/table
- selected group state
- created draft link
- source lineage status

## 7.2 Recommended Matrix Workspace Flow

```text
1. Upload / Load source
2. Select matrix candidate
3. Select groups
4. Create selected-only draft
5. Edit draft
6. Confirm active authority
```

This can be implemented without changing the backend authority architecture.

## 7.3 Required Navigation Actions

From Group Selection:

```text
Back to matrix candidate selection
Change source matrix
Cancel import session
Confirm selected groups
```

From Draft Editor:

```text
Change selected groups
Change source matrix
Save draft
Confirm as active matrix
```

Important:

```text
Change selected groups
```

must not be presented as:

```text
Import Matrix
```

because the user is not importing a new file; the user is correcting the current authority configuration.

## 7.4 Warning Rules

If user changes source matrix after a draft exists:

```text
Changing the source matrix may invalidate current draft edits.
```

If user changes selected groups after editing draft:

```text
Changing selected groups may remove draft edits for unselected groups and add unedited rows for newly selected groups.
```

If user confirms authority:

```text
After confirmation, Project Workbench and Test Record generation will use this matrix.
```

---

# 8. Group Selection UX Requirements

## 8.1 Group Selection Must Be Matrix-Native

Group Selection should feel like:

```text
Selecting columns from the parsed Matrix
```

not like a detached admin list.

The current inline direction from TASK_262A is correct and should be extended carefully.

## 8.2 Selection Mode Display Rules

Show:

- source document name
- selected matrix candidate identity
- Test Item rows as context
- group columns
- group header checkboxes
- sample quantity expression per group
- selected group count
- selected step count if available
- visible blocker if zero groups selected

Hide:

- Section
- Method
- Condition
- Requirement
- draft/revision actions
- right-side edit cards
- execution actions
- Record / Report / Fee actions

## 8.3 Confirmation Summary

Before committing group selection, show a concise summary:

```text
Selected groups: G1, G3, G5
Selected group count: 3
Estimated selected steps: 42
Sample quantities: visible per selected group
```

The goal is to prevent the highest-risk error:

```text
missing required group steps
```

---

# 9. Save / Revision / Confirm UX Rules

## 9.1 Current Problem

The current actions are too easy to confuse:

```text
Save
Create revision draft
Confirm revision
```

All appear in or near Matrix Editor, and the user cannot easily tell what object is being changed.

## 9.2 Required State Banner

Matrix Workspace must always show one of these states:

### Draft Mode

```text
Editing Draft
Not active for downstream outputs
```

### Confirmed Mode

```text
Current Active Matrix Authority
Used by Project Workbench and Test Record generation
```

### Revision Draft Mode

```text
Editing Revision Draft
Changes are not active until confirmed
```

## 9.3 Button Grouping

Use two separate groups.

### Draft Actions

- Save Draft
- Discard Draft Changes
- Change Selected Groups
- Change Source Matrix

### Authority Actions

- Confirm As Active Matrix
- Create Revision Draft
- Confirm Revision

## 9.4 Action Copy

Each action must include a consequence statement.

Example:

```text
Save Draft
Save current edits only. Project Workbench will not use this draft until it is confirmed.
```

```text
Confirm As Active Matrix
Publish this matrix as the current authority. Project Workbench and Test Record generation will use it.
```

```text
Create Revision Draft
Start a new editable copy from the active matrix. Current active authority remains unchanged.
```

```text
Confirm Revision
Replace the active matrix with this revision and record the change.
```

---

# 10. Project Workbench Direction

## 10.1 Correct Product Shape

Project Workbench should evolve toward:

# Laboratory Test Cockpit

Specifically:

```text
Matrix-driven + Record-driven + Evidence-driven
```

not:

```text
generic runtime dashboard
```

## 10.2 Replace Group Card Emphasis With Matrix Table Projection

The current group-card view is useful for smoke validation but not ideal for daily operation.

Future Project Workbench should show:

```text
Matrix table projection
```

Rows:

```text
Test items / sections / step definitions
```

Columns:

```text
Selected groups
```

Cells:

```text
interactive step tokens
```

## 10.3 Each Cell Is A Clickable Step Node

Each non-empty matrix cell should render as a button/token:

```text
[1]
[2]
[3(a)]
[6#]
```

Each token represents:

```text
Group × Step
```

The token should open the right-side Step / Record workspace.

## 10.4 Cell Status Colors

Initial status color rules:

```text
Gray   = not started
Blue   = in progress
Green  = completed / pass
Red    = failed
Yellow = review required
Purple = reopened / retest
```

Important:

The first implementation may use mock/local status or derived placeholder status, but the UI contract should reserve these meanings.

Do not introduce full execution persistence unless explicitly approved later.

## 10.5 Matrix Projection Must Be Read-Only Authority

Project Workbench projection must not edit authority fields.

If the operator needs to change matrix authority:

```text
Go to Matrix Workspace
→ Create or edit draft
→ Confirm active matrix
→ Return to Workbench
```

---

# 11. Step / Record Workspace Direction

When a matrix token is clicked, the right panel should show:

```text
Record Step Workspace
```

It should be record-oriented, not runtime-engine-oriented.

Show:

- Group
- Step token
- Test item
- Section
- Test method
- Test condition
- Requirement / remarks
- Sample quantity
- Record generation status
- Evidence/data placeholders
- Review placeholders

Do not overbuild:

- StepInstance persistence
- structured LLCR forms
- report engine
- AI review
- equipment assignment

until Record generation and projection workflow are usable.

---

# 12. Test Record Generation Direction

## 12.1 Record Button Meaning

The Record button should become:

```text
Generate Test Record Draft
```

not merely:

```text
Open smoke preview
```

## 12.2 Generation Source

Generate only from:

```text
Active ConfirmedMatrix
```

Never generate from:

- SourceMatrix directly
- ProjectMatrixDraft directly
- frontend temporary state
- unconfirmed import preview

## 12.3 Template Strategy

Initial implementation:

```text
Use default Word Test Record template
```

Later implementation:

```text
Use imported historical Test Record as template
```

Do not start with a generic template engine.

## 12.4 Fields To Fill First

Initial .docx generation should focus on:

- Group Number
- Sample Quantity & Number placeholder
- Step
- Test items
- Test Method
- Test conditions
- Remarks
- Product Description if available
- Applicable Specification if available

Leave manual fields blank:

- Start Date/Time
- Complete Date/Time
- Equipment ID No.
- Tested By
- handwritten remarks
- execution data

## 12.5 Output

Output should be:

```text
Generated Word .docx
```

Save/export behavior:

- generated file is downloadable
- generated file can be saved under project folder later
- generation history may be added later

---

# 13. Lightweight Revision History

Because current lifecycle is lightweight:

```text
ConfirmedMatrix = current approved draft
```

Do not implement heavy approval.

But after testing begins, changes must be traceable.

Recommended later task:

```text
Lightweight Matrix Authority Revision History
```

Track:

- when
- changed by
- source matrix changed or not
- selected groups changed or not
- added groups
- removed groups
- added steps
- removed steps
- record regenerated or not

Avoid:

- permissions
- formal approval routing
- enterprise ECN workflow

---

# 14. Recommended Task Series After TASK_265

The following task sequence is recommended for TASK_266+.

## TASK_266 — Matrix Workspace Navigation & State Clarity

Goal:

```text
Make authority workflow navigable and understandable after TASK_265.
```

Scope:

- Rename/clarify workflow state labels
- Add current layer/state banner
- Separate Draft Actions and Authority Actions
- Add consequence copy for Save / Confirm / Revision actions
- Add explicit Change Selected Groups and Change Source Matrix entry points
- Do not change backend authority model

Acceptance:

- User can tell whether they are editing draft, confirmed authority, or revision draft.
- Save/Confirm/Revision actions are no longer visually grouped as equivalent actions.
- Group reselection is not hidden behind Import Matrix.

## TASK_267 — Persistent Matrix Import Session UX

Goal:

```text
Allow users to return from group selection or draft editing to matrix candidate preview safely.
```

Scope:

- Preserve source preview context after import
- Provide Back to matrix candidate selection
- Provide Change Source Matrix
- Warn when changing source may invalidate draft edits
- Keep existing TASK_261 commit API
- Avoid new backend lineage model unless strictly required

Acceptance:

- User can choose another detected matrix table without mentally starting over.
- User can recover from wrong matrix selection.
- Draft invalidation risk is visible.

## TASK_268 — Group Selection Completeness Guard

Goal:

```text
Reduce missing group / missing step risk.
```

Scope:

- Enhance inline selection mode
- Show selected group count
- Show selected step count if derivable
- Show sample quantities
- Add confirmation summary
- Keep Test Item context visible
- Do not turn selection mode into full editor

Acceptance:

- Operator sees what will enter the draft before commit.
- Zero-selection blocker is explicit.
- Highest-risk error, missing groups, is actively guarded.

## TASK_269 — Project Workbench Matrix Projection Prototype

Goal:

```text
Replace group-card mental model with read-only matrix table projection.
```

Scope:

- Use ConfirmedMatrix / TestRecordPreview data as source
- Render rows by test item / section
- Render columns by group
- Render cell tokens as clickable buttons
- Add placeholder status colors
- Open right-side detail panel on token click
- Do not introduce StepInstance persistence

Acceptance:

- Workbench looks like a matrix-driven cockpit.
- Operator can navigate by matrix cell.
- Projection remains read-only authority view.

## TASK_270 — Record Step Workspace Panel

Goal:

```text
Turn clicked matrix token into record-oriented step detail.
```

Scope:

- Right-side panel
- Show group, step token, item, section, method, condition, requirement, sample quantity
- Add placeholders for evidence/data/review without persistence
- Keep panel read-only with respect to authority

Acceptance:

- Matrix token opens meaningful record detail.
- User sees the information needed to prepare/fill Test Record.

## TASK_271 — Test Record Word Generation v1

Goal:

```text
Generate a real Word Test Record draft from active ConfirmedMatrix.
```

Scope:

- Use default Word template
- Fill group-level and step-level fields
- Output .docx
- No formal TestRecord aggregate yet unless proven necessary
- No report engine
- No equipment automation
- No structured execution persistence

Acceptance:

- Clicking Record generates a downloadable Word document.
- Generated document contains selected groups only.
- Group number, steps, test items, methods, conditions, and remarks are populated.
- Manual execution fields remain blank.

## TASK_272 — Lightweight Authority Change History

Goal:

```text
Record matrix authority changes after project execution starts.
```

Scope:

- Minimal history view
- Track group/step changes
- Track confirm/revision events
- No permission model
- No approval workflow

Acceptance:

- User can see when active matrix changed.
- User can understand whether record regeneration may be needed.

---

# 15. Task Planning Rules

Every new task must answer:

```text
How does this improve Matrix → Test Record continuity?
```

If the answer is unclear, the task is probably not a priority.

Every task should declare:

- Current baseline
- User workflow problem
- Scope allowed
- Scope forbidden
- UI state affected
- Backend state affected
- Acceptance criteria
- Validation commands
- Residual risks
- Model Fit Assessment

---

# 16. Anti-Goals For The Next Workstream

Do not start the following unless explicitly approved:

- LLCR runtime persistence
- StepInstance execution persistence
- report engine
- AI recommendation
- equipment recommendation
- fee engine
- large backend refactor
- permissions architecture
- multi-user approval workflow
- generic template engine
- metadata perfection
- Matrix library full implementation
- multi-Matrix append/merge implementation

Current workstream is:

```text
Post-Phase-11 workflow refinement
→ Matrix-driven Test Record generation
→ laboratory execution cockpit foundation
```

---

# 17. Naming Recommendation

Avoid:

```text
phase11_workflow_refinement_and_task_guideline_master_plan.md
```

because Phase 11 is complete.

Recommended:

```text
post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md
```

or:

```text
matrix_driven_lab_execution_task_guideline.md
```

or:

```text
matrix_to_test_record_execution_workflow_guideline.md
```

The first name is recommended because it preserves continuity while clearly stating that this is **after Phase 11**.

---

# 18. Final Direction Statement

The next ConnLab workstream should make the validated Phase 11 smoke flow usable for real laboratory operation.

Target operator experience:

```text
Open specification
→ Import/load matrix
→ Choose correct matrix table
→ Select required groups
→ Confirm active authority
→ Generate Test Record draft
→ Execute testing
→ Upload data/evidence
→ Review
```

This is the correct post-Phase-11 direction:

# Matrix → Test Record continuity system

The immediate goal is not more architecture.

The immediate goal is:

```text
Make the existing authority chain understandable, navigable, and useful for real laboratory work.
```
