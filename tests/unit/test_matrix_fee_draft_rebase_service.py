import pytest

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeRebaseKeyConflictError,
    MatrixFeeDraftRebaseService,
    MatrixFeeRebaseLineage,
    MatrixFeeRebaseSourceRow,
    MatrixFeeRebaseTargetGroup,
    MatrixFeeRebaseTargetRow,
)


def test_matching_rows_preserve_edited_fee_values_and_target_lineage() -> None:
    source = _source_row(
        _lineage(
            confirmed_group_id="old-group",
            confirmed_row_id="old-row",
            source_row_snapshot_id="source-row-1",
        ),
        spend_time="7",
        unit_price="123",
        base_fee="246",
        testing_fee="861",
        notes="operator edit",
    )
    target = _target_row(
        _lineage(
            confirmed_group_id="new-group",
            confirmed_row_id="new-row",
            source_row_snapshot_id="source-row-1",
        ),
        spend_time="1",
        unit_price="10",
        testing_fee="10",
        notes="default",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source,),
        target_rows=(target,),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.summary.preserved_count == 1
    assert result.summary.added_count == 0
    assert result.summary.removed_count == 0
    assert result.inactive_removed_rows == ()
    assert result.active_rows == (
        FeeEvaluationEditedExportRow(
            source_line_id="new-line",
            confirmed_group_id="new-group",
            confirmed_row_id="new-row",
            step_token="1",
            step_index=0,
            spend_time="7",
            unit_price="123",
            unit_type="hour",
            units="2",
            base_fee="246",
            discount="0",
            testing_fee="861",
            notes="operator edit",
        ),
    )


def test_text_only_matrix_edit_preserves_values_with_source_snapshot_id() -> None:
    source = _source_row(
        _lineage(source_row_snapshot_id="source-row-1", test_item="Old item"),
        notes="kept by source snapshot",
    )
    target = _target_row(
        _lineage(source_row_snapshot_id="source-row-1", test_item="New item"),
        notes="default",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source,),
        target_rows=(target,),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.active_rows[0].notes == "kept by source snapshot"
    assert result.summary.preserved_count == 1


def test_text_only_matrix_edit_preserves_values_with_draft_row_id() -> None:
    source = _source_row(
        _lineage(
            source_row_snapshot_id=None,
            draft_row_id="draft-row-1",
            test_item="Old item",
        ),
        notes="kept by draft row",
    )
    target = _target_row(
        _lineage(
            source_row_snapshot_id=None,
            draft_row_id="draft-row-1",
            test_item="New item",
        ),
        notes="default",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source,),
        target_rows=(target,),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.active_rows[0].notes == "kept by draft row"
    assert result.summary.preserved_count == 1


def test_lineage_less_signature_change_becomes_removed_and_added() -> None:
    source = _source_row(
        _lineage(
            source_row_snapshot_id=None,
            draft_row_id=None,
            test_item="Old item",
        ),
        notes="old fee",
    )
    target = _target_row(
        _lineage(
            source_row_snapshot_id=None,
            draft_row_id=None,
            test_item="New item",
        ),
        notes="new default",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source,),
        target_rows=(target,),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.active_rows[0].notes == "new default"
    assert result.inactive_removed_rows[0].previous_row.notes == "old fee"
    assert result.summary.preserved_count == 0
    assert result.summary.added_count == 1
    assert result.summary.removed_count == 1


def test_added_group_or_step_uses_default_fee_row() -> None:
    target = _target_row(_lineage(), spend_time="3", testing_fee="30", notes="default")

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(),
        target_rows=(target,),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.active_rows == (target.default_row,)
    assert result.summary.added_count == 1


def test_removed_group_or_step_becomes_inactive_removed_row() -> None:
    source = _source_row(_lineage(group_key="G1", group_label="Group 1"), notes="removed")

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source,),
        target_rows=(),
        source_manual_rows=(),
        target_groups=(),
    )

    assert result.active_rows == ()
    assert result.inactive_removed_rows[0].previous_row.notes == "removed"
    assert result.inactive_removed_rows[0].previous_group_key == "G1"
    assert result.inactive_removed_rows[0].previous_group_label == "Group 1"
    assert result.inactive_removed_rows[0].inactive_reason == "removed_from_matrix"
    assert result.summary.removed_count == 1


def test_report_preparation_manual_row_is_preserved_globally() -> None:
    manual = _manual_row(row_kind="report_preparation", notes="report edit")

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(),
        target_rows=(),
        source_manual_rows=(manual,),
        target_groups=(),
    )

    assert result.manual_rows == (manual,)
    assert result.summary.preserved_manual_count == 1


def test_sample_preparation_manual_row_matches_by_group_key_or_label() -> None:
    manual = _manual_row(
        row_kind="sample_preparation",
        confirmed_group_id="old-group",
        group_key=" G1 ",
        group_label="Group 1",
        notes="sample edit",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(),
        target_rows=(),
        source_manual_rows=(manual,),
        target_groups=(
            _target_group(
                confirmed_group_id="new-group",
                group_key="g1",
                group_label="Group 1 renamed",
            ),
        ),
    )

    assert result.manual_rows == (
        FeeEvaluationEditedManualRow(
            row_kind="sample_preparation",
            spend_time="2",
            unit_price="50",
            unit_type="sample",
            units="1",
            base_fee="100",
            discount="0",
            testing_fee="100",
            notes="sample edit",
            confirmed_group_id="new-group",
            group_key="g1",
            group_label="Group 1 renamed",
        ),
    )
    assert result.summary.preserved_manual_count == 1


def test_sample_preparation_manual_row_matches_by_group_label_when_key_is_missing() -> None:
    manual = _manual_row(
        row_kind="sample_preparation",
        confirmed_group_id="old-group",
        group_key="",
        group_label="Group 1",
        notes="sample edit",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(),
        target_rows=(),
        source_manual_rows=(manual,),
        target_groups=(
            _target_group(
                confirmed_group_id="new-group",
                group_key="",
                group_label=" group   1 ",
            ),
        ),
    )

    assert result.manual_rows[0].confirmed_group_id == "new-group"
    assert result.manual_rows[0].group_label == " group   1 "


def test_removed_group_sample_preparation_is_not_active() -> None:
    manual = _manual_row(
        row_kind="sample_preparation",
        confirmed_group_id="old-group",
        group_key="G1",
        group_label="Group 1",
    )

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(),
        target_rows=(),
        source_manual_rows=(manual,),
        target_groups=(_target_group(group_key="G2", group_label="Group 2"),),
    )

    assert result.manual_rows == ()
    assert result.summary.removed_manual_count == 1


def test_rebase_summary_counts_preserved_added_removed() -> None:
    source = _source_row(_lineage(source_row_snapshot_id="source-row-1"))
    removed = _source_row(_lineage(source_row_snapshot_id="source-row-2"))
    preserved_target = _target_row(_lineage(source_row_snapshot_id="source-row-1"))
    added_target = _target_row(_lineage(source_row_snapshot_id="source-row-3"))

    result = MatrixFeeDraftRebaseService().rebase(
        source_rows=(source, removed),
        target_rows=(preserved_target, added_target),
        source_manual_rows=(),
        target_groups=(_target_group(),),
    )

    assert result.summary.preserved_count == 1
    assert result.summary.added_count == 1
    assert result.summary.removed_count == 1


def test_duplicate_source_rebase_key_is_rejected() -> None:
    first = _source_row(_lineage(source_row_snapshot_id="source-row-1"), notes="first")
    second = _source_row(_lineage(source_row_snapshot_id="source-row-1"), notes="second")
    target = _target_row(_lineage(source_row_snapshot_id="source-row-1"))

    with pytest.raises(MatrixFeeRebaseKeyConflictError, match="source"):
        MatrixFeeDraftRebaseService().rebase(
            source_rows=(first, second),
            target_rows=(target,),
            source_manual_rows=(),
            target_groups=(_target_group(),),
        )


def test_duplicate_target_rebase_key_is_rejected() -> None:
    source = _source_row(_lineage(source_row_snapshot_id="source-row-1"), notes="source")
    first_target = _target_row(_lineage(source_row_snapshot_id="source-row-1"))
    second_target = _target_row(_lineage(source_row_snapshot_id="source-row-1"))

    with pytest.raises(MatrixFeeRebaseKeyConflictError, match="target"):
        MatrixFeeDraftRebaseService().rebase(
            source_rows=(source,),
            target_rows=(first_target, second_target),
            source_manual_rows=(),
            target_groups=(_target_group(),),
        )


def test_duplicate_target_group_key_for_manual_rows_is_rejected() -> None:
    manual = _manual_row(row_kind="sample_preparation", group_key="G1")

    with pytest.raises(MatrixFeeRebaseKeyConflictError, match="group key"):
        MatrixFeeDraftRebaseService().rebase(
            source_rows=(),
            target_rows=(),
            source_manual_rows=(manual,),
            target_groups=(
                _target_group(confirmed_group_id="group-1", group_key="G1"),
                _target_group(confirmed_group_id="group-2", group_key=" g1 "),
            ),
        )


def test_duplicate_target_group_label_for_manual_rows_is_rejected() -> None:
    manual = _manual_row(row_kind="sample_preparation", group_key="", group_label="Group 1")

    with pytest.raises(MatrixFeeRebaseKeyConflictError, match="group label"):
        MatrixFeeDraftRebaseService().rebase(
            source_rows=(),
            target_rows=(),
            source_manual_rows=(manual,),
            target_groups=(
                _target_group(confirmed_group_id="group-1", group_key="", group_label="Group 1"),
                _target_group(confirmed_group_id="group-2", group_key="", group_label=" group   1 "),
            ),
        )


def _lineage(
    *,
    group_key: str = "G1",
    group_label: str = "Group 1",
    confirmed_group_id: str = "old-group",
    confirmed_row_id: str = "old-row",
    source_row_snapshot_id: str | None = "source-row-1",
    draft_row_id: str | None = "draft-row-1",
    step_token: str = "1",
    step_index: int = 0,
    test_item: str = "LLCR",
    source_section: str = "Sec",
    method: str = "M",
    condition: str = "C",
    requirement: str = "R",
) -> MatrixFeeRebaseLineage:
    return MatrixFeeRebaseLineage(
        group_key=group_key,
        group_label=group_label,
        confirmed_group_id=confirmed_group_id,
        confirmed_row_id=confirmed_row_id,
        source_row_snapshot_id=source_row_snapshot_id,
        draft_row_id=draft_row_id,
        step_token=step_token,
        step_index=step_index,
        test_item=test_item,
        source_section=source_section,
        method=method,
        condition=condition,
        requirement=requirement,
    )


def _source_row(
    lineage: MatrixFeeRebaseLineage,
    *,
    spend_time: str = "2",
    unit_price: str = "50",
    unit_type: str = "hour",
    units: str = "2",
    base_fee: str = "100",
    discount: str = "0",
    testing_fee: str = "100",
    notes: str = "source edit",
) -> MatrixFeeRebaseSourceRow:
    return MatrixFeeRebaseSourceRow(
        lineage=lineage,
        edited_row=FeeEvaluationEditedExportRow(
            source_line_id="old-line",
            confirmed_group_id=lineage.confirmed_group_id,
            confirmed_row_id=lineage.confirmed_row_id,
            step_token=lineage.step_token,
            step_index=lineage.step_index,
            spend_time=spend_time,
            unit_price=unit_price,
            unit_type=unit_type,
            units=units,
            base_fee=base_fee,
            discount=discount,
            testing_fee=testing_fee,
            notes=notes,
        ),
    )


def _target_row(
    lineage: MatrixFeeRebaseLineage,
    *,
    spend_time: str = "1",
    unit_price: str = "10",
    unit_type: str = "hour",
    units: str = "1",
    base_fee: str = "10",
    discount: str = "0",
    testing_fee: str = "10",
    notes: str = "default",
) -> MatrixFeeRebaseTargetRow:
    return MatrixFeeRebaseTargetRow(
        lineage=lineage,
        default_row=FeeEvaluationEditedExportRow(
            source_line_id="new-line",
            confirmed_group_id=lineage.confirmed_group_id,
            confirmed_row_id=lineage.confirmed_row_id,
            step_token=lineage.step_token,
            step_index=lineage.step_index,
            spend_time=spend_time,
            unit_price=unit_price,
            unit_type=unit_type,
            units=units,
            base_fee=base_fee,
            discount=discount,
            testing_fee=testing_fee,
            notes=notes,
        ),
    )


def _manual_row(
    *,
    row_kind: str,
    spend_time: str = "2",
    unit_price: str = "50",
    unit_type: str = "sample",
    units: str = "1",
    base_fee: str = "100",
    discount: str = "0",
    testing_fee: str = "100",
    notes: str = "manual edit",
    confirmed_group_id: str = "",
    group_key: str = "",
    group_label: str = "",
) -> FeeEvaluationEditedManualRow:
    return FeeEvaluationEditedManualRow(
        row_kind=row_kind,
        spend_time=spend_time,
        unit_price=unit_price,
        unit_type=unit_type,
        units=units,
        base_fee=base_fee,
        discount=discount,
        testing_fee=testing_fee,
        notes=notes,
        confirmed_group_id=confirmed_group_id,
        group_key=group_key,
        group_label=group_label,
    )


def _target_group(
    *,
    confirmed_group_id: str = "new-group",
    group_key: str = "G1",
    group_label: str = "Group 1",
) -> MatrixFeeRebaseTargetGroup:
    return MatrixFeeRebaseTargetGroup(
        confirmed_group_id=confirmed_group_id,
        group_key=group_key,
        group_label=group_label,
    )
