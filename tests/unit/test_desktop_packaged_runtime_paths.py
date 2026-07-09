from __future__ import annotations

import os
from pathlib import Path

from backend.desktop.runtime_paths import (
    PackagedRuntimePaths,
    apply_packaged_environment_defaults,
    build_packaged_runtime_paths,
)


def test_packaged_paths_use_local_app_data_and_preserve_existing_config(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Packaged mode keeps mutable operator state outside the release folder."""
    local_app_data = tmp_path / "LocalAppData"
    release_root = tmp_path / "Release" / "ConnLab_20260630_v0.1.0"
    frontend_root = release_root / "_internal" / "frontend_dist"
    frontend_root.mkdir(parents=True)
    existing_config = local_app_data / "ConnLab" / "config" / "connlab.local.toml"
    existing_config.parent.mkdir(parents=True)
    existing_config.write_text(
        '[paths]\ntemplates_dir = "D:/UserConfigured/Templates"\n',
        encoding="utf-8",
    )

    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))

    paths = build_packaged_runtime_paths(
        app_root=release_root,
        frontend_dist=frontend_root,
    )
    paths.ensure_user_directories()

    assert paths.user_root == local_app_data / "ConnLab"
    assert paths.data_dir == local_app_data / "ConnLab" / "data"
    assert paths.projects_dir == local_app_data / "ConnLab" / "projects"
    assert paths.templates_dir == local_app_data / "ConnLab" / "templates"
    assert paths.logs_dir == local_app_data / "ConnLab" / "logs"
    assert paths.config_dir == local_app_data / "ConnLab" / "config"
    assert paths.local_config_path == existing_config
    assert existing_config.read_text(encoding="utf-8") == (
        '[paths]\ntemplates_dir = "D:/UserConfigured/Templates"\n'
    )


def test_packaged_environment_defaults_do_not_override_existing_values(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Packaged defaults are fallbacks and never replace explicit settings."""
    paths = PackagedRuntimePaths(
        app_root=tmp_path / "release",
        frontend_dist=tmp_path / "release" / "frontend_dist",
        user_root=tmp_path / "user",
        data_dir=tmp_path / "user" / "data",
        projects_dir=tmp_path / "user" / "projects",
        templates_dir=tmp_path / "user" / "templates",
        logs_dir=tmp_path / "user" / "logs",
        config_dir=tmp_path / "user" / "config",
        database_path=tmp_path / "user" / "data" / "connlab.sqlite3",
        local_config_path=tmp_path / "user" / "config" / "connlab.local.toml",
    )
    custom_projects = tmp_path / "custom-projects"
    monkeypatch.setenv("CONNLAB_PROJECTS_DIR", str(custom_projects))

    apply_packaged_environment_defaults(paths)

    assert os.environ["CONNLAB_PROJECTS_DIR"] == str(custom_projects)
    assert os.environ["CONNLAB_DATA_DIR"] == str(paths.data_dir)
    assert os.environ["CONNLAB_DATABASE_PATH"] == str(paths.database_path)
    assert os.environ["CONNLAB_LOCAL_CONFIG_PATH"] == str(paths.local_config_path)
