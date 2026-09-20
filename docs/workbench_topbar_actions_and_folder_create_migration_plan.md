# Workbench top-bar action slot and Folder creation migration

Status: Batch 0, Batch 1, and Batch 2 implemented. D1/D2/D3 were resolved using the recommended
task-row placement, primary visual weight, and cross-lifecycle reachability coverage.

Scope: `frontend/src/components/layout/*`, `frontend/src/features/project-workbench/*`,
`frontend/src/pages/ProjectListPage.tsx`. No backend, endpoint, Office, or authority change.

## 1. Current mechanism (verified against source)

`TopBar` renders a two-column header. The second column is the slot:

```tsx
<header className={`top-bar top-bar-${activeRoute}`}>
  <div className="top-bar-title-slot"><h1 title={title}>{title}</h1></div>
  <div className="top-bar-actions" data-top-bar-actions="true" aria-label="Page actions">{actions}</div>
</header>
```

`AppShell` does forward `topBarActions` into `TopBar.actions` (`AppShell.tsx:49`), but `App.tsx:231`
does not pass that prop. In production the slot is therefore filled only by portals.

Three consumers resolve the host themselves and portal a node into it, falling back to in-place
rendering when the host is absent:

| Consumer | Portaled node |
| --- | --- |
| `ProjectListPage.tsx:99-102` | registry management controls |
| `ProjectWorkbenchLayout.tsx:530` | back button + project identity + four action buttons |
| `ProjectWorkbenchExecutionConsole.tsx:61-63` | details toggle |

Layout is `grid` on `.top-bar` with per-route modifiers, plus `.top-bar-workbench .runtime-console-*`
overrides (`workbench.css:10355-10386`) that restyle the portaled workbench command bar to fit the
top bar.

## 2. Finding F1 — workbench slot placement had zero test coverage

`ProjectWorkbenchLayout.test.tsx:1552` renders `ProjectWorkbenchLayout` alone. No `AppShell`/`TopBar`
is mounted, so `document.querySelector("[data-top-bar-actions]")` returns `null` and **all 55 tests in
that file take the fallback branch**. The helper at lines 66-73 scopes to
`aria-label="Project Workbench actions"`, which is an element *inside* the portaled node, so it
matches identically in both branches.

`ProjectListPage.test.tsx` did have one placement case, but it built its own host `<div>` and relied on
the `[data-top-bar-actions]` attribute being discoverable in the document — which is itself the
mechanism batch 1 removes.

Consequences:

- Nothing pinned the workbench command bar's placement. A regression that dropped the portal entirely
  still passed the suite.
- Batch 2 would break roughly 15 `getWorkbenchActionButton("Create project folder")` calls and 4
  `/Matrix Editor\s*Fee Evaluation\s*Basic Information\s*Create project folder/` order assertions,
  all failing with the opaque message `Project Workbench action button not found`.
- A placement test written against `document.querySelector` would have to be rewritten immediately,
  because under batch 1 a component rendered without its provider has no host by design. It was
  therefore written against the replacement instead (see section 7).

## 3. Finding F2 — the create button ignores its own derived label

`ProjectWorkbenchLayout.tsx:291-302` derives:

```tsx
const visibleWorkbenchFolderCommand = isActiveMatrixWorkspace && Boolean(projectNumber)
  ? visibleActiveMatrixFolderCommand
  : {
      label: effectiveFolderReady || officialWorkspacePreview?.status === "completed"
        ? "Update project folder"
        : "Create project folder",
      disabled: true,
      disabledReason: ...
    };
```

Line 522 hardcodes the text and only swaps for the busy state:

```tsx
{officialWorkspaceCreating ? "Generating..." : "Create project folder"}
```

So `visibleWorkbenchFolderCommand.label` is computed and never read, and **"Update project folder"
never renders**. Any rename in batch 2 should be expressed through this existing `label` field rather
than another literal.

Note also that in the non-active-Matrix branch the command is hard-coded `disabled: true` (line 298),
so the top-bar button is permanently disabled in the no-matrix empty state.

## 4. Finding F3 — the Folder Actions header has room, but no slot and no styling

`ProjectFolderActionsSurface` (`ProjectFolderTaskList.tsx:51-93`) renders:

```tsx
<header className="runtime-console-folder-actions-header">
  <p className="eyebrow">Folder Actions</p>
</header>
```

- `workbench.css:3937-3942` is already `display:flex; align-items:center; justify-content:space-between`,
  so a second child lands on the right with no layout change.
- But `workbench.css:3944` styles only `p` (`margin:0`). A header `<button>` needs its own class, and
  the `≤760px` behaviour must be checked. Placement is free; styling is not.
- There is no `headerAction` prop. `footerAction` exists and is already occupied by
  `ProjectFileEncryptionAction` (`ProjectWorkbenchActiveMatrixWorkspace.tsx:79`).
- The surface is instantiated in **two** lifecycle modes: active Matrix workspace (as
  `sideColumnAfter`) and `NoMatrixWorkspaceEmptyState` (`ProjectWorkbenchLifecycleSections.tsx:552`).
  A migrated control must be correct in both.

## 5. Finding F4 — "create folder" is already a reserved action target

- `ProjectFolderTaskActionTarget` already includes `"folder"` (`projectFolderTaskSelectors.ts:28`).
- `handleProjectFolderTaskAction` already routes it:
  `actionTarget === "folder"` → `handleProjectFolderCreateClick()` (`ProjectWorkbenchLayout.tsx:385-388`).
- `isProjectFolderWriteAction` already lists `"folder"` for readonly gating (line 668).
- `deriveProjectFolderTasks` never emits it. It produces only `project_folder`,
  `public_working_copy`, `approval_package`, `approved_folder`.

So the create action can become a task row with no new plumbing. Three constraints to respect:

- `withoutUnavailableFolderAction` (`ProjectWorkbenchActiveMatrixWorkspace.tsx:106-113`) special-cases
  only `key === "project_folder"`. A new create row needs an explicit decision about the
  "folder not ready and cannot generate" state, otherwise it will surface a dead button.
- `selectCurrentProjectFolderTaskKey` returns `tasks[0].key`. Inserting a create row at index 0
  silently changes what "current task" means for `PackagePreparationMode`.
- `ProjectFolderTaskList`'s declared prop type lists `currentTaskKey`, `selectedTaskKey`,
  `onSelectTask`, but the implementation destructures only five props and drops them
  (`ProjectFolderTaskList.tsx:21-39`). Pre-existing drift; do not build on those props without
  settling it first.

## 6. Batch 0 — implemented

| File | Change |
| --- | --- |
| `ProjectWorkbenchExecutionConsole.tsx` | `useEffect` → `useLayoutEffect` (import swapped; the file's only call site) |
| `ProjectWorkbenchLayout.tsx` | added `useLayoutEffect` to the import; slot lookup switched |
| `ProjectListPage.tsx` | split the effect: data loading stays in `useEffect`, slot lookup moved to its own `useLayoutEffect` |
| `components/layout/TopBar.test.tsx` | staged; was untracked while sibling test files were committed |

The `ProjectListPage` split matters: converting the whole effect would have pulled `refreshProjects()`
and `readLastLtrApplyResult()` into a layout effect. Only the DOM lookup belongs there.

Validation: `vitest run` over `TopBar`, `Sidebar`, `ProjectListPage`, `ProjectWorkbenchLayout`,
`ProjectFolderTaskList`, `ProjectRegistryManagementDialog` → **86 passed / 6 files, 12.57s**.
Per F1 this run does not exercise the portal branch.

## 7. Batch 1 — implemented: host discovery through a context

Problems being solved:

- P1 `document.querySelector` takes the first match in the whole document; with a second `TopBar`
  the wrong host is chosen, and the portal content disappears with it.
- P2 Three components each reimplement the same guess. The slot convention exists only as a string
  literal in four places.
- P3 `AppShell.topBarActions` is a public prop with no caller. It is either dead API or the intended
  channel. Do not delete it as a standalone change — that is what batch 1 resolves.

Implemented design:

1. New `components/layout/TopBarActionsContext.tsx` — the repository's first React context (there was
   no prior `createContext` anywhere in `frontend/src`). It exports `TopBarActionsProvider`,
   `useTopBarActionsRoot()`, and `useTopBarHostRegistration()`.
2. The provider owns the host in state and exposes a `useCallback` registration callback. `TopBar`
   attaches it as `ref` on the slot div. Consumers read the host **during render** — no `useState`, no
   `useEffect`, no `document.querySelector` remain at any call site.
3. Registration deliberately uses a **callback ref plus provider state rather than a shared ref
   object read inside a consumer layout effect**. A callback ref fires during the commit phase, so the
   provider's `setState` is flushed synchronously before paint and the portal still lands on the first
   painted frame. Reading `slotRef.current` from a consumer layout effect instead would depend on ref
   attachment order among siblings; if the ref were not attached yet the effect's dependency
   (`slotRef`) would never change and the consumer would be stuck rendering in place forever.
4. `AppShell` wraps `Sidebar` + `TopBar` + `children` in the provider. The unused `topBarActions` prop
   is **deleted** (P3 resolved: one channel, not two).
5. The missing placement test was added first, against the new mechanism:
   `renderWorkbench` gained a `wrapper` argument wired to RTL's `render(ui, { wrapper })`, and
   `ProjectWorkbenchLayout.test.tsx` gained a `ProjectWorkbenchLayout top bar action slot` block with
   two cases (host present → command bar inside `[data-top-bar-actions]`; no host → command bar in
   place). `ProjectListPage.test.tsx`'s existing case was rewritten to render the **real** `AppShell`
   instead of hand-building a host div, because that hand-built host depended on the attribute-based
   discovery this batch removes.

Files changed: `components/layout/TopBarActionsContext.tsx` (new), `components/layout/AppShell.tsx`,
`components/layout/TopBar.tsx`, `features/project-workbench/ProjectWorkbenchLayout.tsx`,
`features/project-workbench/ProjectWorkbenchExecutionConsole.tsx`, `pages/ProjectListPage.tsx`,
`features/project-workbench/ProjectWorkbenchLayout.test.tsx`, `pages/ProjectListPage.test.tsx`.

Validation:

- Targeted run over 7 files → **91 passed / 7 files** (`ProjectWorkbenchLayout` went 55 → 57).
- Negative control: temporarily forcing `useTopBarActionsRoot()` to `return null` produced **exactly 2
  failures** — the two placement cases, one per consumer — with the in-place fallback case still
  passing and no collateral failures. Reverted and verified clean. This proves the new cases pin
  placement instead of passing vacuously.
- Full frontend suite (88 files): 638 passed, 2 failed.
  `ContactMeasurementSetupWorkspace > disables Add row at the 256-category limit` (5 s timeout) and
  `ReportWorkspace > recovers real progress above the disabled generation button` (waits for an
  "N seconds elapsed" tick). Neither module's dependency graph reaches `TopBarActionsContext`,
  `AppShell`, or `TopBar` — verified by exhaustive grep of every reference to the new context — and
  both pass (19 passed) when re-run with `--testTimeout=30000`, the timeout case dropping from 8769 ms
  to 1544 ms. They are host timing/perf sensitivity, not regressions from this batch.

Risk: medium, and realised as designed — three consumers changed together, which is why this had to
precede batch 2 rather than follow it.

## 8. Batch 2 — implemented decisions

### D1 — which surface receives the control

**Option A — make it a task row.** Rejected after UI review because it turns a simple shortcut into
an extra workflow row and changes the established four-operation Folder Actions model.

**Option B — header right corner.** Add `headerAction` to `ProjectFolderActionsSurface` and render a
styled button beside the eyebrow. Matches the stated intent exactly. Costs: new prop, new CSS (F3),
must be passed at both instantiation sites, and does not inherit the per-task blocker rendering.

Implemented: **Option B**. `ProjectFolderActionsSurface` accepts one compact `headerAction` and
renders it at the upper-right of the card header. The existing four operations are unchanged, and
the `Project folder` row keeps its independent Open action.

### D2 — primary visual weight

After the move the command bar holds Matrix Editor / Fee Evaluation / Basic Information /
Test Report Draft — all secondary. `.is-primary` currently only styles
`.runtime-console-commandbar-actions button` (`workbench.css:2529`), so a primary control inside the
Folder Actions card gets no styling unless that selector is widened. Implemented: a scoped header
button owns the page's primary folder command without changing the operation-row visuals.

### D3 — reachability

The Folder Actions surface sits in `sideColumnAfter`; in the no-matrix mode it is inside the empty
state, and under `readonly_archive` its position differs. The top bar was always visible, so the card
may require scrolling or be collapsed at narrow widths. `/projects/*` previously had a horizontal
overflow defect at ~514px. Implemented coverage keeps the command in the shared Folder Actions
surface for active Matrix, no-Matrix, and read-only lifecycle modes.

The command bar no longer contains the folder command. The header shortcut reuses the existing
generation handler and always displays `Create folder`; current disabled state and its authoritative
reason are preserved through the button tooltip. Folder readiness therefore affects behavior, not
the visible command label.

## 9. Cleanup candidate (verify before deleting)

`OfficialWorkspaceActionPanel.tsx` and `ProjectFolderCreationPanel.tsx` have no production reference.
`ProjectFolderCreationPanel` is referenced only by a `vi.mock` in `ProjectWorkbenchLayout.test.tsx`.
Between them they contain alternate "Create project folder" affordances. Settle them before batch 2
adds a third entry point.

## 10. Out of scope

No backend or endpoint change. No change to which surface owns folder generation authority. No new
execution persistence. No introduction of any future scope listed in `AGENTS.md`.
