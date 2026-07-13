"""Focused read-model coverage for TASK_361C workspace enrichment."""

from __future__ import annotations

from types import SimpleNamespace

from backend.application.contact_measurement_plan_workspace_read_service import (
    ContactMeasurementPlanWorkspaceReadService,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_workspace_read_enriches_target_and_candidate_context_without_writes() -> None:
    repository = _Repository()
    service = ContactMeasurementPlanWorkspaceReadService(
        repository=repository,
        confirmed_store=_ConfirmedStore(),
        enabled=True,
    )

    workspace = service.get_workspace("P1")

    assert workspace["status"] == "needs_review"
    assert workspace["matrix_binding"] == {
        "base_confirmed_matrix_id": "cmv-1",
        "base_matrix_revision": 1,
        "current_confirmed_matrix_id": "cmv-2",
        "current_matrix_revision": 2,
        "matrix_binding_fingerprint": "cmv-2:2",
    }
    assert workspace["targets"] == [
        {
            "stable_target_key": "cmp-target:v1|group:cg-1|row:cr-1|step:1|suffix:",
            "group_label": "Qualification group",
            "test_item": "LLCR",
            "contact_kind": "llcr",
            "step_sequence": 1,
            "step_suffix_note": "",
            "sample_quantity_expression": "3",
            "eligible": True,
            "included": True,
            "exclusion_reason": None,
            "is_override": False,
            "coverage_state": "included",
            "readings_per_sample": 4,
            "target_review_state": "unchanged",
            "target_review_reason": None,
            "families": [
                {
                    "family_id": "hp",
                    "family_ordinal": 0,
                    "label": "High Power",
                    "count_per_sample": 4,
                    "record_label": "High Power",
                    "record_prefix": "HP",
                    "included": True,
                    "is_custom": False,
                }
            ],
        }
    ]
    assert workspace["impacts"] == [
        {
            "impact_subject_key": "cmp-candidate:v1|matrix:cmv-2|group:cg-2|row:cr-2|step:2|suffix:A",
            "category": "structural_review_required",
            "severity": "review_required",
            "resolution_state": "open",
            "reason": "A new Matrix target needs review.",
            "candidate": {
                "group_label": "Reliability group",
                "test_item": "CR specified current",
                "step_sequence": 2,
                "step_suffix_note": "A",
            },
        }
    ]
    assert workspace["summary"] == {
        "included_target_count": 1,
        "total_target_count": 1,
        "needs_review_count": 1,
        "readings_by_kind": {"llcr": 4, "cr_specified_current": None},
    }
    assert workspace["family_id_high_water_by_kind"] == {
        "llcr": 3,
        "cr_specified_current": 0,
    }
    assert repository.write_calls == 0


class _Repository:
    write_calls = 0

    def get_root(self, project_id: str):
        assert project_id == "P1"
        return SimpleNamespace(
            measurement_plan_root_id="root-1",
            active_confirmed_revision_id="r-confirmed",
            editable_revision_id="r-draft",
        )

    def get_editable_revision(self, project_id: str):
        return SimpleNamespace(
            measurement_plan_revision_id="r-draft",
            revision_sequence=2,
            state="needs_review",
            revision_fingerprint="draft-fingerprint",
            base_confirmed_matrix_id="cmv-1",
            base_matrix_revision=1,
            matrix_binding_fingerprint="cmv-2:2",
        )

    def get_active_revision(self, project_id: str):
        return None

    def targets(self, revision_id: str):
        assert revision_id == "r-draft"
        return [
            SimpleNamespace(
                measurement_plan_target_snapshot_id="target-1",
                stable_target_key="cmp-target:v1|group:cg-1|row:cr-1|step:1|suffix:",
                group_label="Qualification group",
                test_item="LLCR",
                contact_kind="llcr",
                step_sequence=1,
                step_suffix_note="",
                sample_quantity_expression="3",
                eligible=True,
                included=True,
                exclusion_reason=None,
                is_override=False,
                coverage_state="included",
                readings_per_sample=4,
                impact_status="unchanged",
                impact_reason=None,
            )
        ]

    def families(self, target_id: str):
        assert target_id == "target-1"
        return [
            SimpleNamespace(
                family_id="hp",
                family_ordinal=0,
                label="High Power",
                count_per_sample=4,
                record_label="High Power",
                record_prefix="HP",
                included=True,
                is_custom=False,
            )
        ]

    def impacts(self, revision_id: str):
        assert revision_id == "r-draft"
        return [
            SimpleNamespace(
                impact_subject_key="cmp-candidate:v1|matrix:cmv-2|group:cg-2|row:cr-2|step:2|suffix:A",
                category="structural_review_required",
                severity="review_required",
                resolution_state="open",
                reason="A new Matrix target needs review.",
            )
        ]

    def family_id_high_water_by_kind(self, root_id: str):
        assert root_id == "root-1"
        return {"llcr": 3, "cr_specified_current": 0}


class _ConfirmedStore:
    def get_active_by_project(self, project_id: str):
        return ConfirmedMatrixSnapshot(
            version=ConfirmedMatrixVersion(
                confirmed_matrix_id="cmv-2",
                project_id=project_id,
                project_matrix_draft_id="draft-2",
                source_import_id="source-2",
                source_snapshot_id="snapshot-2",
                confirmed_revision=2,
                is_active_authority=True,
                status=ConfirmedMatrixStatus.CONFIRMED,
                confirmed_by="operator",
                confirmed_at="2026-07-12T10:00:00Z",
            ),
            groups=(
                ConfirmedMatrixGroup(
                    confirmed_group_id="cg-2",
                    confirmed_matrix_id="cmv-2",
                    draft_group_id="dg-2",
                    source_group_snapshot_id="sg-2",
                    group_order=1,
                    group_key="G2",
                    group_label="Reliability group",
                    sample_quantity_expression="2",
                ),
            ),
            rows=(
                ConfirmedMatrixRow(
                    confirmed_row_id="cr-2",
                    confirmed_matrix_id="cmv-2",
                    draft_row_id="dr-2",
                    source_row_snapshot_id="sr-2",
                    row_order=1,
                    test_item="CR specified current",
                ),
            ),
            cells=(),
            step_quantities=(),
        )
