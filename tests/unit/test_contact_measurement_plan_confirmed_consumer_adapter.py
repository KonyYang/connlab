"""TASK_361E typed confirmed-consumer adapter coverage."""

from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    ContactMeasurementPlanConfirmedConsumerAdapter,
)
from tests.unit.test_confirmed_matrix_llcr_cr_record_projection import _snapshot


def test_adapter_exposes_confirmed_lineage_without_stable_key_parsing() -> None:
    result = ContactMeasurementPlanConfirmedConsumerAdapter(
        projection_service=_Projection("complete"), confirmed_store=_Store()
    ).get_effective("project-1")

    assert result is not None
    assert result.legacy_fallback_allowed is False
    assert list(result.lookup) == [("group-1", "row-1", 2, "")]
    assert result.lookup[("group-1", "row-1", 2, "")].contact_plan.readings_per_sample == "3"


def test_adapter_allows_legacy_only_for_not_started_or_disabled() -> None:
    for status in ("not_started", "disabled"):
        result = ContactMeasurementPlanConfirmedConsumerAdapter(
            projection_service=_Projection(status), confirmed_store=_Store()
        ).get_effective("project-1")
        assert result is not None
        assert result.legacy_fallback_allowed is True


class _Projection:
    def __init__(self, status: str) -> None:
        self._status = status

    def get_effective(self, project_id: str):
        return type("Projection", (), {
            "status": self._status,
            "revision_id": "revision-1" if self._status == "complete" else None,
            "revision_sequence": 1 if self._status == "complete" else None,
            "diagnostics": (),
            "targets": (
                ({
                    "confirmed_group_id": "group-1", "confirmed_row_id": "row-1",
                    "step_sequence": 2, "step_suffix_note": "", "contact_kind": "llcr",
                    "included": True, "readings_per_sample": 3, "families": (),
                },) if self._status == "complete" else ()
            ),
        })()


class _Store:
    def get_active_by_project(self, project_id: str):
        return _snapshot()
