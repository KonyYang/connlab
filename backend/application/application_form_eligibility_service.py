"""Application-form eligibility gate for Intake to Precheck."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.domain import IntakeAsset
from backend.infrastructure.office import OfficeFacade, WordDocumentSnapshot, WordHeaderCellResult

EXPECTED_LTR_HEADER_TEXT = "Laboratory Testing Request"
EXPECTED_LTR_FOOTER_TEXT = "E-3718"

logger = logging.getLogger(__name__)


class WordDocumentReader(Protocol):
    """Port for reading Word header cells and document snapshots."""

    def read_word_header_table_cell(
        self,
        source_path: Path,
        row: int,
        column: int,
    ) -> WordHeaderCellResult: ...

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot: ...


class IntakeAssetStore(Protocol):
    """Read port for intake assets."""

    def get(self, asset_id: str) -> IntakeAsset | None: ...


class ApplicationFormEligibilityNotFoundError(LookupError):
    """Raised when an intake asset cannot be found for eligibility checking."""


@dataclass(frozen=True, slots=True)
class ApplicationFormEligibility:
    """Structured eligibility result for one intake asset."""

    eligible: bool
    reason_code: str
    message: str
    observed_header_cell: str | None = None
    observed_footer_text: str | None = None
    expected_text: str = EXPECTED_LTR_HEADER_TEXT


class ApplicationFormEligibilityService:
    """Validate whether an intake asset can enter Precheck as the application form."""

    _header_row = 1
    _header_column = 2
    _observed_limit = 120

    def __init__(
        self,
        office: WordDocumentReader | None = None,
        expected_text: str = EXPECTED_LTR_HEADER_TEXT,
    ) -> None:
        """Create the eligibility service."""
        self._office = office or OfficeFacade()
        self._expected_text = expected_text
        self._expected_footer_text = EXPECTED_LTR_FOOTER_TEXT

    def evaluate(self, asset: IntakeAsset) -> ApplicationFormEligibility:
        """Evaluate one intake asset for application-form selection."""
        extension = _normalized_extension(asset.extension or asset.original_name)
        if extension != ".docx":
            result = self._result(
                False,
                "not_docx",
                "Select a .docx Laboratory Testing Request form to continue.",
            )
            self._log(asset, result, gateway_mode=None)
            return result

        header_error: Exception | None = None
        try:
            header = self._office.read_word_header_table_cell(
                asset.stored_path,
                self._header_row,
                self._header_column,
            )
        except Exception as exc:
            header_error = exc
            header = None

        observed = _clean_observed(header.value, self._observed_limit) if header else None
        if not observed:
            footer_text = self._footer_marker(asset)
            if footer_text:
                result = self._result(
                    True,
                    "ok_footer_fallback",
                    "Application form is ready for Precheck.",
                    None,
                    footer_text,
                )
                self._log(asset, result, gateway_mode=header.gateway_mode if header else None)
                return result
            if header_error is not None:
                result = self._result(
                    False,
                    "word_header_unreadable",
                    "Unable to verify the Word header. Footer marker E-3718 was not found.",
                    None,
                    None,
                )
                self._log(asset, result, gateway_mode=None, error=header_error)
                return result
            result = self._result(
                False,
                "header_cell_empty",
                'Selected document is not recognized as Laboratory Testing Request. Header table cell (1,2): "empty"',
                None,
                None,
            )
            self._log(asset, result, gateway_mode=header.gateway_mode if header else None)
            return result

        if self._expected_text not in observed:
            footer_text = self._footer_marker(asset)
            if footer_text:
                result = self._result(
                    True,
                    "ok_footer_fallback",
                    "Application form is ready for Precheck.",
                    observed,
                    footer_text,
                )
                self._log(asset, result, gateway_mode=header.gateway_mode)
                return result
            result = self._result(
                False,
                "header_cell_mismatch",
                (
                    "Selected document is not recognized as Laboratory Testing Request. "
                    f'Header table cell (1,2): "{observed}"'
                ),
                observed,
                None,
            )
            self._log(asset, result, gateway_mode=header.gateway_mode)
            return result

        result = self._result(
            True,
            "ok",
            "Application form is ready for Precheck.",
            observed,
            None,
        )
        self._log(asset, result, gateway_mode=header.gateway_mode)
        return result

    def _result(
        self,
        eligible: bool,
        reason_code: str,
        message: str,
        observed_header_cell: str | None = None,
        observed_footer_text: str | None = None,
    ) -> ApplicationFormEligibility:
        """Build a result with the configured expected header text."""
        return ApplicationFormEligibility(
            eligible=eligible,
            reason_code=reason_code,
            message=message,
            observed_header_cell=observed_header_cell,
            observed_footer_text=observed_footer_text,
            expected_text=self._expected_text,
        )

    def _footer_marker(self, asset: IntakeAsset) -> str | None:
        """Return the footer text that confirms the application form, if present."""
        try:
            snapshot = self._office.read_word_document(asset.stored_path)
        except Exception:
            return None
        for footer in snapshot.footers:
            observed = _clean_observed(footer, self._observed_limit)
            if observed and self._expected_footer_text in observed:
                return observed
        return None

    def _log(
        self,
        asset: IntakeAsset,
        result: ApplicationFormEligibility,
        *,
        gateway_mode: str | None,
        error: Exception | None = None,
    ) -> None:
        """Write concise diagnostic context for the header gate."""
        logger.info(
            "application_form_header_gate",
            extra={
                "package_id": asset.package_id,
                "asset_id": asset.asset_id,
                "original_name": asset.original_name,
                "extension": asset.extension,
                "reason_code": result.reason_code,
                "expected_text": result.expected_text,
                "observed_header_cell": result.observed_header_cell,
                "observed_header_cell_length": len(result.observed_header_cell or ""),
                "observed_footer_text": result.observed_footer_text,
                "observed_footer_text_length": len(result.observed_footer_text or ""),
                "gateway_mode": gateway_mode,
                "error_type": type(error).__name__ if error else None,
                "error_message": str(error) if error else None,
            },
        )


def _normalized_extension(value: str) -> str:
    """Normalize file extensions with a leading dot."""
    if value.startswith("."):
        extension = value.lower()
    else:
        extension = Path(value).suffix.lower() if "." in value else value.lower()
    if extension and not extension.startswith("."):
        return f".{extension}"
    return extension


def _clean_observed(value: str | None, limit: int) -> str | None:
    """Clean and limit the observed Word header cell text."""
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value.replace("\x07", " ")).strip()
    if not cleaned:
        return None
    return cleaned[:limit]


class IntakeAssetApplicationFormEligibilityService:
    """Load an intake asset and evaluate whether it can enter Precheck."""

    def __init__(
        self,
        asset_store: IntakeAssetStore,
        eligibility: ApplicationFormEligibilityService | None = None,
    ) -> None:
        """Create the query service."""
        self._asset_store = asset_store
        self._eligibility = eligibility or ApplicationFormEligibilityService()

    def evaluate_asset(self, asset_id: str) -> ApplicationFormEligibility:
        """Return eligibility for one stored intake asset."""
        asset = self._asset_store.get(asset_id)
        if asset is None:
            raise ApplicationFormEligibilityNotFoundError(
                f"Intake asset not found: {asset_id}"
            )
        return self._eligibility.evaluate(asset)
