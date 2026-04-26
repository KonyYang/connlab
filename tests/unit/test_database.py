import shutil
import uuid
from pathlib import Path

from sqlalchemy import inspect, text

from backend.infrastructure.storage.database import (
    Base,
    build_sqlite_url,
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_build_sqlite_url_uses_configured_path() -> None:
    database_path = Path("tmp") / "connlab-test.sqlite3"

    assert build_sqlite_url(database_path) == "sqlite:///tmp/connlab-test.sqlite3"


def test_create_engine_session_and_init_db_with_temp_file() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    database_path = workspace_tmp / "storage" / "connlab.sqlite3"
    settings = Settings(
        data_dir=workspace_tmp / "data",
        projects_dir=workspace_tmp / "projects",
        templates_dir=workspace_tmp / "templates",
        database_path=database_path,
    )

    try:
        engine = create_database_engine(settings)
        init_db(engine)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            assert session.execute(text("select 1")).scalar_one() == 1

        assert database_path.is_file()
        assert set(inspect(engine).get_table_names()) == set(Base.metadata.tables.keys())
        engine.dispose()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_defaults_database_path_under_data_dir() -> None:
    workspace_tmp = _make_workspace_temp_dir()

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.database_path == workspace_tmp / "data" / "connlab.sqlite3"
        assert settings.database_path.parent.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_database_path_override(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    monkeypatch.setenv("CONNLAB_DATABASE_PATH", "custom-store/custom.sqlite3")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.database_path == (
            workspace_tmp / "custom-store" / "custom.sqlite3"
        ).resolve()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def _make_workspace_temp_dir() -> Path:
    root = Path.cwd() / "tmp"
    root.mkdir(exist_ok=True)
    path = root / f"task003-{uuid.uuid4().hex}"
    path.mkdir()
    return path
