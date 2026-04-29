from pathlib import Path

import pytest

from backend.application.ltr_readiness_service import (
    LtrReadinessError,
    LtrReadinessNotFoundError,
    LtrReadinessService,
)
from backend.domain import ApplicationForm, FileAsset, FileAssetType, Project, SampleInfo


def test_ltr_readiness_blocks_missing_required_fields() -> None:
    service = _build_service(projects={"P1": _project()})

    result = service.evaluate_project("P1")

    assert result.status == "blocked"
    blocker_keys = {field.key for field in result.blockers}
    assert "project_type" in blocker_keys
    assert "description_pn" in blocker_keys
    assert "phone" in blocker_keys


def test_ltr_readiness_keeps_dl_pending_until_preview_generates_it() -> None:
    service = _build_service(
        projects={"P1": _project()},
        forms={"P1": [_complete_form()]},
        samples={"P1": [_sample()]},
        assets={"P1": [_spec_asset()]},
    )

    result = service.evaluate_project("P1")

    assert result.status == "review_required"
    assert result.blockers == ()
    dl = next(field for field in result.fields if field.key == "dl")
    assert dl.state == "pending_preview"
    assert dl.source == "ltr.preview.pending_generation"


def test_ltr_readiness_returns_review_required_when_blockers_are_confirmed() -> None:
    service = _build_service(
        projects={"P1": _project()},
        forms={"P1": [_complete_form()]},
        samples={"P1": [_sample()]},
        assets={"P1": [_spec_asset()]},
    )

    result = service.evaluate_project("P1", proposed_ltr_number=" dl-2026-04-001 ")

    fields = {field.key: field for field in result.fields}
    assert result.status == "review_required"
    assert result.blockers == ()
    assert fields["dl"].value == "DL-2026-04-001"
    assert fields["dl"].source == "ltr.preview.proposed_ltr_number"
    assert fields["dl"].state == "confirmed"
    assert fields["location"].state == "needs_review"
    assert fields["project_leader"].state == "needs_review"


def test_ltr_readiness_uses_explicit_placeholder_policy() -> None:
    service = _build_service(projects={"P1": _project()})

    result = service.evaluate_project("P1")

    fields = {field.key: field for field in result.fields}
    assert fields["test_result"].state == "placeholder"
    assert fields["test_result"].value == "Pending"
    assert fields["failed_item"].state == "placeholder"
    assert fields["failed_item"].value == "N/A"


def test_ltr_readiness_rejects_invalid_proposed_ltr_number() -> None:
    service = _build_service(projects={"P1": _project()})

    with pytest.raises(LtrReadinessError, match="LTR number must match"):
        service.evaluate_project("P1", proposed_ltr_number="bad")


def test_ltr_readiness_reports_missing_project() -> None:
    service = _build_service()

    with pytest.raises(LtrReadinessNotFoundError, match="Project not found"):
        service.evaluate_project("missing")


class _ProjectRepo:
    def __init__(self, rows: dict[str, Project]) -> None:
        self._rows = rows

    def get(self, project_id: str) -> Project | None:
        return self._rows.get(project_id)


class _FormRepo:
    def __init__(self, rows: dict[str, list[ApplicationForm]]) -> None:
        self._rows = rows

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return self._rows.get(project_id, [])


class _SampleRepo:
    def __init__(self, rows: dict[str, list[SampleInfo]]) -> None:
        self._rows = rows

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        return self._rows.get(project_id, [])


class _AssetRepo:
    def __init__(self, rows: dict[str, list[FileAsset]]) -> None:
        self._rows = rows

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        return self._rows.get(project_id, [])


def _build_service(
    *,
    projects: dict[str, Project] | None = None,
    forms: dict[str, list[ApplicationForm]] | None = None,
    samples: dict[str, list[SampleInfo]] | None = None,
    assets: dict[str, list[FileAsset]] | None = None,
) -> LtrReadinessService:
    return LtrReadinessService(
        project_repository=_ProjectRepo(projects or {}),
        form_repository=_FormRepo(forms or {}),
        sample_repository=_SampleRepo(samples or {}),
        file_asset_repository=_AssetRepo(assets or {}),
    )


def _project() -> Project:
    return Project(
        project_id="P1",
        project_no="PRJ-001",
        product_name="Connector",
        requestor="Alice",
    )


def _complete_form() -> ApplicationForm:
    return ApplicationForm(
        form_id="F1",
        project_id="P1",
        form_no="E-3718",
        revision="H",
        requester="Alice",
        phone="555-0101",
        email="alice@example.test",
        manufacturing_site="DGLAB",
        requested_testing="Durability test per specification",
        subcontract_allowed=False,
        test_type="Validation",
        project_type="Qualification",
        post_testing_disposition="Return samples",
        additional_information="PO pending",
        lab="DGLAB",
        assigned_personnel="Bob",
    )


def _sample() -> SampleInfo:
    return SampleInfo(
        sample_id="S1",
        project_id="P1",
        product_name="Connector",
        part_number="PN-100",
    )


def _spec_asset() -> FileAsset:
    return FileAsset(
        asset_id="A1",
        project_id="P1",
        asset_type=FileAssetType.ATTACHMENT,
        path=Path("spec.pdf"),
        original_name="Connector spec.pdf",
    )
