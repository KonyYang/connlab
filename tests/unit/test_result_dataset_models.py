from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from backend.domain.result_dataset_models import (
    LlcrDatasetPayload,
    LlcrMeasurement,
    LlcrResultEntry,
    ResultDatasetRevision,
    ResultDatasetSourceIdentity,
)


def test_result_dataset_revision_is_immutable_and_requires_confirmed_results() -> None:
    entry = _entry()
    revision = ResultDatasetRevision(
        dataset_id="dataset-1",
        dataset_type="llcr",
        revision=1,
        project_id="P1",
        confirmed_matrix_id="matrix-1",
        confirmed_matrix_revision=3,
        source=ResultDatasetSourceIdentity("record.xlsx", "a" * 64, 1200),
        imported_at="2026-08-29T08:00:00Z",
        imported_by="Even Yang",
        confirmed_at="2026-08-29T08:01:00Z",
        confirmed_by="Even Yang",
        parser_profile_version="connlab-llcr-macro-v1",
        validation_status="confirmed",
        payload=LlcrDatasetPayload((replace(entry, confirmed_outcome="pass"),)),
    )

    assert revision.payload.entries[0].summary_max == Decimal("0.198")
    with pytest.raises(FrozenInstanceError):
        revision.revision = 2  # type: ignore[misc]
    with pytest.raises(ValueError, match="must be confirmed"):
        replace(revision, payload=LlcrDatasetPayload((entry,)))


def test_llcr_manual_override_requires_reason_and_keeps_provisional_value() -> None:
    entry = _entry()

    with pytest.raises(ValueError, match="override requires a reason"):
        replace(entry, confirmed_outcome="fail")

    overridden = replace(
        entry,
        confirmed_outcome="fail",
        override_reason="Visible damage found during review.",
    )
    assert overridden.provisional_outcome == "pass"
    assert overridden.confirmed_outcome == "fail"


def _entry() -> LlcrResultEntry:
    measurements = (
        LlcrMeasurement(
            1, "SIG1", Decimal("0.169"), "mΩ", "SIG", "K10",
            Decimal("0.219"), "mΩ", "D10",
        ),
        LlcrMeasurement(
            1, "SIG2", Decimal("0.198"), "mΩ", "SIG", "K11",
            Decimal("0.248"), "mΩ", "D11",
        ),
    )
    return LlcrResultEntry(
        result_id="result-1",
        confirmed_group_id="group-1",
        group_label="1",
        confirmed_row_id="row-1",
        matrix_step_sequence=2,
        matrix_step_token="2",
        stage="initial",
        stage_label="Initial LLCR",
        requirement="≤0.25mΩ",
        requirement_comparator="<=",
        requirement_limit=Decimal("0.25"),
        requirement_unit="mΩ",
        measurements=measurements,
        summary_min=Decimal("0.169"),
        summary_max=Decimal("0.198"),
        summary_average=Decimal("0.1835"),
        provisional_outcome="pass",
        source_range="SIG!K10:K11",
    )
