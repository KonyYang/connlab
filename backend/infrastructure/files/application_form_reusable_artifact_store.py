"""Reusable Application Form write-back artifact storage."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from backend.application.project_application_form_write_back_support import (
    ReusableApplicationFormArtifactStore,
)
from backend.application.project_folder_required_forms_service import compute_sha256
from backend.application.project_output_record_service import ProjectOutputRecordService
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus


class FileReusableApplicationFormArtifactStore(ReusableApplicationFormArtifactStore):
    """Find and cache safe current Application Form write-back artifacts."""

    def __init__(self, output_service: ProjectOutputRecordService, cache_dir: Path) -> None:
        self._output_service = output_service
        self._cache_dir = cache_dir

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return a reusable filled Application Form artifact when safe."""
        summary = self._output_service.get_status_summary(project_id)
        for item in summary.items:
            if item.output_kind != ProjectOutputKind.SECTION2_WRITE_BACK:
                continue
            if item.status != ProjectOutputStatus.CURRENT:
                return None
            if item.source != ProjectOutputSource.SYSTEM_GENERATED:
                return None
            if item.source_context_signature != source_context_signature:
                return None
            if not item.output_sha256:
                return None
            output_path = Path(item.output_path) if item.output_path else None
            if (
                output_path
                and output_path == final_target_path
                and self._validated_path(output_path, item.output_sha256) is not None
            ):
                return None
            reusable = self._validated_path(output_path, item.output_sha256)
            if reusable is not None:
                return reusable
            cached = self._cache_path(project_id, source_context_signature)
            return self._validated_path(cached, item.output_sha256)
        return None

    def save_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        source_path: Path,
        source_sha256: str,
    ) -> None:
        """Cache a verified filled Application Form artifact."""
        if not source_path.is_file() or source_path.suffix.lower() != ".docx":
            return
        if compute_sha256(source_path) != source_sha256:
            return
        target = self._cache_path(project_id, source_context_signature)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)

    def _validated_path(self, path: Path | None, expected_sha256: str) -> Path | None:
        if path is None or path.suffix.lower() != ".docx" or not path.is_file():
            return None
        return path if compute_sha256(path) == expected_sha256 else None

    def _cache_path(self, project_id: str, source_context_signature: str) -> Path:
        token = hashlib.sha256(source_context_signature.encode("utf-8")).hexdigest()
        return self._cache_dir / project_id / f"{token}.docx"
