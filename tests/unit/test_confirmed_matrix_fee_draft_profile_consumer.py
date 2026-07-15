from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftService,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
)
from tests.unit.test_confirmed_matrix_fee_draft_service import (
    _ConfirmedStore,
    _fixture_row,
    _snapshot,
)


def test_fee_draft_preserves_text_fallback_when_step_quantities_are_absent() -> None:
    row = _fixture_row("Contact Resistance (Low Level)", requirement="5 readings/specimen")
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_snapshot(row=row))
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.unit_price == Decimal("1.5")
    assert line.units == Decimal("25")
    assert line.testing_fee == Decimal("37.5")


def test_fee_draft_uses_confirmed_profile_for_llcr_without_step_quantity() -> None:
    row = _fixture_row("Contact Resistance (Low Level)")
    lineage = "Confirmed Project Point Profile: revision 3 (revision-1; sha256:profile)"
    service = _service_with_profile(row, "not_started", _confirmed_profile(lineage=lineage))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.units == Decimal("20")
    assert line.testing_fee == Decimal("30")
    assert any(metadata.field == "units" and metadata.source == lineage for metadata in line.field_metadata)


def test_fee_draft_uses_profile_when_measurement_plan_is_disabled() -> None:
    service = _service_with_profile(_fixture_row("Contact Resistance (Low Level)"), "disabled")

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    assert draft.groups[0].line_items[0].units == Decimal("20")


def test_fee_draft_blocks_profile_fallback_for_active_measurement_plan_omission() -> None:
    service = _service_with_profile(_fixture_row("Contact Resistance (Low Level)"), "complete")

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.review_required is True
    assert line.units is None
    assert all(metadata.source != _confirmed_profile().lineage for metadata in line.field_metadata)


def test_fee_draft_keeps_invalid_group_quantity_review_required_for_profile() -> None:
    service = _service_with_profile(
        _fixture_row("Contact Resistance (Low Level)"),
        "not_started",
        sample_quantity_expression="5e",
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.review_required is True
    assert line.review_reason == "Confirm sample quantity"
    assert line.units is None


def _service_with_profile(
    row,
    measurement_plan_status: str,
    profile: EffectiveConfirmedPointProfile | None = None,
    *,
    sample_quantity_expression: str = "5",
) -> ConfirmedMatrixFeeDraftService:
    return ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=row, sample_quantity_expression=sample_quantity_expression)
        ),
        contact_measurement_adapter=_ContactAdapter(measurement_plan_status),
        contact_point_profile_adapter=_ProfileAdapter(profile or _confirmed_profile()),
    )


def _confirmed_profile(
    *, lineage: str = "Confirmed Project Point Profile: revision 3 (revision-1; sha256:profile)"
) -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="4",
        revision_id="revision-1",
        revision_sequence=3,
        fingerprint="sha256:profile",
        lineage=lineage,
        message=None,
    )


class _ContactAdapter:
    def __init__(self, status: str) -> None:
        self._status = status

    def get_effective(self, project_id: str):
        return type(
            "Effective",
            (),
            {
                "status": self._status,
                "legacy_fallback_allowed": self._status in {"not_started", "disabled"},
                "lookup": {},
            },
        )()


class _ProfileAdapter:
    def __init__(self, profile: EffectiveConfirmedPointProfile) -> None:
        self._profile = profile

    def get_effective(self, project_id: str) -> EffectiveConfirmedPointProfile:
        return self._profile
