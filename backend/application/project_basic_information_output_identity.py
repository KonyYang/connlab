"""Output-specific identity payloads derived from confirmed Basic Information."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)


@dataclass(frozen=True, slots=True)
class FeeFormIdentity:
    """Basic Information fields written to Fee Evaluation workbook headers."""

    dl_number: str
    product_description: str
    test_item: str
    requested_by: str
    location: str
    lab_performing_tests: str

    def as_dict(self) -> dict[str, str]:
        """Return non-optional Fee Form identity fields as a plain mapping."""
        return {
            "dl_number": self.dl_number,
            "product_description": self.product_description,
            "test_item": self.test_item,
            "requested_by": self.requested_by,
            "location": self.location,
            "lab_performing_tests": self.lab_performing_tests,
        }


@dataclass(frozen=True, slots=True)
class CustomerFeedbackIdentity:
    """Basic Information fields written to Customer Feedback workbook headers."""

    ltr_number: str
    product_name: str
    test_item: str
    requestor: str
    phone: str
    email: str
    location: str
    project_leader: str
    lab: str
    received_date: str
    estimated_completion_date: str

    def as_dict(self) -> dict[str, str]:
        """Return Customer Feedback identity fields as a plain mapping."""
        return {
            "ltr_number": self.ltr_number,
            "product_name": self.product_name,
            "test_item": self.test_item,
            "requestor": self.requestor,
            "phone": self.phone,
            "email": self.email,
            "location": self.location,
            "project_leader": self.project_leader,
            "lab": self.lab,
            "received_date": self.received_date,
            "estimated_completion_date": self.estimated_completion_date,
        }


@dataclass(frozen=True, slots=True)
class ApplicationFormWriteBackIdentity:
    """Basic Information fields for copied Application Form Word write-back."""

    fields: dict[str, str]


@dataclass(frozen=True, slots=True)
class TestRecordHeaderIdentity:
    """Basic Information fields written to Test Record header metadata."""

    lab_test_request_number: str
    product_description: str
    applicable_specification: str


def fee_form_identity(
    snapshot: ConfirmedBasicInformationSnapshot,
) -> FeeFormIdentity:
    """Return Fee Form identity from confirmed Basic Information only."""
    values = snapshot.values
    return FeeFormIdentity(
        dl_number=_text(values, "dl_number"),
        product_description=_text(values, "product_description"),
        test_item=_text(values, "test_item"),
        requested_by=_text(values, "requested_by"),
        location=_text(values, "location"),
        lab_performing_tests=_text(values, "lab_performing_tests"),
    )


def customer_feedback_identity(
    snapshot: ConfirmedBasicInformationSnapshot,
) -> CustomerFeedbackIdentity:
    """Return Customer Feedback identity from confirmed Basic Information only."""
    values = snapshot.values
    return CustomerFeedbackIdentity(
        ltr_number=_text(values, "dl_number"),
        product_name=(
            _text(values, "product_description") or _text(values, "description_pn")
        ),
        test_item=_text(values, "test_item"),
        requestor=_text(values, "requested_by"),
        phone=_text(values, "phone"),
        email=_text(values, "requestor_email"),
        location=_text(values, "location"),
        project_leader=_text(values, "project_leader"),
        lab=_text(values, "lab_performing_tests"),
        received_date=_text(values, "date_lab_received_samples"),
        estimated_completion_date=_text(values, "estimated_completion_date"),
    )


def application_form_identity(
    snapshot: ConfirmedBasicInformationSnapshot,
) -> ApplicationFormWriteBackIdentity:
    """Return Application Form write-back fields from confirmed Basic Information."""
    values = snapshot.values
    fields = {
        "ltr_number": _text(values, "dl_number"),
        "project_number": _text(values, "project_number"),
        "project_type": _text(values, "project_type"),
        "description_pn": _text(values, "description_pn"),
        "product_description": _text(values, "product_description"),
        "test_item": _text(values, "test_item"),
        "applicable_specifications": _text(values, "applicable_specifications"),
        "requested_by": _text(values, "requested_by"),
        "requester": _text(values, "requested_by"),
        "phone": _text(values, "phone"),
        "email": _text(values, "requestor_email"),
        "location": _text(values, "location"),
        "manufacturing_site": _text(values, "location"),
        "project_leader": _text(values, "project_leader"),
        "business_unit": _text(values, "business_unit"),
        "requested_completion_date": _text(values, "requested_completion_date"),
        "results_format": _text(values, "results_format"),
        "test_sample_status": _text(values, "test_sample_status"),
        "lab": _text(values, "lab_performing_tests"),
        "received_date": _text(values, "date_lab_received_samples"),
        "estimated_completion_date": _text(values, "estimated_completion_date"),
        "start_test_date": _text(values, "start_test_date"),
        "finish_test_date": _text(values, "finish_test_date"),
        "report_date": _text(values, "report_date"),
        "test_fee": _text(values, "test_fee"),
        "remarks_po": _text(values, "remarks_po"),
        "sample_condition": _text(values, "condition_of_samples_when_received"),
        "confidential": _text(values, "confidential"),
        "sub_contract": _text(values, "sub_contract"),
        "send_report_copies_to": _text(values, "send_report_copies_to"),
    }
    return ApplicationFormWriteBackIdentity(fields=fields)


def test_record_header_identity(
    snapshot: ConfirmedBasicInformationSnapshot,
) -> TestRecordHeaderIdentity:
    """Return Test Record header identity from confirmed Basic Information only."""
    values = snapshot.values
    return TestRecordHeaderIdentity(
        lab_test_request_number=_text(values, "dl_number"),
        product_description=(
            _text(values, "product_description") or _text(values, "description_pn")
        ),
        applicable_specification=_text(values, "applicable_specifications"),
    )


test_record_header_identity.__test__ = False


def _text(values: dict[str, str], key: str) -> str:
    """Return a stripped Basic Information value."""
    return str(values.get(key, "") or "").strip()
