from decimal import Decimal

import pytest

from backend.application.confirmed_matrix_fee_duration_authority import (
    resolve_confirmed_duration_authority,
)
from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixDurationAuthority,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
)


def _group(group_id: str = "confirmed-group-1") -> ConfirmedMatrixGroup:
    return ConfirmedMatrixGroup(
        confirmed_group_id=group_id,
        confirmed_matrix_id="confirmed-1",
        draft_group_id="draft-group-1",
        source_group_snapshot_id="source-group-1",
        group_order=1,
        group_key="group-1",
        group_label="Group 1",
        sample_quantity_expression="5",
    )


def _row(row_id: str = "confirmed-row-1") -> ConfirmedMatrixRow:
    return ConfirmedMatrixRow(
        confirmed_row_id=row_id,
        confirmed_matrix_id="confirmed-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id="source-row-1",
        row_order=1,
        test_item="Long-term high temperature zone load",
    )


def _authority(**overrides: object) -> ConfirmedMatrixDurationAuthority:
    values: dict[str, object] = {
        "confirmed_duration_authority_id": "duration-1",
        "confirmed_matrix_id": "confirmed-1",
        "confirmed_group_id": "confirmed-group-1",
        "confirmed_row_id": "confirmed-row-1",
        "step_sequence": 1,
        "step_suffix_note": "",
        "duration_value": Decimal("2"),
        "duration_unit": "days",
        "normalized_hours": Decimal("48"),
        "source_kind": "import_structured",
        "source_field": "duration_authorities[0]",
        "source_import_id": "import-1",
        "source_fingerprint": "source-fp",
        "lineage_fingerprint": "lineage-fp",
        "authority_revision": "1",
        "status": "usable",
        "diagnostic_code": None,
        "diagnostic_message": None,
        "created_at": "2026-07-24T00:00:00+00:00",
        "updated_at": "2026-07-24T00:00:00+00:00",
    }
    values.update(overrides)
    return ConfirmedMatrixDurationAuthority(**values)


def test_resolves_exact_owning_row_and_normalized_hours() -> None:
    result = resolve_confirmed_duration_authority(
        group=_group(),
        row=_row(),
        step_sequence=1,
        step_suffix_note=None,
        authorities=(_authority(),),
        expected_confirmed_matrix_id="confirmed-1",
    )

    assert result.is_valid
    assert result.normalized_hours == Decimal("48")
    assert result.confirmed_group_id == "confirmed-group-1"
    assert result.confirmed_row_id == "confirmed-row-1"
    assert result.source == (
        "Confirmed Matrix duration authority: revision 1 "
        "(confirmed-1; lineage-fp)"
    )


@pytest.mark.parametrize(
    ("overrides", "diagnostic"),
    [
        ({"confirmed_group_id": "other-group"}, "wrong_group"),
        ({"confirmed_row_id": "other-row"}, "wrong_row"),
        ({"step_sequence": 2}, "missing"),
        ({"status": "stale"}, "stale"),
        ({"lineage_fingerprint": ""}, "missing_lineage"),
        ({"normalized_hours": Decimal("0")}, "invalid"),
    ],
)
def test_rejects_wrong_identity_or_unusable_authority(
    overrides: dict[str, object],
    diagnostic: str,
) -> None:
    result = resolve_confirmed_duration_authority(
        group=_group(),
        row=_row(),
        step_sequence=1,
        step_suffix_note="",
        authorities=(_authority(**overrides),),
        expected_confirmed_matrix_id="confirmed-1",
    )

    assert not result.is_valid
    assert result.diagnostic == diagnostic


def test_rejects_divergent_duplicate_authorities() -> None:
    result = resolve_confirmed_duration_authority(
        group=_group(),
        row=_row(),
        step_sequence=1,
        step_suffix_note="",
        authorities=(
            _authority(),
            _authority(
                confirmed_duration_authority_id="duration-2",
                duration_value=Decimal("3"),
                normalized_hours=Decimal("72"),
            ),
        ),
        expected_confirmed_matrix_id="confirmed-1",
    )

    assert not result.is_valid
    assert result.diagnostic == "conflict"
