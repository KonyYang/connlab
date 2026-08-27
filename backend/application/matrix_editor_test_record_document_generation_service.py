"""Generate Word Test Record previews from current Matrix Editor UI state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ApplicationFormLookup,
    ConfirmedMatrixTestRecordDocumentWriter,
    IntakeCaseLookup,
    IntakeDraftLookup,
    LtrRecordLookup,
    ProjectLookup,
    TestRecordHeaderMetadata,
    _date_or_min,
    _extract_specification_tokens,
    _parse_json_array,
    _parse_json_object,
    _safe_name,
)
from backend.application.confirmed_matrix_test_record_preview_service import (
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewStep,
    _apply_llcr_step_requirement_mapping,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_output_identity import (
    test_record_header_identity,
)
from backend.domain.enums import LtrStatus
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


class MatrixEditorTestRecordDocumentGenerationError(ValueError):
    """Raised when current Matrix Editor state cannot generate a preview document."""


class MatrixEditorTestRecordDocumentGenerationNotFoundError(LookupError):
    """Raised when required project data is missing."""


@dataclass(frozen=True, slots=True)
class MatrixEditorTestRecordGroupInput:
    """One currently visible Matrix Editor group."""

    group_key: str
    group_label: str
    sample_quantity_expression: str = ""


@dataclass(frozen=True, slots=True)
class MatrixEditorTestRecordRowInput:
    """One currently visible Matrix Editor row."""

    test_item: str
    section: str = ""
    method: str = ""
    condition: str = ""
    requirement: str = ""
    is_sample_row: bool = False
    group_values: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class GenerateMatrixEditorTestRecordDocumentCommand:
    """Command for current Matrix Editor Test Record preview generation."""

    project_id: str
    output_dir: Path
    template_path: Path
    groups: tuple[MatrixEditorTestRecordGroupInput, ...]
    rows: tuple[MatrixEditorTestRecordRowInput, ...]
    require_confirmed_header: bool = False
    output_file_name: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixEditorTestRecordDocumentGenerationResult:
    """Result for one generated current-state Test Record preview."""

    project_id: str
    output_path: Path
    file_name: str
    confirmed_basic_information_version: int | None = None
    confirmed_basic_information_source_signature_hash: str | None = None


class MatrixEditorTestRecordDocumentGenerationService:
    """Generate a preview-only Test Record from Matrix Editor current UI state."""

    def __init__(
        self,
        *,
        project_store: ProjectLookup,
        writer: ConfirmedMatrixTestRecordDocumentWriter,
        ltr_store: LtrRecordLookup | None = None,
        intake_case_store: IntakeCaseLookup | None = None,
        intake_draft_store: IntakeDraftLookup | None = None,
        application_form_store: ApplicationFormLookup | None = None,
        basic_information_reader: ConfirmedBasicInformationReader | None = None,
    ) -> None:
        self._project_store = project_store
        self._writer = writer
        self._ltrs = ltr_store
        self._intake_cases = intake_case_store
        self._intake_drafts = intake_draft_store
        self._forms = application_form_store
        self._basic_information = basic_information_reader

    def generate(
        self, command: GenerateMatrixEditorTestRecordDocumentCommand
    ) -> MatrixEditorTestRecordDocumentGenerationResult:
        """Generate one downloadable preview from the supplied current-state Matrix."""
        template_path = Path(command.template_path)
        if template_path.suffix.lower() != ".docx":
            raise MatrixEditorTestRecordDocumentGenerationError(
                f"Only .docx template is supported: {template_path}"
            )
        if not template_path.is_file():
            raise MatrixEditorTestRecordDocumentGenerationError(
                f"Test Record template does not exist: {template_path}"
            )
        preview_groups = _build_preview_groups(groups=command.groups, rows=command.rows)
        if not preview_groups:
            raise MatrixEditorTestRecordDocumentGenerationError(
                "Current Matrix Editor state has no previewable Test Record steps."
            )

        output_dir = Path(command.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        project = self._project_store.get(command.project_id)
        if project is None:
            raise MatrixEditorTestRecordDocumentGenerationNotFoundError(
                "Project not found."
            )
        project_no = str(getattr(project, "project_no", "") or "")
        basic_information = self._confirmed_basic_information(
            command.project_id,
            required=command.require_confirmed_header,
        )
        header_metadata = self._resolve_header_metadata(
            project_id=command.project_id,
            project=project,
            basic_information=basic_information,
            require_confirmed_header=command.require_confirmed_header,
        )
        file_name = command.output_file_name or _preview_output_file_name(
            command.project_id, project_no
        )
        output_path = output_dir / file_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            written = self._writer.generate_from_confirmed_matrix(
                template_path=template_path,
                output_path=output_path,
                project_id=command.project_id,
                project_no=project_no,
                product_description=header_metadata.product_description,
                applicable_specification="",
                confirmed_matrix_id="Unconfirmed Matrix draft preview",
                groups=tuple(preview_groups),
                header_metadata=header_metadata,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            raise MatrixEditorTestRecordDocumentGenerationError(str(exc)) from exc
        return MatrixEditorTestRecordDocumentGenerationResult(
            project_id=command.project_id,
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

    def _resolve_header_metadata(
        self,
        *,
        project_id: str,
        project: object,
        basic_information: ConfirmedBasicInformationSnapshot | None = None,
        require_confirmed_header: bool = False,
    ) -> TestRecordHeaderMetadata:
        confirmed_identity = None
        if basic_information is not None:
            confirmed_identity = test_record_header_identity(basic_information)
            if (
                require_confirmed_header
                and not confirmed_identity.lab_test_request_number.strip()
            ):
                raise MatrixEditorTestRecordDocumentGenerationError(
                    "Confirm Basic Information before generating Test Record: DL/LTR Number is missing."
                )
            if (
                require_confirmed_header
                and not confirmed_identity.product_description.strip()
            ):
                raise MatrixEditorTestRecordDocumentGenerationError(
                    "Confirm Basic Information before generating Test Record: Product Description is missing."
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
        if confirmed_identity is not None:
            lab_test_request_number = (
                confirmed_identity.lab_test_request_number or lab_test_request_number
            )
            product_description = (
                confirmed_identity.product_description or product_description
            )
            applicable_specification = (
                confirmed_identity.applicable_specification
                or applicable_specification
            )
        return TestRecordHeaderMetadata(
            lab_test_request_number=lab_test_request_number,
            product_description=product_description,
            applicable_specification=applicable_specification,
        )

    def _confirmed_basic_information(
        self, project_id: str, *, required: bool
    ) -> ConfirmedBasicInformationSnapshot | None:
        if self._basic_information is None:
            if required:
                raise MatrixEditorTestRecordDocumentGenerationError(
                    "Confirm Basic Information before saving Test Record to the project folder."
                )
            return None
        snapshot = self._basic_information.get_latest_confirmed(project_id)
        if snapshot is None and required:
            raise MatrixEditorTestRecordDocumentGenerationError(
                "Confirm Basic Information before saving Test Record to the project folder."
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


def _build_preview_groups(
    *,
    groups: tuple[MatrixEditorTestRecordGroupInput, ...],
    rows: tuple[MatrixEditorTestRecordRowInput, ...],
) -> list[ConfirmedMatrixTestRecordPreviewGroup]:
    preview_groups: list[ConfirmedMatrixTestRecordPreviewGroup] = []
    for group in groups:
        steps: list[ConfirmedMatrixTestRecordPreviewStep] = []
        for row in rows:
            if row.is_sample_row:
                continue
            cell_value = _normalize_text((row.group_values or {}).get(group.group_key))
            if not cell_value:
                continue
            parsed_tokens, _warnings = parse_step_tokens(cell_value)
            for token in parsed_tokens:
                steps.append(
                    ConfirmedMatrixTestRecordPreviewStep(
                        sequence=token.sequence,
                        raw_token=token.raw_token,
                        test_item=_normalize_text(row.test_item),
                        section=_normalize_text(row.section),
                        method=_normalize_text(row.method),
                        condition=_normalize_text(row.condition),
                        requirement=_normalize_text(row.requirement),
                    )
                )
        steps.sort(key=lambda step: (step.sequence, step.raw_token))
        _apply_llcr_step_requirement_mapping(steps)
        if not steps:
            continue
        preview_groups.append(
            ConfirmedMatrixTestRecordPreviewGroup(
                group_key=_normalize_text(group.group_key),
                group_label=_normalize_text(group.group_label),
                sample_quantity_expression=_normalize_text(
                    group.sample_quantity_expression
                ),
                step_count=len(steps),
                steps=tuple(steps),
            )
        )
    return preview_groups


def _preview_output_file_name(project_id: str, project_no: str) -> str:
    preferred = _safe_name(project_no) if project_no.strip() else _safe_name(project_id)
    return f"{preferred} Test Record Preview - Unconfirmed Matrix draft.docx"


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()
