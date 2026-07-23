from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.fee_evaluation_pricing_draft_automatic_build import (
    build_current_pricing_defaults,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_to_payload,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    canonical_fingerprint,
)
from backend.application.fee_evaluation_pricing_draft_v2_rebase import (
    rebase_reviewed_values,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)

_FALLBACK_SOURCE = "Matrix Fee automatic Base Fee fallback"


@pytest.mark.parametrize("group_count", (1, 2))
def test_approved_temperature_alias_uses_hours_and_common_base_fee(
    group_count: int,
) -> None:
    draft = _service(
        _snapshot(
            test_item="Long-term high temperature zone load",
            condition="Damp Heat Condition: 85C, 85% RH, 1000h.",
            group_count=group_count,
        )
    ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    lines = tuple(group.line_items[0] for group in draft.groups)
    assert len(lines) == group_count
    assert all(line.matched_rule_id == "fee_rule_high_temperature_life" for line in lines)
    assert all(line.unit_label == "hour" for line in lines)
    assert all(line.unit_price == Decimal("15") for line in lines)
    assert all(line.units == Decimal("1000") for line in lines)
    assert all(line.base_fee == Decimal("0") for line in lines)
    assert all(line.testing_fee == Decimal("15000") for line in lines)
    assert all(_source(line, "base_fee") == "high temperature life" for line in lines)


@pytest.mark.parametrize(
    "test_item",
    ("Long-term temperature cycle with load", "Long-term damp heat"),
)
def test_rejected_temperature_alias_remains_review_only(test_item: str) -> None:
    line = _first_line(
        _service(
            _snapshot(
                test_item=test_item,
                condition="85C, 85% RH, 1000h.",
            )
        )
    )

    assert line.status == "no_rule_match"
    assert line.review_required is True
    assert line.matched_rule_id is None
    assert line.unit_price is None
    assert line.units is None
    assert line.base_fee == Decimal("0")
    assert line.testing_fee is None
    assert _source(line, "base_fee") == _FALLBACK_SOURCE


def test_approved_temperature_alias_without_hours_keeps_dependencies_pending() -> None:
    line = _first_line(
        _service(_snapshot(test_item="Long-term high temperature zone load"))
    )

    assert line.matched_rule_id == "fee_rule_high_temperature_life"
    assert line.status == "review_required"
    assert line.review_reason == "Confirm duration"
    assert line.unit_price == Decimal("15")
    assert line.units is None
    assert line.base_fee == Decimal("0")
    assert line.testing_fee is None


def test_plain_contact_resistance_does_not_consume_llcr_rule() -> None:
    line = _first_line(_service(_snapshot(test_item="CONTACT RESISTANCE")))

    assert line.matched_rule_id == "fee_rule_contact_resistance_specified_current"
    assert line.matched_rule_id != "fee_rule_llcr"
    assert line.status == "review_required"
    assert line.units is None
    assert line.testing_fee is None


def test_non_explicit_suggested_base_fee_uses_common_fallback() -> None:
    line = _first_line(
        _service(_snapshot(test_item="CURRENT RATING", condition="300A"))
    )

    assert line.matched_rule_id == "fee_rule_temperature_rise"
    assert line.status == "calculated"
    assert line.unit_price == Decimal("600")
    assert line.units == Decimal("5")
    assert line.base_fee == Decimal("0")
    assert line.testing_fee == Decimal("3000")
    assert _source(line, "base_fee") == _FALLBACK_SOURCE


@pytest.mark.parametrize("group_count", (1, 2))
def test_explicit_rule_base_fee_is_preserved_for_every_group(
    group_count: int,
) -> None:
    draft = _service(
        _snapshot(
            test_item="Shock (Trapzoidal)",
            group_count=group_count,
        )
    ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    lines = tuple(group.line_items[0] for group in draft.groups)
    assert all(line.base_fee == Decimal("500") for line in lines)
    assert all(line.testing_fee == Decimal("560") for line in lines)
    assert all(_source(line, "base_fee") == "Shock (Trapzoidal)" for line in lines)


def test_automatic_defaults_bind_base_fee_value_and_metadata_source() -> None:
    service = _service(
        _snapshot(
            test_item="Thermal shock",
            condition="10h",
        )
    )

    result = build_current_pricing_defaults("P1", service)

    assert result.automatic_values.rows[0].base_fee == "0"
    assert result.automatic_values.rows[0].testing_fee == "300"
    assert result.source_context.automatic_defaults_fingerprint == canonical_fingerprint(
        edited_values_to_payload(result.automatic_values)
    )
    base_fee = next(
        item
        for item in result.row_safety[0].automatic_fields
        if item.field == "base_fee"
    )
    assert base_fee.source == _FALLBACK_SOURCE
    assert result.row_safety[0].safe_for_rebase is True


def test_reviewed_rebase_preserves_proven_manual_fields() -> None:
    defaults = build_current_pricing_defaults(
        "P1",
        _service(
            _snapshot(
                test_item="Thermal shock",
                condition="10h",
            )
        ),
    ).automatic_values
    row = defaults.rows[0]
    saved = replace(
        defaults,
        rows=(
            replace(
                row,
                spend_time="7",
                unit_price="99",
                unit_type="manual hour",
                units="11",
                base_fee="88",
                discount="12%",
                testing_fee="legacy",
                notes="operator note",
            ),
        ),
    )
    provenance = {
        row.source_line_id: (
            "spend_time",
            "unit_price",
            "unit_type",
            "base_fee",
            "discount",
            "notes",
        )
    }

    rebased = rebase_reviewed_values(
        saved=saved,
        current_defaults=defaults,
        row_provenance=provenance,
    )

    merged = rebased.rows[0]
    assert merged.spend_time == "7"
    assert merged.unit_price == "99"
    assert merged.unit_type == "manual hour"
    assert merged.units == "10"
    assert merged.base_fee == "88"
    assert merged.discount == "12%"
    assert merged.notes == "operator note"
    assert merged.testing_fee == "300"


def _first_line(service: ConfirmedMatrixFeeDraftService):
    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    return draft.groups[0].line_items[0]


def _service(snapshot: ConfirmedMatrixSnapshot) -> ConfirmedMatrixFeeDraftService:
    return ConfirmedMatrixFeeDraftService(confirmed_store=_Store(snapshot))


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot if project_id == "P1" else None


def _snapshot(
    *,
    test_item: str,
    condition: str = "",
    group_count: int = 1,
) -> ConfirmedMatrixSnapshot:
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id="matrix-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id="source-row-1",
        row_order=1,
        test_item=test_item,
        source_section="6.1",
        method="EIA-364",
        condition=condition,
        requirement="No damage",
    )
    groups = tuple(
        ConfirmedMatrixGroup(
            confirmed_group_id=f"group-{index}",
            confirmed_matrix_id="matrix-1",
            draft_group_id=f"draft-group-{index}",
            source_group_snapshot_id=f"source-group-{index}",
            group_order=index,
            group_key=f"g{index}",
            group_label=f"Group {index}",
            sample_quantity_expression="5",
        )
        for index in range(1, group_count + 1)
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="matrix-1",
            project_id="P1",
            project_matrix_draft_id="draft-1",
            source_import_id="import-1",
            source_snapshot_id="snapshot-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-23T09:00:00+08:00",
            sample_received_date="2026-07-23",
        ),
        groups=groups,
        rows=(row,),
        cells=tuple(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cell-{index}",
                confirmed_matrix_id="matrix-1",
                confirmed_row_id=row.confirmed_row_id,
                confirmed_group_id=group.confirmed_group_id,
                draft_row_id=row.draft_row_id,
                draft_group_id=group.draft_group_id,
                cell_value="1",
            )
            for index, group in enumerate(groups, start=1)
        ),
    )


def _source(line, field: str) -> str | None:
    matches = [item for item in line.field_metadata if item.field == field]
    assert len(matches) == 1
    return matches[0].source
