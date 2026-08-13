# TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER Planner Evidence

TASK_ID: TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER
ROLE: Planner
STATUS: ready_for_user_approval
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:cross_frontend_backend
ATTEMPT: 1
ACTION_ID: 5960a14479c4f0e8d6dc63de4d4644319438c16cefec01cd5f6f7f18ac6cf633
PROMPT_SHA256: 9ec357da5f0ae2550770147dd9b6ad31a429cc223898f3d35535c13537293cb3
NEXT: User
BLOCKER: none

## Machine Authority

- Canonical Submit returned `ALLOW_ACTIVATE` from idle board SHA-256
  `1ea55a5aa0bb637490bf5830dc78a1ccdfcb83e9098a25cf1d60e974a3f341e9`.
- Activation was committed board-only at `da41911a`.
- Planner begin-role and invocation were separately persisted through the production writer.
- Planning base and activation parent: `c87fa35bcb9336aa6dda8e40520f08f2624b0729`.
- Primary was clean before activation and throughout read-only discovery.

## Discovery Result

- Existing typed frontend APIs already list project candidates and preview a selected candidate.
- Candidate data already contains the required filename, type, recommendation kind/reason, and
  availability fields.
- Existing backend code owns deterministic recommendation ranking; frontend duplication is neither
  needed nor authorized.
- The current hook cleanly identifies desktop versus browser. The browser path is the only behavior
  being changed.
- The exact implementation scope is seven frontend implementation/test/style paths plus
  `docs/task_board.md`, eight total.
- No backend/API, database, schema, persistence, parser, attachment storage, Matrix authority,
  public-drive, or business-rule change is required.

## Design Influence

`impeccable` product guidance was loaded with `PRODUCT.md`, `DESIGN.md`, and the ConnLab frontend
architecture rules. The Plan uses a familiar, restrained, explicit source chooser with operational
rows and empty states; it avoids an attachment manager, generic framework, decorative cards, or
automatic import.

## Authorization Boundary

No implementation, task host, branch/worktree, Developer, product/test edit, push, or cleanup is
authorized until the User approves the exact committed Plan ref and approved-request SHA-256.

