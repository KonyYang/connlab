from dataclasses import replace
from decimal import Decimal

from backend.application.matrix_editor_session_signature import (
    build_project_matrix_draft_payload_signature,
)
from backend.domain import (
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)
from backend.domain.project_matrix_draft_models import (
    ProjectMatrixDraftDurationAuthority,
)


def test_duration_authority_order_is_canonical_in_saved_draft_signature() -> None:
    first = _authority("duration-1", 1, "48")
    second = _authority("duration-2", 2, "72")

    left = _draft((first, second))
    right = _draft((second, first))

    assert build_project_matrix_draft_payload_signature(left) == (
        build_project_matrix_draft_payload_signature(right)
    )


def test_duration_authority_change_invalidates_saved_draft_signature() -> None:
    original = _draft((_authority("duration-1", 1, "48"),))
    changed_item = replace(
        original.duration_authorities[0],
        duration_value=Decimal("3"),
        normalized_hours=Decimal("72"),
    )
    changed = replace(original, duration_authorities=(changed_item,))

    assert build_project_matrix_draft_payload_signature(original) != (
        build_project_matrix_draft_payload_signature(changed)
    )


def _draft(
    authorities: tuple[ProjectMatrixDraftDurationAuthority, ...],
) -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-1",
            project_id="P1",
            source_import_id="import-1",
            source_snapshot_id="source-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-24T08:00:00+00:00",
            updated_at="2026-07-24T08:00:00+00:00",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="group-1",
                project_matrix_draft_id="draft-1",
                source_group_snapshot_id="source-group-1",
                group_order=1,
                group_key="g1",
                group_label="Group 1",
                is_selected=True,
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="row-1",
                project_matrix_draft_id="draft-1",
                source_row_snapshot_id="source-row-1",
                row_order=1,
                test_item="Long-term high temperature zone load",
            ),
        ),
        duration_authorities=authorities,
    )


def _authority(
    authority_id: str,
    sequence: int,
    normalized_hours: str,
) -> ProjectMatrixDraftDurationAuthority:
    return ProjectMatrixDraftDurationAuthority(
        draft_duration_authority_id=authority_id,
        project_matrix_draft_id="draft-1",
        draft_group_id="group-1",
        draft_row_id="row-1",
        step_sequence=sequence,
        step_suffix_note="",
        duration_value=Decimal(normalized_hours) / Decimal("24"),
        duration_unit="days",
        normalized_hours=Decimal(normalized_hours),
        source_kind="import_structured",
        source_field="duration_authorities",
        source_import_id="import-1",
        source_fingerprint=f"source-{sequence}",
        lineage_fingerprint=f"lineage-{sequence}",
        authority_revision="1",
        status="usable",
        diagnostic_code=None,
        diagnostic_message=None,
        created_at="2026-07-24T08:00:00+00:00",
        updated_at="2026-07-24T08:00:00+00:00",
    )
