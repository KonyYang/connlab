from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import (
    FeeEvaluationLineItem,
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
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)

_FALLBACK_SOURCE = "Matrix Fee automatic Base Fee fallback"


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot
        self.read_count = 0

    def get_active_by_project(
        self,
        project_id: str,
    ) -> ConfirmedMatrixSnapshot | None:
        self.read_count += 1
        return self.snapshot if project_id == "P1" else None


def test_multi_group_draft_applies_common_base_fee_fallback_per_owning_line() -> None:
    store = _Store(_snapshot())
    service = ConfirmedMatrixFeeDraftService(confirmed_store=store)

    result = build_current_pricing_defaults("P1", service)

    assert store.read_count == 1
    draft = result.fee_draft
    assert (draft.draft_status, draft.review_required_count, draft.warnings) == (
        "ready",
        0,
        (),
    )
    assert [
        (group.group_key, group.group_label, len(group.line_items))
        for group in draft.groups
    ] == [
        ("g1", "Group 1", 1),
        ("g2", "Group 2", 1),
    ]

    lines = tuple(group.line_items[0] for group in draft.groups)
    assert [
        (
            line.line_id,
            line.confirmed_group_id,
            line.group_key,
            line.group_label,
            line.confirmed_row_id,
            line.source_row_id,
            line.step_tokens,
        )
        for line in lines
    ] == [
        (
            "matrix-b2:g1:row-current-rating",
            "group-1",
            "g1",
            "Group 1",
            "row-current-rating",
            "source-row-current-rating",
            ("1",),
        ),
        (
            "matrix-b2:g2:row-current-rating",
            "group-2",
            "g2",
            "Group 2",
            "row-current-rating",
            "source-row-current-rating",
            ("1",),
        ),
    ]
    assert [
        (
            line.matched_rule_id,
            line.status,
            line.review_required,
            line.review_reason,
            line.spend_time,
            line.unit_label,
            line.unit_price,
            line.units,
            line.base_fee,
            line.discount_percent,
            line.testing_fee,
        )
        for line in lines
    ] == [
        (
            "fee_rule_temperature_rise",
            "calculated",
            False,
            None,
            "4",
            "sample",
            Decimal("600"),
            Decimal("5"),
            Decimal("0"),
            Decimal("0"),
            Decimal("3000"),
        ),
        (
            "fee_rule_temperature_rise",
            "calculated",
            False,
            None,
            "4",
            "sample",
            Decimal("600"),
            Decimal("5"),
            Decimal("0"),
            Decimal("0"),
            Decimal("3000"),
        ),
    ]
    assert [_base_fee_metadata(line) for line in lines] == [
        (("auto_filled", _FALLBACK_SOURCE, None),),
        (("auto_filled", _FALLBACK_SOURCE, None),),
    ]

    matrix_identities = (
        (
            "matrix-b2:g1:row-current-rating:1:0",
            "group-1",
            "row-current-rating",
            "1",
            0,
        ),
        (
            "matrix-b2:g2:row-current-rating:1:0",
            "group-2",
            "row-current-rating",
            "1",
            0,
        ),
    )
    assert result.ordered_row_identities == (
        *matrix_identities,
        ("sample_preparation", "group-1", "g1", "Group 1"),
        ("sample_preparation", "group-2", "g2", "Group 2"),
        ("report_preparation", "", "", ""),
    )
    assert [
        (
            safety.identity,
            safety.matched_rule_id,
            safety.safe_for_rebase,
            safety.diagnostic_code,
            tuple(
                (field.state, field.source, field.required_for_rebase)
                for field in safety.automatic_fields
                if field.field == "base_fee"
            ),
        )
        for safety in result.row_safety
    ] == [
        (
            matrix_identities[0],
            "fee_rule_temperature_rise",
            True,
            "safe",
            (("auto_filled", _FALLBACK_SOURCE, True),),
        ),
        (
            matrix_identities[1],
            "fee_rule_temperature_rise",
            True,
            "safe",
            (("auto_filled", _FALLBACK_SOURCE, True),),
        ),
    ]
    assert (
        result.source_context.automatic_defaults_fingerprint
        == canonical_fingerprint(edited_values_to_payload(result.automatic_values))
    )


def _snapshot() -> ConfirmedMatrixSnapshot:
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-current-rating",
        confirmed_matrix_id="matrix-b2",
        draft_row_id="draft-row-current-rating",
        source_row_snapshot_id="source-row-current-rating",
        row_order=1,
        test_item="CURRENT RATING",
        source_section="6.1",
        method="EIA-364",
        condition="300A",
        requirement="No damage",
    )
    groups = (
        ConfirmedMatrixGroup(
            confirmed_group_id="group-1",
            confirmed_matrix_id="matrix-b2",
            draft_group_id="draft-group-1",
            source_group_snapshot_id="source-group-1",
            group_order=1,
            group_key="g1",
            group_label="Group 1",
            sample_quantity_expression="5",
        ),
        ConfirmedMatrixGroup(
            confirmed_group_id="group-2",
            confirmed_matrix_id="matrix-b2",
            draft_group_id="draft-group-2",
            source_group_snapshot_id="source-group-2",
            group_order=2,
            group_key="g2",
            group_label="Group 2",
            sample_quantity_expression="5",
        ),
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="matrix-b2",
            project_id="P1",
            project_matrix_draft_id="draft-b2",
            source_import_id="import-b2",
            source_snapshot_id="snapshot-b2",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-25T09:00:00+08:00",
            sample_received_date="2026-07-25",
        ),
        groups=groups,
        rows=(row,),
        cells=tuple(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cell-{index}",
                confirmed_matrix_id="matrix-b2",
                confirmed_row_id=row.confirmed_row_id,
                confirmed_group_id=group.confirmed_group_id,
                draft_row_id=row.draft_row_id,
                draft_group_id=group.draft_group_id,
                cell_value="1",
            )
            for index, group in enumerate(groups, start=1)
        ),
    )


def _base_fee_metadata(
    line: FeeEvaluationLineItem,
) -> tuple[tuple[str, str | None, str | None], ...]:
    return tuple(
        (item.state, item.source, item.message)
        for item in line.field_metadata
        if item.field == "base_fee"
    )
