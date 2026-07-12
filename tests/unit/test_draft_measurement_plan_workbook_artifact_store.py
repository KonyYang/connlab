from pathlib import Path
import os

from backend.infrastructure.files.draft_measurement_plan_workbook_artifact_store import (
    DraftMeasurementPlanWorkbookArtifactStore,
)


def test_publish_resolve_latest_and_retention_preserve_unknown_files(tmp_path: Path) -> None:
    store = DraftMeasurementPlanWorkbookArtifactStore(tmp_path, retention_count=2)
    for index in range(3):
        artifact = store.prepare(
            project_id="P-1", output_label="DRAFT", matrix_revision=1, plan_sequence=index + 1, preview_fingerprint=f"{index:064x}"
        )
        artifact.temporary_path.write_bytes(b"xlsx")
        store.publish(artifact, metadata={"project_id": "P-1", "index": index})
    unknown = tmp_path / "P-1" / "operator-notes.txt"
    unknown.write_text("keep", encoding="utf-8")

    latest = store.latest(project_id="P-1")

    assert latest is not None
    assert latest.metadata["index"] == 2
    assert store.resolve(project_id="P-1", artifact_id=latest.artifact_id).output_path.exists()
    assert unknown.exists()
    assert len(list((tmp_path / "P-1").glob("*.xlsx"))) == 2


def test_resolve_rejects_path_traversal(tmp_path: Path) -> None:
    store = DraftMeasurementPlanWorkbookArtifactStore(tmp_path)

    try:
        store.resolve(project_id="P-1", artifact_id="../outside")
    except ValueError as error:
        assert "identifier" in str(error).lower()
    else:
        raise AssertionError("Expected strict artifact id rejection")


def test_cleanup_preserves_forged_same_stem_pair_and_cleanup_failure_keeps_latest(tmp_path: Path, monkeypatch) -> None:
    store = DraftMeasurementPlanWorkbookArtifactStore(tmp_path, retention_count=1)
    project_dir = tmp_path / "P-1"
    project_dir.mkdir()
    forged_workbook = project_dir / "operator.xlsx"
    forged_manifest = project_dir / "operator.json"
    forged_workbook.write_bytes(b"operator")
    forged_manifest.write_text('{"project_id":"P-1"}', encoding="utf-8")
    os.utime(forged_workbook, (1, 1))
    os.utime(forged_manifest, (1, 1))
    for index in range(2):
        artifact = store.prepare(project_id="P-1", output_label="DRAFT", matrix_revision=1, plan_sequence=index + 1, preview_fingerprint=f"{index:064x}")
        artifact.temporary_path.write_bytes(b"xlsx")
        store.publish(artifact, metadata={"project_id": "P-1"})

    assert forged_workbook.exists()
    assert forged_manifest.exists()

    monkeypatch.setattr(store, "_cleanup", lambda _: (_ for _ in ()).throw(OSError("locked")))
    newest = store.prepare(project_id="P-1", output_label="DRAFT", matrix_revision=1, plan_sequence=3, preview_fingerprint="f" * 64)
    newest.temporary_path.write_bytes(b"xlsx")
    metadata = store.publish(newest, metadata={"project_id": "P-1"})

    assert metadata.output_path.exists()
    assert metadata.cleanup_warning == "Older draft artifacts could not be cleaned up."
    assert store.latest(project_id="P-1").artifact_id == newest.artifact_id
