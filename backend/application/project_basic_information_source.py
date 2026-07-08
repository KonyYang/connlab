"""Project Basic Information source suggestion assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.application.project_identity import (
    select_registered_ltr,
    setup_payload_from_ltr_notes,
)
from backend.application.sample_description import format_description_pn
from backend.domain import ApplicationForm, LtrRecord, Project, SampleInfo


@dataclass(frozen=True, slots=True)
class ProjectBasicInformationFieldSuggestion:
    """Source suggestion for one Basic Information field."""

    field_key: str
    source: str
    source_value: str
    needs_review: bool


class LtrRecordRepositoryPort(Protocol):
    """LTR lookup port."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""


class ApplicationFormRepositoryPort(Protocol):
    """Application form lookup port."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""


class SampleInfoRepositoryPort(Protocol):
    """Application-form sample info lookup port."""

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return sample rows for a project."""


class ProjectBasicInformationSourceAssembler:
    """Assemble Basic Information source suggestions from current 330A providers."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordRepositoryPort,
        application_form_store: ApplicationFormRepositoryPort,
        sample_store: SampleInfoRepositoryPort,
    ) -> None:
        """Create a source assembler for Project/LTR/ApplicationForm sources."""
        self._ltrs = ltr_store
        self._forms = application_form_store
        self._samples = sample_store

    def assemble(self, project: Project) -> dict[str, ProjectBasicInformationFieldSuggestion]:
        """Return current source suggestions for a project."""
        forms = self._forms.list_by_project(project.project_id)
        latest_form = forms[-1] if forms else None
        samples = self._samples.list_by_project(project.project_id)
        ltrs = self._ltrs.list_by_project(project.project_id)
        latest_ltr = ltrs[-1] if ltrs else None
        registered_ltr = select_registered_ltr(ltrs)
        setup_payload = setup_payload_from_ltr_notes(
            registered_ltr.notes if registered_ltr else None
        )
        raw_values: dict[str, tuple[str, str | None]] = {
            "dl_number": (
                "project_identity",
                (latest_ltr.ltr_number if latest_ltr else None) or project.project_no,
            ),
            "project_type": ("application_form", latest_form.project_type if latest_form else None),
            "product_description": ("project_identity", project.product_name),
            "description_pn": ("sample_info", format_description_pn(samples)),
            "tests_to_be_performed": (
                "application_form",
                latest_form.requested_testing if latest_form else None,
            ),
            "test_item": (
                "project_setup_confirmation",
                _text_from_payload(setup_payload.get("test_item")),
            ),
            "requested_by": (
                "application_form",
                (latest_form.requester if latest_form else None) or project.requestor,
            ),
            "project_leader": (
                "application_form",
                latest_form.assigned_personnel if latest_form else None,
            ),
            "lab_performing_tests": (
                "application_form",
                latest_form.lab if latest_form else None,
            ),
            "phone": ("application_form", latest_form.phone if latest_form else None),
            "requestor_email": (
                "application_form",
                latest_form.email if latest_form else None,
            ),
            "location": (
                "application_form",
                latest_form.manufacturing_site if latest_form else None,
            ),
            "business_unit": (
                "application_form",
                (latest_form.business_unit if latest_form else None) or project.business_unit,
            ),
            "test_type": ("application_form", latest_form.test_type if latest_form else None),
            "test_type_in_sheet": (
                "project_setup_confirmation",
                _text_from_payload(setup_payload.get("test_type_in_sheet")),
            ),
            "sub_contract": (
                "application_form",
                latest_form.subcontract if latest_form else None,
            ),
            "condition_of_samples_when_received": (
                "application_form",
                latest_form.sample_condition if latest_form else None,
            ),
            "date_lab_received_samples": (
                "application_form",
                latest_form.received_date if latest_form else None,
            ),
            "estimated_completion_date": (
                "application_form",
                latest_form.estimated_completion_date if latest_form else None,
            ),
        }
        return {
            key: ProjectBasicInformationFieldSuggestion(
                field_key=key,
                source=source,
                source_value=value.strip(),
                needs_review=False,
            )
            for key, (source, value) in raw_values.items()
            if value is not None and value.strip()
        }


def _text_from_payload(value: object) -> str | None:
    """Return stripped setup payload text."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None
