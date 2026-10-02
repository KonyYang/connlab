from __future__ import annotations

from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace

import pytest

from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    GenerateLlcrCrRecordWorkbookCommand,
    LlcrCrRecordWorkbookGenerationError,
    LlcrCrRecordWorkbookGenerationService,
    MatrixEditorLlcrCrRecordPublicationService,
    PreviewMatrixEditorLlcrCrPublicationCommand,
    PublishMatrixEditorLlcrCrPublicationCommand,
)
from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    GenerateMatrixEditorLlcrCrRecordCommand,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    MatrixEditorLlcrCrRecordGroupInput, MatrixEditorLlcrCrRecordRowInput,
)
from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
)
from backend.domain.matrix_contact_measurement_models import MatrixPointCategory, MatrixPointProfile
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)
from backend.infrastructure.files.generation_journal import GenerationJournal
import backend.infrastructure.files.project_folder_required_forms_gateway as contact_file_gateway


def test_generation_writes_managed_xlsx_only_after_matching_preview_fingerprint(tmp_path: Path) -> None:
    service = _service(tmp_path)
    preview = service._preview_service.preview("project-1")

    result = service.generate(
        GenerateLlcrCrRecordWorkbookCommand(
            project_id="project-1", preview_fingerprint=preview.preview_fingerprint or ""
        )
    )

    assert result.file_name.endswith(".xlsx")
    assert result.output_path.is_file()
    assert result.output_path.parent == tmp_path / "generated_llcr_cr_record_files" / "project-1"


def test_generation_rejects_stale_fingerprint_without_writing(tmp_path: Path) -> None:
    service = _service(tmp_path)

    with pytest.raises(LlcrCrRecordWorkbookGenerationError, match="changed"):
        service.generate(
            GenerateLlcrCrRecordWorkbookCommand(
                project_id="project-1", preview_fingerprint="stale"
            )
        )

    assert not list(tmp_path.rglob("*.xlsx"))


def test_publication_preview_keeps_changed_point_ids_in_download_mode(tmp_path: Path) -> None:
    profile = MatrixPointProfile((MatrixPointCategory("SIG", "1-2", True),))
    snapshot = _snapshot()
    snapshot = replace(snapshot,
        version=replace(snapshot.version, point_profile=profile),
        cells=(ConfirmedMatrixCell(
            confirmed_cell_id="cell-1", confirmed_matrix_id="cmv-1",
            confirmed_row_id="row-1", confirmed_group_id="group-1",
            draft_row_id="draft-row-1", draft_group_id="draft-group-1",
            cell_value="2",
        ),),
    )
    workspace = SimpleNamespace(
        project_id="project-1", dl_number="DL-001",
        local_workspace_path=tmp_path / "workspace",
        official_folder_path=tmp_path / "workspace" / "DL-001",
    )
    (workspace.official_folder_path / "Test results").mkdir(parents=True)
    service = MatrixEditorLlcrCrRecordPublicationService(
        confirmed_store=_ConfirmedStore(snapshot),
        preview_service=LlcrCrRecordWorkbookPreviewService(confirmed_store=_ConfirmedStore(snapshot)),
        workspace_store=SimpleNamespace(get_by_project=lambda _id: workspace),
        workspace_verifier=lambda _record: True,
    )
    draft = GenerateMatrixEditorLlcrCrRecordCommand(
        project_id="project-1", record_type="llcr",
        groups=(MatrixEditorLlcrCrRecordGroupInput("G1", "Group 1", "1", draft_group_id="draft-group-1"),),
        rows=(MatrixEditorLlcrCrRecordRowInput("LLCR", group_values={"G1": "2"}, draft_row_id="draft-row-1"),),
        point_profile=profile,
    )

    confirmed = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    changed = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(
        replace(draft, point_profile=MatrixPointProfile((MatrixPointCategory("SIG", "1-3", True),))),
    ))

    assert (confirmed.mode, confirmed.authority_status, confirmed.status) == ("official", "confirmed", "ready")
    assert confirmed.target_path == workspace.official_folder_path / "Test results" / "DL-001 LLCR Record.xlsx"
    assert (changed.mode, changed.authority_status, changed.status) == ("download", "unconfirmed", "ready")
    assert changed.target_path is None


def test_publication_preview_blocks_unrenderable_draft_before_download_confirmation(tmp_path: Path) -> None:
    service, draft, _target = _publication_fixture(tmp_path)

    missing_points = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(
        replace(draft, point_profile=None),
    ))
    missing_steps = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(
        replace(draft, rows=(replace(draft.rows[0], test_item="Examination"),)),
    ))

    assert (missing_points.mode, missing_points.status) == ("download", "blocked")
    assert missing_points.blockers
    assert (missing_steps.mode, missing_steps.status) == ("download", "blocked")
    assert missing_steps.blockers
    with pytest.raises(ValueError, match="changed|not ready"):
        service.validate_download(
            PreviewMatrixEditorLlcrCrPublicationCommand(replace(draft, point_profile=None)),
            missing_points.preview_token,
        )


def test_publication_archives_existing_form_and_rejects_stale_preview(tmp_path: Path) -> None:
    profile = MatrixPointProfile((MatrixPointCategory("SIG", "1-2", True),))
    snapshot = replace(_snapshot(), version=replace(_snapshot().version, point_profile=profile),
                       cells=(ConfirmedMatrixCell(
                           confirmed_cell_id="cell-1", confirmed_matrix_id="cmv-1",
                           confirmed_row_id="row-1", confirmed_group_id="group-1",
                           draft_row_id="draft-row-1", draft_group_id="draft-group-1", cell_value="2",
                       ),))
    workspace = SimpleNamespace(
        project_id="project-1", dl_number="DL-001", local_workspace_path=tmp_path / "workspace",
        official_folder_path=tmp_path / "workspace" / "DL-001",
    )
    target_dir = workspace.official_folder_path / "Test results"
    target_dir.mkdir(parents=True)
    target = target_dir / "DL-001 LLCR Record.xlsx"
    target.write_bytes(b"measured values")
    store = _ConfirmedStore(snapshot)
    outputs = _OutputService()
    service = MatrixEditorLlcrCrRecordPublicationService(
        confirmed_store=store,
        preview_service=LlcrCrRecordWorkbookPreviewService(confirmed_store=store),
        workspace_store=SimpleNamespace(get_by_project=lambda _id: workspace),
        workspace_verifier=lambda _record: True,
        journal=GenerationJournal(tmp_path / "publication-journal"),
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        output_service=outputs, staging_root=tmp_path / "source-stage", commit=lambda: None,
    )
    draft = GenerateMatrixEditorLlcrCrRecordCommand(
        project_id="project-1", record_type="llcr",
        groups=(MatrixEditorLlcrCrRecordGroupInput("G1", "Group 1", "1", draft_group_id="draft-group-1"),),
        rows=(MatrixEditorLlcrCrRecordRowInput("LLCR", group_values={"G1": "2"}, draft_row_id="draft-row-1"),),
        point_profile=profile,
    )
    request = PreviewMatrixEditorLlcrCrPublicationCommand(draft)
    preview = service.preview(request)
    assert preview.status == "conflict"
    with pytest.raises(ValueError, match="archive"):
        service.publish(PublishMatrixEditorLlcrCrPublicationCommand(draft, preview.preview_token, "none"))
    target.write_bytes(b"operator changed measurement")
    with pytest.raises(ValueError, match="changed"):
        service.publish(PublishMatrixEditorLlcrCrPublicationCommand(draft, preview.preview_token, "archive"))
    current = service.preview(request)
    result = service.publish(PublishMatrixEditorLlcrCrPublicationCommand(draft, current.preview_token, "archive"))
    assert target.is_file() and target.read_bytes() != b"operator changed measurement"
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"operator changed measurement"
    assert len(outputs.records) == 1


def test_publication_retries_pre_effect_writer_crash_only_with_unchanged_preview(tmp_path: Path) -> None:
    service, draft, target = _publication_fixture(tmp_path)
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    real_writer = service._writer

    class _FailOnce:
        def __init__(self) -> None:
            self.failed = False

        def write(self, *, output_path, projection):
            if not self.failed:
                self.failed = True
                raise RuntimeError("simulated writer crash")
            return real_writer.write(output_path=output_path, projection=projection)

    service._writer = _FailOnce()
    command = PublishMatrixEditorLlcrCrPublicationCommand(draft, preview.preview_token, "archive")
    with pytest.raises(RuntimeError, match="simulated writer crash"):
        service.publish(command)
    assert target.read_bytes() == b"measured values"
    result = service.publish(command)
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"measured values"


def test_publication_recovers_after_archive_before_new_form(tmp_path: Path, monkeypatch) -> None:
    service, draft, target = _publication_fixture(tmp_path)
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    command = PublishMatrixEditorLlcrCrPublicationCommand(draft, preview.preview_token, "archive")
    real_link = contact_file_gateway.os.link
    calls = 0

    def interrupt_once(source, destination):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("simulated crash after archive")
        return real_link(source, destination)

    monkeypatch.setattr(contact_file_gateway.os, "link", interrupt_once)
    with pytest.raises(RuntimeError, match="simulated crash"):
        service.publish(command)
    assert not target.exists()
    result = service.publish(command)
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"measured values"
    assert target.is_file()
    assert len(service._outputs.records) == 1


def test_publication_never_replaces_colliding_history_file(tmp_path: Path) -> None:
    service, draft, target = _publication_fixture(tmp_path)
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    journal = service._journal
    create = journal.create
    archive_holder = {}

    def create_with_history_collision(project_id, strategy, context):
        state = create(project_id, strategy, context)
        archive = (target.parents[2] / "History" / "Test results"
                   / f"{target.stem} {state['operation_id']}{target.suffix}")
        archive.parent.mkdir(parents=True)
        archive.write_bytes(b"unrelated history")
        archive_holder["path"] = archive
        return state

    journal.create = create_with_history_collision
    with pytest.raises(ValueError, match="Archived contact record changed"):
        service.publish(PublishMatrixEditorLlcrCrPublicationCommand(
            draft, preview.preview_token, "archive",
        ))
    assert target.read_bytes() == b"measured values"
    assert archive_holder["path"].read_bytes() == b"unrelated history"


def test_publication_refuses_unfinished_create_folder_operation(tmp_path: Path) -> None:
    service, draft, target = _publication_fixture(tmp_path)
    folder_journal = GenerationJournal(tmp_path / "project-folder-generation")
    service._folder_journal = folder_journal
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    folder_journal.create("project-1", "create", "folder-context")
    with pytest.raises(ValueError, match="folder generation is unfinished"):
        service.publish(PublishMatrixEditorLlcrCrPublicationCommand(
            draft, preview.preview_token, "archive",
        ))
    assert target.read_bytes() == b"measured values"
    assert service._journal.read("project-1") is None


def test_publication_token_expires_if_confirmed_projection_changes(tmp_path: Path) -> None:
    service, draft, target = _publication_fixture(tmp_path)
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    current_previewer = service._preview_service
    service._preview_service = SimpleNamespace(
        preview=lambda project_id, kind: replace(
            current_previewer.preview(project_id, kind),
            preview_fingerprint="changed-contact-plan",
        ),
    )
    with pytest.raises(ValueError, match="changed"):
        service.publish(PublishMatrixEditorLlcrCrPublicationCommand(
            draft, preview.preview_token, "archive",
        ))
    assert target.read_bytes() == b"measured values"


def _publication_fixture(tmp_path: Path):
    profile = MatrixPointProfile((MatrixPointCategory("SIG", "1-2", True),))
    base = _snapshot()
    snapshot = replace(base, version=replace(base.version, point_profile=profile),
                       cells=(ConfirmedMatrixCell(
                           confirmed_cell_id="cell-1", confirmed_matrix_id="cmv-1",
                           confirmed_row_id="row-1", confirmed_group_id="group-1",
                           draft_row_id="draft-row-1", draft_group_id="draft-group-1", cell_value="2",
                       ),))
    workspace = SimpleNamespace(
        project_id="project-1", dl_number="DL-001", local_workspace_path=tmp_path / "workspace",
        official_folder_path=tmp_path / "workspace" / "DL-001",
    )
    target_dir = workspace.official_folder_path / "Test results"
    target_dir.mkdir(parents=True)
    target = target_dir / "DL-001 LLCR Record.xlsx"
    target.write_bytes(b"measured values")
    store = _ConfirmedStore(snapshot)
    service = MatrixEditorLlcrCrRecordPublicationService(
        confirmed_store=store,
        preview_service=LlcrCrRecordWorkbookPreviewService(confirmed_store=store),
        workspace_store=SimpleNamespace(get_by_project=lambda _id: workspace),
        workspace_verifier=lambda _record: True,
        journal=GenerationJournal(tmp_path / "publication-journal"),
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        output_service=_OutputService(), staging_root=tmp_path / "source-stage", commit=lambda: None,
    )
    draft = GenerateMatrixEditorLlcrCrRecordCommand(
        project_id="project-1", record_type="llcr",
        groups=(MatrixEditorLlcrCrRecordGroupInput("G1", "Group 1", "1", draft_group_id="draft-group-1"),),
        rows=(MatrixEditorLlcrCrRecordRowInput("LLCR", group_values={"G1": "2"}, draft_row_id="draft-row-1"),),
        point_profile=profile,
    )
    return service, draft, target
    repeated = service.publish(PublishMatrixEditorLlcrCrPublicationCommand(draft, current.preview_token, "archive"))
    assert repeated == result
    assert len(outputs.records) == 1


def test_ir_dwv_download_token_binds_template_and_header_context(tmp_path):
    from backend.application.matrix_editor_ir_dwv_record_projection import build_matrix_editor_ir_dwv_record_projection
    profile = MatrixPointProfile((), electrical_point_pairs="Odd&Even")
    context = ["source-v1"]
    def builder(**values):
        return build_matrix_editor_ir_dwv_record_projection(**values, source_fingerprint=context[0])
    service = MatrixEditorLlcrCrRecordPublicationService(
        confirmed_store=SimpleNamespace(get_active_by_project=lambda _: None),
        preview_service=None, workspace_store=SimpleNamespace(get_by_project=lambda _: None),
        workspace_verifier=lambda _: False, draft_projection_builder=builder,
    )
    draft = GenerateMatrixEditorLlcrCrRecordCommand("P1", "ir_dwv", (MatrixEditorLlcrCrRecordGroupInput("g1", "1", "5"),),
        (MatrixEditorLlcrCrRecordRowInput("IR", group_values={"g1": "1"}),), point_profile=profile)
    command = PreviewMatrixEditorLlcrCrPublicationCommand(draft)
    preview = service.preview(command)
    assert preview.mode == "download" and preview.status == "ready"
    context[0] = "source-v2"
    with pytest.raises(ValueError, match="changed"):
        service.validate_download(command, preview.preview_token)


def test_ir_dwv_form_publishes_with_correct_kind_and_preserves_old_measurements(tmp_path):
    from backend.application.matrix_editor_ir_dwv_record_projection import build_ir_dwv_record_projection, build_matrix_editor_ir_dwv_record_projection
    from backend.domain import ProjectOutputKind
    service, draft, old_target = _publication_fixture(tmp_path)
    profile = MatrixPointProfile((), electrical_point_pairs="Odd&Even")
    snapshot = service._confirmed._snapshot
    snapshot = replace(snapshot, version=replace(snapshot.version, point_profile=profile), rows=(replace(snapshot.rows[0], test_item="IR"),))
    service._confirmed._snapshot = snapshot
    service._draft_projection_builder = build_matrix_editor_ir_dwv_record_projection
    service._preview_service = SimpleNamespace(preview=lambda *args: build_ir_dwv_record_projection(snapshot))
    class Writer:
        def write(self, *, output_path, projection):
            output_path.write_bytes(b"new IR DWV workbook")
    service._writer = Writer()
    draft = replace(draft, record_type="ir_dwv", point_profile=profile, rows=(replace(draft.rows[0], test_item="IR"),))
    target = old_target.with_name("DL-001 IR&DWV Record.xlsx")
    target.write_bytes(b"previous measured IR DWV")
    preview = service.preview(PreviewMatrixEditorLlcrCrPublicationCommand(draft))
    assert preview.status == "conflict" and preview.target_path == target
    result = service.publish(PublishMatrixEditorLlcrCrPublicationCommand(draft, preview.preview_token, "archive"))
    assert target.read_bytes() == b"new IR DWV workbook"
    assert result.archive_path.read_bytes() == b"previous measured IR DWV"
    assert service._outputs.records[0].output_kind == ProjectOutputKind.IR_DWV_RECORD_FORM


class _OutputService:
    def __init__(self) -> None:
        self.records = []

    def get_status_summary(self, _project_id):
        return SimpleNamespace(active_draft_id=None)

    def list_records(self, _project_id):
        return self.records

    def register_output(self, command):
        self.records.append(command)
        return command


def _service(tmp_path: Path) -> LlcrCrRecordWorkbookGenerationService:
    preview_service = LlcrCrRecordWorkbookPreviewService(
        confirmed_store=_ConfirmedStore(_snapshot())
    )
    return LlcrCrRecordWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=LlcrCrSpecializedRecordArtifactStore(
            tmp_path / "generated_llcr_cr_record_files"
        ),
    )


class _ConfirmedStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self._snapshot if project_id == self._snapshot.version.project_id else None


def _snapshot() -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="cmv-1",
        project_id="project-1",
        project_matrix_draft_id="draft-1",
        source_import_id="import-1",
        source_snapshot_id="source-1",
        confirmed_revision=4,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator",
        confirmed_at="2026-07-10T10:00:00+00:00",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="group-1",
        confirmed_matrix_id="cmv-1",
        draft_group_id="draft-group-1",
        source_group_snapshot_id=None,
        group_order=1,
        group_key="G1",
        group_label="Group 1",
        sample_quantity_expression="1",
    )
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id="cmv-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id=None,
        row_order=1,
        test_item="LLCR",
    )
    plan = MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample="1",
        families=(
            MatrixStepContactFamily(
                family_id="signal",
                family_label="Signal",
                count_per_sample="1",
                record_label="Signal contact",
                record_prefix="SIG",
                included=True,
                is_custom=False,
            ),
        ),
    )
    quantity = ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="quantity-1",
        confirmed_matrix_id="cmv-1",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        draft_group_id="draft-group-1",
        draft_row_id="draft-row-1",
        step_sequence=2,
        step_suffix_note=None,
        raw_token="2",
        test_points_per_sample=None,
        readings_per_point=None,
        contact_points_per_sample=None,
        source="matrix_contact_plan",
        review_required=False,
        review_reason=None,
        confirmed_at=version.confirmed_at,
        contact_plan=plan,
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=(group,),
        rows=(row,),
        step_quantities=(quantity,),
    )
