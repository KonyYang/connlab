"""Read-only lookup service for project, sample, and testing summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import ApplicationForm, FileAsset, LtrRecord, Project, SampleInfo


class LookupNotFoundError(LookupError):
    """Raised when a lookup target cannot be found."""


@dataclass(frozen=True, slots=True)
class ProjectLookupRow:
    """One project lookup result row."""

    project_id: str
    project_no: str | None
    product_name: str
    requestor: str
    status: str
    ltr_numbers: tuple[str, ...]
    sample_part_numbers: tuple[str, ...]
    matched_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SampleSummaryRow:
    """One sample summary row for a project."""

    sample_id: str
    product_name: str
    part_number: str
    revision: str | None
    lot_or_traceability: str | None
    material: str | None
    plating: str | None
    housing_material: str | None
    quantity: int | None


@dataclass(frozen=True, slots=True)
class SampleSummary:
    """Read-only sample summary for a project."""

    project_id: str
    project_no: str | None
    product_name: str
    requestor: str
    ltr_numbers: tuple[str, ...]
    samples: tuple[SampleSummaryRow, ...]


@dataclass(frozen=True, slots=True)
class TestingSummary:
    """Read-only testing condition/method summary for a project."""

    project_id: str
    project_no: str | None
    requested_testing: str | None
    test_type: str | None
    sample_condition: str | None
    requested_completion_date: str | None
    applicable_specifications: tuple[str, ...]
    lab: str | None
    assigned_personnel: str | None


class ProjectRepositoryPort(Protocol):
    """Project repository behavior required by lookup service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def list(self) -> list[Project]:
        """Return all projects."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form repository behavior required by lookup service."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


class SampleInfoRepositoryPort(Protocol):
    """Sample repository behavior required by lookup service."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return samples for a project."""


class LtrRepositoryPort(Protocol):
    """LTR repository behavior required by lookup service."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository behavior required by lookup service."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return file assets for a project."""


class LookupService:
    """Provide read-only lookup over structured ConnLab records."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        form_repository: ApplicationFormRepositoryPort,
        sample_repository: SampleInfoRepositoryPort,
        ltr_repository: LtrRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
    ) -> None:
        """Create a lookup service with repository ports."""
        self._projects = project_repository
        self._forms = form_repository
        self._samples = sample_repository
        self._ltrs = ltr_repository
        self._assets = file_asset_repository

    def search_projects(self, query: str) -> list[ProjectLookupRow]:
        """Search projects by project, sample, requestor, product, or LTR text."""
        text = query.strip().lower()
        if not text:
            return []
        ltr_project_ids = {
            ltr.project_id for ltr in self._ltrs.search(query) if _contains(ltr.ltr_number, text)
        }
        rows: list[ProjectLookupRow] = []
        for project in self._projects.list():
            samples = self._samples.list_by_project(project.project_id)
            ltrs = self._ltrs.list_by_project(project.project_id)
            matched = _matched_fields(project, samples, ltrs, text, ltr_project_ids)
            if matched:
                rows.append(_lookup_row(project, samples, ltrs, matched))
        return rows

    def sample_summary(self, project_id: str) -> SampleSummary:
        """Return structured sample information for one project."""
        project = self._get_project(project_id)
        ltrs = self._ltrs.list_by_project(project.project_id)
        samples = self._samples.list_by_project(project.project_id)
        return SampleSummary(
            project_id=project.project_id,
            project_no=project.project_no,
            product_name=project.product_name,
            requestor=project.requestor,
            ltr_numbers=tuple(ltr.ltr_number for ltr in ltrs),
            samples=tuple(_sample_row(sample) for sample in samples),
        )

    def testing_summary(self, project_id: str) -> TestingSummary:
        """Return structured testing condition/method text for one project."""
        project = self._get_project(project_id)
        forms = self._forms.list_by_project(project.project_id)
        form = forms[-1] if forms else None
        assets = self._assets.list_by_project(project.project_id)
        return TestingSummary(
            project_id=project.project_id,
            project_no=project.project_no,
            requested_testing=form.requested_testing if form else None,
            test_type=form.test_type if form else None,
            sample_condition=form.sample_condition if form else None,
            requested_completion_date=form.requested_completion_date if form else None,
            applicable_specifications=_specification_names(assets, form),
            lab=form.lab if form else None,
            assigned_personnel=form.assigned_personnel if form else None,
        )

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise not found."""
        project = self._projects.get(project_id)
        if project is None:
            raise LookupNotFoundError(f"Project not found: {project_id}")
        return project


def _lookup_row(
    project: Project,
    samples: list[SampleInfo],
    ltrs: list[LtrRecord],
    matched: tuple[str, ...],
) -> ProjectLookupRow:
    """Create a lookup result row."""
    return ProjectLookupRow(
        project_id=project.project_id,
        project_no=project.project_no,
        product_name=project.product_name,
        requestor=project.requestor,
        status=project.status.value,
        ltr_numbers=tuple(ltr.ltr_number for ltr in ltrs),
        sample_part_numbers=tuple(sample.part_number for sample in samples),
        matched_fields=matched,
    )


def _matched_fields(
    project: Project,
    samples: list[SampleInfo],
    ltrs: list[LtrRecord],
    query: str,
    ltr_project_ids: set[str],
) -> tuple[str, ...]:
    """Return fields matched by a search query."""
    matched: list[str] = []
    if _contains(project.project_no, query):
        matched.append("project_no")
    if _contains(project.product_name, query):
        matched.append("product_name")
    if _contains(project.requestor, query):
        matched.append("requestor")
    if project.project_id in ltr_project_ids or any(_contains(ltr.ltr_number, query) for ltr in ltrs):
        matched.append("ltr_number")
    if any(_contains(sample.part_number, query) for sample in samples):
        matched.append("sample.part_number")
    if any(_contains(sample.product_name, query) for sample in samples):
        matched.append("sample.product_name")
    return tuple(dict.fromkeys(matched))


def _sample_row(sample: SampleInfo) -> SampleSummaryRow:
    """Convert sample info to summary row."""
    return SampleSummaryRow(
        sample_id=sample.sample_id,
        product_name=sample.product_name,
        part_number=sample.part_number,
        revision=sample.revision,
        lot_or_traceability=sample.lot_or_traceability,
        material=sample.material,
        plating=sample.plating,
        housing_material=sample.housing_material,
        quantity=sample.quantity,
    )


def _specification_names(
    assets: list[FileAsset],
    form: ApplicationForm | None,
) -> tuple[str, ...]:
    """Return structured specification labels from assets or form text."""
    names = [
        asset.original_name or asset.path.name
        for asset in assets
        if _looks_like_specification(asset.original_name or asset.path.name)
    ]
    if not names and form and form.requested_testing:
        text = form.requested_testing
        if "spec" in text.lower() or "standard" in text.lower():
            names.append(text)
    return tuple(dict.fromkeys(name for name in names if name))


def _looks_like_specification(value: str) -> bool:
    """Return whether a filename looks like a specification document."""
    lowered = value.lower()
    return (
        "spec" in lowered
        or "standard" in lowered
        or "requirement" in lowered
        or lowered.endswith(".pdf")
    )


def _contains(value: object, query: str) -> bool:
    """Return whether query appears in a stringified value."""
    return query in str(value or "").lower()
