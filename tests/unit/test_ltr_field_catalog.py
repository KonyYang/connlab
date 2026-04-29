from __future__ import annotations

import importlib

import pytest

from backend.modules.ltr import (
    LtrFieldDefinition,
    ReadinessSeverity,
    get_ltr_field_catalog,
    get_ltr_field_definition,
)


def test_ltr_field_catalog_defines_all_19_fields() -> None:
    """TASK_039 defines one complete catalog entry for each LTR field."""
    catalog = get_ltr_field_catalog()

    assert len(catalog) == 19
    assert len({field.key for field in catalog}) == 19
    assert all(isinstance(field, LtrFieldDefinition) for field in catalog)
    assert all(field.display_label for field in catalog)
    assert all(field.fallback_policy for field in catalog)
    assert all(field.operator_action for field in catalog)
    assert [field.display_label for field in catalog] == [
        "DL",
        "Project Type",
        "Description P/N",
        "Test Item",
        "Applicable Specifications",
        "Test Type",
        "Requested by",
        "Location",
        "Project Leader",
        "Test Result",
        "Failed item",
        "Sample deposition",
        "Sub-contract",
        "Test Fee",
        "Remarks (PO)",
        "Phone",
        "E-mail of Requestor",
        "Product Description",
        "Lab Performing the Tests",
    ]


def test_ltr_field_catalog_sets_required_source_and_policy() -> None:
    """Every field has either source paths or an explicit placeholder policy."""
    for field in get_ltr_field_catalog():
        assert field.severity in set(ReadinessSeverity)
        if field.severity is ReadinessSeverity.PLACEHOLDER_ALLOWED:
            assert field.placeholder_policy
            assert field.source_paths == ()
        else:
            assert field.source_paths or field.fallback_policy
            if field.severity is ReadinessSeverity.BLOCKER:
                assert field.placeholder_policy is None


def test_future_result_fields_are_placeholder_allowed() -> None:
    """Future result fields must not accidentally block registration."""
    test_result = get_ltr_field_definition("test_result")
    failed_item = get_ltr_field_definition("failed_item")

    assert test_result.severity is ReadinessSeverity.PLACEHOLDER_ALLOWED
    assert test_result.placeholder_policy == 'Use "Pending" until test results are recorded.'
    assert failed_item.severity is ReadinessSeverity.PLACEHOLDER_ALLOWED
    assert failed_item.placeholder_policy == 'Use "N/A" until failures are known.'


def test_blocker_fields_cover_core_registration_inputs() -> None:
    """Core LTR registration fields are blockers before preview/commit."""
    blockers = {
        field.key
        for field in get_ltr_field_catalog()
        if field.severity is ReadinessSeverity.BLOCKER
    }

    assert {
        "dl",
        "project_type",
        "description_pn",
        "test_item",
        "applicable_specifications",
        "test_type",
        "requested_by",
        "sub_contract",
        "phone",
        "requestor_email",
        "product_description",
        "lab_performing_tests",
    } <= blockers


def test_ltr_field_catalog_is_pure_python_boundary() -> None:
    """The catalog module must not import infrastructure or service layers."""
    module = importlib.import_module("backend.modules.ltr.ltr_field_catalog")
    imported_names = set(module.__dict__)

    forbidden_names = {"Document", "Session", "FastAPI", "Settings", "OfficeFacade"}
    assert not imported_names & forbidden_names


def test_get_ltr_field_definition_rejects_unknown_key() -> None:
    """Unknown catalog keys fail loudly for later service code."""
    with pytest.raises(KeyError, match="Unknown LTR readiness field key"):
        get_ltr_field_definition("missing")
