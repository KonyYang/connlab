from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, Lock

import pytest
from sqlalchemy import create_engine, event

from fastapi.testclient import TestClient

from backend.api import dependencies
from backend.api.dependencies import _official_workspace_settings_from_registry
from backend.api.main import app
from backend.domain import ExternalResource, ExternalResourceType


def test_project_api_uses_default_session_dependency(tmp_path: Path, monkeypatch) -> None:
    """The real FastAPI dependency stack can open a local SQLite session."""
    monkeypatch.setenv("CONNLAB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CONNLAB_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("CONNLAB_TEMPLATES_DIR", str(tmp_path / "templates"))
    monkeypatch.setenv("CONNLAB_DATABASE_PATH", str(tmp_path / "connlab.sqlite3"))

    _clear_dependency_caches()
    client = TestClient(app)

    try:
        response = client.get("/api/projects")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        _clear_dependency_caches()


def test_official_workspace_settings_use_default_locations_registry(
    tmp_path: Path,
) -> None:
    """TASK_316 should reuse ordinary Settings locations, not hidden path fields."""
    project_root = tmp_path / "Test Project"
    template_root = tmp_path / "Template"
    public_root = tmp_path / "Public"
    resources = _ResourceStore(
        {
            ExternalResourceType.PROJECT_OUTPUT_ROOT: project_root,
            ExternalResourceType.PROJECT_FOLDER_TEMPLATE: template_root,
            ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT: public_root,
        }
    )

    settings = _official_workspace_settings_from_registry(
        resources,
    )

    assert settings.local_workspace_root == project_root
    assert settings.template_path == template_root
    assert settings.public_drive_root == public_root


def test_official_workspace_settings_do_not_fallback_to_hidden_config(
    tmp_path: Path,
) -> None:
    """Missing visible Settings locations must stay missing instead of using hidden config."""
    settings = _official_workspace_settings_from_registry(
        _ResourceStore({}),
    )

    assert settings.local_workspace_root is None
    assert settings.template_path is None
    assert settings.public_drive_root is None


def _clear_dependency_caches() -> None:
    """Reset cached app-level database objects between dependency-stack checks."""
    engine = dependencies.get_engine.cache_info().currsize and dependencies.get_engine()
    dependencies.get_session_factory.cache_clear()
    dependencies.get_engine.cache_clear()
    if engine:
        engine.dispose()


class _ResourceStore:
    def __init__(self, paths: dict[ExternalResourceType, Path]) -> None:
        self._paths = paths

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        path = self._paths.get(resource_type)
        if path is None:
            return None
        return ExternalResource(
            resource_id=resource_type.value,
            resource_type=resource_type,
            path=path,
            active=True,
        )


def test_concurrent_cold_engine_requests_share_one_completed_initialization(tmp_path, monkeypatch):
    _clear_dependency_caches()
    engines = []
    calls = []
    calls_lock = Lock()
    first_entered, second_entered, release = Event(), Event(), Event()
    start = Barrier(5)
    real_init = dependencies.init_db

    def create_isolated_engine():
        engine = create_engine(f"sqlite:///{(tmp_path / 'concurrent.sqlite3').as_posix()}")
        engines.append(engine)
        return engine

    def blocked_init(engine):
        with calls_lock:
            calls.append(engine)
            (first_entered if len(calls) == 1 else second_entered).set()
        assert release.wait(5), 'initialization was never released'
        real_init(engine)

    def request_engine():
        start.wait(timeout=5)
        return dependencies.get_engine()

    monkeypatch.setattr(dependencies, 'create_database_engine', create_isolated_engine)
    monkeypatch.setattr(dependencies, 'init_db', blocked_init)
    try:
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(request_engine) for _ in range(5)]
            try:
                assert first_entered.wait(5)
                assert not second_entered.wait(0.5), 'concurrent initialization entered twice'
                assert all(not future.done() for future in futures)
            finally:
                release.set()
            results = [future.result(timeout=10) for future in futures]
        assert len(calls) == 1
        assert all(engine is results[0] for engine in results)
        with results[0].connect() as connection:
            assert connection.exec_driver_sql('SELECT count(*) FROM projects').scalar_one() == 0
        assert dependencies.get_engine.cache_info().currsize == 1
        dependencies.get_engine.cache_clear()
        assert dependencies.get_engine.cache_info().currsize == 0
        assert dependencies.get_engine() is not results[0]
        assert len(calls) == 2
    finally:
        release.set()
        _clear_dependency_caches()
        for engine in engines:
            engine.dispose()


def test_failed_engine_initialization_disposes_and_can_retry(tmp_path, monkeypatch):
    _clear_dependency_caches()
    engines, disposed = [], []
    real_init = dependencies.init_db

    def create_isolated_engine():
        engine = create_engine(f"sqlite:///{(tmp_path / 'retry.sqlite3').as_posix()}")
        event.listen(engine, 'engine_disposed', lambda engine: disposed.append(engine))
        engines.append(engine)
        return engine

    def fail_once(engine):
        if len(engines) == 1:
            with engine.connect() as connection:
                connection.exec_driver_sql('SELECT 1')
            raise RuntimeError('synthetic initialization failure')
        real_init(engine)

    monkeypatch.setattr(dependencies, 'create_database_engine', create_isolated_engine)
    monkeypatch.setattr(dependencies, 'init_db', fail_once)
    try:
        with pytest.raises(RuntimeError, match='synthetic initialization failure'):
            dependencies.get_engine()
        assert disposed == [engines[0]]
        assert dependencies.get_engine.cache_info().currsize == 0
        engine = dependencies.get_engine()
        assert engine is engines[1]
        with engine.connect() as connection:
            assert connection.exec_driver_sql('SELECT count(*) FROM projects').scalar_one() == 0
        assert dependencies.get_engine() is engine
    finally:
        _clear_dependency_caches()
        for engine in engines:
            engine.dispose()
