"""Contained manifest-backed storage for editable-plan draft workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from uuid import uuid4

_ARTIFACT_ID = re.compile(r"^[a-f0-9]{32}$")
_OWNED_WORKBOOK = re.compile(
    r"^.+_contact_measurement_(?:DRAFT|NEEDS_REVIEW)_m[0-9]+_p[0-9]+_[a-f0-9]{12}_([a-f0-9]{32})\.xlsx$"
)


@dataclass(frozen=True, slots=True)
class DraftWorkbookArtifact:
    artifact_id: str
    file_name: str
    output_path: Path
    temporary_path: Path
    manifest_path: Path


@dataclass(frozen=True, slots=True)
class DraftWorkbookArtifactMetadata:
    artifact_id: str
    file_name: str
    output_path: Path
    metadata: dict[str, object]
    cleanup_warning: str | None = None


class DraftMeasurementPlanWorkbookArtifactStore:
    """Publish and resolve only app-owned workbook/manifest pairs."""

    def __init__(self, output_root: Path, retention_count: int = 10) -> None:
        self._output_root = Path(output_root)
        self._retention_count = retention_count

    def prepare(self, *, project_id: str, output_label: str, matrix_revision: int, plan_sequence: int, preview_fingerprint: str) -> DraftWorkbookArtifact:
        artifact_id = uuid4().hex
        project_dir = self._project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        safe_project = _safe_segment(project_id)
        label = "NEEDS_REVIEW" if output_label == "NEEDS REVIEW" else "DRAFT"
        file_name = f"{safe_project}_contact_measurement_{label}_m{matrix_revision}_p{plan_sequence}_{preview_fingerprint[:12]}_{artifact_id}.xlsx"
        output_path = project_dir / file_name
        temporary_path = project_dir / f".{file_name}.{artifact_id}.tmp.xlsx"
        return DraftWorkbookArtifact(artifact_id, file_name, output_path, temporary_path, output_path.with_suffix(".json"))

    def publish(self, artifact: DraftWorkbookArtifact, *, metadata: dict[str, object]) -> DraftWorkbookArtifactMetadata:
        if not artifact.temporary_path.is_file():
            raise FileNotFoundError("Draft workbook temporary output was not written.")
        artifact.temporary_path.replace(artifact.output_path)
        payload = {**metadata, "artifact_id": artifact.artifact_id, "file_name": artifact.file_name, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "manifest_version": 1}
        temporary_manifest = artifact.manifest_path.with_suffix(".json.tmp")
        temporary_manifest.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        temporary_manifest.replace(artifact.manifest_path)
        latest = artifact.output_path.parent / "latest.json"
        latest_tmp = latest.with_suffix(".json.tmp")
        latest_tmp.write_text(json.dumps({"artifact_id": artifact.artifact_id, "manifest_version": 1}), encoding="utf-8")
        latest_tmp.replace(latest)
        cleanup_warning = None
        try:
            self._cleanup(artifact.output_path.parent)
        except OSError:
            # Publication is complete before retention maintenance. A locked old pair
            # must not invalidate the new artifact or its latest pointer.
            cleanup_warning = "Older draft artifacts could not be cleaned up."
        return DraftWorkbookArtifactMetadata(
            artifact.artifact_id,
            artifact.file_name,
            artifact.output_path,
            payload,
            cleanup_warning,
        )

    def latest(self, *, project_id: str) -> DraftWorkbookArtifactMetadata | None:
        pointer = self._project_dir(project_id) / "latest.json"
        if not pointer.is_file():
            return None
        try:
            return self.resolve(project_id=project_id, artifact_id=str(json.loads(pointer.read_text(encoding="utf-8"))["artifact_id"]))
        except (KeyError, ValueError, FileNotFoundError, json.JSONDecodeError):
            return None

    def resolve(self, *, project_id: str, artifact_id: str) -> DraftWorkbookArtifactMetadata:
        if not _ARTIFACT_ID.fullmatch(artifact_id):
            raise ValueError("Invalid generated workbook identifier.")
        project_dir = self._project_dir(project_id)
        matches = tuple(project_dir.glob(f"*_{artifact_id}.xlsx")) if project_dir.is_dir() else ()
        if len(matches) != 1:
            raise FileNotFoundError("Draft workbook artifact was not found.")
        output_path = matches[0].resolve()
        if output_path.parent != project_dir.resolve():
            raise ValueError("Generated workbook path is invalid.")
        manifest_path = output_path.with_suffix(".json")
        metadata = self._validated_pair(project_dir, manifest_path, project_id)
        if metadata is None:
            raise FileNotFoundError("Draft workbook manifest was not found.")
        return DraftWorkbookArtifactMetadata(artifact_id, output_path.name, output_path, metadata)

    def discard_incomplete(self, artifact: DraftWorkbookArtifact) -> None:
        for path in (artifact.temporary_path, artifact.output_path, artifact.manifest_path):
            if path.exists() and path.parent == self._project_dir_from_path(artifact.output_path):
                path.unlink()

    def _cleanup(self, project_dir: Path) -> None:
        pairs = []
        for manifest in project_dir.glob("*.json"):
            if manifest.name == "latest.json":
                continue
            metadata = self._validated_pair(project_dir, manifest, None)
            if metadata is not None:
                workbook = manifest.with_suffix(".xlsx")
                pairs.append((manifest.stat().st_mtime, workbook, manifest))
        for _, workbook, manifest in sorted(pairs, reverse=True)[self._retention_count:]:
            workbook.unlink(missing_ok=True)
            manifest.unlink(missing_ok=True)

    def _project_dir(self, project_id: str) -> Path:
        return self._output_root / _safe_segment(project_id)

    @staticmethod
    def _validated_pair(
        project_dir: Path, manifest_path: Path, expected_project_id: str | None
    ) -> dict[str, object] | None:
        """Return metadata only for an exact owned workbook/manifest pair."""
        if not manifest_path.is_file() or manifest_path.parent.resolve() != project_dir.resolve():
            return None
        workbook = manifest_path.with_suffix(".xlsx")
        match = _OWNED_WORKBOOK.fullmatch(workbook.name)
        if match is None or not workbook.is_file() or workbook.parent.resolve() != project_dir.resolve():
            return None
        try:
            metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        project_id = metadata.get("project_id")
        if not isinstance(project_id, str) or (expected_project_id and project_id != expected_project_id):
            return None
        if metadata.get("artifact_id") != match.group(1) or metadata.get("file_name") != workbook.name:
            return None
        if metadata.get("manifest_version") != 1:
            return None
        return metadata

    @staticmethod
    def _project_dir_from_path(path: Path) -> Path:
        return path.parent


def _safe_segment(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    if not normalized:
        raise ValueError("Project identity is required for generated workbook storage.")
    return normalized[:96]
