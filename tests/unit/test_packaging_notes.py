from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_local_run_scripts_exist_and_use_expected_commands() -> None:
    """TASK_015 local run scripts are present and target the MVP processes."""
    scripts = {
        "scripts/init_db.ps1": ["create_database_engine", "init_db"],
        "scripts/run_backend.ps1": ["uvicorn", "backend.api.main:app"],
        "scripts/run_frontend.ps1": ["npm install", "npm run dev"],
        "scripts/run_mvp_dev.ps1": ["run_backend.ps1", "run_frontend.ps1"],
    }

    for relative_path, expected_terms in scripts.items():
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "[Console]::OutputEncoding" in source
        for term in expected_terms:
            assert term in source


def test_readme_documents_setup_run_and_validation() -> None:
    """README documents clone-time setup, run commands, and verification."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for term in [
        "py -m pip install -e .[dev]",
        "npm install",
        ".\\scripts\\init_db.ps1",
        ".\\scripts\\run_backend.ps1",
        ".\\scripts\\run_frontend.ps1",
        ".\\scripts\\run_tests.ps1",
        ".\\scripts\\run_frontend_build.ps1",
        "docs\\archive\\validation_summaries\\frontend_smoke_checklist.md",
    ]:
        assert term in readme


def test_frontend_smoke_checklist_covers_phase5_mvp_flow() -> None:
    """TASK_023 documents the manual frontend validation guard."""
    checklist = (ROOT / "docs" / "archive" / "validation_summaries" / "frontend_smoke_checklist.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "project registry page loads",
        "Create a project",
        "project detail page opens",
        "Application Form",
        "Precheck",
        "LTR",
        "Project Folder",
        "Matrix is not exposed",
        "Report generation is not exposed",
        ".\\scripts\\run_frontend_build.ps1",
    ]:
        assert term in checklist


def test_frontend_build_script_runs_npm_build_from_repo_root() -> None:
    """TASK_023 provides a root-level frontend build command."""
    script = (ROOT / "scripts" / "run_frontend_build.ps1").read_text(
        encoding="utf-8"
    )

    assert "[Console]::OutputEncoding" in script
    assert 'Push-Location "frontend"' in script
    assert "npm run build" in script


def test_packaging_notes_are_mvp_scoped() -> None:
    """Packaging notes explicitly avoid installer scope for the MVP."""
    notes = (ROOT / "docs" / "packaging_notes.md").read_text(encoding="utf-8")

    assert "no installer" in notes.lower()
    assert "PyInstaller" in notes
    assert "PyWebView" in notes
    assert "CONNLAB_DATABASE_PATH" in notes
