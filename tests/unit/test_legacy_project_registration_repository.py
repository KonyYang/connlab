from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import (
    ProjectModel, ProjectOfficialWorkspaceRecordModel, ProjectPublicFolderWorkflowOperationModel,
)
from backend.infrastructure.storage.repositories.legacy_projects import LegacyProjectRepository


def test_retained_workspace_and_public_workflow_locations_remain_owned(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'references.db'}")
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="retained", project_no="DL-2020-01-001", product_name="Original", requestor="User", status="DRAFT", registry_state="history"))
        session.add(ProjectOfficialWorkspaceRecordModel(workspace_id="ws", project_id="retained", dl_number="DL-2020-01-001", local_workspace_path="D:/old/workspace", source_book_path="D:/old/workspace/Source Book", official_folder_path="D:/old/official", manifest_path="D:/old/workspace/.connlab/manifest.json", template_source_path="D:/templates", created_at="2026-01-01"))
        session.add(ProjectPublicFolderWorkflowOperationModel(operation_id="op", project_id="retained", operation_type="preview", status="completed", preview_hash="hash", requested_at="2026-01-01", started_at="2026-01-01", completed_at="2026-01-01", local_official_folder_path="D:/local/official", counts_json="{}", snapshot_json="{}"))
        session.commit()
        ref = LegacyProjectRepository(session).references()[0]
        assert ref["paths"] == ["D:/old/workspace", "D:/old/official", "D:/local/official"]
        assert ref["numbers"] == ["DL-2020-01-001"]
        assert ref["source_id"] == "retained"
    engine.dispose()
