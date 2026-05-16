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

Current deferred scope (not active in the present stage baseline): AI review, multi-user permissions, LAN deployment, full installer, and PyInstaller packaging.

## Documentation Read Order

Current source-of-truth order:

1. `AGENTS.md`
2. `docs\task_board.md`
3. current `tasks\TASK_XXX_*.md`
4. task-specific plan or architecture docs
5. `docs\README.md`

Current governance and product references:

- Runtime governance: `docs\runtime_governance_freeze_rule.md`
- Product purpose: `PRODUCT.md`
- Documentation map: `docs\README.md`
- Domain snapshot: `docs\03_DOMAIN_MODEL.md`
- API surface snapshot: `docs\04_API_CONTRACTS.md`

Historical phase plans and packed blueprints are context only unless confirmed by `AGENTS.md`, `docs\task_board.md`, or the active task.

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

Or start both in separate PowerShell windows:

```powershell
.\scripts\run_mvp_dev.ps1
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
docs\frontend_smoke_checklist.md
```

Phase 5 UX status:

```text
docs\phase5_workbench_ux_decision.md
```

Packaging status:

```text
docs\packaging_notes.md
```
