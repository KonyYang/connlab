from __future__ import annotations

from pathlib import Path

from backend.application.project_output_record_service import ProjectOutputStatusItem
from backend.application.project_application_form_write_back_support import sha256_file
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.infrastructure.files.application_form_reusable_artifact_store import (
    FileReusableApplicationFormArtifactStore,
)


def test_reusable_application_form_store_uses_cache_when_target_path_was_rebuilt(
    tmp_path: Path,
) -> None:
    target = tmp_path / "project" / "Submitted Material" / "request.docx"
    cache_dir = tmp_path / "cache"
    context = "application-form:F1@source:abc|basic:1@hash|application-form-output:lab_section_v1"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"fresh source copy")
    cached = cache_dir / "P1" / _cache_name(context)
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"filled application form")
    output_service = _OutputService(
        ProjectOutputStatusItem(
            output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
            status=ProjectOutputStatus.CURRENT,
            output_path=str(target),
            source=ProjectOutputSource.SYSTEM_GENERATED,
            draft_id=None,
            draft_version=None,
            reason="current",
            updated_at="2026-06-25T00:00:00+00:00",
            output_sha256=sha256_file(cached),
            output_size_bytes=cached.stat().st_size,
            source_context_signature=context,
        )
    )
    store = FileReusableApplicationFormArtifactStore(output_service, cache_dir)

    reusable = store.find_current_artifact(
        project_id="P1",
        source_context_signature=context,
        final_target_path=target,
    )

    assert reusable == cached


def _cache_name(context: str) -> str:
    import hashlib

    return f"{hashlib.sha256(context.encode('utf-8')).hexdigest()}.docx"


class _OutputService:
    def __init__(self, item: ProjectOutputStatusItem) -> None:
        self._item = item

    def get_status_summary(self, project_id: str):
        return type("_Summary", (), {"items": (self._item,)})()
