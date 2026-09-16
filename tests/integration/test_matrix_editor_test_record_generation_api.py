from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.api.dependencies import get_settings
from backend.api.main import app
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)
from backend.infrastructure.storage.repositories import ExternalResourceRepository
from backend.infrastructure.storage.repositories.project_output_record import (
    ProjectOutputRecordRepository,
)
from backend.infrastructure.storage.repositories.official_workspace import (
    ProjectOfficialWorkspaceRepository,
)
from backend.shared.config import Settings, TestRecordSettings
from tests.integration.test_confirmed_matrix_test_record_generation_api import (
    _build_template,
    _seed_basic_information,
    _seed_header_metadata_sources,
)
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _client,
    _seed_project,
)


def test_matrix_editor_test_record_generation_uses_current_ui_payload(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        template_path = _build_template(tmp_path / "template.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template_path),
        )
        _seed_project("P1", tmp_path)
        _seed_header_metadata_sources("P1", tmp_path)

        response = _download_after_preview(
            client,
            {
                "source": "matrix_editor_current_ui_state",
                "groups": [
                    {
                        "group_key": "g1",
                        "group_label": "1",
                        "sample_quantity_expression": "7",
                    }
                ],
                "rows": [
                    {
                        "test_item": "Unsaved Visual Check",
                        "section": "9.9",
                        "method": "Unsaved method from UI",
                        "condition": "Unsaved condition from UI",
                        "requirement": "Unsaved requirement from UI",
                        "is_sample_row": False,
                        "group_values": {"g1": "1"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert "Preview" in response.headers["content-disposition"]
        assert "Unconfirmed" in response.headers["content-disposition"]
        output = tmp_path / "downloaded-preview.docx"
        output.write_bytes(response.content)
        document = Document(output)
        header_text = "\n".join(
            cell.text
            for table in document.sections[0].header.tables
            for row in table.rows
            for cell in row.cells
        )
        body_text = "\n".join(
            cell.text for table in document.tables for row in table.rows for cell in row.cells
        )
        assert "Unsaved Visual Check" in body_text
        assert "Unsaved method from UI" in body_text
        assert "Unsaved condition from UI" in body_text
        assert "DL-2026-05-003" in header_text
        assert "Coolpower HDF 3.40mm pin" in header_text
        assert "GS-12-1507" in header_text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_step_text_draft_docx_and_invalid_identity_are_scoped(tmp_path: Path):
    from io import BytesIO

    client, engine, _ = _client(tmp_path)
    try:
        template = _build_template(tmp_path / "template.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates", database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template),
        )
        _seed_project("P1", tmp_path)
        payload = {
            "source": "matrix_editor_current_ui_state",
            "groups": [{"group_key": "g1", "group_label": "1", "sample_quantity_expression": "5"}],
            "rows": [{"test_item": "samples", "is_sample_row": True},
                     {"test_item": "LLCR", "requirement": "<= 10", "group_values": {"g1": "1,2(a)"}}],
            "step_text_overrides": [{"group_key": "g1", "row_order": 2, "step_sequence": 2,
                                     "step_suffix_note": "(a)", "description": "Stage-only description",
                                     "requirement": "Specific nonnumeric requirement"}],
        }
        response = _download_after_preview(client, payload)
        assert response.status_code == 200, response.text
        assert "Unconfirmed" in response.headers["content-disposition"]
        table = Document(BytesIO(response.content)).tables[0]
        assert table.rows[1].cells[1].text == "LLCR"
        assert table.rows[2].cells[1].text == "Stage-only description"
        assert table.rows[2].cells[8].text == "Specific nonnumeric requirement"
        payload["step_text_overrides"][0]["row_order"] = 1
        response = client.post("/api/projects/P1/matrix-editor/test-record-publication/preview", json=payload)
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_preview_uses_confirmed_header_in_all_active_header_variants(
    tmp_path: Path,
) -> None:
    from io import BytesIO

    client, engine, session_factory = _client(tmp_path)
    try:
        template = _build_header_variant_template(tmp_path / "template-variants.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template),
        )
        _seed_project("P1", tmp_path)
        _seed_header_metadata_sources("P1", tmp_path)
        _seed_basic_information("P1", tmp_path)

        response = _download_after_preview(client, _draft_payload("Preview method"))

        assert response.status_code == 200, response.text
        assert "Preview" in response.headers["content-disposition"]
        assert "Unconfirmed" in response.headers["content-disposition"]
        document = Document(BytesIO(response.content))
        first = document.sections[0]
        for header in (first.header, first.first_page_header, first.even_page_header):
            header_text = "\n".join(
                cell.text
                for table in header.tables
                for row in table.rows
                for cell in row.cells
            )
            assert "DL-2026-05-003" in header_text
            assert "Confirmed Coolpower HDF 3.40mm pin" in header_text
            assert "GS-12-9999" in header_text
        assert document.sections[1].header.is_linked_to_previous is True
        assert "DL-2026-05-003" in document.sections[1].header.tables[0].cell(0, 2).text
        with session_factory() as session:
            assert ProjectOutputRecordRepository(session).list_by_project("P1") == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_test_record_generation_uses_settings_template_folder(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        template_folder = tmp_path / "template-folder"
        template_folder.mkdir()
        _build_template(template_folder / "FDQF-E-036 Test Record Template-Even.docx")
        _seed_template_folder(session_factory, template_folder)
        _seed_project("P1", tmp_path)
        _seed_header_metadata_sources("P1", tmp_path)

        response = _download_after_preview(
            client,
            {
                "source": "matrix_editor_current_ui_state",
                "groups": [
                    {
                        "group_key": "g1",
                        "group_label": "1",
                        "sample_quantity_expression": "3",
                    }
                ],
                "rows": [
                    {
                        "test_item": "Visual Check",
                        "section": "5.1",
                        "method": "EIA-364-18B",
                        "condition": "Normal",
                        "requirement": "No defect",
                        "group_values": {"g1": "1"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert "Preview" in response.headers["content-disposition"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_test_record_generation_rejects_wrong_source(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        response = client.post(
            "/api/projects/P1/matrix-editor/test-record-draft/generate",
            json={
                "source": "saved_draft",
                "groups": [],
                "rows": [],
                "preview_token": "not-used-for-invalid-source",
            },
        )
        assert response.status_code == 422
        assert response.json()["detail"] == (
            "Matrix Editor Test Record preview requires current UI state payload."
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_publication_preview_keeps_download_mode_without_project_folder(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.post(
            "/api/projects/P1/matrix-editor/test-record-publication/preview",
            json=_draft_payload("Unsaved method"),
        )

        assert response.status_code == 200
        assert response.json()["mode"] == "download"
        assert response.json()["status"] == "ready"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_publication_downloads_current_ui_draft_when_matrix_is_unconfirmed(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        template_path = _build_template(tmp_path / "template.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template_path),
        )
        _seed_project("P1", tmp_path)
        _seed_basic_information("P1", tmp_path)
        workspace = _seed_workspace(session_factory, tmp_path)
        payload = _draft_payload("Unsaved method from Matrix Editor")

        preview = client.post(
            "/api/projects/P1/matrix-editor/test-record-publication/preview",
            json=payload,
        )
        assert preview.status_code == 200
        assert preview.json()["mode"] == "download"
        assert preview.json()["status"] == "ready"
        assert not (
            workspace.official_folder_path
            / "Submitted Material"
            / "DL-2026-05-003 Test Record.docx"
        ).exists()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_unconfirmed_matrix_does_not_replace_existing_official_test_record(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        template_path = _build_template(tmp_path / "template.docx")
        app.dependency_overrides[get_settings] = lambda: Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
            test_record=TestRecordSettings(template_path=template_path),
        )
        _seed_project("P1", tmp_path)
        _seed_basic_information("P1", tmp_path)
        workspace = _seed_workspace(session_factory, tmp_path)
        target = (
            workspace.official_folder_path
            / "Submitted Material"
            / "DL-2026-05-003 Test Record.docx"
        )
        target.write_text("operator old record", encoding="utf-8")
        payload = _draft_payload("replacement method")

        preview = client.post(
            "/api/projects/P1/matrix-editor/test-record-publication/preview",
            json=payload,
        )
        assert preview.json()["mode"] == "download"
        assert preview.json()["status"] == "ready"
        assert target.read_text(encoding="utf-8") == "operator old record"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_template_folder(session_factory, template_folder: Path) -> None:
    with session_factory() as session:
        ExternalResourceRepository(session).upsert(
            ExternalResource(
                resource_id="template-folder",
                resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
                path=template_folder,
                active=True,
                validation_status=ExternalResourceValidationStatus.VALID,
            )
        )
        session.commit()


def _draft_payload(method: str) -> dict[str, object]:
    return {
        "source": "matrix_editor_current_ui_state",
        "groups": [
            {
                "group_key": "g1",
                "group_label": "1",
                "sample_quantity_expression": "5",
            }
        ],
        "rows": [
            {
                "test_item": "Visual Check",
                "section": "5.1",
                "method": method,
                "condition": "Normal",
                "requirement": "No defect",
                "group_values": {"g1": "1"},
            }
        ],
    }


def _download_after_preview(client, payload: dict[str, object]):
    preview = client.post(
        "/api/projects/P1/matrix-editor/test-record-publication/preview",
        json=payload,
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["mode"] == "download"
    return client.post(
        "/api/projects/P1/matrix-editor/test-record-draft/generate",
        json={**payload, "preview_token": preview.json()["preview_token"]},
    )


def _build_header_variant_template(path: Path) -> Path:
    from docx.enum.section import WD_SECTION

    document = Document()
    document.settings.odd_and_even_pages_header_footer = True
    first = document.sections[0]
    first.different_first_page_header_footer = True
    for header in (first.header, first.first_page_header, first.even_page_header):
        width = first.page_width - first.left_margin - first.right_margin
        table0 = header.add_table(rows=1, cols=3, width=width)
        table0.cell(0, 2).text = "Lab Test Request Number:\n实验室测试项目编号："
        table1 = header.add_table(rows=1, cols=6, width=width)
        table1.cell(0, 0).text = "Product Description\n产品描述"
        table1.cell(0, 2).text = "Applicable Specification\n适用的规范"
        table1.cell(0, 4).text = "Estimated Completion Date\n预计完成日期"
    document.add_paragraph("Group Number: PLACEHOLDER")
    step_table = document.add_table(rows=1, cols=9)
    step_table.rows[0].cells[0].text = "Step"
    document.add_paragraph("EQUIPMENT USED 使用的设备:")
    equipment_table = document.add_table(rows=1, cols=7)
    equipment_table.rows[0].cells[0].text = "Equipment"
    linked = document.add_section(WD_SECTION.NEW_PAGE)
    linked.header.is_linked_to_previous = True
    linked.first_page_header.is_linked_to_previous = True
    linked.even_page_header.is_linked_to_previous = True
    document.save(path)
    return path


def _seed_workspace(session_factory, tmp_path: Path) -> OfficialWorkspaceRecord:
    local = tmp_path / "DL-2026-05-003"
    official = local / "DL-2026-05-003 Connector Qualification test"
    (official / "Submitted Material").mkdir(parents=True)
    record = OfficialWorkspaceRecord(
        workspace_id="workspace-1",
        project_id="P1",
        dl_number="DL-2026-05-003",
        local_workspace_path=local,
        source_book_path=local / "Source Book",
        official_folder_path=official,
        manifest_path=local / ".connlab" / "manifest.json",
        template_source_path=tmp_path / "template-source",
        created_at="2026-08-28T00:00:00+00:00",
    )
    with session_factory() as session:
        ProjectOfficialWorkspaceRepository(session).save(record)
        session.commit()
    return record
