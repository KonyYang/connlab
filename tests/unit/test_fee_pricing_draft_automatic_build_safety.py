from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.application.confirmed_matrix_fee_draft_build_result import (
    ConfirmedMatrixFeeAuthorityBuildResult,
)
from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationHeader,
    FeeEvaluationLineItem,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
)
from backend.application.fee_evaluation_pricing_draft_automatic_build import (
    build_current_pricing_defaults,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)
from backend.modules.fee_evaluation import FeeFieldMetadata


def test_single_build_uses_one_authority_snapshot_and_keeps_manual_base_fee_safe() -> None:
    snapshot = _snapshot()
    provider = _Provider(_authority_result(snapshot, _cr_line()))

    result = build_current_pricing_defaults("P1", provider)

    assert provider.calls == 1
    assert result.confirmed_matrix is snapshot
    assert result.automatic_values.rows[0].units == "40"
    assert result.source_context.measurement_plan_revision_id == "plan-1"
    assert result.source_context.point_profile_revision_id == "profile-1"
    assert result.row_safety[0].safe_for_rebase is True
    assert result.row_safety[0].diagnostic_code == "safe"
    base_fee = next(
        field for field in result.row_safety[0].automatic_fields if field.field == "base_fee"
    )
    assert base_fee.required_for_rebase is False


@pytest.mark.parametrize(
    "reason",
    (
        "Target omitted",
        "Target excluded",
        "Target affected",
        "Wrong target kind",
        "Mixed target authority",
        "Target diagnostic",
        "Missing target lineage",
        "Invalid readings",
        "Invalid owning Group quantity",
    ),
)
def test_cr_unsafe_authority_is_recorded_before_flattening(reason: str) -> None:
    snapshot = _snapshot()
    line = _cr_line()
    unsafe_metadata = tuple(
        replace(field, state="manual_required", source=None, message=reason)
        if field.field == "units"
        else field
        for field in line.field_metadata
    )
    provider = _Provider(
        _authority_result(
            snapshot,
            replace(
                line,
                review_required=True,
                review_reason=reason,
                field_metadata=unsafe_metadata,
            ),
        )
    )

    result = build_current_pricing_defaults("P1", provider)

    assert provider.calls == 1
    assert result.row_safety[0].safe_for_rebase is False
    assert result.row_safety[0].diagnostic_code == "automatic_authority_review_required"
    assert result.row_safety[0].diagnostic_text == reason


def test_confirmed_fee_service_exposes_every_fact_from_one_authority_build() -> None:
    snapshot = _snapshot(test_item="Visual Examination")
    plan = _authority_result(snapshot, _cr_line()).effective_measurement_plan
    profile = _authority_result(snapshot, _cr_line()).effective_point_profile
    plan_adapter = _Adapter(plan)
    profile_adapter = _Adapter(profile)
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(snapshot),
        contact_measurement_adapter=plan_adapter,
        contact_point_profile_adapter=profile_adapter,
    )

    result = service.build_authority_result(
        BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
    )

    assert result.confirmed_matrix is snapshot
    assert result.effective_measurement_plan is plan
    assert result.effective_point_profile is profile
    assert result.draft.header.confirmed_matrix_id == "matrix-1"
    assert result.rule_library.version.version_id == result.draft.header.pricing_rule_version_id
    assert plan_adapter.calls == 1
    assert profile_adapter.calls == 1


class _Provider:
    def __init__(self, result: ConfirmedMatrixFeeAuthorityBuildResult) -> None:
        self.result = result
        self.calls = 0

    def build_authority_result(self, command) -> ConfirmedMatrixFeeAuthorityBuildResult:
        assert command.project_id == "P1"
        self.calls += 1
        return self.result


class _Store:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot if project_id == "P1" else None


class _Adapter:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls = 0

    def get_effective(self, project_id: str) -> object:
        assert project_id == "P1"
        self.calls += 1
        return self.value


def _authority_result(
    snapshot: ConfirmedMatrixSnapshot,
    line: FeeEvaluationLineItem,
) -> ConfirmedMatrixFeeAuthorityBuildResult:
    draft = FeeEvaluationDraft(
        header=FeeEvaluationHeader(
            project_id="P1",
            confirmed_matrix_id="matrix-1",
            confirmed_revision=2,
            pricing_rule_version_id="rules-1",
            pricing_source_file_name="rules.json",
            pricing_source_hash="sha256:test",
            pricing_effective_from="2026-07-19",
            generated_at="2026-07-19T00:00:00+00:00",
        ),
        draft_status="needs_review",
        total_fee=None,
        review_required_count=1,
        groups=(
            FeeEvaluationGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="5",
                manual_line_items=(),
                line_items=(line,),
            ),
        ),
        manual_line_items=(),
        warnings=(),
    )
    plan = EffectiveContactMeasurementPlan(
        status="complete",
        snapshot=snapshot,
        revision_id="plan-1",
        revision_sequence=3,
        targets=(),
        diagnostics=(),
    )
    profile = EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="3",
        revision_id="profile-1",
        revision_sequence=2,
        fingerprint="profile-fp",
        lineage="profile lineage",
        message=None,
    )
    return ConfirmedMatrixFeeAuthorityBuildResult(
        draft=draft,
        confirmed_matrix=snapshot,
        rule_library=SimpleNamespace(version=SimpleNamespace(version_id="rules-1")),
        effective_measurement_plan=plan,
        effective_point_profile=profile,
    )


def _cr_line() -> FeeEvaluationLineItem:
    automatic = ("unit_price", "unit_label", "units", "testing_fee")
    metadata = tuple(
        FeeFieldMetadata(
            field=field,
            state="auto_filled",
            source="Confirmed CR Measurement Plan: revision 3 (plan-1; plan-fp)",
            message=None,
        )
        for field in automatic
    ) + (
        FeeFieldMetadata(
            field="base_fee",
            state="manual_required",
            source=None,
            message="Review base fee",
        ),
    )
    return FeeEvaluationLineItem(
        line_id="matrix-1:g1:row-1",
        status="review_required",
        review_required=True,
        review_reason="Review base fee",
        confirmed_matrix_id="matrix-1",
        confirmed_revision=2,
        group_key="g1",
        group_label="Group 1",
        confirmed_group_id="group-1",
        sample_quantity_expression="5",
        spend_time="0",
        confirmed_row_id="row-1",
        source_row_id="source-row-1",
        row_order=1,
        test_item="Contact Resistance at Specified Current",
        section="6.1",
        method="EIA-364-23",
        condition="",
        requirement="",
        step_tokens=("1",),
        matched_rule_id="fee_rule_contact_resistance_specified_current",
        matched_rule_version_id="rules-1",
        matched_rule_name="CR specified current",
        match_reason="exact",
        calculation_strategy="per_reading",
        unit_label="reading",
        unit_price=Decimal("10"),
        units=Decimal("40"),
        base_fee=None,
        discount_percent=Decimal("0"),
        testing_fee=Decimal("400"),
        field_metadata=metadata,
        warnings=(),
    )


def _snapshot(*, test_item: str = "Contact Resistance at Specified Current") -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="matrix-1",
        project_id="P1",
        project_matrix_draft_id="draft-1",
        source_import_id="import-1",
        source_snapshot_id="snapshot-1",
        confirmed_revision=2,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator",
        confirmed_at="2026-07-19T00:00:00+00:00",
        sample_received_date="2026-07-19",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="group-1",
        confirmed_matrix_id="matrix-1",
        draft_group_id="draft-group-1",
        source_group_snapshot_id="source-group-1",
        group_order=1,
        group_key="g1",
        group_label="Group 1",
        sample_quantity_expression="5",
    )
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id="matrix-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id="source-row-1",
        row_order=1,
        test_item=test_item,
        source_section="6.1",
        method="EIA-364-23",
        condition="",
        requirement="",
    )
    cell = ConfirmedMatrixCell(
        confirmed_cell_id="cell-1",
        confirmed_matrix_id="matrix-1",
        confirmed_row_id="row-1",
        confirmed_group_id="group-1",
        draft_row_id="draft-row-1",
        draft_group_id="draft-group-1",
        cell_value="1",
    )
    return ConfirmedMatrixSnapshot(version=version, groups=(group,), rows=(row,), cells=(cell,))
