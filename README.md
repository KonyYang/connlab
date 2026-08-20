# ConnLab

ConnLab is an offline Windows-first workbench for an electronic connector laboratory.

Current working stage:

```text
Project Workbench / Matrix / Approval Package
```

Current foundation baseline:

```text
Phase 11 - controlled foundation baseline
```

Next product direction:

```text
Matrix-driven Laboratory Execution Phase
```

Governance principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Historical MVP baseline (already implemented and extended):

```text
Project -> Application form -> Precheck -> LTR -> Project Folder
```

Current deferred scope (not active unless a task requests it): AI review, multi-user permissions, LAN deployment, and a managed multi-user installer.

## Documentation Read Order

Current source-of-truth order:

1. the User's current request
2. `AGENTS.md`
3. current code, tests, configuration, external behavior, and Git state
4. `docs\task_board.md` for compact WIP/recovery state
5. `docs\project_management\SOL_NATIVE_WORKFLOW.md` when detailed task routing or recovery is needed

Current governance and product references:

- Documentation map: `docs\INDEX.md`
- Product and engineering context: `docs\PROJECT_CONTEXT.md`
- Product purpose and visual direction: `PRODUCT.md`, `DESIGN.md`, `DESIGN.json`
- Frontend structure: `docs\FRONTEND_GUIDE.md`

Historical phase plans, role evidence, dated snapshots, and packed blueprints are searchable context
only. They never create scope or reactivate retired workflows.

## Requirements

- Windows development machine.
- Python 3.11 or newer.
- Node.js and npm for the React frontend.
- Microsoft Office on Windows for realistic DOCX/XLSX lab workflows. The current parser uses `python-docx`; future Office automation must stay behind gateway/facade classes.

## First Setup

Run from repository root:

```powershell
py -m pip install -e .[dev]
Set-Location frontend
npm install
Set-Location ..
.\scripts\init_db.ps1
```

Default local runtime paths:

- SQLite database: `data\connlab.sqlite3`
- Project output root: `projects\`
- Folder templates: `templates\`

These can be overridden with environment variables:

- `CONNLAB_DATA_DIR`
- `CONNLAB_PROJECTS_DIR`
- `CONNLAB_TEMPLATES_DIR`
- `CONNLAB_DATABASE_PATH`
- `CONNLAB_LOG_LEVEL`

## Run Locally

Backend API:

```powershell
.\scripts\run_backend.ps1
```

Frontend:

```powershell
.\scripts\run_frontend.ps1
```

Desktop shell (after backend and frontend are running):

```powershell
.\scripts\run_desktop_shell.ps1
```

Or start both in separate PowerShell windows:

```powershell
.\scripts\run_mvp_dev.ps1
```

Or start backend, frontend, and the desktop shell in separate PowerShell windows:

```powershell
.\scripts\run_mvp_dev.ps1 -WithDesktopShell
```

Open the Vite URL shown by the frontend script. The frontend proxies `/api` to `http://127.0.0.1:8000`.

## Verify

Backend tests:

```powershell
.\scripts\run_tests.ps1
```

Frontend build:

```powershell
.\scripts\run_frontend_build.ps1
```

Manual frontend smoke checklist:

```text
docs\archive\validation_summaries\frontend_smoke_checklist.md
```

Phase 5 UX status:

```text
docs\archive\historical_plans\phase5_workbench_ux_decision.md
```

Packaging status:

```text
docs\packaging_notes.md
```
