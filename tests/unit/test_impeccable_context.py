from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_product_context_declares_product_register_and_scope() -> None:
    """PRODUCT.md gives impeccable the correct product UI context."""
    source = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")

    assert "## Register\n\nproduct" in source
    assert "laboratory engineers" in source
    assert "Workflow before tools" in source
    assert "Matrix, Reports, or AI" in source


def test_design_context_uses_stitch_sections_and_real_stack() -> None:
    """DESIGN.md follows the expected structure and avoids stale stack claims."""
    source = (ROOT / "DESIGN.md").read_text(encoding="utf-8")

    for heading in [
        "## 1. Overview",
        "## 2. Colors",
        "## 3. Typography",
        "## 4. Elevation",
        "## 5. Components",
        "## 6. Do's and Don'ts",
    ]:
        assert heading in source
    assert "Tailwind" not in source
    assert "shadcn" not in source
    assert "The Lab Ledger Workbench" in source


def test_design_json_sidecar_is_valid_and_mentions_core_components() -> None:
    """DESIGN.json sidecar is valid for future impeccable/live usage."""
    data = json.loads((ROOT / "DESIGN.json").read_text(encoding="utf-8"))

    assert data["schemaVersion"] == 2
    assert data["narrative"]["northStar"] == "The Lab Ledger Workbench"
    assert {component["kind"] for component in data["components"]} >= {
        "button",
        "chip",
        "card",
    }


def test_design_context_uses_cool_low_saturation_palette() -> None:
    """UI palette uses cool white / blue-gray surfaces and blue-cyan-green function colors."""
    design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    styles = (ROOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")

    for term in [
        "#f4f7fb",
        "#fbfdff",
        "#e8eef6",
        "#1f66d1",
        "#0f8ea8",
        "#2f8f68",
        "#eef4fb",
        "#e7f0fb",
        "#bfd7f2",
    ]:
        assert term in design
        assert term in styles

    assert "light blue-gray navigation layer" in design

    for stale_color in [
        "#f4efe4",
        "#fffaf0",
        "#e9dfce",
        "#9a4c25",
    ]:
        assert stale_color not in design
        assert stale_color not in styles
