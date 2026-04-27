"""Application service for intake upload and precheck workflows."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    PrecheckIssue,
    PrecheckResult,
    Project,
    SampleInfo,
)
from backend.application.intake_mappers import (
    from_application_form,
    to_application_form,
    to_sample_infos,
    with_persistent_ids,
)
from backend.modules.intake import ApplicationFormParser, ParsedApplicationForm
from backend.modules.precheck import PrecheckEngine
from backend.shared.config import Settings


class IntakeNotFoundError(LookupError):
    """Raised when a workflow record cannot be found."""


class ProjectRepositoryPort(Protocol):
    """Project repository operations required by the intake service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form repository operations required by the intake service."""

    def create_with_samples(
        self,
        form: ApplicationForm,
        samples: tuple[SampleInfo, ...],
    ) -> ApplicationForm:
        """Persist an application form with samples."""

    def get(self, form_id: str) -> ApplicationForm | None:
        """Return an application form by ID."""


class SampleInfoRepositoryPort(Protocol):
    """Sample repository operations required by the intake service."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return samples for a project."""


class FileAssetRepositoryPort(Protocol):
    """File asset repository operations required by the intake service."""

    def create(self, asset: FileAsset) -> FileAsset:
        """Persist a file asset."""

    def get(self, asset_id: str) -> FileAsset | None:
        """Return a file asset by ID."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return registered file assets for a project."""


class PrecheckResultRepositoryPort(Protocol):
    """Precheck repository operations required by the intake service."""

    def create(self, result: PrecheckResult) -> PrecheckResult:
        """Persist a precheck result."""

    def latest_by_project(self, project_id: str) -> PrecheckResult | None:
        """Return latest precheck for a project."""

    def resolve_issue(self, issue_id: str) -> PrecheckIssue | None:
        """Resolve an issue by ID."""


@dataclass(frozen=True, slots=True)
class ParsedFormRecord:
    """Persisted parsed form and sample rows returned by intake upload."""

    form: ApplicationForm
    samples: tuple[SampleInfo, ...]
    asset: FileAsset


class IntakePrecheckService:
    """Coordinate application-form upload, parsing, persistence, and precheck."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        form_repository: ApplicationFormRepositoryPort,
        sample_repository: SampleInfoRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
        precheck_repository: PrecheckResultRepositoryPort,
        settings: Settings,
    ) -> None:
        """Create an intake/precheck service with storage dependencies."""
        self._projects = project_repository
        self._forms = form_repository
        self._samples = sample_repository
        self._assets = file_asset_repository
        self._prechecks = precheck_repository
        self._settings = settings
        self._parser = ApplicationFormParser()
        self._engine = PrecheckEngine()

    def upload_application_form(
        self,
        project_id: str,
        filename: str,
        source,
    ) -> ParsedFormRecord:
        """Save, parse, and persist an uploaded application form."""
        project = self._get_project(project_id)
        form_id = uuid4().hex
        target_path = self._save_upload(project.project_id, form_id, filename, source)
        parsed = self._parser.parse(target_path)
        form = to_application_form(form_id, project.project_id, parsed)
        samples = to_sample_infos(project.project_id, parsed.samples)
        asset = FileAsset(
            asset_id=form_id,
            project_id=project.project_id,
            asset_type=FileAssetType.APPLICATION_FORM,
            path=target_path,
            original_name=filename,
            registered_on=date.today(),
        )
        self._forms.create_with_samples(form, samples)
        self._assets.create(asset)
        return ParsedFormRecord(form=form, samples=samples, asset=asset)

    def run_precheck(self, application_form_id: str) -> PrecheckResult:
        """Run and persist deterministic precheck for an application form."""
        form = self._forms.get(application_form_id)
        if form is None:
            raise IntakeNotFoundError(f"Application form not found: {application_form_id}")
        parsed = self._load_parsed_form(form)
        result = self._engine.run(
            parsed,
            registered_attachments=self._registered_supporting_attachments(form.project_id),
        )
        persisted = with_persistent_ids(result, application_form_id)
        return self._prechecks.create(persisted)

    def latest_precheck(self, project_id: str) -> PrecheckResult:
        """Return the latest precheck result for a project."""
        self._get_project(project_id)
        result = self._prechecks.latest_by_project(project_id)
        if result is None:
            raise IntakeNotFoundError(f"No precheck result found for project: {project_id}")
        return result

    def resolve_issue(self, issue_id: str) -> PrecheckIssue:
        """Resolve a precheck issue."""
        issue = self._prechecks.resolve_issue(issue_id)
        if issue is None:
            raise IntakeNotFoundError(f"Precheck issue not found: {issue_id}")
        return issue

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise a workflow-level not-found error."""
        project = self._projects.get(project_id)
        if project is None:
            raise IntakeNotFoundError(f"Project not found: {project_id}")
        return project

    def _save_upload(self, project_id: str, form_id: str, filename: str, source) -> Path:
        """Save an uploaded file under the controlled data directory."""
        safe_name = _safe_filename(filename)
        target_dir = self._settings.data_dir / "projects" / project_id / "assets"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{form_id}_{safe_name}"
        with target_path.open("wb") as target:
            shutil.copyfileobj(source, target)
        return target_path

    def _load_parsed_form(self, form: ApplicationForm) -> ParsedApplicationForm:
        """Load parser output from original file when available."""
        asset = self._assets.get(form.form_id)
        if asset and asset.path.exists():
            return self._parser.parse(asset.path)
        return from_application_form(form, self._samples.list_by_project(form.project_id))

    def _registered_supporting_attachments(self, project_id: str) -> tuple[str, ...]:
        """Return project attachments that can satisfy attachment references."""
        return tuple(
            asset.original_name or asset.path.name
            for asset in self._assets.list_by_project(project_id)
            if asset.asset_type is not FileAssetType.APPLICATION_FORM
        )


def _safe_filename(filename: str) -> str:
    """Return a conservative filename safe for local storage."""
    return Path(filename).name.replace("/", "_").replace("\\", "_") or "application.docx"
