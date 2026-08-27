"""Generate Test Status workbooks from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.test_status_workbook_projection import (
    TestStatusProjection,
    build_confirmed_test_status_projection,
)
from backend.domain import ConfirmedMatrixSnapshot


class ConfirmedMatrixTestStatusWorkbookGenerationError(ValueError):
    """Raised when confirmed Matrix data cannot generate Test Status."""


class ConfirmedMatrixTestStatusWorkbookGenerationNotFoundError(LookupError):
    """Raised when active confirmed Matrix authority is missing."""


class ConfirmedMatrixAuthorityStore(Protocol):
    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed Matrix snapshot."""


class TestStatusWorkbookWriter(Protocol):
    def write(self, *, output_path: Path, projection: TestStatusProjection) -> Path:
        """Write one Test Status workbook."""


@dataclass(frozen=True, slots=True)
class GenerateConfirmedMatrixTestStatusWorkbookCommand:
    project_id: str
    output_dir: Path
    target_name: str


class ConfirmedMatrixTestStatusWorkbookGenerationService:
    """Generate the authority-derived Test Status workbook in controlled staging."""

    def __init__(
        self,
        *,
        confirmed_store: ConfirmedMatrixAuthorityStore,
        writer: TestStatusWorkbookWriter,
    ) -> None:
        self._confirmed = confirmed_store
        self._writer = writer

    def generate(self, command: GenerateConfirmedMatrixTestStatusWorkbookCommand) -> Path:
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixTestStatusWorkbookGenerationNotFoundError(
                "Active confirmed matrix not found."
            )
        command.output_dir.mkdir(parents=True, exist_ok=True)
        try:
            projection = build_confirmed_test_status_projection(snapshot)
            return self._writer.write(
                output_path=command.output_dir / command.target_name,
                projection=projection,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            raise ConfirmedMatrixTestStatusWorkbookGenerationError(str(exc)) from exc
