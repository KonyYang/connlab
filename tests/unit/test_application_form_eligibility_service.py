from __future__ import annotations

from pathlib import Path

from backend.application.application_form_eligibility_service import (
    ApplicationFormEligibilityNotFoundError,
    ApplicationFormEligibilityService,
    IntakeAssetApplicationFormEligibilityService,
)
from backend.domain import IntakeAsset, IntakeAssetRole
from backend.infrastructure.office import WordDocumentSnapshot, WordHeaderCellResult


class FakeOfficeReader:
    def __init__(self, header_value: str | None, footer_values: list[str] | None = None) -> None:
        self.header_value = header_value
        self.footer_values = footer_values or []

    def read_word_header_table_cell(
        self,
        source_path: Path,
        row: int,
        column: int,
    ) -> WordHeaderCellResult:
        assert row == 1
        assert column == 2
        return WordHeaderCellResult(value=self.header_value, gateway_mode="fake")

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot:
        return WordDocumentSnapshot(
            paragraphs=[],
            tables=[],
            headers=[],
            footers=self.footer_values,
            raw_text="\n".join(self.footer_values),
        )


class FakeAssetStore:
    def __init__(self, asset: IntakeAsset | None) -> None:
        self.asset = asset

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self.asset if self.asset and self.asset.asset_id == asset_id else None


def test_application_form_eligibility_accepts_matching_docx_header() -> None:
    service = ApplicationFormEligibilityService(
        FakeOfficeReader("Laboratory Testing Request\r\x07")
    )

    result = service.evaluate(_asset("form.docx"))

    assert result.eligible is True
    assert result.reason_code == "ok"
    assert result.observed_header_cell == "Laboratory Testing Request"


def test_application_form_eligibility_rejects_non_docx() -> None:
    result = ApplicationFormEligibilityService(FakeOfficeReader(None)).evaluate(
        _asset("legacy.doc")
    )

    assert result.eligible is False
    assert result.reason_code == "not_docx"
    assert ".docx Laboratory Testing Request" in result.message


def test_application_form_eligibility_reports_observed_mismatch() -> None:
    result = ApplicationFormEligibilityService(
        FakeOfficeReader("Connector Test Request")
    ).evaluate(_asset("form.docx"))

    assert result.eligible is False
    assert result.reason_code == "header_cell_mismatch"
    assert result.observed_header_cell == "Connector Test Request"
    assert 'Header table cell (1,2): "Connector Test Request"' in result.message


def test_application_form_eligibility_reports_empty_header_cell() -> None:
    result = ApplicationFormEligibilityService(FakeOfficeReader("\r\x07")).evaluate(
        _asset("form.docx")
    )

    assert result.eligible is False
    assert result.reason_code == "header_cell_empty"
    assert 'Header table cell (1,2): "empty"' in result.message


def test_application_form_eligibility_accepts_footer_marker_when_header_changes() -> None:
    service = ApplicationFormEligibilityService(
        FakeOfficeReader("Connector Test Request", ["Form No. E-3718 Rev H"])
    )

    result = service.evaluate(_asset("form.docx"))

    assert result.eligible is True
    assert result.reason_code == "ok_footer_fallback"
    assert result.observed_header_cell == "Connector Test Request"
    assert result.observed_footer_text == "Form No. E-3718 Rev H"


def test_intake_asset_eligibility_service_loads_asset() -> None:
    asset = _asset("form.docx", asset_id="asset-1")
    service = IntakeAssetApplicationFormEligibilityService(
        FakeAssetStore(asset),
        ApplicationFormEligibilityService(FakeOfficeReader("Laboratory Testing Request")),
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
