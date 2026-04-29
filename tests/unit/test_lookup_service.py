from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.lookup_service import LookupNotFoundError, LookupService
from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectStatus,
    SampleInfo,
)


def test_lookup_searches_by_ltr_part_product_and_requestor() -> None:
    service = _service()

    assert service.search_projects("DL-2026-04-001")[0].matched_fields == ("ltr_number",)
    assert service.search_projects("PN-100")[0].matched_fields == ("sample.part_number",)
    assert service.search_projects("Connector")[0].project_no == "PRJ-100"
    assert service.search_projects("Alice")[0].matched_fields == ("requestor",)


def test_sample_summary_returns_structured_rows_and_ltr_numbers() -> None:
    summary = _service().sample_summary("P1")

    assert summary.project_no == "PRJ-100"
    assert summary.ltr_numbers == ("DL-2026-04-001",)
    assert summary.samples[0].part_number == "PN-100"
    assert summary.samples[0].quantity == 12


def test_testing_summary_uses_structured_form_and_spec_assets() -> None:
    summary = _service().testing_summary("P1")

    assert summary.requested_testing == "Durability test per customer specification"
    assert summary.test_type == "Validation"
    assert summary.sample_condition == "Good"
    assert summary.applicable_specifications == ("customer_specification.pdf",)
    assert summary.lab == "DGLAB"


def test_lookup_missing_project_raises_not_found() -> None:
    service = _service()

    with pytest.raises(LookupNotFoundError):
        service.sample_summary("missing")


def _service() -> LookupService:
    """Create a lookup service with in-memory stores."""
    project = Project(
        project_id="P1",
        project_no="PRJ-100",
        product_name="Connector",
        requestor="Alice",
        status=ProjectStatus.LTR_REGISTERED,
    )
    form = ApplicationForm(
        form_id="F1",
        project_id="P1",
        form_no="E-3718",
        revision="H",
        requester="Alice",
        requested_testing="Durability test per customer specification",
        test_type="Validation",
        sample_condition="Good",
        requested_completion_date="2026-05-10",
        lab="DGLAB",
        assigned_personnel="Bob",
    )
    sample = SampleInfo(
        sample_id="S1",
        project_id="P1",
        product_name="Connector",
        part_number="PN-100",
        revision="A",
        quantity=12,
    )
    ltr = LtrRecord(
        ltr_id="L1",
        project_id="P1",
        ltr_number="DL-2026-04-001",
        status=LtrStatus.REGISTERED,
    )
    asset = FileAsset(
        asset_id="A1",
        project_id="P1",
        asset_type=FileAssetType.ATTACHMENT,
        path=Path("customer_specification.pdf"),
        original_name="customer_specification.pdf",
    )
    return LookupService(
        project_repository=_ProjectRepo([project]),
        form_repository=_ByProjectRepo([form], "project_id"),
        sample_repository=_ByProjectRepo([sample], "project_id"),
        ltr_repository=_LtrRepo([ltr]),
        file_asset_repository=_ByProjectRepo([asset], "project_id"),
    )


class _ProjectRepo:
    """In-memory project repository."""

    def __init__(self, projects: list[Project]) -> None:
        """Create a repository."""
        self._projects = {project.project_id: project for project in projects}

    def get(self, project_id: str) -> Project | None:
        """Return one project."""
        return self._projects.get(project_id)

    def list(self) -> list[Project]:
        """Return all projects."""
        return list(self._projects.values())


class _ByProjectRepo:
    """In-memory project-scoped repository."""

    def __init__(self, items: list[object], key: str) -> None:
        """Create a repository."""
        self._items = items
        self._key = key

    def list_by_project(self, project_id: str):
        """Return rows for one project."""
        return [item for item in self._items if getattr(item, self._key) == project_id]


class _LtrRepo(_ByProjectRepo):
    """In-memory LTR repository."""

    def __init__(self, records: list[LtrRecord]) -> None:
        """Create a repository."""
        super().__init__(records, "project_id")
        self._records = records

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR numbers."""
        return [record for record in self._records if query in record.ltr_number]
