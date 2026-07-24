"""Confirmed Fee draft consumption of typed Matrix duration authority."""

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)
from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixDurationAuthority,
)
from tests.unit.test_confirmed_matrix_fee_draft_service import (
    _ConfirmedStore,
    _fixture_row,
    _snapshot as _legacy_snapshot,
)


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot if project_id == self.snapshot.version.project_id else None


def test_each_group_uses_only_its_own_confirmed_duration_authority() -> None:
    draft = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(_snapshot(include_second_authority=True))
    ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    group_1, group_2 = draft.groups
    line_1 = group_1.line_items[0]
    line_2 = group_2.line_items[0]
    assert (line_1.units, line_1.unit_price, line_1.testing_fee) == (
        Decimal("48"),
        Decimal("15"),
        Decimal("720"),
    )
    assert (line_2.units, line_2.unit_price, line_2.testing_fee) == (
        Decimal("72"),
        Decimal("15"),
        Decimal("1080"),
    )
    assert "lineage-g1" in _field_source(line_1, "units")
    assert "lineage-g2" in _field_source(line_2, "units")


def test_missing_owning_group_authority_never_uses_other_group_or_duration_text() -> None:
    draft = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(_snapshot(include_second_authority=False))
    ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    first = draft.groups[0].line_items[0]
    second = draft.groups[1].line_items[0]
    assert first.status == "calculated"
    assert second.status == "review_required"
    assert second.review_reason == "Duration authority belongs to another Matrix group"
    assert (second.units, second.testing_fee) == (None, None)


def test_plain_contact_resistance_never_falls_back_to_llcr_authority() -> None:
    row = _fixture_row("CONTACT RESISTANCE")
    draft = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_legacy_snapshot(row=row))
    ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert (line.status, line.review_required) == ("review_required", True)
    assert line.review_reason == "Confirmed CR Measurement Plan authority is unavailable."
    assert (line.unit_price, line.units, line.testing_fee) == (None, None, None)


def _snapshot(*, include_second_authority: bool) -> ConfirmedMatrixSnapshot:
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id="matrix-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id="source-row-1",
        row_order=1,
        test_item="Long-term high temperature zone load",
        condition="999 hours from untrusted prose",
    )
    groups = tuple(_group(index) for index in (1, 2))
    authorities = [_authority(group_index=1, days="2", hours="48")]
    if include_second_authority:
        authorities.append(_authority(group_index=2, days="3", hours="72"))
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="matrix-1",
            project_id="P1",
            project_matrix_draft_id="draft-1",
            source_import_id="import-1",
            source_snapshot_id="source-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-24T08:00:00+00:00",
            sample_received_date="2026-07-24",
        ),
        groups=groups,
        rows=(row,),
        cells=tuple(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cell-{index}",
                confirmed_matrix_id="matrix-1",
                confirmed_row_id="row-1",
                confirmed_group_id=f"group-{index}",
                draft_row_id="draft-row-1",
                draft_group_id=f"draft-group-{index}",
                cell_value="1",
            )
            for index in (1, 2)
        ),
        duration_authorities=tuple(authorities),
    )


def _group(index: int) -> ConfirmedMatrixGroup:
    return ConfirmedMatrixGroup(
        confirmed_group_id=f"group-{index}",
        confirmed_matrix_id="matrix-1",
        draft_group_id=f"draft-group-{index}",
        source_group_snapshot_id=f"source-group-{index}",
        group_order=index,
        group_key=f"g{index}",
        group_label=f"Group {index}",
        sample_quantity_expression=str(index + 4),
    )


def _authority(
    *,
    group_index: int,
    days: str,
    hours: str,
) -> ConfirmedMatrixDurationAuthority:
    return ConfirmedMatrixDurationAuthority(
        confirmed_duration_authority_id=f"duration-{group_index}",
        confirmed_matrix_id="matrix-1",
        confirmed_group_id=f"group-{group_index}",
        confirmed_row_id="row-1",
        step_sequence=1,
        step_suffix_note="",
        duration_value=Decimal(days),
        duration_unit="days",
        normalized_hours=Decimal(hours),
        source_kind="import_structured",
        source_field="duration_authorities",
        source_import_id="import-1",
        source_fingerprint=f"source-g{group_index}",
        lineage_fingerprint=f"lineage-g{group_index}",
        authority_revision="1",
        status="usable",
        diagnostic_code=None,
        diagnostic_message=None,
        created_at="2026-07-24T08:00:00+00:00",
        updated_at="2026-07-24T08:00:00+00:00",
    )


def _field_source(line, field: str) -> str:
    return next(item.source or "" for item in line.field_metadata if item.field == field)
