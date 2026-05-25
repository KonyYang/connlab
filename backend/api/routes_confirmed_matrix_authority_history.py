"""Confirmed-Matrix authority history read-only API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.dependencies import get_confirmed_matrix_authority_history_service
from backend.application.confirmed_matrix_authority_history_service import (
    BuildConfirmedMatrixAuthorityHistoryCommand,
    ConfirmedMatrixAuthorityHistory,
    ConfirmedMatrixAuthorityHistoryEntry,
    ConfirmedMatrixAuthorityHistoryService,
)


router = APIRouter(tags=["confirmed-matrix-authority-history"])


class ConfirmedMatrixAuthorityHistoryEntryResponse(BaseModel):
    confirmed_matrix_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: str
    confirmed_by: str
    confirmed_at: str
    superseded_at: str | None
    superseded_reason: str | None
    source_snapshot_changed: bool
    group_change_count: int
    step_change_count: int
    token_change_count: int
    record_regeneration_recommended: bool
    change_summary: str


class ConfirmedMatrixAuthorityHistoryResponse(BaseModel):
    project_id: str
    entries: list[ConfirmedMatrixAuthorityHistoryEntryResponse]


@router.get(
    "/api/projects/{project_id}/confirmed-matrix/authority-history",
    response_model=ConfirmedMatrixAuthorityHistoryResponse,
)
def get_confirmed_matrix_authority_history(
    project_id: str,
    service: ConfirmedMatrixAuthorityHistoryService = Depends(
        get_confirmed_matrix_authority_history_service
    ),
) -> ConfirmedMatrixAuthorityHistoryResponse:
    history = service.build_history(
        BuildConfirmedMatrixAuthorityHistoryCommand(project_id=project_id)
    )
    return _to_response(history)


def _to_response(
    history: ConfirmedMatrixAuthorityHistory,
) -> ConfirmedMatrixAuthorityHistoryResponse:
    return ConfirmedMatrixAuthorityHistoryResponse(
        project_id=history.project_id,
        entries=[_to_entry_response(entry) for entry in history.entries],
    )


def _to_entry_response(
    entry: ConfirmedMatrixAuthorityHistoryEntry,
) -> ConfirmedMatrixAuthorityHistoryEntryResponse:
    return ConfirmedMatrixAuthorityHistoryEntryResponse(
        confirmed_matrix_id=entry.confirmed_matrix_id,
        confirmed_revision=entry.confirmed_revision,
        is_active_authority=entry.is_active_authority,
        status=entry.status,
        confirmed_by=entry.confirmed_by,
        confirmed_at=entry.confirmed_at,
        superseded_at=entry.superseded_at,
        superseded_reason=entry.superseded_reason,
        source_snapshot_changed=entry.source_snapshot_changed,
        group_change_count=entry.group_change_count,
        step_change_count=entry.step_change_count,
        token_change_count=entry.token_change_count,
        record_regeneration_recommended=entry.record_regeneration_recommended,
        change_summary=entry.change_summary,
    )
