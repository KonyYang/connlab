from __future__ import annotations

from pathlib import Path

from backend.application.application_form_eligibility_service import (
    ApplicationFormEligibilityNotFoundError,
    ApplicationFormEligibilityService,
    IntakeAssetApplicationFormEligibilityService,
)
from backend.domain import IntakeAsset, IntakeAssetRole
from backend.infrastructure.office import WordHeaderCellResult


class FakeHeaderReader:
    def __init__(self, value: str | None) -> None:
        self.value = value

    def read_word_header_table_cell(
        self,
        source_path: Path,
        row: int,
        column: int,
    ) -> WordHeaderCellResult:
        assert row == 1
        assert column == 2
        return WordHeaderCellResult(value=self.value, gateway_mode="fake")


class FakeAssetStore:
    def __init__(self, asset: IntakeAsset | None) -> None:
        self.asset = asset

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self.asset if self.asset and self.asset.asset_id == asset_id else None


def test_application_form_eligibility_accepts_matching_docx_header() -> None:
    service = ApplicationFormEligibilityService(
        FakeHeaderReader("Laboratory Testing Request\r\x07")
    )

    result = service.evaluate(_asset("form.docx"))

    assert result.eligible is True
    assert result.reason_code == "ok"
    assert result.observed_header_cell == "Laboratory Testing Request"


def test_application_form_eligibility_rejects_non_docx() -> None:
    result = ApplicationFormEligibilityService(FakeHeaderReader(None)).evaluate(
        _asset("legacy.doc")
    )

    assert result.eligible is False
    assert result.reason_code == "not_docx"
    assert ".docx Laboratory Testing Request" in result.message


def test_application_form_eligibility_reports_observed_mismatch() -> None:
    result = ApplicationFormEligibilityService(
        FakeHeaderReader("Connector Test Request")
    ).evaluate(_asset("form.docx"))

    assert result.eligible is False
    assert result.reason_code == "header_cell_mismatch"
    assert result.observed_header_cell == "Connector Test Request"
    assert 'Header table cell (1,2): "Connector Test Request"' in result.message


def test_application_form_eligibility_reports_empty_header_cell() -> None:
    result = ApplicationFormEligibilityService(FakeHeaderReader("\r\x07")).evaluate(
        _asset("form.docx")
    )

    assert result.eligible is False
    assert result.reason_code == "header_cell_empty"
    assert 'Header table cell (1,2): "empty"' in result.message


def test_intake_asset_eligibility_service_loads_asset() -> None:
    asset = _asset("form.docx", asset_id="asset-1")
    service = IntakeAssetApplicationFormEligibilityService(
        FakeAssetStore(asset),
        ApplicationFormEligibilityService(FakeHeaderReader("Laboratory Testing Request")),
    )

    assert service.evaluate_asset("asset-1").eligible is True


def test_intake_asset_eligibility_service_rejects_missing_asset() -> None:
    service = IntakeAssetApplicationFormEligibilityService(FakeAssetStore(None))

    try:
        service.evaluate_asset("missing")
    except ApplicationFormEligibilityNotFoundError as exc:
        assert "Intake asset not found: missing" in str(exc)
    else:
        raise AssertionError("Expected ApplicationFormEligibilityNotFoundError")


def _asset(name: str, asset_id: str = "asset-a") -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=name,
        stored_path=Path(name),
        extension=Path(name).suffix,
        mime_type="application/octet-stream",
        size_bytes=10,
        sha256="a" * 64,
        asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
    )
