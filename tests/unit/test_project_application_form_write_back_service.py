from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_application_form_write_back_service import (
    ProjectApplicationFormWriteBackService,
)
from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    Project,
    ProjectStatus,
)


def test_application_form_write_back_updates_copied_submitted_material_docx(
    tmp_path: Path,
) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    submitted = official / "Submitted Material"
    target = submitted / "application.docx"
    _write_docx(target)
    output_store = _OutputStore()
    service = ProjectApplicationFormWriteBackService(
        project_store=_ProjectStore(),
        workspace_store=_WorkspaceStore(official),
        application_form_store=_ApplicationFormStore(),
        file_asset_store=_FileAssetStore(target),
        output_record_service=output_store,
    )

    result = service.write_back("P1")

    assert result.status == "updated"
    assert result.target_path == target
    values = _read_table_values(target)
    assert values["Product Description"] == "Connector"
    assert values["Requested Testing"] == "Qualification Testing"
    assert values["Requester"] == "MP Cao"
    assert values["E-mail of Requestor"] == "mp@example.test"
    assert values["Received Date"] == "2026-06-01"
    assert output_store.commands
    assert str(target) == output_store.commands[-1].output_path


def _write_docx(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    table = document.add_table(rows=0, cols=2)
    for label in (
        "Product Description",
        "Requested Testing",
        "Requester",
        "E-mail of Requestor",
        "Received Date",
    ):
        row = table.add_row()
        row.cells[0].text = label
        row.cells[1].text = ""
    document.save(path)


def _read_table_values(path: Path) -> dict[str, str]:
    document = Document(path)
    return {
        row.cells[0].text.strip(): row.cells[1].text.strip()
        for row in document.tables[0].rows
    }


class _ProjectStore:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no="DL-001",
            product_name="Connector",
            requestor="MP Cao",
            status=ProjectStatus.FOLDER_CREATED,
            business_unit="BU",
        )


class _WorkspaceStore:
    def __init__(self, official: Path) -> None:
        self.official = official

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord:
        return OfficialWorkspaceRecord(
            workspace_id="W1",
            project_id=project_id,
            dl_number="DL-001",
            local_workspace_path=self.official.parent,
            source_book_path=self.official.parent / "Source Book",
            official_folder_path=self.official,
            manifest_path=self.official.parent / ".connlab" / "manifest.json",
            template_source_path=Path("D:/Source/Template/DL-XXXX-YY-ZZZ project"),
            created_at="2026-06-19T00:00:00Z",
        )


class _ApplicationFormStore:
    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [
            ApplicationForm(
                form_id="F1",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="MP Cao",
                email="mp@example.test",
                requested_testing="Qualification Testing",
                received_date="2026-06-01",
            )
        ]


class _FileAssetStore:
    def __init__(self, target: Path) -> None:
        self.target = target

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        return [
            FileAsset(
                asset_id="A1",
                project_id=project_id,
                asset_type=FileAssetType.APPLICATION_FORM,
                path=self.target,
                original_name="application.docx",
                source_role="selected_application_form",
            )
        ]


class _OutputStore:
    def __init__(self) -> None:
        self.commands = []

    def get_status_summary(self, project_id: str):
        class _Summary:
            active_draft_id = "D1"

        return _Summary()

    def register_output(self, command):
        self.commands.append(command)

        class _Record:
            output_record_id = "O1"

        return _Record()
