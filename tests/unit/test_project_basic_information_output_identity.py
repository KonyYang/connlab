from __future__ import annotations

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_output_identity import (
    application_form_identity,
    customer_feedback_identity,
    fee_form_identity,
    test_record_header_identity,
)


def test_output_identity_maps_fee_form_fields_from_basic_information_only() -> None:
    identity = fee_form_identity(_snapshot())

    assert identity.as_dict() == {
        "dl_number": "DL-BI",
        "product_description": "Connector BI",
        "test_item": "Qualification BI",
        "requested_by": "Requester BI",
        "location": "Dongguan",
        "lab_performing_tests": "Dongguan Lab",
    }


def test_output_identity_maps_customer_feedback_fields() -> None:
    identity = customer_feedback_identity(_snapshot())

    assert identity.as_dict() == {
        "ltr_number": "DL-BI",
        "product_name": "Connector BI",
        "test_item": "Qualification BI",
        "requestor": "Requester BI",
        "phone": "12345",
        "email": "requester@example.test",
        "location": "Dongguan",
        "project_leader": "Even Yang",
        "lab": "Dongguan Lab",
        "received_date": "20 Jun 2026",
        "estimated_completion_date": "02 Jul 2026",
    }


def test_output_identity_keeps_optional_values_empty_without_fallback() -> None:
    identity = application_form_identity(
        _snapshot(
            {
                "dl_number": "DL-BI",
                "product_description": "",
                "description_pn": "101-ABC",
                "tests_to_be_performed": "Qualification BI",
                "requested_by": "Requester BI",
            }
        )
    )

    assert identity.fields["product_description"] == ""
    assert identity.fields["description_pn"] == "101-ABC"
    assert "Connector from Project" not in identity.fields.values()


def test_output_identity_maps_test_record_header() -> None:
    identity = test_record_header_identity(_snapshot())

    assert identity.lab_test_request_number == "DL-BI"
    assert identity.product_description == "Connector BI"
    assert identity.applicable_specification == "GS-12-BI"


def _snapshot(
    values: dict[str, str] | None = None,
) -> ConfirmedBasicInformationSnapshot:
    payload = {
        "dl_number": "DL-BI",
        "project_number": "PN-BI",
        "project_type": "NPD",
        "description_pn": "",
        "product_description": "Connector BI",
        "tests_to_be_performed": "Qualification BI",
        "applicable_specifications": "GS-12-BI",
        "requested_by": "Requester BI",
        "phone": "12345",
        "requestor_email": "requester@example.test",
        "location": "Dongguan",
        "project_leader": "Even Yang",
        "lab_performing_tests": "Dongguan Lab",
        "date_lab_received_samples": "20 Jun 2026",
        "estimated_completion_date": "02 Jul 2026",
        "business_unit": "BU-BI",
        "requested_completion_date": "30 Jul 2026",
        "results_format": "Electronic",
        "test_sample_status": "Available",
        "confidential": "No",
        "sub_contract": "No",
        "send_report_copies_to": "Andy Lu",
    }
    if values is not None:
        payload.update(values)
    return ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=1,
        values=payload,
        source_signature='{"dl_number":"DL-BI"}',
        confirmed_at="2026-06-21T00:00:00+00:00",
        confirmed_by="Lab User",
    )
