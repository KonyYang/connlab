"""Generate Word Test Record drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Protocol
from datetime import date

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_output_identity import (
    test_record_header_identity,
)
from backend.domain.enums import LtrStatus


class ConfirmedMatrixTestRecordDocumentGenerationError(ValueError):
    """Raised when active confirmed Matrix data cannot generate a document."""


class ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(LookupError):
    """Raised when required active authority or project data is missing."""


class ProjectLookup(Protocol):
    """Project read operations needed for document metadata."""

    def get(self, project_id: str):
        """Return one project domain object by id."""


class LtrRecordLookup(Protocol):
    """LTR read operations needed for header metadata resolution."""

    def list_by_project(self, project_id: str):
        """Return LTR records linked to one project."""


class IntakeCaseLookup(Protocol):
    """Intake case lookup needed for confirmed-project draft traversal."""

    def get_by_confirmed_project(self, project_id: str):
        """Return one intake case linked to a confirmed project."""


class IntakeDraftLookup(Protocol):
    """Intake draft lookup needed for specification resolution."""

    def get_by_case(self, case_id: str):
        """Return one intake draft by case id."""


class ApplicationFormLookup(Protocol):
    """Application form lookup used as specification fallback."""

    def list_by_project(self, project_id: str):
        """Return project-linked application forms."""


@dataclass(frozen=True, slots=True)
class TestRecordHeaderMetadata:
    """Resolved metadata for Test Record header cells."""

    __test__ = False
    lab_test_request_number: str = ""
    product_description: str = ""
    applicable_specification: str = ""


class ConfirmedMatrixTestRecordDocumentWriter(Protocol):
    """Infrastructure writer for Word Test Record drafts."""

    def generate_from_confirmed_matrix(
        self,
        *,
        template_path: Path,
        output_path: Path,
        project_id: str,
        project_no: str,
        product_description: str,
        applicable_specification: str,
        confirmed_matrix_id: str,
        groups: tuple,
        header_metadata: TestRecordHeaderMetadata,
    ) -> Path:
        """Write one `.docx` draft and return its output path."""


@dataclass(frozen=True, slots=True)
class GenerateConfirmedMatrixTestRecordDocumentCommand:
    """Command for ConfirmedMatrix-backed Test Record Word generation."""

    project_id: str
    output_dir: Path
    template_path: Path


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordDocumentGenerationResult:
    """Result for one generated Test Record Word draft."""

    project_id: str
    confirmed_matrix_id: str
    output_path: Path
    file_name: str
    confirmed_basic_information_version: int | None = None
    confirmed_basic_information_source_signature_hash: str | None = None


class ConfirmedMatrixTestRecordDocumentGenerationService:
    """Generate one Word Test Record draft from active ConfirmedMatrix preview data."""

    def __init__(
        self,
        *,
        preview_service: ConfirmedMatrixTestRecordPreviewService,
        project_store: ProjectLookup,
        writer: ConfirmedMatrixTestRecordDocumentWriter,
        folder_store: "ProjectFolderLookup | None" = None,
        ltr_store: LtrRecordLookup | None = None,
        intake_case_store: IntakeCaseLookup | None = None,
        intake_draft_store: IntakeDraftLookup | None = None,
        application_form_store: ApplicationFormLookup | None = None,
        basic_information_reader: ConfirmedBasicInformationReader | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._project_store = project_store
        self._writer = writer
        self._folder_store = folder_store
        self._ltrs = ltr_store
        self._intake_cases = intake_case_store
        self._intake_drafts = intake_draft_store
        self._forms = application_form_store
        self._basic_information = basic_information_reader

    def generate(
        self,
        command: GenerateConfirmedMatrixTestRecordDocumentCommand,
    ) -> ConfirmedMatrixTestRecordDocumentGenerationResult:
        """Generate a downloadable Word draft from active ConfirmedMatrix authority."""
        template_path = Path(command.template_path)
        if not template_path.suffix.lower() == ".docx":
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                f"Only .docx template is supported: {template_path}"
            )
        if not template_path.is_file():
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                f"Test Record template does not exist: {template_path}"
            )
        output_dir = Path(command.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        preview = self._load_preview(command.project_id)
        if preview.preview_status != "ready" or not preview.groups:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                "Active confirmed matrix has no previewable Test Record steps."
            )

        project = self._project_store.get(command.project_id)
        project_no = str(getattr(project, "project_no", "") or "")
        basic_information = self._confirmed_basic_information(command.project_id)
        header_metadata = self._resolve_header_metadata(
            project_id=command.project_id,
            project=project,
            basic_information=basic_information,
        )
        product_description = header_metadata.product_description
        file_name = _output_file_name(command.project_id, project_no)
        output_path = self._resolve_output_path(
            project_id=command.project_id,
            output_dir=output_dir,
            file_name=file_name,
        )
        output_path = _non_overwriting_output_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            written = self._writer.generate_from_confirmed_matrix(
                template_path=template_path,
                output_path=output_path,
                project_id=command.project_id,
                project_no=project_no,
                product_description=product_description,
                applicable_specification="",
                confirmed_matrix_id=preview.confirmed_matrix_id,
                groups=preview.groups,
                header_metadata=header_metadata,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(str(exc)) from exc
        return ConfirmedMatrixTestRecordDocumentGenerationResult(
            project_id=command.project_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            output_path=written,
            file_name=file_name,
            confirmed_basic_information_version=(
                basic_information.version if basic_information is not None else None
            ),
            confirmed_basic_information_source_signature_hash=(
                basic_information.source_signature_hash
                if basic_information is not None
                else None
            ),
        )

    def _load_preview(self, project_id: str):
        try:
            return self._preview_service.build_preview(
                BuildConfirmedMatrixTestRecordPreviewCommand(project_id=project_id)
            )
        except ConfirmedMatrixTestRecordPreviewNotFoundError as exc:
            raise ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(str(exc)) from exc

    def _resolve_output_path(
        self, *, project_id: str, output_dir: Path, file_name: str
    ) -> Path:
        if self._folder_store is None:
            return output_dir / file_name
        folders = self._folder_store.list_by_project(project_id)
        if not folders:
            return output_dir / file_name
        latest = max(
            folders,
            key=lambda folder: (
                folder.created_on is not None,
                folder.created_on,
                str(folder.folder_path),
            ),
        )
        return latest.folder_path / "Submitted Material" / file_name

    def _resolve_header_metadata(
        self,
        *,
        project_id: str,
        project: object,
        basic_information: ConfirmedBasicInformationSnapshot | None = None,
    ) -> TestRecordHeaderMetadata:
        if basic_information is not None:
            identity = test_record_header_identity(basic_information)
            lab_test_request_number = _required_identity_text(
                identity.lab_test_request_number,
                "DL/LTR Number",
            )
            product_description = _required_identity_text(
                identity.product_description,
                "Product Description",
            )
            applicable_specification = identity.applicable_specification
            if not applicable_specification:
                applicable_specification = self._resolve_applicable_specification(project_id)
            return TestRecordHeaderMetadata(
                lab_test_request_number=lab_test_request_number,
                product_description=product_description,
                applicable_specification=applicable_specification,
            )

        registered_ltr = self._latest_registered_ltr(project_id)
        lab_test_request_number = ""
        product_description = str(getattr(project, "product_name", "") or "")
        if registered_ltr is not None:
            lab_test_request_number = str(getattr(registered_ltr, "ltr_number", "") or "")
            notes = _parse_json_object(getattr(registered_ltr, "notes", None))
            sample_description = str(notes.get("sample_description", "") or "").strip()
            if sample_description:
                product_description = sample_description

        applicable_specification = self._resolve_applicable_specification(project_id)
        return TestRecordHeaderMetadata(
            lab_test_request_number=lab_test_request_number,
            product_description=product_description,
            applicable_specification=applicable_specification,
        )

    def _confirmed_basic_information(
        self, project_id: str
    ) -> ConfirmedBasicInformationSnapshot | None:
        if self._basic_information is None:
            return None
        snapshot = self._basic_information.get_latest_confirmed(project_id)
        if snapshot is None:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                "Confirm Basic Information before generating Test Record."
            )
        return snapshot

    def _latest_registered_ltr(self, project_id: str):
        if self._ltrs is None:
            return None
        candidates = [
            ltr
            for ltr in self._ltrs.list_by_project(project_id)
            if getattr(ltr, "status", None) is LtrStatus.REGISTERED
        ]
        if not candidates:
            return None
        return max(
            candidates,
            key=lambda ltr: (
                _date_or_min(getattr(ltr, "registered_on", None)),
                str(getattr(ltr, "ltr_number", "") or ""),
            ),
        )

    def _resolve_applicable_specification(self, project_id: str) -> str:
        spec_from_draft = self._resolve_specification_from_confirmed_intake_draft(project_id)
        if spec_from_draft:
            return spec_from_draft
        if self._forms is None:
            return ""
        forms = self._forms.list_by_project(project_id)
        if not forms:
            return ""
        fallback_text = str(getattr(forms[-1], "requested_testing", "") or "")
        return _extract_specification_tokens(fallback_text)

    def _resolve_specification_from_confirmed_intake_draft(self, project_id: str) -> str:
        if self._intake_cases is None or self._intake_drafts is None:
            return ""
        intake_case = self._intake_cases.get_by_confirmed_project(project_id)
        if intake_case is None:
            return ""
        draft = self._intake_drafts.get_by_case(intake_case.case_id)
        if draft is None:
            return ""
        payload = _parse_json_array(draft.requested_testing_json)
        specs: list[str] = []
        seen: set[str] = set()
        for item in payload:
            if not isinstance(item, dict):
                continue
            value = str(item.get("applicable_specification", "") or "").strip()
            if not value:
                continue
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            specs.append(value)
        return "; ".join(specs)


class ProjectFolderLookup(Protocol):
    """Project folder lookup operations used to resolve target path."""

    def list_by_project(self, project_id: str):
        """Return all folder records linked to one project."""


def _safe_name(value: str) -> str:
    safe = value.replace("/", "_").replace("\\", "_").strip()
    return safe or "project"


def _output_file_name(project_id: str, project_no: str) -> str:
    preferred = _safe_name(project_no) if project_no.strip() else _safe_name(project_id)
    return f"{preferred} Test Record.docx"


def _non_overwriting_output_path(path: Path) -> Path:
    """Return a unique draft path so existing user documents are not overwritten."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem} ({index}){suffix}")
        if not candidate.exists():
            return candidate
    raise ConfirmedMatrixTestRecordDocumentGenerationError(
        f"Cannot find an available Test Record output name near: {path}"
    )


def _required_basic_text(
    values: dict[str, str],
    keys: tuple[str, ...],
    label: str,
) -> str:
    """Return a required value from confirmed Basic Information."""
    for key in keys:
        value = str(values.get(key, "") or "").strip()
        if value:
            return value
    raise ConfirmedMatrixTestRecordDocumentGenerationError(
        f"Confirm Basic Information before generating Test Record: {label} is missing."
    )


def _required_identity_text(value: str, label: str) -> str:
    """Return a required Test Record header identity value."""
    if value.strip():
        return value.strip()
    raise ConfirmedMatrixTestRecordDocumentGenerationError(
        f"Confirm Basic Information before generating Test Record: {label} is missing."
    )


def _parse_json_object(raw: object) -> dict[str, object]:
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _parse_json_array(raw: object) -> list[object]:
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def _date_or_min(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.min


def _extract_specification_tokens(raw: str) -> str:
    text = raw.strip()
    if not text:
        return ""
    pattern = re.compile(r"\b(?:EIA-\d+(?:-\d+[A-Z]?)?|GS-[A-Z0-9-]+|QG-[A-Z0-9-]+|IEC\s*\d+(?:-\d+)*|ASTM\s*[A-Z]?\d+[A-Z0-9-]*|UL\s*\d+[A-Z0-9-]*)\b", re.IGNORECASE)
    matches = pattern.findall(text)
    if not matches:
        return ""
    unique: list[str] = []
    seen: set[str] = set()
    for match in matches:
        token = re.sub(r"\s+", " ", match).strip()
        key = token.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(token)
    return "; ".join(unique)
