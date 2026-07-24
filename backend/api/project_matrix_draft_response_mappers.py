"""Response mappers for Project Matrix draft routes."""

from backend.api.project_matrix_draft_dtos import (
    ConfirmedMatrixCellResponse,
    ConfirmedMatrixGroupResponse,
    ConfirmedMatrixRowResponse,
    ConfirmedMatrixSnapshotResponse,
    ConfirmedMatrixVersionResponse,
    MatrixDurationAuthorityResponse,
    ProjectMatrixDraftCellResponse,
    ProjectMatrixDraftGroupResponse,
    ProjectMatrixDraftRecordResponse,
    ProjectMatrixDraftResponse,
    ProjectMatrixDraftRowResponse,
)
from backend.domain import ConfirmedMatrixSnapshot, ProjectMatrixDraftSnapshot


def to_project_matrix_draft_response(
    draft: ProjectMatrixDraftSnapshot,
) -> ProjectMatrixDraftResponse:
    return ProjectMatrixDraftResponse(
        record=ProjectMatrixDraftRecordResponse(
            **{
                field: getattr(draft.record, field)
                for field in ProjectMatrixDraftRecordResponse.model_fields
                if field != "status"
            },
            status=draft.record.status.value,
        ),
        groups=[
            ProjectMatrixDraftGroupResponse(
                **{
                    field: getattr(group, field)
                    for field in ProjectMatrixDraftGroupResponse.model_fields
                }
            )
            for group in draft.groups
        ],
        rows=[
            ProjectMatrixDraftRowResponse(
                **{
                    field: getattr(row, field)
                    for field in ProjectMatrixDraftRowResponse.model_fields
                }
            )
            for row in draft.rows
        ],
        cells=[
            ProjectMatrixDraftCellResponse(
                **{
                    field: getattr(cell, field)
                    for field in ProjectMatrixDraftCellResponse.model_fields
                }
            )
            for cell in draft.cells
        ],
        duration_authorities=[
            MatrixDurationAuthorityResponse(
                duration_authority_id=item.draft_duration_authority_id,
                group_id=item.draft_group_id,
                row_id=item.draft_row_id,
                **_duration_fields(item),
            )
            for item in draft.duration_authorities
        ],
    )


def to_confirmed_matrix_response(
    snapshot: ConfirmedMatrixSnapshot,
) -> ConfirmedMatrixSnapshotResponse:
    return ConfirmedMatrixSnapshotResponse(
        version=ConfirmedMatrixVersionResponse(
            **{
                field: (
                    snapshot.version.status.value
                    if field == "status"
                    else getattr(snapshot.version, field)
                )
                for field in ConfirmedMatrixVersionResponse.model_fields
            }
        ),
        groups=[
            ConfirmedMatrixGroupResponse(
                **{
                    field: getattr(group, field)
                    for field in ConfirmedMatrixGroupResponse.model_fields
                }
            )
            for group in snapshot.groups
        ],
        rows=[
            ConfirmedMatrixRowResponse(
                **{
                    field: getattr(row, field)
                    for field in ConfirmedMatrixRowResponse.model_fields
                }
            )
            for row in snapshot.rows
        ],
        cells=[
            ConfirmedMatrixCellResponse(
                **{
                    field: getattr(cell, field)
                    for field in ConfirmedMatrixCellResponse.model_fields
                }
            )
            for cell in snapshot.cells
        ],
        duration_authorities=[
            MatrixDurationAuthorityResponse(
                duration_authority_id=item.confirmed_duration_authority_id,
                group_id=item.confirmed_group_id,
                row_id=item.confirmed_row_id,
                **_duration_fields(item),
            )
            for item in snapshot.duration_authorities
        ],
    )


def _duration_fields(item: object) -> dict[str, object]:
    names = (
        "step_sequence",
        "step_suffix_note",
        "duration_value",
        "duration_unit",
        "normalized_hours",
        "source_kind",
        "source_field",
        "source_import_id",
        "source_fingerprint",
        "lineage_fingerprint",
        "authority_revision",
        "status",
        "diagnostic_code",
        "diagnostic_message",
    )
    return {name: getattr(item, name) for name in names}
