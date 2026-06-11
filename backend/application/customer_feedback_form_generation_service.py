"""Customer Feedback Form generation application service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.customer_feedback_template_discovery import (
    CustomerFeedbackTemplateAmbiguousError as TemplateDiscoveryAmbiguousError,
    CustomerFeedbackTemplateDiscoveryError,
    discover_customer_feedback_template,
)
from backend.domain import ExternalResource, ExternalResourceType, Project


class CustomerFeedbackGenerationError(RuntimeError):
    """Base error for Customer Feedback generation failures."""


class CustomerFeedbackReadinessError(CustomerFeedbackGenerationError):
    """Raised when required Customer Feedback inputs are not ready."""


class CustomerFeedbackProjectNotFoundError(CustomerFeedbackReadinessError):
    """Raised when the target project does not exist."""


class CustomerFeedbackTemplateAmbiguousError(CustomerFeedbackReadinessError):
    """Raised when more than one Customer Feedback template candidate exists."""


class CustomerFeedbackProjectStore(Protocol):
    """Repository port for project lookup."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class CustomerFeedbackExternalResourceStore(Protocol):
    """Repository port for external resource lookup."""

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        """Return an external resource by type."""


class CustomerFeedbackWorkbookWriter(Protocol):
    """Gateway port for workbook generation."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        identity: dict[str, str],
    ) -> tuple[Path, tuple[str, ...]]:
        """Generate a Customer Feedback workbook and return warnings."""


@dataclass(frozen=True, slots=True)
class CustomerFeedbackFormGenerationCommand:
    """Input command for Customer Feedback Form generation."""

    project_id: str
    output_dir: Path | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class CustomerFeedbackFormGenerationResult:
    """Result metadata for Customer Feedback Form generation."""

    project_id: str
    template_path: Path
    output_path: Path
    output_file_name: str
    warnings: tuple[str, ...] = ()


class CustomerFeedbackFormGenerationService:
    """Generate Customer Feedback Form workbooks from configured templates."""

    def __init__(
        self,
        *,
        project_store: CustomerFeedbackProjectStore,
        external_resource_store: CustomerFeedbackExternalResourceStore,
        workbook_gateway: CustomerFeedbackWorkbookWriter,
        generated_root: Path,
    ) -> None:
        """Create the service with explicit persistence and gateway ports."""
        self._project_store = project_store
        self._external_resource_store = external_resource_store
        self._workbook_gateway = workbook_gateway
        self._generated_root = Path(generated_root)

    def generate(
        self,
        command: CustomerFeedbackFormGenerationCommand,
    ) -> CustomerFeedbackFormGenerationResult:
        """Generate a Customer Feedback Form workbook for one project."""
        project = self._project_store.get(command.project_id)
        if project is None:
            raise CustomerFeedbackProjectNotFoundError(
                f"Project was not found: {command.project_id}"
            )
        template_folder = self._template_folder()
        template_path = _discover_template(template_folder)
        output_dir = self._controlled_output_dir(command)
        output_path = _available_output_path(output_dir, _output_file_name(project))
        identity = _identity_from_project(project)
        try:
            generated_path, warnings = self._workbook_gateway.generate(
                template_path=template_path,
                output_path=output_path,
                identity=identity,
            )
        except Exception as exc:
            raise CustomerFeedbackGenerationError(
                f"Customer Feedback workbook generation failed: {exc}"
            ) from exc
        return CustomerFeedbackFormGenerationResult(
            project_id=command.project_id,
            template_path=template_path,
            output_path=generated_path,
            output_file_name=generated_path.name,
            warnings=tuple(warnings),
        )

    def _template_folder(self) -> Path:
        resource = self._external_resource_store.get_by_type(
            ExternalResourceType.PROJECT_FOLDER_TEMPLATE
        )
        if resource is None:
            raise CustomerFeedbackReadinessError("Template folder is not configured.")
        folder = Path(resource.path)
        if not folder.is_dir():
            raise CustomerFeedbackReadinessError(
                f"Template folder does not exist or is not a folder: {folder}"
            )
        return folder

    def _controlled_output_dir(
        self,
        command: CustomerFeedbackFormGenerationCommand,
    ) -> Path:
        generated_root = self._generated_root.resolve()
        output_dir = (
            Path(command.output_dir)
            if command.output_dir is not None
            else self._generated_root / command.project_id
        )
        resolved_output_dir = output_dir.resolve()
        if (
            resolved_output_dir != generated_root
            and generated_root not in resolved_output_dir.parents
        ):
            raise CustomerFeedbackReadinessError(
                "Customer Feedback output must stay under the controlled generated output folder."
            )
        return resolved_output_dir


def _discover_template(template_folder: Path) -> Path:
    try:
        return discover_customer_feedback_template(template_folder)
    except TemplateDiscoveryAmbiguousError as exc:
        raise CustomerFeedbackTemplateAmbiguousError(str(exc)) from exc
    except CustomerFeedbackTemplateDiscoveryError as exc:
        raise CustomerFeedbackReadinessError(str(exc)) from exc


def _identity_from_project(project: Project) -> dict[str, str]:
    identity: dict[str, str] = {
        "requestor": project.requestor,
        "product_name": project.product_name,
    }
    if project.project_no:
        identity["ltr_number"] = project.project_no
    return identity


def _output_file_name(project: Project) -> str:
    stem = project.project_no or project.project_id
    return f"{_safe_file_stem(stem)}_customer_feedback_E-4243.xlsx"


def _available_output_path(output_dir: Path, file_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / file_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        next_candidate = output_dir / f"{stem}_{index}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        index += 1


def _safe_file_stem(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned.strip("._") or "customer_feedback"
