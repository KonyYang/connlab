from __future__ import annotations

import json
from dataclasses import replace
from datetime import date

import pytest

from backend.application.project_basic_information_service import (
    ConfirmProjectBasicInformationCommand,
    ProjectBasicInformationMissingRequiredError,
    ProjectBasicInformationRecord,
    ProjectBasicInformationService,
    SaveProjectBasicInformationDraftCommand,
)
from backend.domain import (
    ApplicationForm,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectStatus,
    SampleInfo,
)


def test_existing_project_without_records_returns_assembled_unconfirmed_draft() -> None:
    service = _service()

    result = service.get("P1")

    assert result.status == "unconfirmed"
    assert result.draft.values["dl_number"] == "DL-2026-05-011"
    assert result.draft.values["project_type"] == "NPD"
    assert result.draft.values["description_pn"] == (
        "Coolpower HDF:PN-001, Shield:PN-002"
    )
    assert result.draft.values["requested_by"] == "MP Cao"
    assert result.draft.values["phone"] == "1234"
    assert result.latest_confirmed is None


def test_saved_draft_values_survive_later_source_changes() -> None:
    projects = _ProjectStore()
    forms = _ApplicationFormStore()
    ltrs = _LtrStore()
    records = _BasicInformationStore()
    service = ProjectBasicInformationService(
        project_store=projects,
        ltr_store=ltrs,
        application_form_store=forms,
        sample_store=_SampleInfoStore(),
        basic_information_store=records,
        clock=lambda: "2026-06-20T09:00:00+08:00",
        id_factory=_id_factory(),
    )
    service.save_draft(
        SaveProjectBasicInformationDraftCommand(
            project_id="P1",
            values={"project_type": "PEX", "requested_by": "Operator"},
        )
    )
    forms.forms[0] = _form(project_type="NPD", requester="Changed Requester")

    result = service.get("P1")

    assert result.draft.values["project_type"] == "PEX"
    assert result.draft.values["requested_by"] == "Operator"
    assert result.field_suggestions["requested_by"].source_value == "Changed Requester"


def test_latest_confirmed_values_beat_source_suggestions_without_draft() -> None:
    service = _service()
    service.confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values=_complete_values(project_type="PEX", requested_by="Confirmed User"),
            confirmed_by="Lab User",
        )
    )

    result = service.get("P1")

    assert result.status == "confirmed"
    assert result.draft.values["project_type"] == "PEX"
    assert result.draft.values["requested_by"] == "Confirmed User"
    assert result.changed_source_fields == tuple()


def test_confirm_allows_description_pn_when_product_description_is_missing() -> None:
    service = _service()

    result = service.confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values={
                "dl_number": "DL-2026-05-011",
                "project_type": "NPD",
                "description_pn": "PN-123",
                "test_item": "Qualification Testing",
                "requested_by": "MP Cao",
                "project_leader": "Even Yang",
                "lab_performing_tests": "Dongguan",
            },
            confirmed_by="Lab User",
        )
    )

    assert result.latest_confirmed is not None
    assert result.latest_confirmed.version == 1


def test_changed_sources_after_confirmation_mark_needs_review_without_mutation() -> None:
    projects = _ProjectStore()
    forms = _ApplicationFormStore()
    ltrs = _LtrStore()
    records = _BasicInformationStore()
    service = ProjectBasicInformationService(
        project_store=projects,
        ltr_store=ltrs,
        application_form_store=forms,
        sample_store=_SampleInfoStore(),
        basic_information_store=records,
        clock=lambda: "2026-06-20T09:00:00+08:00",
        id_factory=_id_factory(),
    )
    confirmed = service.confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values=_complete_values(requested_by="MP Cao"),
            confirmed_by="Lab User",
        )
    ).latest_confirmed
    forms.forms[0] = _form(requester="Changed Requester")

    result = service.get("P1")

    assert result.status == "needs_review"
    assert result.latest_confirmed == confirmed
    assert result.latest_confirmed is not None
    assert result.latest_confirmed.values["requested_by"] == "MP Cao"
    assert "requested_by" in result.changed_source_fields
    assert result.field_suggestions["requested_by"].needs_review is True


def test_source_assembly_keeps_application_test_type_separate_from_sheet_test_type() -> None:
    ltrs = _LtrStore()
    ltrs.records = [
        LtrRecord(
            ltr_id="DRAFT",
            project_id="P1",
            ltr_number="DL-2026-05-010",
            status=LtrStatus.DRAFT,
            registered_on=date(2026, 5, 1),
            notes=_ltr_notes("Analysis"),
        ),
        LtrRecord(
            ltr_id="REGISTERED",
            project_id="P1",
            ltr_number="DL-2026-05-011",
            status=LtrStatus.REGISTERED,
            registered_on=date(2026, 5, 2),
            notes=_ltr_notes("Qualification"),
        ),
    ]
    service = ProjectBasicInformationService(
        project_store=_ProjectStore(),
        ltr_store=ltrs,
        application_form_store=_ApplicationFormStore(),
        sample_store=_SampleInfoStore(),
        basic_information_store=_BasicInformationStore(),
        clock=lambda: "2026-06-20T09:00:00+08:00",
        id_factory=_id_factory(),
    )

    result = service.get("P1")

    assert result.draft.values["test_type"] == "Partial Qualification"
    assert result.field_suggestions["test_type"].source == "application_form"
    assert result.draft.values["test_type_in_sheet"] == "Qualification"
    assert result.field_suggestions["test_type_in_sheet"].source == (
        "project_setup_confirmation"
    )


def test_new_sheet_test_type_source_marks_existing_confirmed_snapshot_needs_review() -> None:
    ltrs = _LtrStore()
    ltrs.records[0] = replace(
        ltrs.records[0],
        status=LtrStatus.REGISTERED,
        registered_on=date(2026, 5, 2),
        notes=_ltr_notes("Qualification"),
    )
    records = _BasicInformationStore()
    records.records.append(
        ProjectBasicInformationRecord(
            record_id="LEGACY",
            project_id="P1",
            status="confirmed",
            version=1,
            values=_complete_values(test_type="Partial Qualification"),
            source_signature='{"test_type":"Partial Qualification"}',
            created_at="2026-06-19T09:00:00+08:00",
            updated_at="2026-06-19T09:00:00+08:00",
            confirmed_at="2026-06-19T09:00:00+08:00",
            confirmed_by="Lab User",
        )
    )
    service = ProjectBasicInformationService(
        project_store=_ProjectStore(),
        ltr_store=ltrs,
        application_form_store=_ApplicationFormStore(),
        sample_store=_SampleInfoStore(),
        basic_information_store=records,
        clock=lambda: "2026-06-20T09:00:00+08:00",
        id_factory=_id_factory(),
    )
    result = service.get("P1")

    assert result.status == "needs_review"
    assert "test_type_in_sheet" in result.changed_source_fields
    assert result.field_suggestions["test_type_in_sheet"].needs_review is True


def test_confirm_rejects_missing_required_fields_with_business_labels() -> None:
    service = _service()

    with pytest.raises(ProjectBasicInformationMissingRequiredError) as exc_info:
        service.confirm(
            ConfirmProjectBasicInformationCommand(
                project_id="P1",
                values={"dl_number": "DL-2026-05-011"},
                confirmed_by="Lab User",
            )
        )

    assert "Project Type" in exc_info.value.missing_labels
    assert "Product Description or Description P/N" in exc_info.value.missing_labels
    assert "Test Item" in exc_info.value.missing_labels
    assert "Lab Performing the Tests" in exc_info.value.missing_labels


def test_confirm_creates_new_versions_without_overwriting_old_versions() -> None:
    records = _BasicInformationStore()
    service = _service(records=records)

    first = service.confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values=_complete_values(project_type="NPD"),
            confirmed_by="Lab User",
        )
    ).latest_confirmed
    second = service.confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values=_complete_values(project_type="PEX"),
            confirmed_by="Lab User",
        )
    ).latest_confirmed

    assert first is not None
    assert second is not None
    assert first.version == 1
    assert second.version == 2
    assert [record.version for record in records.list_confirmed_by_project("P1")] == [1, 2]
    assert records.list_confirmed_by_project("P1")[0].values["project_type"] == "NPD"


def _service(records: _BasicInformationStore | None = None) -> ProjectBasicInformationService:
    return ProjectBasicInformationService(
        project_store=_ProjectStore(),
        ltr_store=_LtrStore(),
        application_form_store=_ApplicationFormStore(),
        sample_store=_SampleInfoStore(),
        basic_information_store=records or _BasicInformationStore(),
        clock=lambda: "2026-06-20T09:00:00+08:00",
        id_factory=_id_factory(),
    )


def _id_factory():
    count = 0

    def next_id() -> str:
        nonlocal count
        count += 1
        return f"BASIC-{count}"

    return next_id


def _complete_values(**overrides: str) -> dict[str, str]:
    values = {
        "dl_number": "DL-2026-05-011",
        "project_type": "NPD",
        "product_description": "Coolpower HDF",
        "test_item": "Qualification Testing",
        "requested_by": "MP Cao",
        "project_leader": "Even Yang",
        "lab_performing_tests": "Dongguan",
    }
    values.update(overrides)
    return values


def _project() -> Project:
    return Project(
        project_id="P1",
        project_no="DL-2026-05-011",
        product_name="Coolpower HDF",
        requestor="MP Cao",
        status=ProjectStatus.CONFIRMED,
        business_unit="BU",
        created_on=date(2026, 6, 20),
    )


def _form(
    *,
    project_type: str = "NPD",
    requester: str = "MP Cao",
) -> ApplicationForm:
    return ApplicationForm(
        form_id="F1",
        project_id="P1",
        form_no="E-3718",
        revision="H",
        requester=requester,
        request_date=date(2026, 6, 20),
        phone="1234",
        email="mp@example.com",
        business_unit="BU",
        manufacturing_site="Dongguan",
        requested_testing="Qualification Testing",
        subcontract_allowed=True,
        project_number="DL-2026-05-011",
        test_type="Partial Qualification",
        project_type=project_type,
        subcontract="Yes",
        lab="Dongguan",
        assigned_personnel="Even Yang",
        received_date="20 Jun 2026",
        estimated_completion_date="20 Jun 2026",
        sample_condition="Acceptable",
    )


def _sample(
    *,
    sample_id: str = "S1",
    product_name: str = "Coolpower HDF",
    part_number: str = "PN-001",
) -> SampleInfo:
    return SampleInfo(
        sample_id=sample_id,
        project_id="P1",
        product_name=product_name,
        part_number=part_number,
        lot_or_traceability="LOT-1",
        material="Base material",
        plating="Contact plating",
        housing_material="Housing material",
    )


class _ProjectStore:
    def __init__(self) -> None:
        self.project = _project()

    def get(self, project_id: str) -> Project | None:
        return self.project if project_id == self.project.project_id else None


class _LtrStore:
    def __init__(self) -> None:
        self.records = [
            LtrRecord(
                ltr_id="L1",
                project_id="P1",
                ltr_number="DL-2026-05-011",
                status=LtrStatus.REGISTERED,
                requested_by="MP Cao",
                requested_date=date(2026, 6, 20),
            )
        ]

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [record for record in self.records if record.project_id == project_id]


class _ApplicationFormStore:
    def __init__(self) -> None:
        self.forms = [_form()]

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [form for form in self.forms if form.project_id == project_id]


class _SampleInfoStore:
    def __init__(self) -> None:
        self.samples = [
            _sample(),
            _sample(sample_id="S2", product_name="Shield", part_number="PN-002"),
        ]

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        return [sample for sample in self.samples if sample.project_id == project_id]


def _ltr_notes(test_type_in_sheet: str) -> str:
    return json.dumps(
        {
            "operator_note": json.dumps(
                {
                    "source": "new_project_setup_confirmation",
                    "test_type_in_sheet": test_type_in_sheet,
                },
                sort_keys=True,
            )
        },
        sort_keys=True,
    )


class _BasicInformationStore:
    def __init__(self) -> None:
        self.records = []

    def get_latest_draft(self, project_id: str):
        drafts = [
            record
            for record in self.records
            if record.project_id == project_id and record.status == "draft"
        ]
        return drafts[-1] if drafts else None

    def get_latest_confirmed(self, project_id: str):
        confirmed = self.list_confirmed_by_project(project_id)
        return confirmed[-1] if confirmed else None

    def list_confirmed_by_project(self, project_id: str):
        return [
            record
            for record in self.records
            if record.project_id == project_id and record.status == "confirmed"
        ]

    def save_draft(self, record):
        existing = self.get_latest_draft(record.project_id)
        if existing is not None:
            self.records.remove(existing)
        self.records.append(record)
        return record

    def create_confirmed(self, record):
        self.records.append(record)
        return record

    def next_confirmed_version(self, project_id: str) -> int:
        return len(self.list_confirmed_by_project(project_id)) + 1
