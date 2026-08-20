# ConnLab Frontend Guide

Status: current focused guidance for substantive React/UI work.

Read `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json` only for changes to behavior, layout, interaction,
visual hierarchy, or product copy. Localized literals, defaults, mappings, and existing-state fixes
should stay local and use targeted tests.

## Dependency and responsibility

```text
pages -> features -> reusable components
pages/features -> typed API modules -> backend
```

- Route pages own route parameters, navigation, composition, and page-level loading/fatal errors.
- Feature modules own workflow components, selectors, hooks, field/table configuration, and local draft
  orchestration.
- Only frontend API modules call `fetch()`; components do not touch Office, SQLite, or local paths.
- Backend remains authoritative for persisted business decisions. Selectors derive display state from
  typed responses; they do not invent persistent truth.
- Prefer named business modules over universal form, panel, table, or workflow abstractions.

Do not reorganize folders merely to match an ideal tree. Extract when a page is accumulating multiple
change reasons, repeated decisions, or independently testable behavior.

## State and interaction

- Keep route/session state at the narrowest owner that must survive navigation.
- Use feature hooks for request orchestration and editable draft state.
- Use selectors for eligibility, disabled reasons, blockers, next actions, and display status.
- Avoid duplicating the same decision in JSX, hook state, and backend responses.
- Preserve loading, empty, error, read-only, cancellation, stale-response, and retry behavior relevant
  to the changed operation.
- Never expose local filesystem paths in browser UI or accept arbitrary client paths as authority.

## UI quality

- Optimize for a 14-inch Windows laptop and operator workflows: current state, blockers, and next
  actions should be obvious.
- Use restrained semantic color paired with text; avoid decorative hierarchy that competes with work.
- Reuse established components and styles when they fit. A helper skill is optional, not a gate.
- Keep mock/reference content clearly inactive and do not present unimplemented features as available.
- User-facing errors should be actionable and omit raw stack traces or backend identifiers unless the
  surface is explicitly diagnostic.

## Validation

- Test behavior through the narrowest public seam that proves it.
- Run relevant frontend tests and `npm run build` for substantive TypeScript or build-affecting work.
- Use browser verification when observable interaction, layout, focus, navigation, or responsive
  behavior changed; do not require it for behavior already fully proven at a narrower seam.
- Review for requirement fit, stale async behavior, accessibility, narrow-width operation, direct
  `fetch()` leakage, and accidental business logic in display components.
