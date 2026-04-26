from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT = Path(__file__).resolve().parents[2] / "frontend"


def test_frontend_shell_core_files_exist() -> None:
    """Minimal React shell files are present."""
    expected_files = [
        "package.json",
        "index.html",
        "tsconfig.json",
        "vite.config.ts",
        "src/main.tsx",
        "src/App.tsx",
        "src/api/client.ts",
        "src/styles.css",
    ]

    for relative_path in expected_files:
        assert (FRONTEND_ROOT / relative_path).is_file()


def test_frontend_shell_uses_api_client_and_mvp_routes() -> None:
    """The shell exposes project routes and keeps API calls in the client layer."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    list_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    assert 'pathname === "/projects"' in app_source
    assert "/projects/" in app_source
    assert "listProjects" in list_page_source
    assert "getProject" in workbench_source
    assert '"/api/projects"' in client_source
    assert 'fetch(`${API_BASE}${path}`' in client_source


def test_frontend_shell_shows_only_mvp_task_cards() -> None:
    """The detail workbench shows only MVP cards required by TASK_013."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    assert "<h3>Precheck</h3>" in workbench_source
    assert "<h3>LTR</h3>" in workbench_source
    assert "<h3>Project Folder</h3>" in workbench_source
    assert "Matrix" not in workbench_source
    assert "Report" not in workbench_source


def test_frontend_workflow_integration_calls_mvp_actions() -> None:
    """The workbench wires the visible MVP actions to API client functions."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    for api_name in [
        "uploadApplicationForm",
        "runPrecheck",
        "registerLtr",
        "previewFolder",
        "generateFolder",
    ]:
        assert api_name in workbench_source
