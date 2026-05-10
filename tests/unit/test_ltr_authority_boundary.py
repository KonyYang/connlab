from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_api_routes_do_not_import_excel_or_com_gateway_details() -> None:
    """Route modules must depend on application services, not Office gateway internals."""
    forbidden_terms = [
        "ExcelComLTRWorkbookGateway",
        "LtrWorkbookTransactionGateway",
        "OfficeLifecycleManager",
    ]
    for route_path in (ROOT / "backend" / "api").glob("routes_*.py"):
        source = route_path.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in source, f"{term} leaked into {route_path.name}"


def test_new_project_completion_depends_on_authority_boundary() -> None:
    """New Project completion orchestration should target authority seam, not workbook service."""
    source = (
        ROOT / "backend" / "application" / "new_project_completion_service.py"
    ).read_text(encoding="utf-8")
    assert "LtrAuthorityPort" in source
    assert "CommitLtrAuthorityCommand" in source
    assert "LtrWorkbookWriteCommitService" not in source
    assert "CommitLtrWorkbookWriteCommand" not in source


def test_new_project_route_does_not_import_workbook_specific_commit_error() -> None:
    """New Project route should stay bound to authority errors, not workbook errors."""
    source = (
        ROOT / "backend" / "api" / "routes_new_project_completion.py"
    ).read_text(encoding="utf-8")
    assert "LtrAuthorityCommitError" in source
    assert "LtrWorkbookWriteCommitError" not in source
