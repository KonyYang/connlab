from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.application.confirmed_matrix_fee_cr_specified_current import (
    resolve_cr_specified_current_readings,
)
from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
    EffectiveContactMeasurementTarget,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    MatrixStepContactPlan,
)
from backend.modules.test_plan.matrix_step_sequence_validation import ParsedStepToken
from backend.modules.fee_evaluation import FeeDefaultFillContext, load_active_fee_rule_library
from backend.modules.fee_evaluation.fee_default_fill import build_fee_default_fill

_RULE = next(
    rule
    for rule in load_active_fee_rule_library().rules
    if rule.rule_id == "fee_rule_contact_resistance_specified_current"
)


def test_exact_cr_targets_are_homogeneous_and_source_lineage_is_preserved() -> None:
    result = resolve_cr_specified_current_readings(
        group=_group(),
        row=_row(),
        parsed_tokens=(
            ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),
            ParsedStepToken(raw_token="2", sequence=2, suffix_note=None),
        ),
        effective_plan=_plan("8", (1, 2)),
    )

    assert result[0].total_readings == "8"
    assert result[0].cr_authority is not None
    assert result[0].cr_authority.revision_sequence == 4
    assert result[0].cr_authority.fingerprint


@pytest.mark.parametrize(
    "plan_kind, expected",
    [
        ("missing", "unavailable"),
        ("status", "status"),
        ("kind", "kind"),
        ("excluded", "excluded"),
        ("diagnostics", "diagnostics"),
    ],
)
def test_cr_authority_rejects_missing_or_unsafe_targets(plan_kind: str, expected: str) -> None:
    plan = {
        "missing": None,
        "status": _plan("8", (1,), status="not_started"),
        "kind": _plan("8", (1,), contact_kind="llcr"),
        "excluded": _plan("8", (1,), included=False),
        "diagnostics": _plan("8", (1,), diagnostics=("affected target",)),
    }[plan_kind]
    result = resolve_cr_specified_current_readings(
        group=_group(),
        row=_row(),
        parsed_tokens=(ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),),
        effective_plan=plan,
    )

    assert result[0].total_readings is None
    assert expected in (result[0].review_reason or "").lower()


def test_cr_authority_does_not_sum_divergent_steps() -> None:
    result = resolve_cr_specified_current_readings(
        group=_group(),
        row=_row(),
        parsed_tokens=(
            ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),
            ParsedStepToken(raw_token="2", sequence=2, suffix_note=None),
        ),
        effective_plan=_plan("8", (1, 2), second_readings="12"),
    )

    assert result[0].total_readings is None
    assert "homogeneous" in (result[0].review_reason or "")


def test_cr_authority_requires_revision_lineage_before_calculation() -> None:
    plan = _plan("8", (1,))
    plan = plan.__class__(
        status=plan.status, snapshot=plan.snapshot, revision_id=None,
        revision_sequence=plan.revision_sequence, targets=plan.targets,
        diagnostics=plan.diagnostics,
    )
    result = resolve_cr_specified_current_readings(
        group=_group(), row=_row(),
        parsed_tokens=(ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),),
        effective_plan=plan,
    )

    assert result[0].cr_authority is not None
    assert result[0].cr_authority.is_valid is False
    assert result[0].total_readings is None


def test_cr_authority_missing_lineage_attributes_blocks_without_exception() -> None:
    result = resolve_cr_specified_current_readings(
        group=_group(),
        row=_row(),
        parsed_tokens=(ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),),
        effective_plan=SimpleNamespace(status="not_started", lookup={}),
    )

    assert result[0].review_required is True
    assert result[0].total_readings is None
    assert "lineage" in (result[0].review_reason or "").lower()


@pytest.mark.parametrize(
    ("readings", "samples", "expected_units", "expected_price"),
    [("8", "5", Decimal("40"), Decimal("10")), ("12", "3", Decimal("36"), Decimal("5"))],
)
def test_cr_default_uses_authoritative_readings_tier_and_owning_samples(
    readings: str,
    samples: str,
    expected_units: Decimal,
    expected_price: Decimal,
) -> None:
    authority = _plan(readings, (1,))
    resolved = resolve_cr_specified_current_readings(
        group=_group(), row=_row(),
        parsed_tokens=(ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),),
        effective_plan=authority,
    )
    result = build_fee_default_fill(
        rule=_RULE,
        context=FeeDefaultFillContext(
            test_item="Contact Resistance specified current",
            method="", condition="", requirement="",
                sample_quantity_expression=samples,
                step_quantities=resolved,
                cr_authority=resolved[0].cr_authority,
        ),
    )

    assert result.review_required is False
    assert result.units == expected_units
    assert result.unit_price == expected_price


def test_production_draft_uses_each_groups_cr_target_and_owning_quantity() -> None:
    snapshot = _two_group_snapshot()
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(snapshot),
        contact_measurement_adapter=_Adapter(_two_group_plan()),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="p1"))

    lines = [group.line_items[0] for group in draft.groups]
    assert [(line.units, line.unit_price) for line in lines] == [
        (Decimal("40"), Decimal("10")),
        (Decimal("36"), Decimal("5")),
    ]
    required_fields = {"unit_price", "unit_label", "units", "testing_fee"}
    assert all(
        all(
            "Confirmed CR Measurement Plan" in (item.source or "")
            for item in line.field_metadata
            if item.field in required_fields
        )
        for line in lines
    )


def test_production_cr_missing_plan_does_not_fallback_to_legacy_step_quantity() -> None:
    snapshot = _two_group_snapshot()
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(snapshot),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="p1"))

    line = draft.groups[0].line_items[0]
    assert line.review_required is True
    assert line.units is None
    assert "CR Measurement Plan" in (line.review_reason or "")


def test_production_cr_uses_confirmed_point_profile_coverage_without_measurement_plan() -> None:
    snapshot = _two_group_snapshot()
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(snapshot),
        contact_point_profile_adapter=_Adapter(
            SimpleNamespace(
                status="confirmed",
                is_usable=True,
                readings_per_sample="9",
                cr_readings_per_sample="4",
                revision_id="profile-2",
                revision_sequence=2,
                fingerprint="profile-fingerprint-2",
                lineage="Confirmed Project Point Profile: revision 2",
                message=None,
            )
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="p1"))

    lines = [group.line_items[0] for group in draft.groups]
    assert [line.units for line in lines] == [Decimal("20"), Decimal("12")]
    assert all(line.review_required is False for line in lines)
    assert all(
        any(
            item.field == "units"
            and "Confirmed Project Point Profile" in (item.source or "")
            for item in line.field_metadata
        )
        for line in lines
    )


def test_production_cr_measurement_plan_precedes_confirmed_point_profile() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(_two_group_snapshot()),
        contact_measurement_adapter=_Adapter(_two_group_plan()),
        contact_point_profile_adapter=_Adapter(
            SimpleNamespace(
                status="confirmed",
                cr_readings_per_sample="4",
                revision_id="profile-2",
                revision_sequence=2,
                fingerprint="profile-fingerprint-2",
                lineage="Confirmed Project Point Profile: revision 2",
            )
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="p1"))

    assert [line.units for group in draft.groups for line in group.line_items] == [
        Decimal("40"),
        Decimal("36"),
    ]
    assert all(
        any(
            "Confirmed CR Measurement Plan" in (item.source or "")
            for item in line.field_metadata
            if item.field == "units"
        )
        for group in draft.groups
        for line in group.line_items
    )


def test_cr_default_rejects_invalid_owning_sample_quantity() -> None:
    result = build_fee_default_fill(
        rule=_RULE,
        context=FeeDefaultFillContext(
            test_item="Contact Resistance specified current",
            method="", condition="", requirement="", sample_quantity_expression="0.5",
            step_quantities=(
                _context("8"),
            ),
        ),
    )

    assert result.review_required is True
    assert result.units is None


def _context(readings: str):
    return next(iter(resolve_cr_specified_current_readings(
        group=_group(), row=_row(),
        parsed_tokens=(ParsedStepToken(raw_token="1", sequence=1, suffix_note=None),),
        effective_plan=_plan(readings, (1,)),
    )))


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot if project_id == self.snapshot.version.project_id else None


class _Adapter:
    def __init__(self, plan: EffectiveContactMeasurementPlan) -> None:
        self.plan = plan

    def get_effective(self, project_id: str) -> EffectiveContactMeasurementPlan:
        return self.plan


def _two_group_plan() -> EffectiveContactMeasurementPlan:
    return EffectiveContactMeasurementPlan(
        status="complete", snapshot=_two_group_snapshot(), revision_id="cr-rev-1",
        revision_sequence=2, targets=(
            _target("g1", "r1", "8"), _target("g2", "r2", "12"),
        ), diagnostics=(),
    )


def _target(group_id: str, row_id: str, readings: str) -> EffectiveContactMeasurementTarget:
    return EffectiveContactMeasurementTarget(
        confirmed_group_id=group_id, confirmed_row_id=row_id, step_sequence=1,
        step_suffix_note="", contact_plan=MatrixStepContactPlan(
            contact_kind="cr_specified_current", coverage_status="included", included=True,
            exclusion_reason=None, is_override=False, readings_per_sample=readings, families=(),
        ),
    )


def _two_group_snapshot() -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="m1", project_id="p1", project_matrix_draft_id="d1",
        source_import_id="i1", source_snapshot_id="fingerprint-1", confirmed_revision=1,
        is_active_authority=True, status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="tester", confirmed_at="2026-07-19T00:00:00Z",
    )
    groups = tuple(
        ConfirmedMatrixGroup(
            confirmed_group_id=group_id, confirmed_matrix_id="m1", draft_group_id=f"d-{group_id}",
            source_group_snapshot_id=None, group_order=index, group_key=group_id,
            group_label=group_id, sample_quantity_expression=samples,
        )
        for index, (group_id, samples) in enumerate((("g1", "5"), ("g2", "3")), 1)
    )
    rows = tuple(
        ConfirmedMatrixRow(
            confirmed_row_id=row_id, confirmed_matrix_id="m1", draft_row_id=f"d-{row_id}",
            source_row_snapshot_id=None, row_order=index,
            test_item="Contact Resistance specified current",
        )
        for index, row_id in enumerate(("r1", "r2"), 1)
    )
    cells = tuple(
        ConfirmedMatrixCell(
            confirmed_cell_id=f"c-{group_id}", confirmed_matrix_id="m1",
            confirmed_row_id=row_id, confirmed_group_id=group_id,
            draft_row_id=f"d-{row_id}", draft_group_id=f"d-{group_id}", cell_value="1",
        )
        for group_id, row_id in (("g1", "r1"), ("g2", "r2"))
    )
    return ConfirmedMatrixSnapshot(version=version, groups=groups, rows=rows, cells=cells)


def _plan(
    readings: str,
    sequences: tuple[int, ...],
    *,
    status: str = "complete",
    contact_kind: str = "cr_specified_current",
    included: bool = True,
    second_readings: str | None = None,
    diagnostics: tuple[str, ...] = (),
) -> EffectiveContactMeasurementPlan:
    targets = tuple(
        EffectiveContactMeasurementTarget(
            confirmed_group_id="g1",
            confirmed_row_id="r1",
            step_sequence=sequence,
            step_suffix_note="" if sequence == 1 else "",
            contact_plan=MatrixStepContactPlan(
                contact_kind=contact_kind,
                coverage_status="included" if included else "excluded",
                included=included,
                exclusion_reason=None,
                is_override=False,
                readings_per_sample=second_readings if sequence == 2 and second_readings else readings,
                families=(),
            ),
        )
        for sequence in sequences
    )
    return EffectiveContactMeasurementPlan(
        status=status,
        snapshot=_snapshot(),
        revision_id="revision-4",
        revision_sequence=4,
        targets=targets,
        diagnostics=diagnostics,
    )


def _group() -> ConfirmedMatrixGroup:
    return ConfirmedMatrixGroup(
        confirmed_group_id="g1", confirmed_matrix_id="m1", draft_group_id="dg1",
        source_group_snapshot_id=None, group_order=1, group_key="G1", group_label="G1",
        sample_quantity_expression="5",
    )


def _row() -> ConfirmedMatrixRow:
    return ConfirmedMatrixRow(
        confirmed_row_id="r1", confirmed_matrix_id="m1", draft_row_id="dr1",
        source_row_snapshot_id=None, row_order=1, test_item="CR specified current",
    )


def _snapshot() -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="m1", project_id="p1", project_matrix_draft_id="d1",
            source_import_id="i1", source_snapshot_id="fingerprint-1", confirmed_revision=1,
            is_active_authority=True, status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="tester", confirmed_at="2026-07-19T00:00:00Z",
        )
    )
