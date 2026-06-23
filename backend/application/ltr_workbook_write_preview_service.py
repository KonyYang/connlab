"""No-write preview for mapping project data to the LTR workbook row."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from backend.application.sample_description import format_description_pn
from backend.domain import ApplicationForm, Project, SampleInfo
from backend.infrastructure.office import LtrWorkbookRowData
from backend.infrastructure.office.models import LtrWorkbookSnapshot
from backend.modules.ltr import LtrNumberError, LtrNumberKind, parse_ltr_number
from backend.shared.config import LtrWorkbookSettings


class LtrWorkbookWritePreviewError(ValueError):
    """Raised when an LTR workbook write preview cannot be built."""


@dataclass(frozen=True, slots=True)
class PreviewLtrWorkbookWriteCommand:
    """Input command for a no-write LTR workbook row preview."""

    ltr_number: str
    plan_date: date
    test_item: str
    sample_description: str
    location: str
    test_type_in_sheet: str
    project_leader: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookWriteColumnPreview:
    """One target workbook column and its preview value."""

    column: str
    field_name: str
    value: object


@dataclass(frozen=True, slots=True)
class LtrWorkbookWritePreview:
    """No-write preview of an LTR workbook row write."""

    project_id: str
    workbook_path: Path | None
    target_sheet: str
    target_row: int | None
    row_data: LtrWorkbookRowData
    columns: tuple[LtrWorkbookWriteColumnPreview, ...]
    warnings: tuple[str, ...] = ()


class ProjectStore(Protocol):
    """Project repository behavior required by the preview service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ApplicationFormStore(Protocol):
    """Application form repository behavior required by the preview service."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


class SampleInfoStore(Protocol):
    """Sample repository behavior required by the preview service."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return sample rows for a project."""


class LtrWorkbookSnapshotProvider(Protocol):
    """Optional read-only workbook snapshot provider."""

    def get_snapshot(self) -> LtrWorkbookSnapshot | None:
        """Return the current read-only workbook snapshot."""


class LtrWorkbookWritePreviewService:
    """Build no-write LTR workbook row previews from confirmed project data."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        application_form_store: ApplicationFormStore,
        sample_store: SampleInfoStore,
        workbook_settings: LtrWorkbookSettings,
        snapshot_provider: LtrWorkbookSnapshotProvider | None = None,
    ) -> None:
        """Create the preview service."""
        self._projects = project_store
        self._forms = application_form_store
        self._samples = sample_store
        self._settings = workbook_settings
        self._snapshot_provider = snapshot_provider

    def preview_project(
        self,
        project_id: str,
        command: PreviewLtrWorkbookWriteCommand,
    ) -> LtrWorkbookWritePreview:
        """Return the no-write workbook row preview for one project."""
        project = self._projects.get(project_id)
        if project is None:
            raise LtrWorkbookWritePreviewError(f"Project not found: {project_id}")
        parsed_number = _parse_standard_number(command.ltr_number)
        form = _latest(self._forms.list_by_project(project_id))
        samples = self._samples.list_by_project(project_id)
        snapshot = self._snapshot()
        target_sheet = f"{parsed_number.year:04d}"
        target_row = _target_row(snapshot, target_sheet)
        row_data = LtrWorkbookRowData(
            month=command.plan_date.strftime("%b"),
            total=max((target_row or 2) - 2, 0),
            monthly_number=parsed_number.sequence or 0,
            dl_number=parsed_number.normalized,
            project_type=_project_type_to_ltr_value(getattr(form, "project_type", None)),
            description_pn=_text(command.sample_description) or format_description_pn(samples),
            test_item=_required_text(command.test_item, "Test Item"),
            test_type=_required_text(command.test_type_in_sheet, "Test Type in sheet"),
            requested_by=_text(project.requestor) or _text(getattr(form, "requester", None)),
            location=_required_mfg_site(form),
            project_leader=_required_text(command.project_leader, "Project Leader"),
            test_result=None,
            failed_item=None,
            sample_deposition=_text(getattr(form, "post_testing_disposition", None)),
            sub_contract=_subcontract_value(form),
            test_fee=None,
            remarks_po=_text(getattr(form, "additional_information", None)),
        )
        return LtrWorkbookWritePreview(
            project_id=project_id,
            workbook_path=self._settings.path,
            target_sheet=target_sheet,
            target_row=target_row,
            row_data=row_data,
            columns=_column_previews(row_data),
            warnings=_warnings(self._settings, snapshot, target_sheet),
        )

    def _snapshot(self) -> LtrWorkbookSnapshot | None:
        """Return a snapshot when one is available without opening for write."""
        if self._snapshot_provider is None:
            return None
        return self._snapshot_provider.get_snapshot()


def _parse_standard_number(value: str):
    """Parse and require a standard DL number."""
    try:
        parsed = parse_ltr_number(value)
    except LtrNumberError as exc:
        raise LtrWorkbookWritePreviewError(str(exc)) from exc
    if parsed.kind is not LtrNumberKind.STANDARD_DL or parsed.year is None:
        raise LtrWorkbookWritePreviewError(
            "LTR workbook write preview requires a DL-YYYY-MM-NNN number."
        )
    return parsed


def _latest(values: list[ApplicationForm]) -> ApplicationForm | None:
    """Return the latest form record by repository order."""
    return values[-1] if values else None


def _target_row(snapshot: LtrWorkbookSnapshot | None, sheet_name: str) -> int | None:
    """Return the likely target row when the snapshot can identify the sheet."""
    if snapshot is None or sheet_name not in snapshot.readable_sheet_names:
        return None
    return len(snapshot.existing_ltr_numbers) + 2


def _column_previews(
    row_data: LtrWorkbookRowData,
) -> tuple[LtrWorkbookWriteColumnPreview, ...]:
    """Return workbook A:Q column previews."""
    field_names = (
        "month",
        "total",
        "monthly_number",
        "dl_number",
        "project_type",
        "description_pn",
        "test_item",
        "test_type",
        "requested_by",
        "location",
        "project_leader",
        "test_result",
        "failed_item",
        "sample_deposition",
        "sub_contract",
        "test_fee",
        "remarks_po",
    )
    return tuple(
        LtrWorkbookWriteColumnPreview(
            column=chr(ord("A") + index),
            field_name=field_name,
            value=value,
        )
        for index, (field_name, value) in enumerate(
            zip(field_names, row_data.as_excel_row(), strict=True)
        )
    )


def _warnings(
    settings: LtrWorkbookSettings,
    snapshot: LtrWorkbookSnapshot | None,
    target_sheet: str,
) -> tuple[str, ...]:
    """Return preview-only warnings that do not mutate the workbook."""
    warnings: list[str] = []
    if settings.path is None:
        warnings.append("LTR workbook path is not configured.")
    if snapshot is None:
        warnings.append("Workbook snapshot is unavailable; target row is unknown.")
    elif target_sheet not in snapshot.readable_sheet_names:
        warnings.append(f"Target workbook sheet is not in the snapshot: {target_sheet}")
    return tuple(warnings)


def _subcontract_value(form: ApplicationForm | None) -> str | None:
    """Return subcontract value as workbook-ready text."""
    if form is None:
        return None
    if form.subcontract_allowed is not None:
        return "Yes" if form.subcontract_allowed else "No"
    return _text(form.subcontract)


def _required_text(value: str, label: str) -> str:
    """Return stripped required setup text."""
    text = _text(value)
    if text is None:
        raise LtrWorkbookWritePreviewError(f"{label} is required.")
    return text


def _required_mfg_site(form: ApplicationForm | None) -> str:
    """Return required Mfg. Site workbook value from the application form."""
    text = _text(getattr(form, "manufacturing_site", None))
    if text is None:
        raise LtrWorkbookWritePreviewError("Mfg. Site is required.")
    return text


def _project_type_to_ltr_value(project_type: object) -> str:
    """Map ConnLab project type to LTR workbook E-column value."""
    source = _text(project_type)
    if source is None:
        raise LtrWorkbookWritePreviewError("Project Type has no LTR workbook mapping: <empty>")
    mapping = {
        "New Product Development": "NPD",
        "Product Extension": "PEX",
        "Innovation": "ADM",
        "Lab Activities (Lab Use Only)": "ADM",
        "Operational Support": "OPS",
        "Cost Reduction": "CR",
    }
    target = mapping.get(source)
    if target is None:
        raise LtrWorkbookWritePreviewError(
            f"Project Type has no LTR workbook mapping: {source}"
        )
    return target


def _text(value: object) -> str | None:
    """Return stripped text or None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None
