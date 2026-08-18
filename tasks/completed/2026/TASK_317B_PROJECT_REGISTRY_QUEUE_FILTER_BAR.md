# TASK_317B_PROJECT_REGISTRY_QUEUE_FILTER_BAR

Status: Implemented. TASK_317B scope is complete. Post-completion semantic correction applied: the generic attention queue was replaced by business-specific registry queues.

Post-completion UI correction: the separate `Showing: <Queue> Projects` text line was removed. The current queue is indicated by the selected queue button state only.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION` complete. `TASK_317B` is an interleaved UI task inserted before the planned `TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR`.

Allowed reason: The Projects overview page needs a compact Queue Filter Bar before TASK_318 adds more project-folder detail elsewhere. TASK_317B is a frontend-only UI refinement that does not consume or rename TASK_318. TASK_318 remains reserved.

Executable plan:

- `docs/task_317b_project_registry_queue_filter_bar_plan.md`

## Goal

Replace the large top summary cards on the `/projects` page with a compact **Queue Filter Bar** integrated into the Project Registry table header, so operators can quickly find projects by queue category without scrolling past dashboard cards.

## User Story

As a lab operator, I want to see how many projects are in each major queue and filter the registry table with one click, so I can find the correct project quickly without navigating a detailed workflow page.

## Business Context

The Projects page is a high-level **Project Registry entry page**, not a detailed workflow page. Each row's **Open** button enters the project Workbench, where Matrix, Project Folder, Execution, Test Record, Fee Evaluation, and material details belong.

The Projects page should help users:

1. find the correct project quickly,
2. understand which project queue they are viewing from the selected queue button,
3. see how many projects are in each major queue,
4. open the correct project Workbench.

## Current Problem

The page currently shows 5 large summary metric cards (Total projects, In progress, Pending review, Completed, Draft) above the registry table. These cards:

- occupy substantial vertical space (~104px per card × 5 = ~520px + gap),
- push the actual registry table below the fold,
- duplicate information that a compact queue filter can provide inline,
- are styled as dashboard cards rather than table filters.

## Scope

**Frontend-only** change to `ProjectListPage.tsx` and `project-dashboard.css`:

1. Remove the 5 large summary metric cards (`project-metric-grid` / `buildMetrics`).
2. Add a compact **QueueFilterBar** component above the search/filter toolbar.
3. Implement queue classification logic based on existing `ProjectRegistryRow` fields.
4. Compose queue filter with existing search and `showCancelled` toggle.
5. Use active queue button styling to show the current queue.
6. Add CSS for the Queue Filter Bar and active queue styling.

**No backend changes.** Queue classification is frontend-only using existing DTO fields.

## Non-Goals

- Do NOT add new backend API endpoints or DTO fields.
- Do NOT move Matrix, Fee Evaluation, Test Record, Execution, or detailed Workbench actions into the Projects page.
- Do NOT change the row-level **Open** button behavior.
- Do NOT remove or change the existing `showCancelled` toggle, search, Filter/Columns buttons, pagination, or refresh.
- Do NOT modify `App.tsx` routing.
- Do NOT consume or rename TASK_318.

## Proposed Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Projects                                                   │
│  Laboratory project registry                                │
│                                          [New Project]       │
├─────────────────────────────────────────────────────────────┤
│  Project Registry                                           │
│                                                             │
│  [All 15]  [Planning 4]  [Matrix Needed 6]                   │
│  [Ready to Test 0]  [Folder Blocked 0]  [Completed 1]        │
│                                                             │
│  ┌─ Search LTR, sample, test item... ───── [☐ Show cancelled]│
│  │                                      [Filter] [Columns]  │
│  │                                      [☰] [⊞] [↻] [New]   │
│  └──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐
│  │ LTR Number │ Sample Desc │ Test Item │ Status │ Progress │
│  │  ...                                                      │
│  └──────────────────────────────────────────────────────────┘
│  Showing 1-20 of 15 projects          Page 1 / 1  [Prev] [Next]
└─────────────────────────────────────────────────────────────┘
```

## Queue Filter Behavior

### Queue Items

| Queue | Source | Count Basis |
|-------|--------|-------------|
| **All** | All scoped rows | `scopedRows.length` |
| **Planning** | Identity-based | Temporary projects without formal registered LTR/DL |
| **Matrix Needed** | Conservative registered-project classification | Registered projects without active Matrix fields in the current DTO |
| **Ready to Test** | Matrix readiness | Requires future explicit active Matrix/readiness field |
| **Folder Blocked** | Folder readiness | Requires future explicit folder/package readiness field |
| **Completed** | Status-based | See classification table |

### Queue Classification (Conservative, Frontend-Only)

Final user-facing queue set:

```text
All / Planning / Matrix Needed / Ready to Test / Folder Blocked / Completed
```

Based on the current `ProjectRegistryRow.status` and `ltr_number` fields. The current DTO does not expose active Matrix or formal Project Folder readiness fields, so TASK_317B must not fake Ready to Test or Folder Blocked precision from generic status labels.

| Status Value | Queue |
|-------------|-------|
| no LTR/DL number | Planning |
| registered LTR/DL, non-completed, no active Matrix field available | Matrix Needed |
| active Matrix field available in a future DTO | Ready to Test |
| formal folder/readiness blocker field available in a future DTO | Folder Blocked |
| `folder_created` | Completed |
| `closed` | Completed |
| `cancelled` | (filtered by showCancelled) |

No-LTR temporary planning projects are valid planning records. They belong to **Planning** by default. They must not enter **Matrix Needed** or **Folder Blocked** solely because the LTR number is missing.

**Data limitation:**
The current registry DTO does not expose active Matrix or formal folder readiness fields. `Ready to Test` and `Folder Blocked` are rendered as stable business queues, but remain conservative until future DTO fields are added. Future fields may include `display_project_id_kind`, `has_registered_ltr`, `has_active_matrix`, `matrix_readiness`, `testing_readiness`, `folder_readiness`, `primary_blocker`, and `next_action`.

### Filtering Rules

1. **One active queue at a time.** Clicking a queue item sets it as active.
2. **Default active queue is All.**
3. **Queue filter composes with search**: if active queue is "Folder Blocked" (count 0) and user searches "DL-2026", the table shows only Folder Blocked projects matching "DL-2026".
4. **Queue filter composes with showCancelled**: counts and filtering respect the current `showCancelled` toggle state.
5. **Queue counts update** when `showCancelled` toggles.
6. **Clicking All** restores the full scoped registry list.
7. **Active queue styling**: selected item has stronger border/background/font-weight (`view-toggle-active` style or similar).
8. **Queue count of 0**: still clickable and shows the selected button state with "No projects in this queue" empty state.

### Active Queue Display

The active queue is shown only through the selected queue button state. Do not render a separate `Showing: <Queue> Projects` line between the Queue Filter Bar and the search toolbar.

## Component Structure

```
ProjectListPage
├── PageHeader (existing: "Projects" + "Laboratory project registry" + New Project button)
└── ProjectRegistryPanel
    ├── LTR apply result banner (existing, conditional)
    ├── QueueFilterBar          ← NEW
    │   ├── QueueButton "All"
    │   ├── QueueButton "Planning"
    │   ├── QueueButton "Matrix Needed"
    │   ├── QueueButton "Ready to Test"
    │   ├── QueueButton "Folder Blocked"
    │   └── QueueButton "Completed"
    ├── RegistryToolbar (existing: search, showCancelled, Filter, Columns, view toggle, refresh, New Project)
    ├── Empty/Loading/Error states (existing)
    ├── ProjectRegistryTable (existing: table + pagination)
    └── RegistryFooter (existing)
```

## Data Classification Assumptions

1. **Frontend-only classification**: Queues are derived from fields already returned by `GET /api/projects/registry`. No new backend logic.

2. **No LTR/DL → Planning**: Temporary planning projects are valid early planning records, not invalid projects.

3. **Registered LTR/DL without active Matrix fields → Matrix Needed**: With the current DTO, registered non-completed projects cannot prove active Matrix authority in the registry view, so the safest primary queue is Matrix Needed.

4. **Ready to Test requires explicit active Matrix/readiness signal**: The queue exists now, but TASK_317B does not infer it from generic status labels.

5. **Folder Blocked requires explicit formal preparation blocker signal**: Without backend fields for official folder, submitted material, Section 2, Fee form, or formal preparation blockers, the count is 0 with documentation.

6. **Cancelled projects**: Continue to be filtered by the existing `showCancelled` toggle, not by queue.

7. **TASK_317C boundary**: TASK_317C remains responsible for Temporary Planning Project identity, temporary display ID, registered/temporary display distinction, and Workbench temporary planning copy. TASK_317B owns only the Projects overview Queue Filter Bar labels, ordering, counts, filtering behavior, and classification semantics.

## Implementation Plan

### Files to Modify

| File | Change |
|------|--------|
| `frontend/src/pages/ProjectListPage.tsx` | Remove metric cards; add QueueFilterBar, queue state, classification logic; compose queue filter with search/scopedRows |
| `frontend/src/project-dashboard.css` | Remove metric card styles; add QueueFilterBar, queue button, and active queue styles |

### Files to Create

None. TASK_317B is a modification of the existing page only.

### Detailed Changes

#### ProjectListPage.tsx

1. **Remove**: `buildMetrics()` function and the `metrics` useMemo.
2. **Remove**: The `<div className="project-metric-grid">...</div>` JSX block (lines 79-92).
3. **Add** `QueueName` type:
   ```ts
   type QueueName = "all" | "planning" | "matrix_needed" | "ready_to_test" | "folder_blocked" | "completed";
   ```
4. **Add** `activeQueue` state: `const [activeQueue, setActiveQueue] = useState<QueueName>("all");`
5. **Add** `queueCounts` useMemo: derives counts from `scopedRows` using classification function.
6. **Add** `classifyQueue(row: RegistryRow): QueueName` function (conservative status-based mapping).
7. **Add** `queueFilteredRows` useMemo: applies active queue filter on top of existing scoped search.
8. **Replace** `filteredRows` in pagination/table with `queueFilteredRows`.
9. **Add** `queueLabel(queue: QueueName): string` helper for display text.
10. **Add** JSX: QueueFilterBar with 6 queue buttons, each showing `<QueueLabel> <Count>`.
11. **Do not add** a separate active queue text line; the selected queue button is the active-state indicator.
12. **Reset pagination** to page 1 when `activeQueue` changes (add to existing useEffect).

#### project-dashboard.css

1. **Remove**: `.project-metric-grid`, `.project-metric-card`, `.metric-icon`, `.metric-icon-total`, `.metric-icon-progress`, `.metric-icon-review`, `.metric-icon-completed`, `.metric-icon-draft`, and related responsive rules.
2. **Add**: `.queue-filter-bar` (flex container, gap, margin-bottom).
3. **Add**: `.queue-filter-button` (inline-flex, badge-like, border, border-radius, padding, cursor, font-weight).
4. **Add**: `.queue-filter-button-active` (stronger border-color, background highlight, font-weight 800).
5. **Add**: `.queue-filter-count` (slightly muted, smaller font).
6. **Do not add**: `.active-queue-label`; no separate active queue text line is displayed.

## Acceptance Criteria

- [ ] Large top summary cards (`project-metric-grid`) are removed.
- [ ] Queue Filter Bar appears between the LTR banner and the search toolbar, inside `project-register-panel`.
- [ ] Queue items are: All, Planning, Matrix Needed, Ready to Test, Folder Blocked, Completed.
- [ ] Each queue item shows a count.
- [ ] Clicking a queue filters the table.
- [ ] Active queue has clear selected styling.
- [ ] Search composes with active queue (both filters apply simultaneously).
- [ ] showCancelled toggle composes with active queue (counts and rows update).
- [ ] Existing Filter, Columns, cancelled visibility, pagination, refresh, and Open behavior are preserved.
- [ ] Projects page remains a high-level registry and does not expose Matrix/Fee/Test Record/Execution workflow actions.
- [ ] UI is more compact than the current card-based design (more table rows visible above the fold).
- [ ] Need Action and Needs Attention are not visible queue labels.
- [ ] Package Blocked is not visible; user-facing label is Folder Blocked.
- [ ] Folder Blocked shows count 0 with documented limitation while no folder readiness fields exist in DTO.
- [ ] Temporary planning projects are classified as Planning.
- [ ] Temporary planning projects are not treated as Matrix Needed or Folder Blocked solely because they lack LTR.
- [ ] TASK_317C remains focused on temporary planning identity and copy, not TASK_317B queue wording.
- [ ] `frontend; npm run build` passes.
- [ ] `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_registry or task303"` passes.

## Manual Smoke Checklist

1. Open `/projects`.
2. Confirm large summary cards are no longer occupying the top area.
3. Confirm Queue Filter Bar is visible inside the Project Registry panel.
4. Confirm **All** is selected by default with count matching total scoped rows.
5. Click **Planning** and verify no-LTR temporary projects show there.
6. Click **Matrix Needed** and verify registered projects without active Matrix fields show there.
7. Click **Ready to Test** and verify active-Matrix projects show there when future DTO data allows.
8. Click **Folder Blocked** and verify table shows empty state until folder readiness fields are available.
9. Click **Completed** and verify completed/closed projects show.
10. Click **All** and verify full visible list returns.
11. Type a search term while a queue is active and verify both filters apply.
12. Clear search and verify the active queue remains selected.
13. Toggle "Show cancelled" and verify queue counts and rows update.
14. Confirm row **Open** buttons still navigate to the correct project Workbench.
15. Confirm Filter and Columns controls still render.
16. Confirm no Matrix/Fee/Test Record/Execution detailed actions were added to the Projects page.
