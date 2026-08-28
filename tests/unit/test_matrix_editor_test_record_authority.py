from __future__ import annotations

from types import SimpleNamespace

from backend.application.matrix_editor_test_record_authority import (
    ConfirmedMatrixTestRecordAuthorityMatcher,
    build_matrix_editor_test_record_signature,
)


def test_matcher_accepts_current_payload_equal_to_active_matrix() -> None:
    snapshot = _snapshot()
    matcher = ConfirmedMatrixTestRecordAuthorityMatcher(_Store(snapshot))

    assert matcher.matches_active_authority(
        "P1",
        build_matrix_editor_test_record_signature(
            groups=(
                SimpleNamespace(
                    group_key="g1",
                    group_label="1",
                    sample_quantity_expression="5",
                ),
            ),
            rows=(
                SimpleNamespace(
                    test_item="Visual",
                    section="5.1",
                    method="EIA",
                    condition="Normal",
                    requirement="No damage",
                    is_sample_row=False,
                    group_values={"g1": "1"},
                ),
            ),
        ),
    )


def test_matcher_rejects_changed_current_payload() -> None:
    matcher = ConfirmedMatrixTestRecordAuthorityMatcher(_Store(_snapshot()))

    assert not matcher.matches_active_authority(
        "P1",
        build_matrix_editor_test_record_signature(
            groups=(
                SimpleNamespace(
                    group_key="g1",
                    group_label="1",
                    sample_quantity_expression="5",
                ),
            ),
            rows=(
                SimpleNamespace(
                    test_item="Visual",
                    section="5.1",
                    method="Changed method",
                    condition="Normal",
                    requirement="No damage",
                    is_sample_row=False,
                    group_values={"g1": "1"},
                ),
            ),
        ),
    )


def test_matcher_ignores_sample_instruction_rows_not_consumed_by_test_record() -> None:
    matcher = ConfirmedMatrixTestRecordAuthorityMatcher(_Store(_snapshot()))

    assert matcher.matches_active_authority(
        "P1",
        build_matrix_editor_test_record_signature(
            groups=(
                SimpleNamespace(
                    group_key="g1",
                    group_label="1",
                    sample_quantity_expression="5",
                ),
            ),
            rows=(
                SimpleNamespace(
                    test_item="Visual",
                    section="5.1",
                    method="EIA",
                    condition="Normal",
                    requirement="No damage",
                    is_sample_row=False,
                    group_values={"g1": "1"},
                ),
                SimpleNamespace(
                    test_item="Sample instruction",
                    section="",
                    method="",
                    condition="",
                    requirement="",
                    is_sample_row=True,
                    group_values={"g1": "handling note"},
                ),
            ),
        ),
    )


def test_matcher_rejects_when_no_active_matrix_exists() -> None:
    matcher = ConfirmedMatrixTestRecordAuthorityMatcher(_Store(None))

    assert not matcher.matches_active_authority("P1", "anything")


def _snapshot():
    group = SimpleNamespace(
        confirmed_group_id="cg1",
        group_key="g1",
        group_label="1",
        sample_quantity_expression="5",
    )
    row = SimpleNamespace(
        confirmed_row_id="r1",
        test_item="Visual",
        source_section="5.1",
        method="EIA",
        condition="Normal",
        requirement="No damage",
    )
    return SimpleNamespace(
        groups=(group,),
        rows=(row,),
        cells=(
            SimpleNamespace(
                confirmed_group_id="cg1",
                confirmed_row_id="r1",
                cell_value="1",
            ),
        ),
    )


class _Store:
    def __init__(self, snapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str):
        return self.snapshot
