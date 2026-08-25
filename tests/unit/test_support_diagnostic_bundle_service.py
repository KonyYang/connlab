import io
import json
import zipfile
from pathlib import Path

from backend.application.support_diagnostic_bundle_service import (
    SupportDiagnosticBundleService,
)


def test_bundle_contains_only_redacted_logs_and_safe_release_metadata(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "connlab.log").write_text(
        "failure at C:\\Users\\White\\Project Folder\\without-extension\n"
        "password=hunter2\n"
        '\"token\": \"json-secret\"\n',
        encoding="utf-8",
    )
    (logs_dir / "connlab.log.1").write_text("previous run\n", encoding="utf-8")
    (logs_dir / "database.sqlite3").write_text("not allowed", encoding="utf-8")
    (logs_dir / "connlab.log.private").write_text("not allowed", encoding="utf-8")
    release_manifest = tmp_path / "release_manifest.json"
    release_manifest.write_text(
        json.dumps(
            {
                "release_name": "ConnLab_Web_20260825_v0.1.0",
                "version": "0.1.0",
                "git_commit": "abc123",
                "built_at_utc": "2026-08-25T12:00:00Z",
                "unexpected_secret": "must not leak",
            }
        ),
        encoding="utf-8",
    )

    bundle = SupportDiagnosticBundleService(
        logs_dir=logs_dir,
        release_manifest_path=release_manifest,
    ).build_bundle()

    with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
        assert sorted(archive.namelist()) == [
            "logs/connlab.log",
            "logs/connlab.log.1",
            "manifest.json",
        ]
        exported_log = archive.read("logs/connlab.log").decode("utf-8")
        exported_manifest = json.loads(archive.read("manifest.json"))

    assert "C:\\Users\\White" not in exported_log
    assert "Project Folder" not in exported_log
    assert "hunter2" not in exported_log
    assert "json-secret" not in exported_log
    assert "<LOCAL_PATH>" in exported_log
    assert "password=<REDACTED>" in exported_log
    assert exported_manifest["release"]["git_commit"] == "abc123"
    assert "unexpected_secret" not in exported_manifest["release"]
    assert bundle.filename.startswith("ConnLab_Diagnostics_")
