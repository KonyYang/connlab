from __future__ import annotations

import pytest

from backend.application.official_project_workspace_naming import (
    OfficialWorkspaceNamingError,
    build_official_project_folder_name,
)


def test_official_folder_name_replaces_invalid_windows_characters() -> None:
    name = build_official_project_folder_name(
        dl_number="DL-2025-11-074",
        product_description='Coolpower 3.40mm Pin:Busbar/Socket*PCB',
        test_description='Qualification test? "A"',
    )

    assert name == "DL-2025-11-074 Coolpower 3.40mm Pin Busbar Socket PCB Qualification test A"
    for invalid in '<>:"/\\|?*':
        assert invalid not in name


def test_official_folder_name_uses_business_fallbacks() -> None:
    name = build_official_project_folder_name(
        dl_number="DL-2025-11-074",
        product_description=" ",
        test_description=None,
    )

    assert name == "DL-2025-11-074 Product Qualification test"


def test_official_folder_name_preserves_dl_prefix_when_truncating() -> None:
    name = build_official_project_folder_name(
        dl_number="DL-2025-11-074",
        product_description="A" * 200,
        test_description="B" * 200,
        max_segment_length=80,
    )

    assert name.startswith("DL-2025-11-074 ")
    assert len(name) <= 80


def test_official_folder_name_rejects_missing_dl_number() -> None:
    with pytest.raises(OfficialWorkspaceNamingError, match="DL number is required"):
        build_official_project_folder_name(
            dl_number=" ",
            product_description="Product",
            test_description="Qualification test",
        )
