from dataclasses import replace
from pathlib import Path

import pytest

from backend.application.current_report_update_service import CurrentReportArtifact
from backend.application.internal_report_generation_service import (
    GenerateInternalReportCommand,
    InternalReportGenerationError,
    InternalReportGenerationService,
    InternalReportGenerationSnapshot,
)
from backend.application.test_report_draft_service import GenerateTestReportDraftCommand, TestReportDraftService
from backend.infrastructure.files.report_publication_gateway import ReportPublicationGateway
from tests.unit.test_test_report_draft_service import _BasicInformationReader, _PreviewService, _Writer, _basic_information, _preview, _template


def test_regenerates_from_template_only_after_confirmation_and_blocks_replay(tmp_path: Path):
    current = tmp_path / "DL-2026-05-011 Old Report_Rev_A.docx"
    current.write_bytes(b"manual results and photos")
    files = ReportPublicationGateway()
    writer = _Writer()
    draft = TestReportDraftService(preview_service=_PreviewService(_preview()), basic_information_reader=_BasicInformationReader(_basic_information()), writer=writer)
    prepared = draft.prepare(GenerateTestReportDraftCommand("P1", _template(tmp_path), tmp_path, "official_current"))
    snapshot = InternalReportGenerationSnapshot(
        prepared=prepared,
        current_report=CurrentReportArtifact("ready", "official", current.name, current, files.fingerprint(current), tmp_path / "History" / "Report"),
        target_dir=tmp_path,
        history_root=tmp_path / "History" / "Report",
        mode="official",
        authority_signature="basic-1/matrix-1/workspace-1/report-revision-1",
    )
    state = [snapshot]
    saved = []

    def persist(**kwargs):
        saved.append(kwargs)
        path = kwargs["path"]
        state[0] = replace(snapshot, authority_signature="report-revision-2", current_report=replace(snapshot.current_report, file_path=path, file_name=path.name, file_sha256=files.fingerprint(path)))

    service = InternalReportGenerationService(read_snapshot=lambda project: state[0], drafts=draft, files=files, persist=persist, staging_root=tmp_path / "stage")
    preview = service.preview("P1")
    assert preview.requires_confirmation
    assert current.read_bytes() == b"manual results and photos"
    assert not writer.calls
    with pytest.raises(InternalReportGenerationError, match="confirm"):
        service.generate(GenerateInternalReportCommand("P1", preview.preview_token, False))
    assert not writer.calls
    result = service.generate(GenerateInternalReportCommand("P1", preview.preview_token, True))
    assert result.archive_path.read_bytes() == b"manual results and photos"
    assert not current.exists()
    assert result.file_name == prepared.file_name
    assert writer.calls[0]["template_path"] == prepared.template_path
    assert saved[0]["confirmed_matrix_id"] == "cmv-1"
    with pytest.raises(InternalReportGenerationError, match="changed"):
        service.generate(GenerateInternalReportCommand("P1", preview.preview_token, True))
    assert not list((tmp_path / "stage").iterdir())
