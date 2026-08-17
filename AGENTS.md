# ConnLab Engineering Rules

This file contains ConnLab-specific product and engineering facts. The only task workflow is
`docs/project_management/TASK_WORKFLOW.md`; machine state is in `docs/task_board.md`.

## Product mission

ConnLab is an offline, Windows-first workbench for an electronic connector laboratory. Project is the
lifecycle and traceability container. Matrix is the authoritative test-execution map. Test records,
reports, fee evaluation, and approval packages are derived outputs.

Current controlled foundation:

```text
Phase 11 - Project Workbench / Matrix / Approval Package
```

The next direction is Matrix-driven laboratory execution. Do not implement future concepts such as
StepInstance persistence, image asset management, AI review, multi-user permissions, or LAN deployment
unless the current User request requires them. Do not copy the old TestFlowManager architecture.

## Authority and compatibility

ConnLab currently operates in legacy-authority compatibility mode:

- Public-drive LTR workbooks and approved Word/Excel templates remain business authority or delivery
  templates where the existing workflow says so.
- SQLite is a local personal-workstation cache, automation aid, and migration backup; it must not
  silently replace authoritative public-drive workflows.
- Project lifecycle identity belongs to Project. Matrix owns what must be tested.
- Word and Excel are input/output formats, not the primary long-term domain model.
- A future authority cutover requires an explicit migration task.

When a task touches these areas, inspect the real current code and external-file behavior before
changing it. Preserve existing authority unless the User explicitly requests a migration.

## Technical stack

- Python 3.11+ and pytest.
- FastAPI with typed Pydantic v2 responses.
- SQLAlchemy 2.x and SQLite.
- React and TypeScript frontend.
- Windows and Microsoft Office integration where required.
- Prefer `python-docx` and `openpyxl` for offline parsing; keep `pywin32` behind a gateway.

## Architecture

Use the existing layers as real dependency rules, not directory decoration:

```text
backend/domain          pure domain concepts
backend/application     use cases and orchestration
backend/infrastructure  persistence, files, Office and platform adapters
backend/modules         bounded domain implementations
backend/api             thin routes and transport DTOs
backend/shared          genuinely shared primitives
```

- Domain must not depend on API, infrastructure, modules, UI, SQLAlchemy, or Office libraries.
- Application coordinates domain interfaces and must not contain concrete Office or SQLite access.
- Infrastructure supplies concrete adapters.
- API routes call application modules and return typed responses.
- Frontend and API routes must not manipulate Office files or project folders directly.
- Put business decisions in the deepest existing module whose interface naturally owns them.
- Prefer explicit dependencies and one state channel over global singletons or duplicate event/state
  propagation.

Before a structural change, trace the real entry point, dependency flow, state flow, data flow, and
resource lifecycle. Documentation does not override observable code behavior.

## Domain invariants

- Project remains the lifecycle and traceability center.
- Matrix remains the execution authority map and must not become an Excel-like string store.
- Extracted or confirmed information is stored as structured records.
- Application form starts the project; precheck is its first quality gate.
- LTR and project-folder operations remain downstream of a confirmed project.
- External files, parsers, validation, persistence, and UI concerns remain separate.
- Routes and UI handlers coordinate; they do not absorb domain logic.
- Do not add dependencies or future-scope abstractions without a current need.

## Windows and Office behavior

- Release COM objects, file handles, temporary resources, and child processes deterministically.
- Keep blocking Office and filesystem work off the UI thread.
- Test development-path and packaged-path resolution when a task changes resources or configuration.
- Never overwrite an existing project folder or authoritative workbook without an explicit safe
  conflict strategy in the current request.
- Include enough context in file, network, process, and COM errors to diagnose the failed operation.

## Frontend and UX

Use `PRODUCT.md`, `DESIGN.md`, `DESIGN.json`, `docs/02_ARCHITECTURE_RULES.md`, and
`docs/frontend_architecture_rules.md` when the task actually changes product behavior, layout,
interaction, visual design, component structure, or frontend architecture. A localized literal,
default, mapping, or existing-state fix does not require loading the whole design corpus.

- Keep UI focused on operator work, current state, blockers, and next actions.
- Preserve feature and page seams; do not grow route pages with unrelated workflow state.
- Use existing selectors, hooks, components, API clients, and styling conventions when they fit.
- Verify observable browser behavior when it changes. Do not require browser automation for a change
  already proven through a narrower public seam.

Project-local UI helper skills are optional methods, not mandatory gates.

## Implementation and testing

- Prefer the smallest coherent behavioral change, not the smallest line count.
- Preserve compatibility unless the User requests a breaking change.
- Do not swallow exceptions without a deliberate fallback and useful logging.
- Add regression protection for substantive behavior when a practical public seam exists.
- Test happy behavior and the important negative or recovery path introduced by the change.
- Run validation proportional to risk. The independent QA pass for a standard/high-risk task is the
  only default repetition of the complete approved matrix.
- After the final code or test byte changes, rerun affected validation on that exact subject.
- Keep fixtures and tests behavior-focused; do not simulate the governance implementation itself.

Functions and modules should remain understandable and cohesive. Split code when responsibilities or
change reasons diverge; do not split merely to satisfy an arbitrary line threshold.

## Task execution

Use GPT-5.6 Sol and the three tiers defined in `docs/project_management/TASK_WORKFLOW.md`:

- micro: direct Sol implementation, self-review, targeted validation;
- standard: one Sol plan/implementation work unit, independent Reviewer, one independent QA pass,
  automatic clean integration;
- high risk: Planner, Developer, Reviewer, QA, and Integrator.

Normal User interactions are Submit and final Close. Do not request routine plan approval. The User's
request is the behavioral scope; optional path scope only tightens it.

Use `scripts/connlab_sol_task.py` as the sole board writer. Persist only meaningful recovery
checkpoints. Git supplies HEAD and changed-path facts; do not create role begin/invocation/callback
microstates or separate evidence files by default.

## Safety and completion

- Preserve unrelated User work and inspect a dirty worktree before touching overlapping paths.
- Do not silently restore, reset, stash, clean, rebase, delete, push, or overwrite external state.
- Stop for scope expansion, new destructive authority, a material unresolved product choice, or a
  repeated failure whose cause cannot be established.
- Finish with the exact changed paths, validation results, independent review outcome where required,
  and residual risk.
- Stop at `ready_for_close`. Only the User's explicit Close releases WIP and permits another task.
