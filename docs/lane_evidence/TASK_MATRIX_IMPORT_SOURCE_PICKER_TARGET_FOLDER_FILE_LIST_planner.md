# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST Planner Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST
ROLE: Planner
STATUS: ready_for_user_approval
SUBJECT: 847211b7efdac1c8e153028c9b963e50b1daac21
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: 62cfc802605fde4347877b8211697eb9d44c7fa35f7eebfbdbf60e2e301b9d3a
ATTEMPT: 1
NEXT: User
BLOCKER: none

## Machine authority

- Read-only primary HEAD: `847211b7efdac1c8e153028c9b963e50b1daac21`.
- Approved base and activation parent: `900c26a78009264ab0fc06f2c038e50d6d280869`.
- Board raw SHA-256: `d1b831f9e59f016dc1323e5bd490b9fde1de1654a44ba5b39aa2418b4b04a499`.
- Board was `running / planning / Planner attempt 1 / callback_pending`; primary was clean.
- Planner performed no repository, board, ref, worktree, database, attachment, or external-file write.

## Discovery and decision

- Preserve the Project Workbench registered-asset default and add one browser-only
  `resolved_directory` view on the existing endpoints.
- Enumerate direct `.doc/.docx/.pdf` files with namespaced opaque IDs and exact re-enumeration; add no
  persistence, endpoint, registry, path input, parser behavior or external write.
- The reviewed opaque ID binds project ID, source kind, canonical resolved-directory identity and
  filename. Directory identity is digest-only and never exposed; changing to another same-kind directory
  invalidates the old selection even when the new folder contains the same filename.
- Simplify the browser chooser to a source-kind title and filename-only buttons; retain standard
  Cancel/Upload actions, actionable states, read-only gating and desktop behavior.
- Exact implementation/test scope is 12 paths within the submitted 20-path envelope.
- Execution roles freeze to `gpt-5.6-sol / medium / risk:api_contract`.
- Pre-approval machine validation corrected only the route-table encoding to the production-readable
  `model / effort / reason` form; the approved request, scope, behavior and route values are unchanged.
- User review revision P0 is closed without scope expansion: canonical directory identity is part of
  the opaque digest, and the Plan calls this an existing GET/POST contract extension, not a new endpoint.

## Design influence

`impeccable`, `PRODUCT.md`, `DESIGN.md` and frontend architecture rules require a restrained operational
file list, concise copy, accessible states and familiar primary/secondary controls rather than nested
recommendation cards.

STATUS: ready_for_user_approval

NEXT: User

BLOCKER: none
