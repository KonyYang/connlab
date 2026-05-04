# Frontend Architecture Rules

## Purpose

This document defines the ConnLab frontend boundary rules for React UI work. It is the UI counterpart to the backend architecture rules in `AGENTS.md` and `docs/02_ARCHITECTURE_RULES.md`.

The goal is to keep Intake, Precheck, LTR Number, and Project Folder screens maintainable while the product evolves through controlled tasks. These rules apply before adding fields, states, actions, copy, or visual changes.

## Current Frontend Shape

Current implementation:

```text
frontend/src/
  App.tsx                  # hand-written route parsing and app session state
  api/client.ts            # typed API client and response DTOs
  components/              # shared layout, common, project, precheck, workflow components
  pages/                   # route-level pages
  *.css                    # global and page-level styles
```

The current architecture is workable because API access is centralized and the UI does not directly touch Office, SQLite, or project folders. The main maintainability risk is large page files accumulating fields, state, workflow decisions, and JSX at the same time.

## Target Boundary

Use this frontend dependency direction:

```text
pages -> features -> components/common
pages/features -> api
styles -> component/page/feature class names only
```

Recommended structure for new or refactored UI:

```text
frontend/src/
  api/
    client.ts              # may be split later by domain, but remains the only fetch boundary
  components/
    common/                # generic UI states and small reusable primitives
    layout/                # shell, sidebar, top bar
  features/
    intake/
    precheck/
    ltr/
    folder/
  pages/
```

`features/*` is the preferred business boundary for future UI work. Add it gradually. Do not rewrite existing pages just to match the target structure unless a task explicitly authorizes that refactor.

## Page Rules

Route pages may:

- load the route-level view model or call a feature hook
- own route parameters and route navigation callbacks
- compose feature components into the page layout
- hold minimal page loading and fatal error state

Route pages must not keep accumulating:

- long field configuration arrays
- table column definitions for business records
- repeated formatter/helper functions
- multi-branch workflow permission logic
- large nested JSX sections that can be named as business components
- direct `fetch()` calls

Target page responsibility:

```tsx
const model = usePrecheckReviewModel(packageId, initialCaseId);

return <PrecheckReviewLayout model={model} onBack={onBack} />;
```

## Feature Rules

A feature folder owns one business workflow surface, for example Intake or Precheck.

Feature folders may contain:

- page-specific business components
- field and table configuration
- selectors that calculate disabled state, blockers, next action, or display status
- custom hooks that coordinate API calls and local draft state
- small formatters that are not globally reusable

Suggested Precheck shape:

```text
frontend/src/features/precheck/
  PrecheckReviewLayout.tsx
  PrecheckSourceCheck.tsx
  PrecheckFieldGrid.tsx
  PrecheckSampleTable.tsx
  PrecheckRequestedTesting.tsx
  PrecheckFooterActions.tsx
  precheckFieldConfig.ts
  precheckReviewSelectors.ts
  usePrecheckReviewModel.ts
```

Suggested Intake shape:

```text
frontend/src/features/intake/
  IntakeWorkflowLayout.tsx
  IntakeSourcePanel.tsx
  AttachmentList.tsx
  AttachmentPreviewPanel.tsx
  intakeSelectors.ts
  useIntakeImportModel.ts
```

## Field And Table Rules

Field changes must go through configuration first.

Good:

```ts
export const PRECHECK_PROJECT_FIELDS = [
  { key: "requester", label: "Requested By", required: true, kind: "input" },
  { key: "request_date", label: "Date", required: true, kind: "date" }
];
```

Then render through a component:

```tsx
<PrecheckFieldGrid fields={PRECHECK_PROJECT_FIELDS} values={fieldValues} onChange={setFieldValue} />
```

Avoid adding one-off labels and inputs directly into a large page JSX block unless the field is truly local and temporary.

Table columns follow the same rule. Business table headers and cell mapping should be defined in a feature config or feature component, not scattered across a route page.

## State Rules

Classify state before adding `useState`.

Allowed page-level state:

- route session state such as the current in-memory intake session in `App.tsx`
- fatal loading/error state for the whole page
- selected tab or selected workflow step when it is purely presentational

Intake session state represents one current New Project source package and one selected application form. Importing a new email package or direct Word form must replace the previous session. Selecting a different eligible application form clears the previous Precheck case id until the backend returns the case for the new selected form. Precheck may resolve an active case from route/session state, but it must not present a multi-case switcher in the New Project workflow.

Prefer feature hooks for:

- imported package state
- selected attachment state
- selected review case state
- editable draft field values
- save/confirm loading flags
- operation success/error messages

Prefer selectors for:

- whether an action is enabled
- why an action is disabled
- next action text
- workflow status labels
- blocker and warning summaries

Do not scatter compound conditions through JSX. Compute them once and render the result.

## Business Rule Rules

UI may present business state, but backend remains authoritative for persisted operations.

Frontend selectors may calculate display-only state from typed API responses, but they must not invent persistent business truth. Examples:

- confirmation eligibility can be displayed from `confirm_allowed` and `missing_required_fields`
- lifecycle button disabled reasons can mirror backend guard outcomes
- folder/evidence actions must still call preview/execute APIs rather than touching files directly

If the UI needs a new authoritative rule, add or expose it through backend application/API layers in a separate approved task.

Intake application-form entry gate:

- Intake may display eligibility state returned by backend validation.
- Continue-to-Precheck disabled state should be computed in `features/intake` selectors from typed API DTOs.
- UI copy may show a cleaned observed Word header cell value returned by the backend, but frontend code must not read local Word files.
- The backend remains authoritative when `select-form` is called.

## API Rules

Only the API layer may call `fetch()`.

Allowed:

```text
frontend/src/api/client.ts
frontend/src/api/request.ts       # if the client is later split
frontend/src/api/*.ts             # future domain-specific API modules
```

Forbidden:

- `fetch()` inside pages
- `fetch()` inside display components
- display components importing backend concepts that are not part of API DTOs
- UI accepting arbitrary local file paths for backend file operations

`api/client.ts` may be split later by domain when the task is explicitly about frontend maintenance. The split must preserve one shared request helper and typed response DTOs.

## Component Rules

Use business components before inventing generic abstractions.

Good:

- `PrecheckSampleTable`
- `AttachmentPreviewPanel`
- `LtrReadinessPanel`
- `FolderEvidencePlan`

Avoid premature generic components:

- `UniversalWorkflowEngine`
- `UniversalFormBuilder`
- `UniversalPanel`

Shared components under `components/common` must be truly generic and free of ConnLab business workflow assumptions.

## Copy And Mock Data Rules

User-facing copy must be operational and business-readable. Avoid backend terms such as `asset_id`, route names, raw enum names, or stack traces unless the screen is explicitly diagnostic.

Do not mix mock/reference content into real data regions without a clear disabled or placeholder state. Fixed recipients, fixed test rows, disabled future controls, and reference-template messages must be marked as inactive or temporary and should be removed or wired to data in a later explicit task.

Never expose future-scope features as available actions:

- Matrix
- Report generation
- AI review
- LAN deployment
- permissions
- Outlook inbox auto-scan
- email sending
- copied/external LTR workbook write unless the active task permits it

## Styling Rules

ConnLab is a product UI. Follow `PRODUCT.md`, `DESIGN.md`, and `$impeccable` product guidance for UI work.

Rules:

- keep the left navigation plus top bar product shell
- use restrained state color for action, selection, warning, success, and danger
- pair color with text labels
- avoid nested cards and decorative-only panels
- avoid gradient text, decorative glassmorphism, and thick colored side stripes
- keep 14-inch laptop fit in mind for Intake and Precheck

CSS should be scoped by page or feature naming. Avoid dumping new unrelated classes into `styles.css` when a feature-specific stylesheet is more appropriate.

## Refactor Safety Rules

When improving existing UI architecture:

1. Extract named business components first.
2. Move field/table configs out of pages.
3. Move repeated workflow decisions into selectors.
4. Move API orchestration and draft state into feature hooks.
5. Only then consider splitting `api/client.ts` or CSS files.

Keep behavior stable during extraction. A cleanup task should not change business flow, API behavior, or feature scope unless explicitly stated.

## Review Checklist For UI Changes

Before closing a UI task, verify:

- pages do not grow further without justification
- no direct `fetch()` outside `frontend/src/api`
- no UI direct Office, SQLite, or filesystem operations
- fields and table columns are config-driven when they are business records
- disabled states have visible reasons when the operator needs to act
- mock/reference content is clearly inactive or removed
- `npm run build` passes from `frontend/`
- relevant manual smoke path is documented when the task changes operator flow
