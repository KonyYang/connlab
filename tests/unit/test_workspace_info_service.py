from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.shared.config import Settings
from backend.application.workspace_info_service import WorkspaceInfoService
from backend.infrastructure.workspace_info import WorkspaceInfoReader


def test_workspace_uses_actual_session_database_and_never_initializes_configured_database(tmp_path):
    actual = tmp_path / "actual.sqlite3"
    other = tmp_path / "do-not-open.sqlite3"
    engine = create_engine(f"sqlite:///{actual.as_posix()}")
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates", database_path=other)
    with Session(engine) as session:
        info = WorkspaceInfoService(WorkspaceInfoReader(session, settings)).read()
    assert info["database_path"] == str(actual)
    assert info["sqlite_user_version"] == 0
    assert info["schema_status"] == "unversioned"
    assert not other.exists()
    engine.dispose()
