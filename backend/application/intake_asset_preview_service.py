"""Preview registered intake assets for the New Project intake workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from backend.domain import IntakeAsset
from backend.modules.intake.application_form_parser import (
    ApplicationFormParser,
    ParsedApplicationForm,
    ParsedSampleInfo,
)


class IntakeAssetPreviewNotFoundError(LookupError):
    """Raised when an intake asset cannot be found."""


class IntakeAssetPreviewError(RuntimeError):
    """Raised when preview generation fails for a registered asset."""


class IntakeAssetStore(Protocol):
    """Persistence behavior required for intake asset preview."""

    def get(self, asset_id: str) -> IntakeAsset | None:
        """Return one intake asset by id."""


@dataclass(frozen=True, slots=True)
class PreviewMetadata:
    """Safe file metadata for preview rendering."""

    asset_id: str
    original_name: str
    extension: str
    mime_type: str | None
    size_bytes: int
    asset_role: str


@dataclass(frozen=True, slots=True)
class PreviewField:
    """One business field shown in a structured preview."""

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class PreviewTable:
    """A compact table-like section for attachment preview."""

    title: str
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class IntakeAssetPreview:
    """Typed intake asset preview payload."""

    kind: str
    metadata: PreviewMetadata
    title: str
    fields: tuple[PreviewField, ...] = field(default_factory=tuple)
    tables: tuple[PreviewTable, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    message: str | None = None


class IntakeAssetPreviewService:
    """Build safe attachment previews from registered intake asset records."""

    _docx_extensions = {".docx"}

    def __init__(
        self,
        asset_store: IntakeAssetStore,
        parser: ApplicationFormParser | None = None,
    ) -> None:
        """Create the preview service with repository and parser dependencies."""
        self._asset_store = asset_store
        self._parser = parser or ApplicationFormParser()

    def preview_asset(self, asset_id: str) -> IntakeAssetPreview:
        """Return a preview for one registered intake asset."""
        asset = self._asset_store.get(asset_id)
        if asset is None:
            raise IntakeAssetPreviewNotFoundError(f"Intake asset not found: {asset_id}")

        metadata = _metadata(asset)
        extension = _normalized_extension(asset)
        if extension in self._docx_extensions:
            return self._docx_preview(asset, metadata)
        return IntakeAssetPreview(
            kind="unsupported",
            metadata=metadata,
            title="Preview not available",
            message=f"{extension or 'This file type'} is registered, but structured preview is not implemented in this task.",
        )

    def _docx_preview(
        self,
        asset: IntakeAsset,
        metadata: PreviewMetadata,
    ) -> IntakeAssetPreview:
        """Build a structured Laboratory Testing Request preview from a DOCX asset."""
        if not asset.stored_path.is_file():
            raise IntakeAssetPreviewError(
                f"Stored intake asset file is missing: {asset.original_name}"
            )
        try:
            parsed = self._parser.parse(asset.stored_path)
            outline = self._parser.table_outline(asset.stored_path)
        except Exception as exc:
            raise IntakeAssetPreviewError(
                f"Unable to preview Word application form: {asset.original_name}"
            ) from exc

        fields = _preview_fields(parsed)
        tables = tuple(
            table
            for table in (
                _sample_table(parsed),
                _requested_testing_table(parsed),
                _document_outline_table(outline),
            )
            if table is not None
        )
        warnings = _preview_warnings(parsed, tables)
        return IntakeAssetPreview(
            kind="docx_application_form",
            metadata=metadata,
            title="Laboratory Testing Request preview",
            fields=fields,
            tables=tables,
            warnings=warnings,
        )


def _metadata(asset: IntakeAsset) -> PreviewMetadata:
    """Convert an intake asset to path-free preview metadata."""
    return PreviewMetadata(
        asset_id=asset.asset_id,
        original_name=asset.original_name,
        extension=asset.extension,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        asset_role=asset.asset_role.value,
    )


def _normalized_extension(asset: IntakeAsset) -> str:
    """Return the lower-case asset extension with a leading dot."""
    extension = asset.extension or Path(asset.original_name).suffix
    extension = extension.lower()
    if extension and not extension.startswith("."):
        return f".{extension}"
    return extension


def _preview_fields(parsed: ParsedApplicationForm) -> tuple[PreviewField, ...]:
    """Return business-recognizable fields for operator verification."""
    values = [
        ("Form No.", parsed.form_no),
        ("Revision", parsed.form_rev),
        ("Reference doc.", parsed.reference_doc),
        ("Requested By", parsed.requested_by),
        ("Phone #", parsed.phone),
        ("Date", parsed.request_date),
        ("Email", parsed.email),
        ("Business Unit", parsed.business_unit),
        ("Mfg. Site", parsed.manufacturing_site),
        ("Project #", parsed.project_number),
        ("Results Format", parsed.results_format),
        ("Test Type", parsed.test_type),
        ("Test Sample Status", parsed.sample_status),
        ("Project Type", parsed.project_type),
        ("Completion Date", parsed.requested_completion_date),
        ("Post-Testing Disposition", parsed.post_testing_disposition),
        ("Confidential", parsed.confidential),
        ("Subcontracted", parsed.subcontract),
    ]
    return tuple(PreviewField(label, value) for label, value in values if _text(value))


def _sample_table(parsed: ParsedApplicationForm) -> PreviewTable | None:
    """Return sample rows extracted from the application form."""
    if not parsed.samples:
        return None
    headers = (
        "Product Name",
        "Part Number",
        "Revision",
        "Traceability / Lot",
        "Material",
        "Plating",
        "Housing",
        "Quantity",
    )
    rows = tuple(_sample_row(sample) for sample in parsed.samples)
    return PreviewTable("Test Sample Information", headers, rows)


def _sample_row(sample: ParsedSampleInfo) -> tuple[str, ...]:
    """Convert one parsed sample to preview table cells."""
    return (
        _text(sample.product_name),
        _text(sample.part_number),
        _text(sample.revision),
        _text(sample.lot_or_traceability),
        _text(sample.material),
        _text(sample.plating),
        _text(sample.housing_material),
        _text(sample.quantity),
    )


def _requested_testing_table(parsed: ParsedApplicationForm) -> PreviewTable | None:
    """Return requested testing and additional information as preview rows."""
    rows: list[tuple[str, str]] = []
    if _text(parsed.requested_testing_description):
        rows.append(("Requested Testing", _text(parsed.requested_testing_description)))
    if _text(parsed.additional_information):
        rows.append(("Additional Information", _text(parsed.additional_information)))
    if _text(parsed.send_copies_recipients):
        rows.append(("Send Copies To", _text(parsed.send_copies_recipients)))
    if not rows:
        return None
    return PreviewTable(
        "Requested Testing",
        ("Field", "Value"),
        tuple(rows),
    )


def _document_outline_table(outline: tuple[tuple[str, str], ...]) -> PreviewTable | None:
    """Return a compact outline of non-empty Word tables for orientation."""
    if not outline:
        return None
    return PreviewTable("Document structure", ("Section", "First visible text"), outline)


def _preview_warnings(
    parsed: ParsedApplicationForm,
    tables: tuple[PreviewTable, ...],
) -> tuple[str, ...]:
    """Return non-blocking preview warnings for partial parses."""
    warnings: list[str] = []
    if not parsed.requested_by and not parsed.email:
        warnings.append("Requestor fields were not found in the Word preview.")
    if not parsed.samples:
        warnings.append("Sample rows were not found in the Word preview.")
    if not tables:
        warnings.append("No structured sections were found for preview.")
    return tuple(warnings)


def _text(value: object | None) -> str:
    """Return a stripped text value for preview rendering."""
    if value is None:
        return ""
    return str(value).strip()
