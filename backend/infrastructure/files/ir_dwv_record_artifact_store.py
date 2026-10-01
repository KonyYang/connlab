"""Contained local artifact storage for generated IR/DWV record workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from uuid import uuid4

_ARTIFACT_ID = re.compile(r"^[a-f0-9]{32}$")


@dataclass(frozen=True, slots=True)
class IrDwvRecordArtifact:
    artifact_id: str
    file_name: str
    output_path: Path


class IrDwvRecordArtifactStore:
    """Create and resolve contained macro-free IR/DWV draft workbooks."""

    def __init__(self, output_root: Path) -> None:
        self._output_root = Path(output_root)

    def prepare_draft(
        self,
        *,
        project_id: str,
        record_type: str = "ir_dwv",
    ) -> IrDwvRecordArtifact:
        if record_type != "ir_dwv":
            raise ValueError("Record type must be ir_dwv.")
        artifact_id = uuid4().hex
        project_dir = self._project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        display_project = _safe_file_segment(project_id)
        file_name = (
            f"{display_project}_ir_dwv_record_Preview_Unconfirmed_Matrix_draft_"
            f"{artifact_id}.xlsx"
        )
        return IrDwvRecordArtifact(
            artifact_id=artifact_id,
            file_name=file_name,
            output_path=project_dir / file_name,
        )

    def resolve(
        self,
        *,
        project_id: str,
        artifact_id: str,
    ) -> IrDwvRecordArtifact:
        if not _ARTIFACT_ID.fullmatch(artifact_id):
            raise ValueError("Invalid generated workbook identifier.")
        project_dir = self._project_dir(project_id)
        matches = (
            tuple(project_dir.glob(f"*_{artifact_id}.xlsx"))
            if project_dir.is_dir()
            else ()
        )
        if len(matches) != 1:
            raise FileNotFoundError("Generated IR/DWV workbook not found.")
        path = matches[0].resolve()
        root = project_dir.resolve()
        if path.parent != root or path.suffix.lower() != ".xlsx":
            raise ValueError("Generated workbook path is invalid.")
        return IrDwvRecordArtifact(
            artifact_id=artifact_id,
            file_name=path.name,
            output_path=path,
        )

    def _project_dir(self, project_id: str) -> Path:
        return self._output_root / _safe_file_segment(project_id)


def _safe_file_segment(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    if not normalized:
        raise ValueError("Project identity is required for generated workbook storage.")
    return normalized[:96]
