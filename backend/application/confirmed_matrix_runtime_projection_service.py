"""Build runtime projection snapshots from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.application.runtime_projection_read_only_service import (
    RuntimeProjectionReadOnlyService,
)
from backend.domain import ConfirmedMatrixSnapshot
from backend.modules.runtime_projection.models import MatrixRowTechnicalContext
from backend.modules.runtime_projection.snapshot_adapter import (
    RuntimeProjectionSnapshot,
    SnapshotBuildInput,
    SnapshotMatrixRowInput,
)


class ConfirmedMatrixRuntimeProjectionError(ValueError):
    """Raised when active confirmed Matrix cannot be mapped into projection input."""


class ConfirmedMatrixRuntimeProjectionNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority read operations required by this consumer."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""


@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixRuntimeProjectionCommand:
    """Input payload for confirmed-authority runtime projection snapshot building."""

    project_id: str
    selected_token_reference: str | None = None


class ConfirmedMatrixRuntimeProjectionService:
    """Adapt active confirmed Matrix authority into existing projection snapshot input."""

    def __init__(
        self,
        *,
        confirmed_store: ConfirmedMatrixAuthorityStore,
        runtime_projection_service: RuntimeProjectionReadOnlyService,
    ) -> None:
        self._confirmed = confirmed_store
        self._runtime_projection = runtime_projection_service

    def build_snapshot(
        self,
        command: BuildConfirmedMatrixRuntimeProjectionCommand,
    ) -> RuntimeProjectionSnapshot:
        """Return one read-only runtime projection snapshot from active confirmed authority."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixRuntimeProjectionNotFoundError(
                "Active confirmed matrix not found."
            )
        build_input = _build_input_from_confirmed(
            confirmed=snapshot,
            selected_token_reference=command.selected_token_reference,
        )
        return self._runtime_projection.build_snapshot(build_input)


def _build_input_from_confirmed(
    *,
    confirmed: ConfirmedMatrixSnapshot,
    selected_token_reference: str | None,
) -> SnapshotBuildInput:
    matrix_reference = (
        f"{confirmed.version.confirmed_matrix_id}:r{confirmed.version.confirmed_revision}"
    )
    groups_by_id = {group.confirmed_group_id: group for group in confirmed.groups}
    rows_by_id = {row.confirmed_row_id: row for row in confirmed.rows}
    row_inputs: list[SnapshotMatrixRowInput] = []
    for cell in confirmed.cells:
        cell_value = cell.cell_value.strip()
        if not cell_value:
            continue
        group = groups_by_id.get(cell.confirmed_group_id)
        row = rows_by_id.get(cell.confirmed_row_id)
        if group is None or row is None:
            raise ConfirmedMatrixRuntimeProjectionError(
                "Confirmed matrix cell lineage is invalid."
            )
        group_identity = group.group_key.strip()
        group_label = group.group_label.strip()
        test_item_label = row.test_item.strip()
        if not group_identity or not group_label or not test_item_label:
            raise ConfirmedMatrixRuntimeProjectionError(
                "Confirmed matrix group/row fields must be nonblank."
            )
        row_inputs.append(
            SnapshotMatrixRowInput(
                group_identity=group_identity,
                group_label=group_label,
                row_context=MatrixRowTechnicalContext(
                    test_item_label=test_item_label,
                    section=(row.source_section or "").strip(),
                    method=(row.method or "").strip(),
                    condition=(row.condition or "").strip(),
                    requirement=(row.requirement or "").strip(),
                ),
                raw_step_token_value=cell_value,
            )
        )
    return SnapshotBuildInput(
        project_reference=confirmed.version.project_id,
        matrix_reference=matrix_reference,
        rows=tuple(row_inputs),
        selected_token_reference=selected_token_reference,
    )
