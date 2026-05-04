"""Preview registered intake assets for the New Project intake workspace."""

from __future__ import annotations

import base64
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
    image_data_url: str | None = None


class IntakeAssetPreviewService:
    """Build safe attachment previews from registered intake asset records."""

    _docx_extensions = {".docx"}
    _image_extensions = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}
    _max_inline_image_bytes = 5 * 1024 * 1024

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
        if extension in self._image_extensions:
            return self._image_preview(asset, metadata)
        if extension in self._docx_extensions:
            return self._docx_preview(asset, metadata)
        return _metadata_preview(metadata, extension)

    def _image_preview(
        self,
        asset: IntakeAsset,
        metadata: PreviewMetadata,
    ) -> IntakeAssetPreview:
        """Build a browser-safe inline image preview for a stored image asset."""
        if not asset.stored_path.is_file():
            raise IntakeAssetPreviewError(
                f"Stored intake asset file is missing: {asset.original_name}"
            )
        if asset.size_bytes > self._max_inline_image_bytes:
            return _metadata_preview(
                metadata,
                _normalized_extension(asset),
                "Image preview is metadata-only because the file is larger than the inline preview limit.",
            )
        image_bytes = asset.stored_path.read_bytes()
        mime_type = metadata.mime_type or _image_mime_type(_normalized_extension(asset))
        return IntakeAssetPreview(
            kind="image",
            metadata=metadata,
            title="Image preview",
            image_data_url=f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}",
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
        except Exception as exc:
            raise IntakeAssetPreviewError(
                f"Unable to preview Word application form: {asset.original_name}"
            ) from exc
        if not _looks_like_application_form(parsed):
            return _metadata_preview(
                metadata,
                _normalized_extension(asset),
                "This Word document is registered as an attachment. It does not look like a Laboratory Test Request application form.",
            )

        fields = _preview_fields(parsed)
        tables = tuple(
            table
            for table in (
                _sample_table(parsed),
                _requested_testing_table(parsed),
                _additional_information_table(parsed),
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


def _metadata_preview(
    metadata: PreviewMetadata,
    extension: str,
    message: str | None = None,
) -> IntakeAssetPreview:
    """Return a path-free metadata-only preview for non-rendered attachments."""
    file_type = _file_type_label(extension)
    return IntakeAssetPreview(
        kind="metadata_only",
        metadata=metadata,
        title=f"{file_type} attachment",
        fields=(
            PreviewField("File name", metadata.original_name),
            PreviewField("File type", file_type),
            PreviewField("File size", _format_bytes(metadata.size_bytes)),
            PreviewField("Role", metadata.asset_role.replace("_", " ")),
        ),
        message=message or f"{file_type} content is stored with this intake package. Detailed rendering is not implemented in this task.",
    )


def _normalized_extension(asset: IntakeAsset) -> str:
    """Return the lower-case asset extension with a leading dot."""
    extension = asset.extension or Path(asset.original_name).suffix
    extension = extension.lower()
    if extension and not extension.startswith("."):
        return f".{extension}"
    return extension


def _image_mime_type(extension: str) -> str:
    """Return a browser-friendly image MIME type for known image extensions."""
    if extension in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if extension == ".png":
        return "image/png"
    if extension == ".gif":
        return "image/gif"
    if extension == ".bmp":
        return "image/bmp"
    if extension in {".tif", ".tiff"}:
        return "image/tiff"
    return "application/octet-stream"


def _file_type_label(extension: str) -> str:
    """Return an operator-readable file type label."""
    labels = {
        ".doc": "Word",
        ".docx": "Word",
        ".xls": "Excel",
        ".xlsx": "Excel",
        ".pdf": "PDF",
        ".msg": "MSG",
    }
    return labels.get(extension, (extension.replace(".", "").upper() or "File"))


def _format_bytes(value: int) -> str:
    """Return a compact file size string for metadata previews."""
    if value >= 1024 * 1024:
        return f"{value / 1024 / 1024:.1f} MB"
    if value >= 1024:
        return f"{round(value / 1024)} KB"
    return f"{value} B"


def _looks_like_application_form(parsed: ParsedApplicationForm) -> bool:
    """Return true when a Word file has enough request-form signals for structured preview."""
    return any(
        [
            _text(parsed.form_no),
            _text(parsed.form_rev),
            _text(parsed.requested_by),
            _text(parsed.email),
            _text(parsed.requested_testing_description),
            parsed.samples,
        ]
    )


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
        ("Requested Completion Date", parsed.requested_completion_date),
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
        "Part Number / Revision",
        "Traceability Manufacturing Lot Info",
        "Contact Base Material",
        "Contact Plating",
        "Contact Lubricant",
        "Housing Material",
        "Quantity",
    )
    rows = tuple(_sample_row(sample) for sample in parsed.samples)
    return PreviewTable("Test Sample Information", headers, rows)


def _part_number_revision(sample: ParsedSampleInfo) -> str:
    """Combine part number and revision, avoiding duplication."""
    part_number = _text(sample.part_number)
    revision = _text(sample.revision)
    if not part_number:
        return revision
    if not revision:
        return part_number
    if part_number.strip().lower().endswith(f" {revision.strip().lower()}"):
        return part_number
    return f"{part_number} {revision}"


def _sample_row(sample: ParsedSampleInfo) -> tuple[str, ...]:
    """Convert one parsed sample to preview table cells."""
    return (
        _text(sample.product_name),
        _part_number_revision(sample),
        _text(sample.lot_or_traceability),
        _text(sample.material),
        _text(sample.plating),
        _text(sample.lubricant),
        _text(sample.housing_material),
        _text(sample.quantity),
    )


def _requested_testing_table(parsed: ParsedApplicationForm) -> PreviewTable | None:
    """Return requested testing rows as a two-column preview table."""
    if parsed.requested_testing_rows:
        rows = tuple(
            (r.test_to_be_performed, r.applicable_specification)
            for r in parsed.requested_testing_rows
        )
        return PreviewTable(
            "Description of Requested Testing",
            ("Tests to be Performed", "Applicable Specifications"),
            rows,
        )
    if _text(parsed.requested_testing_description):
        return PreviewTable(
            "Description of Requested Testing",
            ("Tests to be Performed", "Applicable Specifications"),
            ((_text(parsed.requested_testing_description), ""),),
        )
    return None


def _additional_information_table(parsed: ParsedApplicationForm) -> PreviewTable | None:
    """Return Additional Information as a separate preview table."""
    if _text(parsed.additional_information):
        return PreviewTable(
            "Additional Information",
            ("Value",),
            ((_text(parsed.additional_information),),),
        )
    return None


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
