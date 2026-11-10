from pathlib import Path
from types import SimpleNamespace

from backend.application.project_file_generation_staging import RequiredFormsStagingGenerator


def test_operation_stage_overrides_legacy_shared_stage(tmp_path: Path):
    seen = []
    class Status:
        def generate(self, command):
            seen.append(command.output_dir)
            output = command.output_dir / command.target_name
            output.write_bytes(b"status")
            return output
    generator = RequiredFormsStagingGenerator(
        settings=SimpleNamespace(data_dir=tmp_path / "data"),
        fee_template_resource_store=None,
        test_record_service=None, fee_export_service=None,
        customer_feedback_service=None, test_status_service=Status())
    operation_stage = tmp_path / "operation" / "test_status"
    operation_stage.mkdir(parents=True)
    output = generator.generate(project_id="P1", key="test_status", target_name="status.xlsx",
        basic_information=None, confirmed_fee=None, stage_dir=operation_stage)
    assert output == operation_stage / "status.xlsx"
    assert seen == [operation_stage]
    assert not (tmp_path / "data").exists()


def application_service(tmp_path, *, selected=True):
    from backend.application.project_application_form_write_back_service import ProjectApplicationFormWriteBackService
    from backend.application.project_basic_information_output import ConfirmedBasicInformationSnapshot
    from backend.domain import FileAsset, FileAssetType
    from backend.application.project_folder_required_forms_service import compute_sha256
    official = tmp_path / "official"
    submitted = official / "Submitted Material"
    submitted.mkdir(parents=True)
    target = submitted / "application.docx"
    target.write_bytes(b"original Word")
    basic = ConfirmedBasicInformationSnapshot("P1", 1, {
        "dl_number":"DL-001", "lab_performing_tests":"Lab", "project_leader":"Leader",
        "date_lab_received_samples":"10 Nov 2026", "condition_of_samples_when_received":"Good"},
        "basic", None, None)
    asset = FileAsset(asset_id="A1",project_id="P1",asset_type=FileAssetType.APPLICATION_FORM,
        path=tmp_path/"original.docx", original_name="application.docx",sha256=compute_sha256(target))
    calls = []
    class Office:
        def write_word_application_form_fields_with_owned_session(self, path, fields):
            assert len(str(path)) < 240
            calls.append(dict(fields))
            path.write_bytes(b"staged Word")
    service = ProjectApplicationFormWriteBackService(
        project_store=SimpleNamespace(get=lambda _: object()),
        workspace_store=SimpleNamespace(get_by_project=lambda _: SimpleNamespace(official_folder_path=official)),
        application_form_store=SimpleNamespace(list_by_project=lambda _: [SimpleNamespace(form_id="F1",assigned_personnel="Leader")]),
        file_asset_store=SimpleNamespace(list_by_project=lambda _: [asset] if selected else []),
        basic_information_reader=SimpleNamespace(get_latest_confirmed=lambda _: basic),
        project_schedule_reader=SimpleNamespace(get_latest_confirmed=lambda _: SimpleNamespace(
            context_signature="schedule",estimated_completion_date="20 Nov 2026")),
        output_record_service=SimpleNamespace(get_status_summary=lambda _: SimpleNamespace(items=())),
        file_gateway=SimpleNamespace(), office=Office())
    return service,target,calls


def test_application_generation_stages_without_publishing_or_registering(tmp_path):
    service,target,calls = application_service(tmp_path)
    context = service.prepare_staging("P1")
    stage = tmp_path / "owned-stage"
    stage.mkdir()
    output = service.generate_staged(context, stage_dir=stage, target_name=target.name)
    assert output == stage / "application.docx"
    assert output.read_bytes() == b"staged Word"
    assert target.read_bytes() == b"original Word"
    assert calls[0]["estimated_completion_date"] == "20 Nov 2026"


def test_application_generation_does_not_accept_a_lone_unproven_docx(tmp_path):
    import pytest
    service,target,calls = application_service(tmp_path,selected=False)
    with pytest.raises(ValueError, match="proven"):
        service.prepare_staging("P1")
    assert target.read_bytes() == b"original Word"
    assert calls == []
