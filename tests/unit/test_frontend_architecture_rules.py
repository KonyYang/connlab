from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_frontend_architecture_rules_document_ui_boundaries() -> None:
    """TASK_076 documents the frontend UI boundaries for future work."""
    source = (ROOT / "docs" / "frontend_architecture_rules.md").read_text(
        encoding="utf-8"
    )

    for term in [
        "pages -> features -> components/common",
        "Only the API layer may call `fetch()`",
        "Classify state before adding `useState`",
        "Field changes must go through configuration first",
        "Prefer selectors for:",
        "Use business components before inventing generic abstractions",
        "Do not mix mock/reference content into real data regions",
        "`npm run build` passes from `frontend/`",
    ]:
        assert term in source


def test_frontend_architecture_rules_are_linked_from_project_rules() -> None:
    """The general architecture rules point UI work to TASK_076 boundaries."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    architecture_rules = (ROOT / "docs" / "02_ARCHITECTURE_RULES.md").read_text(
        encoding="utf-8"
    )
    board = (ROOT / "docs" / "task_board.md").read_text(encoding="utf-8")
    task = (
        ROOT / "tasks" / "completed" / "2026" / "TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY.md"
    ).read_text(encoding="utf-8")

    assert "docs/02_ARCHITECTURE_RULES.md" in agents
    assert "docs/frontend_architecture_rules.md" in agents
    assert "before any frontend/UI implementation" in agents
    assert "docs/frontend_architecture_rules.md" in architecture_rules
    assert "`TASK_076_FRONTEND_ARCHITECTURE_RULES_AND_UI_BOUNDARY` is complete" in board
    assert "No frontend code refactor" in task
    assert "No copied-workbook LTR write hardening" in task
