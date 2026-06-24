"""Project Folder Required forms preview and generation service."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Protocol

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordError,
    ProjectOutputRecordNotFoundError,
    ProjectOutputStatusSummary,
    RegisterProjectOutputCommand,
)
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.domain.models import ApplicationForm


REQUIRED_FORM_DEFINITIONS: tuple[tuple[str, str, ProjectOutputKind, str, str | None], ...] = (
    (
        "test_record",
        "Test Record",
        ProjectOutputKind.TEST_RECORD_FORM,
        "{dl} Test Record.docx",
        "Submitted Material",
    ),
    (
        "fee_form",
        "Fee Form",
        ProjectOutputKind.FEE_EVALUATION,
        "{dl} Fee Form.xls",
        None,
    ),
    (
        "customer_feedback_form",
        "Customer Feedback Form",
        ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
        "{dl} Customer Feedback Form{owner}.xlsx",
        None,
    ),
)

REQUIRED_FORM_GENERATION_ORDER = {
    "customer_feedback_form": 0,
    "fee_form": 1,
    "test_record": 2,
}


class RequiredFormsError(ValueError):
    """Base error for Project Folder Required forms workflows."""


class RequiredFormsContextMismatchError(RequiredFormsError):
    """Raised when a generate request no longer matches the current preview."""


class RequiredFormsConflictError(RequiredFormsError):
    """Raised when final target placement has conflicts."""


class RequiredFormsTargetChangedError(RequiredFormsError):
    """Raised when a managed target changed before safe update."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Completed Official project workspace lookup."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the completed local workspace record for a project."""


class OfficialFolderCheckPort(Protocol):
    """Official folder check preview dependency."""

    def preview(self, project_id: str) -> object:
        """Return TASK_318 Official folder check preview."""


class ConfirmedMatrixReader(Protocol):
    """Active Confirmed Matrix reader."""

    def get_active_snapshot(self, project_id: str) -> object | None:
        """Return active Confirmed Matrix snapshot."""


class ConfirmedFeeReader(Protocol):
    """Confirmed Fee reader."""

    def get_latest(self, project_id: str) -> object:
        """Return latest Confirmed Fee status/read model."""


class CustomerFeedbackTemplateReader(Protocol):
    """Customer Feedback template readiness reader."""

    def preview_template(self, project_id: str) -> Path:
        """Return the unique Customer Feedback template path."""


class FeeFormTemplateContextReader(Protocol):
    """Fee Form template identity reader for safe output reuse."""

    def preview_template_context(self, project_id: str) -> str:
        """Return a stable Fee Form template context token."""


class ApplicationFormReader(Protocol):
    """Application Form reader for formal Project Folder naming."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return Application Forms for a project."""


class RequiredFormsStagingGenerator(Protocol):
    """Output-record-free staging generator for Required forms."""

    def generate(
        self,
        *,
        project_id: str,
        key: str,
        target_name: str,
        basic_information: ConfirmedBasicInformationSnapshot,
    ) -> Path:
        """Generate one form into ConnLab-controlled staging."""


class RequiredFormsFileGateway(Protocol):
    """Final file placement gateway."""

    def create_new(self, source: Path, target: Path, *, key: str) -> None:
        """Create a new target without overwriting."""

    def update_managed(
        self,
        source: Path,
        target: Path,
        *,
        key: str,
        expected_existing_sha256: str,
    ) -> None:
        """Update an unchanged ConnLab-managed target."""


class OutputStatusServicePort(Protocol):
    """Project output status and registration dependency."""

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        """Return current project output status."""

    def register_output(self, command: RegisterProjectOutputCommand) -> object:
        """Register one project output record."""


class ReusableFeeFormArtifactReader(Protocol):
    """Reader for a current generated Fee Form artifact that can be reused."""

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return a safe reusable Fee Form source path, if one exists."""


class NullReusableFeeFormArtifactReader:
    """Default no-op Fee Form artifact reader."""

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return no reusable artifact."""
        return None


@dataclass(frozen=True, slots=True)
class RequiredFormPreviewItem:
    """One Required form preview item."""

    key: str
    label: str
    target_path: Path | None
    status: str
    action: str
    message: str
    output_kind: ProjectOutputKind
    existing_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class RequiredFormsPreview:
    """Read-only Required forms preview."""

    project_id: str
    status: str
    official_project_folder_path: Path | None
    confirmed_matrix_id: str | None
    confirmed_revision: int | None
    confirmed_fee_id: str | None
    confirmed_fee_revision: int | None
    confirmed_fee_pricing_draft_edit_id: str | None
    confirmed_basic_information_version: int | None
    confirmed_basic_information_source_signature_hash: str | None
    customer_feedback_template_path: Path | None
    source_context_signature: str | None
    items: tuple[RequiredFormPreviewItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RequiredFormsGenerateTarget:
    """Expected final target from the operator preview."""

    key: str
    target_path: Path


@dataclass(frozen=True, slots=True)
class GenerateRequiredFormsCommand:
    """Command for generating Project Folder Required forms."""

    project_id: str
    expected_official_project_folder_path: Path
    expected_confirmed_matrix_id: str
    expected_confirmed_revision: int
    expected_confirmed_fee_id: str
    expected_confirmed_fee_revision: int
    expected_confirmed_fee_pricing_draft_edit_id: str
    expected_confirmed_basic_information_version: int
    expected_confirmed_basic_information_source_signature_hash: str
    expected_customer_feedback_template_path: Path
    expected_targets: tuple[RequiredFormsGenerateTarget, ...]


@dataclass(frozen=True, slots=True)
class RequiredFormsGenerateItem:
    """One Required forms generation item result."""

    key: str
    label: str
    target_path: Path
    status: str
    source_path: Path | None
    output_record_id: str | None
    message: str


@dataclass(frozen=True, slots=True)
class RequiredFormsTiming:
    """Diagnostic timing entry for one Required forms generation step."""

    label: str
    elapsed_ms: int


@dataclass(frozen=True, slots=True)
class RequiredFormsGenerateResult:
    """Required forms generation result."""

    project_id: str
    status: str
    official_project_folder_path: Path
    items: tuple[RequiredFormsGenerateItem, ...]
    warnings: tuple[str, ...]
    timings: tuple[RequiredFormsTiming, ...] = tuple()


class ProjectFolderRequiredFormsService:
    """Preview and generate the Project Folder Required forms."""

    def __init__(
        self,
        *,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        folder_check_service: OfficialFolderCheckPort,
        confirmed_matrix_reader: ConfirmedMatrixReader,
        confirmed_fee_reader: ConfirmedFeeReader,
        basic_information_reader: ConfirmedBasicInformationReader,
        customer_feedback_template_reader: CustomerFeedbackTemplateReader,
        fee_form_template_context_reader: FeeFormTemplateContextReader,
        application_form_reader: ApplicationFormReader,
        generator: RequiredFormsStagingGenerator,
        file_gateway: RequiredFormsFileGateway,
        output_status_service: OutputStatusServicePort,
        reusable_fee_form_reader: ReusableFeeFormArtifactReader | None = None,
    ) -> None:
        """Create the Required forms service with explicit ports."""
        self._workspaces = workspace_repository
        self._folder_check = folder_check_service
        self._matrices = confirmed_matrix_reader
        self._fees = confirmed_fee_reader
        self._basic_information = basic_information_reader
        self._feedback_templates = customer_feedback_template_reader
        self._fee_form_templates = fee_form_template_context_reader
        self._application_forms = application_form_reader
        self._generator = generator
        self._reusable_fee_forms = (
            reusable_fee_form_reader or NullReusableFeeFormArtifactReader()
        )
        self._files = file_gateway
        self._outputs = output_status_service

    def preview(self, project_id: str) -> RequiredFormsPreview:
        """Return the current Required forms preview."""
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.exists():
            return _blocked_preview(project_id, "Create the Official project folder first.")
        folder_check = self._folder_check.preview(project_id)
        if getattr(folder_check, "status", "blocked") in {"blocked", "conflict"}:
            return _blocked_preview(project_id, "Resolve Project Folder check blockers first.")

        matrix = self._matrices.get_active_snapshot(project_id)
        if matrix is None:
            return _blocked_preview(project_id, "Confirm Matrix authority before generating Required forms.")
        fee_result = self._fees.get_latest(project_id)
        if getattr(fee_result, "status", None) != "current":
            return _blocked_preview(project_id, "Confirm Fee before generating Required forms.")
        fee = getattr(fee_result, "latest_confirmed_fee", None)
        if fee is None:
            return _blocked_preview(project_id, "Confirmed Fee is missing.")
        basic_information = self._basic_information.get_latest_confirmed(project_id)
        if basic_information is None:
            return _blocked_preview(
                project_id,
                "Confirm Basic Information before generating Project Folder outputs.",
            )
        template_path = self._feedback_templates.preview_template(project_id)
        owner_suffix = _owner_suffix(
            self._application_forms.list_by_project(project_id),
            basic_information,
        )
        fee_template_context = self._fee_form_templates.preview_template_context(project_id)
        source_context = _source_context_signature(
            matrix,
            fee,
            basic_information,
            fee_template_context,
        )
        summary = self._outputs.get_status_summary(project_id)
        by_kind = {item.output_kind: item for item in summary.items}
        items = tuple(
            self._preview_item(
                definition=definition,
                workspace=workspace,
                owner_suffix=owner_suffix,
                source_context=source_context,
                output_item=by_kind.get(definition[2]),
            )
            for definition in REQUIRED_FORM_DEFINITIONS
        )
        if any(item.status == "conflict" for item in items):
            status = "conflict"
        elif all(item.status == "current" for item in items):
            status = "current"
        else:
            status = "ready"
        return RequiredFormsPreview(
            project_id=project_id,
            status=status,
            official_project_folder_path=workspace.official_folder_path,
            confirmed_matrix_id=_matrix_id(matrix),
            confirmed_revision=_matrix_revision(matrix),
            confirmed_fee_id=_fee_id(fee),
            confirmed_fee_revision=_fee_revision(fee),
            confirmed_fee_pricing_draft_edit_id=str(getattr(fee, "pricing_draft_edit_id")),
            confirmed_basic_information_version=basic_information.version,
            confirmed_basic_information_source_signature_hash=(
                basic_information.source_signature_hash
            ),
            customer_feedback_template_path=template_path,
            source_context_signature=source_context,
            items=items,
            blockers=tuple(),
            warnings=tuple(),
        )

    def generate(self, command: GenerateRequiredFormsCommand) -> RequiredFormsGenerateResult:
        """Generate and place Required forms after rechecking the preview context."""
        total_start = perf_counter()
        timings: list[RequiredFormsTiming] = []
        preview_start = perf_counter()
        preview = self.preview(command.project_id)
        _append_timing(timings, "required_forms.preview", preview_start)
        validate_start = perf_counter()
        self._validate_context(command, preview)
        basic_information = self._require_basic_information(command.project_id)
        self._validate_basic_information_context(command, basic_information)
        _append_timing(timings, "required_forms.validate_context", validate_start)
        if preview.status == "blocked":
            raise RequiredFormsConflictError(
                preview.blockers[0] if preview.blockers else "Required forms are blocked."
            )
        expected_target_keys = {item.key for item in command.expected_targets}
        generated: list[RequiredFormsGenerateItem] = []
        warnings: list[str] = []
        final_placement_success_count = 0
        for item in sorted(
            preview.items,
            key=lambda preview_item: (
                REQUIRED_FORM_GENERATION_ORDER.get(preview_item.key, 99),
                preview_item.key,
            ),
        ):
            if item.key not in expected_target_keys:
                continue
            if item.target_path is None:
                continue
            if item.action == "conflict":
                generated.append(_failed_item(item, "conflict", item.message))
                continue
            if item.action == "skip":
                generated.append(
                    RequiredFormsGenerateItem(
                        key=item.key,
                        label=item.label,
                        target_path=item.target_path,
                        status="skipped",
                        source_path=None,
                        output_record_id=None,
                        message=item.message,
                    )
                )
                continue
            try:
                source = self._source_for_item(
                    command=command,
                    item=item,
                    basic_information=basic_information,
                    source_context=preview.source_context_signature,
                    timings=timings,
                )
                place_start = perf_counter()
                if item.action == "update" and item.existing_sha256:
                    self._files.update_managed(
                        source,
                        item.target_path,
                        key=item.key,
                        expected_existing_sha256=item.existing_sha256,
                    )
                    status = "updated"
                else:
                    self._files.create_new(source, item.target_path, key=item.key)
                    status = "generated"
                _append_timing(timings, f"{item.key}.place", place_start)
            except RequiredFormsTargetChangedError as exc:
                generated.append(
                    _failed_item(item, "conflict", f"Target changed before update: {exc}")
                )
                return RequiredFormsGenerateResult(
                    project_id=command.project_id,
                    status="conflict",
                    official_project_folder_path=command.expected_official_project_folder_path,
                    items=tuple(generated),
                    warnings=tuple(warnings),
                    timings=_finish_timings(timings, total_start),
                )
            except OSError as exc:
                generated.append(_failed_item(item, "failed", str(exc)))
                return RequiredFormsGenerateResult(
                    project_id=command.project_id,
                    status="partial" if final_placement_success_count > 0 else "blocked",
                    official_project_folder_path=command.expected_official_project_folder_path,
                    items=tuple(generated),
                    warnings=tuple(warnings),
                    timings=_finish_timings(timings, total_start),
                )
            output_record_id: str | None = None
            register_start = perf_counter()
            try:
                record = self._register_output(
                    command.project_id, item, preview.source_context_signature
                )
                output_record_id = str(getattr(record, "output_record_id", "")) or None
            except (ProjectOutputRecordError, ProjectOutputRecordNotFoundError) as exc:
                warnings.append(f"{item.label} was placed, but output tracking was not updated: {exc}")
            _append_timing(timings, f"{item.key}.register_output", register_start)
            final_placement_success_count += 1
            generated.append(
                RequiredFormsGenerateItem(
                    key=item.key,
                    label=item.label,
                    target_path=item.target_path,
                    status=status,
                    source_path=source,
                    output_record_id=output_record_id,
                    message="Placed in the Official project folder.",
                )
            )
        statuses = {item.status for item in generated}
        overall = "generated"
        if "failed" in statuses:
            overall = "partial" if final_placement_success_count > 0 else "blocked"
        elif "conflict" in statuses:
            overall = "partial" if final_placement_success_count > 0 else "conflict"
        return RequiredFormsGenerateResult(
            project_id=command.project_id,
            status=overall,
            official_project_folder_path=command.expected_official_project_folder_path,
            items=tuple(generated),
            warnings=tuple(warnings),
            timings=_finish_timings(timings, total_start),
        )

    def _preview_item(
        self,
        *,
        definition: tuple[str, str, ProjectOutputKind, str, str | None],
        workspace: OfficialWorkspaceRecord,
        owner_suffix: str | None,
        source_context: str,
        output_item: object | None,
    ) -> RequiredFormPreviewItem:
        key, label, kind, pattern, relative_folder = definition
        target_path = _target_path(
            workspace,
            pattern,
            relative_folder,
            owner_suffix=owner_suffix if key == "customer_feedback_form" else None,
        )
        if not target_path.exists():
            return RequiredFormPreviewItem(
                key=key,
                label=label,
                target_path=target_path,
                status="ready",
                action="generate",
                message="Ready to generate.",
                output_kind=kind,
            )
        if output_item is None:
            return _conflict_item(key, label, target_path, kind)
        if getattr(output_item, "output_path", None) != str(target_path):
            return _conflict_item(key, label, target_path, kind)
        stored_sha = getattr(output_item, "output_sha256", None)
        if not stored_sha or compute_sha256(target_path) != stored_sha:
            return _conflict_item(key, label, target_path, kind, "Target was changed outside ConnLab.")
        stored_context = getattr(output_item, "source_context_signature", None)
        action = "skip" if stored_context == source_context else "update"
        status = "current" if action == "skip" else "ready"
        return RequiredFormPreviewItem(
            key=key,
            label=label,
            target_path=target_path,
            status=status,
            action=action,
            message=(
                "Current."
                if action == "skip"
                else "Existing ConnLab-generated file can be safely updated."
            ),
            output_kind=kind,
            existing_sha256=stored_sha,
        )

    def _validate_context(
        self,
        command: GenerateRequiredFormsCommand,
        preview: RequiredFormsPreview,
    ) -> None:
        expected_targets = {item.key: item.target_path for item in command.expected_targets}
        current_targets = {
            item.key: item.target_path
            for item in preview.items
            if item.action in {"generate", "update"}
        }
        all_current_targets = {item.key: item.target_path for item in preview.items}
        expected_keys = set(expected_targets)
        expected_paths_match = all(
            all_current_targets.get(key) == path for key, path in expected_targets.items()
        )
        target_context_matches = (
            expected_targets == current_targets or expected_targets == all_current_targets
            or (expected_paths_match and expected_keys.issubset(current_targets.keys()))
        )
        if (
            preview.official_project_folder_path != command.expected_official_project_folder_path
            or preview.confirmed_matrix_id != command.expected_confirmed_matrix_id
            or preview.confirmed_revision != command.expected_confirmed_revision
            or preview.confirmed_fee_id != command.expected_confirmed_fee_id
            or preview.confirmed_fee_revision != command.expected_confirmed_fee_revision
            or preview.confirmed_fee_pricing_draft_edit_id
            != command.expected_confirmed_fee_pricing_draft_edit_id
            or preview.confirmed_basic_information_version
            != command.expected_confirmed_basic_information_version
            or preview.confirmed_basic_information_source_signature_hash
            != command.expected_confirmed_basic_information_source_signature_hash
            or preview.customer_feedback_template_path
            != command.expected_customer_feedback_template_path
            or not target_context_matches
        ):
            raise RequiredFormsContextMismatchError("Required forms preview is stale.")

    def _register_output(
        self,
        project_id: str,
        item: RequiredFormPreviewItem,
        source_context: str | None,
    ) -> object:
        if item.target_path is None:
            raise RequiredFormsConflictError("Cannot register a missing target path.")
        summary = self._outputs.get_status_summary(project_id)
        active_draft_id = getattr(summary, "active_draft_id", None)
        return self._outputs.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=item.output_kind,
                status=ProjectOutputStatus.CURRENT,
                source=ProjectOutputSource.SYSTEM_GENERATED,
                output_path=str(item.target_path),
                draft_id=active_draft_id,
                output_sha256=compute_sha256(item.target_path),
                output_size_bytes=item.target_path.stat().st_size,
                source_context_signature=source_context,
            )
        )

    def _require_basic_information(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot:
        """Return confirmed Basic Information or raise a generation conflict."""
        snapshot = self._basic_information.get_latest_confirmed(project_id)
        if snapshot is None:
            raise RequiredFormsConflictError(
                "Confirm Basic Information before generating Project Folder outputs."
            )
        return snapshot

    def _validate_basic_information_context(
        self,
        command: GenerateRequiredFormsCommand,
        snapshot: ConfirmedBasicInformationSnapshot,
    ) -> None:
        """Ensure generation uses the same Basic Information snapshot as preview."""
        if (
            snapshot.version != command.expected_confirmed_basic_information_version
            or snapshot.source_signature_hash
            != command.expected_confirmed_basic_information_source_signature_hash
        ):
            raise RequiredFormsContextMismatchError("Required forms preview is stale.")

    def _source_for_item(
        self,
        *,
        command: GenerateRequiredFormsCommand,
        item: RequiredFormPreviewItem,
        basic_information: ConfirmedBasicInformationSnapshot,
        source_context: str | None,
        timings: list[RequiredFormsTiming],
    ) -> Path:
        """Return a staging source for one item, reusing Fee Form when safe."""
        if (
            item.key == "fee_form"
            and item.target_path is not None
            and source_context is not None
        ):
            reuse_start = perf_counter()
            reusable = self._reusable_fee_forms.find_current_artifact(
                project_id=command.project_id,
                source_context_signature=source_context,
                final_target_path=item.target_path,
            )
            _append_timing(timings, "fee_form.reuse_lookup", reuse_start)
            if reusable is not None:
                return reusable
        generate_start = perf_counter()
        source = self._generator.generate(
            project_id=command.project_id,
            key=item.key,
            target_name=item.target_path.name if item.target_path else item.key,
            basic_information=basic_information,
        )
        _append_timing(timings, f"{item.key}.generate", generate_start)
        return source


def compute_sha256(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _append_timing(
    timings: list[RequiredFormsTiming], label: str, start: float
) -> None:
    """Append one elapsed timing entry."""
    timings.append(RequiredFormsTiming(label=label, elapsed_ms=_elapsed_ms(start)))


def _finish_timings(
    timings: list[RequiredFormsTiming], total_start: float
) -> tuple[RequiredFormsTiming, ...]:
    """Append total elapsed timing and return immutable entries."""
    return tuple(
        [
            *timings,
            RequiredFormsTiming(
                label="required_forms.total",
                elapsed_ms=_elapsed_ms(total_start),
            ),
        ]
    )


def _elapsed_ms(start: float) -> int:
    return int(round((perf_counter() - start) * 1000))


def _target_path(
    workspace: OfficialWorkspaceRecord,
    pattern: str,
    relative_folder: str | None,
    *,
    owner_suffix: str | None = None,
) -> Path:
    dl = _safe_name(workspace.dl_number)
    owner = f"_{_safe_name(owner_suffix)}" if owner_suffix else ""
    folder = (
        workspace.official_folder_path / relative_folder
        if relative_folder
        else workspace.official_folder_path
    )
    return folder / pattern.format(dl=dl, owner=owner)


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", " "} else " " for ch in value).strip(" .")


def _owner_suffix(
    forms: list[ApplicationForm],
    basic_information: ConfirmedBasicInformationSnapshot,
) -> str | None:
    """Return the Project Leader suffix for Customer Feedback file names."""
    project_leader = basic_information.values.get("project_leader", "").strip()
    if project_leader:
        return project_leader
    form = forms[-1] if forms else None
    if form is None:
        return None
    text = (form.assigned_personnel or "").strip()
    return text or None


def _source_context_signature(
    matrix: object,
    fee: object,
    basic_information: ConfirmedBasicInformationSnapshot,
    fee_template_context: str,
) -> str:
    return (
        f"matrix:{_matrix_id(matrix)}@{_matrix_revision(matrix)}"
        f"|fee:{_fee_id(fee)}@{_fee_revision(fee)}"
        f"|pricing:{getattr(fee, 'pricing_draft_edit_id')}"
        f"|{basic_information.context_signature}"
        f"|{fee_template_context}"
        "|fee-output:matrix_basic_with_basic_information"
    )


def _matrix_id(matrix: object) -> str:
    version = getattr(matrix, "version", matrix)
    return str(getattr(version, "confirmed_matrix_id"))


def _matrix_revision(matrix: object) -> int:
    version = getattr(matrix, "version", matrix)
    return int(getattr(version, "confirmed_revision", getattr(version, "revision", 0)))


def _fee_id(fee: object) -> str:
    return str(getattr(fee, "confirmed_fee_id"))


def _fee_revision(fee: object) -> int:
    return int(getattr(fee, "confirmed_fee_revision", getattr(fee, "revision", 0)))


def _blocked_preview(project_id: str, message: str) -> RequiredFormsPreview:
    return RequiredFormsPreview(
        project_id=project_id,
        status="blocked",
        official_project_folder_path=None,
        confirmed_matrix_id=None,
        confirmed_revision=None,
        confirmed_fee_id=None,
        confirmed_fee_revision=None,
        confirmed_fee_pricing_draft_edit_id=None,
        confirmed_basic_information_version=None,
        confirmed_basic_information_source_signature_hash=None,
        customer_feedback_template_path=None,
        source_context_signature=None,
        items=tuple(),
        blockers=(message,),
        warnings=tuple(),
    )


def _conflict_item(
    key: str,
    label: str,
    target_path: Path,
    kind: ProjectOutputKind,
    message: str = "Existing file is not a safe ConnLab-managed target.",
) -> RequiredFormPreviewItem:
    return RequiredFormPreviewItem(
        key=key,
        label=label,
        target_path=target_path,
        status="conflict",
        action="conflict",
        message=message,
        output_kind=kind,
    )


def _failed_item(
    item: RequiredFormPreviewItem,
    status: str,
    message: str,
) -> RequiredFormsGenerateItem:
    return RequiredFormsGenerateItem(
        key=item.key,
        label=item.label,
        target_path=item.target_path or Path("."),
        status=status,
        source_path=None,
        output_record_id=None,
        message=message,
    )
