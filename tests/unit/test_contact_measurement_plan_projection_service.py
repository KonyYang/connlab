"""Unit coverage for independent authority projection boundaries."""

from __future__ import annotations

from backend.application.contact_measurement_plan_projection_service import (
    ContactMeasurementPlanProjectionService,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactPlan,
)


def test_projection_reports_authority_corrupt_when_root_has_no_confirmed_revision() -> None:
    service = ContactMeasurementPlanProjectionService(
        _RootWithoutActiveRevisionRepository(),
        enabled=True,
    )

    result = service.get_effective("P1")

    assert result.status == "authority_corrupt"
    assert result.targets == ()
    assert result.diagnostics == (
        "Contact measurement authority requires maintenance before it can be projected.",
    )


def test_projection_omits_review_required_targets_and_keeps_compatible_targets() -> None:
    service = ContactMeasurementPlanProjectionService(
        _PartialRepository(),
        enabled=True,
    )

    result = service.get_effective("P1")

    assert result.status == "partial_compatible"
    assert [target["stable_target_key"] for target in result.targets] == ["compatible"]
    assert result.diagnostics == ("1 target requires review and is not projected.",)


def test_projection_uses_current_matrix_classifier_without_mutating_plan() -> None:
    repository = _CurrentMatrixRepository()
    service = ContactMeasurementPlanProjectionService(
        repository,
        enabled=True,
        confirmed_store=_CurrentMatrixStore(),
    )

    result = service.get_effective("P1")

    assert result.status == "needs_review"
    assert [target["stable_target_key"] for target in result.targets] == [
        "cmp-target:v1|group:sg-1|row:sr-1|step:1|suffix:"
    ]
    assert result.diagnostics == (
        "1 current Matrix target requires review and is not projected.",
    )
    assert repository.targets_were_mutated is False


class _RootWithoutActiveRevisionRepository:
    def get_root(self, project_id: str):
        return object()

    def get_active_revision(self, project_id: str):
        return None


class _PartialRepository:
    def get_root(self, project_id: str):
        return object()

    def get_active_revision(self, project_id: str):
        return type(
            "Revision",
            (),
            {
                "measurement_plan_revision_id": "r1",
                "revision_sequence": 1,
            },
        )()

    def targets(self, revision_id: str):
        return [
            type(
                "Target",
                (),
                {
                    "measurement_plan_target_snapshot_id": "t-compatible",
                    "stable_target_key": "compatible",
                    "contact_kind": "llcr",
                    "included": True,
                    "readings_per_sample": 2,
                    "impact_status": "unchanged",
                },
            )(),
            type(
                "Target",
                (),
                {
                    "measurement_plan_target_snapshot_id": "t-review",
                    "stable_target_key": "review",
                    "contact_kind": "llcr",
                    "included": True,
                    "readings_per_sample": 3,
                    "impact_status": "structural_review_required",
                },
            )(),
        ]

    def families(self, target_id: str):
        return []


class _CurrentMatrixRepository(_PartialRepository):
    targets_were_mutated = False

    def targets(self, revision_id: str):
        return [
            type(
                "Target",
                (),
                {
                    "measurement_plan_target_snapshot_id": "target-1",
                    "stable_target_key": (
                        "cmp-target:v1|group:sg-1|row:sr-1|step:1|suffix:"
                    ),
                    "source_group_snapshot_id": "sg-1",
                    "manual_group_anchor_id": None,
                    "source_row_snapshot_id": "sr-1",
                    "manual_row_anchor_id": None,
                    "step_sequence": 1,
                    "step_suffix_note": "",
                    "contact_kind": "llcr",
                    "eligible": True,
                    "included": True,
                    "group_label": "Old group",
                    "test_item": "LLCR",
                    "sample_quantity_expression": "2",
                    "readings_per_sample": 2,
                    "impact_status": "unchanged",
                },
            )(),
        ]


class _CurrentMatrixStore:
    def get_active_by_project(self, project_id: str):
        return ConfirmedMatrixSnapshot(
            version=ConfirmedMatrixVersion(
                confirmed_matrix_id="cmv-current",
                project_id=project_id,
                project_matrix_draft_id="pmd-current",
                source_import_id="smi-current",
                source_snapshot_id="sms-current",
                confirmed_revision=2,
                is_active_authority=True,
                status=ConfirmedMatrixStatus.CONFIRMED,
                confirmed_by="operator",
                confirmed_at="2026-07-12T10:00:00Z",
            ),
            groups=(
                ConfirmedMatrixGroup(
                    confirmed_group_id="cg-1",
                    confirmed_matrix_id="cmv-current",
                    draft_group_id="dg-1",
                    source_group_snapshot_id="sg-1",
                    group_order=1,
                    group_key="g1",
                    group_label="Current group",
                    sample_quantity_expression="3",
                ),
                ConfirmedMatrixGroup(
                    confirmed_group_id="cg-2",
                    confirmed_matrix_id="cmv-current",
                    draft_group_id="dg-2",
                    source_group_snapshot_id="sg-2",
                    group_order=2,
                    group_key="g2",
                    group_label="New group",
                    sample_quantity_expression="2",
                ),
            ),
            rows=(
                ConfirmedMatrixRow(
                    confirmed_row_id="cr-1",
                    confirmed_matrix_id="cmv-current",
                    draft_row_id="dr-1",
                    source_row_snapshot_id="sr-1",
                    row_order=1,
                    test_item="LLCR",
                ),
            ),
            step_quantities=tuple(
                ConfirmedMatrixStepQuantity(
                    confirmed_step_quantity_id=f"q-{group_id}",
                    confirmed_matrix_id="cmv-current",
                    confirmed_group_id=group_id,
                    confirmed_row_id="cr-1",
                    draft_group_id=f"d{group_id}",
                    draft_row_id="dr-1",
                    step_sequence=1,
                    step_suffix_note=None,
                    raw_token="1",
                    test_points_per_sample=None,
                    readings_per_point=None,
                    contact_points_per_sample=None,
                    source="matrix_contact_plan",
                    review_required=False,
                    review_reason=None,
                    confirmed_at="2026-07-12T10:00:00Z",
                    contact_plan=MatrixStepContactPlan(
                        contact_kind="llcr",
                        coverage_status="included",
                        included=True,
                        exclusion_reason=None,
                        is_override=False,
                        readings_per_sample="2",
                        families=(),
                    ),
                )
                for group_id in ("cg-1", "cg-2")
            ),
        )
