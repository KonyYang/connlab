from __future__ import annotations

from decimal import Decimal

import pytest

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftNotFoundError,
    ConfirmedMatrixFeeDraftService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
)
from backend.modules.fee_evaluation.fee_rule_models import (
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleVersion,
)


def test_fee_draft_header_uses_confirmed_matrix_version_sample_received_date() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    assert draft.header.project_id == "P1"
    assert draft.header.confirmed_matrix_id == "cmv-1"
    assert draft.header.confirmed_revision == 1
    assert draft.header.pricing_rule_version_id == "fee_rules_v2026_07_17_r6"
    assert draft.header.pricing_source_file_name == "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    assert draft.header.pricing_effective_from == "2026-06-03"
    assert draft.draft_status == "ready"


def test_fee_draft_not_found_when_no_active_authority() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=None))

    with pytest.raises(ConfirmedMatrixFeeDraftNotFoundError, match="Active confirmed matrix not found"):
        service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))


def test_fee_draft_warns_when_pricing_effective_from_is_missing() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_snapshot(sample_received_date=None))
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    assert draft.header.pricing_effective_from is None
    assert draft.draft_status == "needs_review"
    assert draft.warnings[0].code == "missing_pricing_effective_from"
    assert draft.review_required_count >= 1


def test_fee_draft_autofills_visual_exam_defaults() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_visual_exam"
    assert line.matched_rule_version_id == "fee_rules_v2026_07_17_r6"
    assert line.calculation_strategy == "per_photo"
    assert line.unit_price == Decimal("10")
    assert line.units == Decimal("3")
    assert line.discount_percent == Decimal("100")
    assert line.testing_fee == Decimal("0")
    assert line.spend_time == "0.5"
    assert line.step_tokens == ("1",)
    assert any(
        metadata.field == "units" and metadata.state == "auto_filled"
        for metadata in line.field_metadata
    )


def test_fee_draft_autofills_examination_of_product_as_visual_exam_defaults() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=_fixture_row("Examination of Product"))
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_visual_exam"
    assert line.calculation_strategy == "per_photo"
    assert line.spend_time == "0.5"
    assert line.unit_price == Decimal("10")
    assert line.unit_label == "photo"
    assert line.units == Decimal("3")
    assert line.discount_percent == Decimal("100")
    assert line.testing_fee == Decimal("0")


def test_fee_draft_converts_mfg_labeled_phase_hours_to_days() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row(
                    "MFG",
                    condition="Class IIA; unmated 224 hours; mated 112 hours",
                )
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_mfg_class_iia"
    assert line.unit_price == Decimal("1000")
    assert line.unit_label == "day"
    assert line.units == Decimal("14")
    assert line.base_fee == Decimal("0")
    assert line.discount_percent == Decimal("0")
    assert line.testing_fee == Decimal("14000")


def test_fee_draft_preserves_explicit_mfg_days() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=_fixture_row("MFG", condition="Class IIA, 14 days"))
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.units == Decimal("14")
    assert line.testing_fee == Decimal("14000")


def test_fee_draft_keeps_incomplete_mfg_phase_duration_pending() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row("MFG", condition="Class IIA; unmated 224 hours")
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.review_required is True
    assert line.unit_price == Decimal("1000")
    assert line.unit_label == "day"
    assert line.units is None
    assert line.testing_fee is None


def test_fee_draft_autofills_preconditioning_durability_cycles() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row("Durability (Preconditioning 20 cycles)"),
                sample_quantity_expression="5",
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_durability"
    assert line.calculation_strategy == "per_cycle"
    assert line.unit_price == Decimal("2")
    assert line.unit_label == "cycle"
    assert line.units == Decimal("100")
    assert line.discount_percent == Decimal("0")
    assert line.testing_fee == Decimal("200")


def test_fee_draft_autofills_reseating_manual_cycles() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row("Reseating", condition="Manual 3 cycles"),
                sample_quantity_expression="5",
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_reseating"
    assert line.calculation_strategy == "per_cycle"
    assert line.unit_price == Decimal("2")
    assert line.unit_label == "cycle"
    assert line.units == Decimal("15")
    assert line.discount_percent == Decimal("0")
    assert line.testing_fee == Decimal("30")


def test_fee_draft_defaults_reseating_to_three_cycles_when_cycle_text_is_absent() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row("Reseating", condition="Manual"),
                sample_quantity_expression="5",
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.matched_rule_id == "fee_rule_reseating"
    assert line.unit_label == "cycle"
    assert line.units == Decimal("15")
    assert line.testing_fee == Decimal("30")


def test_fee_draft_includes_backend_owned_manual_default_rows() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    sample_line = draft.groups[0].manual_line_items[0]
    assert sample_line.line_id == "sample-preparation:g1"
    assert sample_line.test_item == "Sample preparation"
    assert sample_line.spend_time == "0.5"
    assert sample_line.unit_price == Decimal("50")
    assert sample_line.unit_label == "sample"
    assert sample_line.units == Decimal("5")
    assert sample_line.discount_percent == Decimal("100")
    assert sample_line.testing_fee == Decimal("0")
    assert any(
        metadata.field == "units" and metadata.state == "auto_filled"
        for metadata in sample_line.field_metadata
    )

    report_line = draft.manual_line_items[0]
    assert report_line.line_id == "manual-report-preparation"
    assert report_line.test_item == "Report preparation"
    assert report_line.spend_time == "4"
    assert report_line.unit_price == Decimal("600")
    assert report_line.unit_label == "report"
    assert report_line.units == Decimal("1")
    assert report_line.discount_percent == Decimal("100")
    assert report_line.testing_fee == Decimal("0")


def test_fee_draft_marks_unmatched_row_as_no_rule_match() -> None:
    row = ConfirmedMatrixRow(
        confirmed_row_id="cmr-unknown",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-unknown",
        source_row_snapshot_id="smr-unknown",
        row_order=1,
        test_item="Laser welding simulation",
        source_section="9.9",
        method="",
        condition="",
        requirement="",
    )
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot(row=row)))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "no_rule_match"
    assert line.review_required is True
    assert line.matched_rule_id is None
    assert line.matched_rule_version_id is None
    assert line.review_reason == "No fee rule match."


def test_fee_draft_defaults_insulation_resistance_without_duration() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=_fixture_row("INSULATION RESISTANCE"))
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    line = draft.groups[0].line_items[0]

    assert line.matched_rule_id == "fee_rule_insulation_resistance"
    assert line.status == "review_required"
    assert line.unit_label == "reading"
    assert line.unit_price is None
    assert line.units == Decimal("1")
    assert line.base_fee == Decimal("0")
    assert line.testing_fee is None
    assert line.review_reason == "Confirm 1-minute/2-minute price."


def test_fee_draft_uses_insulation_resistance_duration_price_from_condition() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row("INSULATION RESISTANCE", condition="2 minutes")
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    line = draft.groups[0].line_items[0]

    assert line.matched_rule_id == "fee_rule_insulation_resistance"
    assert line.status == "calculated"
    assert line.unit_label == "reading"
    assert line.unit_price == Decimal("10")
    assert line.units == Decimal("1")
    assert line.base_fee == Decimal("0")
    assert line.testing_fee == Decimal("10")
    assert line.review_reason is None


def test_fee_draft_leaves_dwv_price_pending_when_condition_has_only_current_limit() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row(
                    "DIELECTRIC WITHSTANDING VOLTAGE",
                    condition="1mA",
                )
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    line = draft.groups[0].line_items[0]

    assert line.matched_rule_id == "fee_rule_dielectric_withstanding_voltage"
    assert line.status == "review_required"
    assert line.unit_label == "reading"
    assert line.unit_price is None
    assert line.units == Decimal("1")
    assert line.base_fee == Decimal("0")
    assert line.testing_fee is None
    assert line.review_reason == "Confirm 1-minute/2-minute price."


def test_fee_draft_uses_temperature_rise_rule_for_current_rating() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=_fixture_row("CURRENT RATING", condition="300A"))
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    line = draft.groups[0].line_items[0]

    assert line.matched_rule_id == "fee_rule_temperature_rise"
    assert (line.status, line.review_required, line.review_reason) == ("calculated", False, None)
    assert line.spend_time == "4"
    assert line.unit_label == "sample"
    assert line.unit_price == Decimal("600")
    assert line.units == Decimal("5")
    assert line.base_fee == Decimal("0")
    assert line.testing_fee == Decimal("3000")


@pytest.mark.parametrize("test_item", ("Long-term high temperature zone load", "Long-term temperature cycle with load", "Long-term damp heat"))
def test_fee_draft_defaults_non_rise_temperature_items_to_per_hour(
    test_item: str,
) -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                row=_fixture_row(
                    test_item,
                    condition="Damp Heat Condition: 85C, 85% RH, 1000h (mated test).",
                )
            )
        )
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    line = draft.groups[0].line_items[0]

    if test_item != "Long-term high temperature zone load":
        assert line.matched_rule_id is None
        assert line.status == "no_rule_match"
        assert line.review_required is True
        assert line.review_reason == "No fee rule match."
        assert (line.unit_price, line.units, line.base_fee, line.testing_fee) == (None, None, Decimal("0"), None)
        return
    assert line.matched_rule_id == "fee_rule_high_temperature_life"
    assert (line.status, line.review_reason) == ("review_required", "Missing confirmed duration authority")
    assert line.unit_price == Decimal("15")
    assert line.unit_label == "hour"
    assert line.units is None
    assert line.base_fee == Decimal("0")
    assert line.testing_fee is None


def test_fee_draft_calculates_fixed_per_group_when_rule_is_deterministic() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_snapshot(row=_fixture_row("Fixture setup"))),
        rule_library=_single_rule_library(
            rule_id="fee_rule_fixture",
            display_name="Fixture setup",
            aliases=("Fixture setup",),
            unit_price=Decimal("100"),
            base_fee=Decimal("0"),
            strategy="fixed_per_group",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.review_required is False
    assert line.units == Decimal("1")
    assert line.testing_fee == Decimal("100")
    assert draft.total_fee == Decimal("100")


def test_fee_draft_marks_manual_required_rule_for_review() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_snapshot(row=_fixture_row("Manual item"))),
        rule_library=_single_rule_library(
            rule_id="fee_rule_manual",
            display_name="Manual item",
            aliases=("Manual item",),
            unit_price=Decimal("100"),
            base_fee=Decimal("0"),
            strategy="manual_required",
            review_required=True,
            review_reason="Manual pricing requires operator review.",
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.review_required is True
    assert line.testing_fee is None
    assert line.review_reason == "Manual pricing requires operator review."


def test_fee_draft_suppresses_total_when_root_warning_exists() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(sample_received_date=None, row=_fixture_row("Fixture setup"))
        ),
        rule_library=_single_rule_library(
            rule_id="fee_rule_fixture",
            display_name="Fixture setup",
            aliases=("Fixture setup",),
            unit_price=Decimal("100"),
            base_fee=Decimal("0"),
            strategy="fixed_per_group",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    assert draft.groups[0].line_items[0].status == "calculated"
    assert draft.total_fee is None
    assert draft.draft_status == "needs_review"


def test_fee_draft_marks_step_token_warning_review_required_even_for_deterministic_rule() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(row=_fixture_row("Fixture setup"), cell_value="1 X")
        ),
        rule_library=_single_rule_library(
            rule_id="fee_rule_fixture",
            display_name="Fixture setup",
            aliases=("Fixture setup",),
            unit_price=Decimal("100"),
            base_fee=Decimal("0"),
            strategy="fixed_per_group",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.review_required is True
    assert line.testing_fee is None
    assert line.warnings
    assert "step token" in (line.review_reason or "").lower()
    assert draft.total_fee is None


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self.active = active

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self.active and self.active.version.project_id == project_id:
            return self.active
        return None


def _snapshot(
    *,
    sample_quantity_expression: str = "5",
    row: ConfirmedMatrixRow | None = None,
    cell_value: str = "1",
    sample_received_date: str | None = "2026-06-03",
    step_quantities: tuple[ConfirmedMatrixStepQuantity, ...] = (),
) -> ConfirmedMatrixSnapshot:
    row = row or _fixture_row("Visual Examination")
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-03T09:00:00+08:00",
            sample_received_date=sample_received_date,
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-1",
                source_group_snapshot_id="smg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression=sample_quantity_expression,
            ),
        ),
        rows=(row,),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id=row.confirmed_row_id,
                confirmed_group_id="cmg-1",
                draft_row_id=row.draft_row_id,
                draft_group_id="pmdg-1",
                cell_value=cell_value,
            ),
        ),
        step_quantities=step_quantities,
    )


def _fixture_row(
    test_item: str,
    *,
    condition: str = "Visual Inspection",
    requirement: str = "No damage",
) -> ConfirmedMatrixRow:
    return ConfirmedMatrixRow(
        confirmed_row_id=f"cmr-{test_item.lower().replace(' ', '-')}",
        confirmed_matrix_id="cmv-1",
        draft_row_id=f"pmdr-{test_item.lower().replace(' ', '-')}",
        source_row_snapshot_id=f"smr-{test_item.lower().replace(' ', '-')}",
        row_order=1,
        test_item=test_item,
        source_section="6.1",
        method="EIA-364-18",
        condition=condition,
        requirement=requirement,
    )


def _step_quantity(
    *,
    row: ConfirmedMatrixRow,
    step_sequence: int = 1,
    raw_token: str = "1",
    test_points_per_sample: str | None,
    readings_per_point: str | None,
    contact_points_per_sample: str | None = None,
    review_required: bool = False,
) -> ConfirmedMatrixStepQuantity:
    return ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id=f"cmsq-{raw_token}",
        confirmed_matrix_id="cmv-1",
        confirmed_group_id="cmg-1",
        confirmed_row_id=row.confirmed_row_id,
        draft_group_id="pmdg-1",
        draft_row_id=row.draft_row_id,
        step_sequence=step_sequence,
        step_suffix_note=None,
        raw_token=raw_token,
        test_points_per_sample=test_points_per_sample,
        readings_per_point=readings_per_point,
        contact_points_per_sample=contact_points_per_sample,
        source="matrix_step_override",
        review_required=review_required,
        review_reason="Confirm Step quantity values." if review_required else None,
        confirmed_at="2026-07-08T09:00:00+00:00",
    )


def _single_rule_library(
    *,
    rule_id: str,
    display_name: str,
    aliases: tuple[str, ...],
    unit_price: Decimal,
    base_fee: Decimal,
    strategy: str,
    review_required: bool,
    review_reason: str | None = None,
) -> FeeRuleLibrary:
    return FeeRuleLibrary(
        version=FeeRuleVersion(
            version_id="fee_rules_test",
            source_file_name="test.xlsx",
            source_sheet="Unit Price Reference",
            source_hash="sha256:" + "1" * 64,
            effective_from_basis="project.sample_received_date",
            created_at="2026-06-04T00:00:00+08:00",
        ),
        rules=(
            FeeRule(
                rule_id=rule_id,
                display_name=display_name,
                aliases=aliases,
                base_fee=FeeAmount(amount=base_fee, text=format(base_fee, "f")),
                unit_price=FeeAmount(amount=unit_price, text=format(unit_price, "f")),
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy=strategy,
                review_required=review_required,
                review_reason=review_reason or ("test review" if review_required else None),
            ),
        ),
    )
