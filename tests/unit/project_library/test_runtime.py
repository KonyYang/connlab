from pathlib import Path
import os
import json
import pytest
from backend.shared.config import Settings
from backend.desktop.runtime_paths import build_packaged_runtime_paths, apply_packaged_environment_defaults


def clear_paths(monkeypatch):
    monkeypatch.setattr(os, "environ", dict(os.environ))
    for name in ("CONNLAB_LIBRARY_ROOT", "CONNLAB_DATA_DIR", "CONNLAB_DATABASE_PATH",
                 "CONNLAB_PROJECTS_DIR", "CONNLAB_TEMPLATES_DIR", "CONNLAB_LOCAL_CONFIG_PATH",
                 "CONNLAB_ADMIN_CONFIG_PATH", "CONNLAB_LOGS_DIR"):
        monkeypatch.delenv(name, raising=False)


def test_development_and_release_use_one_selected_library_without_changing_default(monkeypatch, tmp_path):
    clear_paths(monkeypatch)
    library = tmp_path / "business"
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT", str(library))
    development = Settings.load(base_dir=tmp_path / "source")
    paths = build_packaged_runtime_paths(app_root=tmp_path / "release", user_root=tmp_path / "user")
    apply_packaged_environment_defaults(paths)
    release = Settings.load(base_dir=tmp_path / "release")
    assert development.library_root == release.library_root == library
    assert development.database_path == release.database_path == library / "Data" / "connlab.sqlite3"
    assert development.projects_dir == release.projects_dir == library / "Projects"
    assert not (tmp_path / "source" / "data").exists()


def test_library_binding_rejects_a_database_outside_selected_root_before_creating_it(monkeypatch, tmp_path):
    clear_paths(monkeypatch)
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT", str(tmp_path / "business"))
    monkeypatch.setenv("CONNLAB_DATABASE_PATH", str(tmp_path / "other" / "data.sqlite3"))
    with pytest.raises(ValueError, match="selected project library"):
        Settings.load(base_dir=tmp_path / "source")
    assert not (tmp_path / "other").exists()


def test_release_reads_library_binding_from_operator_config(monkeypatch, tmp_path):
    clear_paths(monkeypatch)
    library = tmp_path / "selected"
    user = tmp_path / "user"
    config = user / "config" / "connlab.local.toml"
    config.parent.mkdir(parents=True)
    config.write_text('[paths]\nlibrary_root = ' + json.dumps(str(library)) + '\n', encoding="utf-8")
    paths = build_packaged_runtime_paths(app_root=tmp_path / "release", user_root=user)
    apply_packaged_environment_defaults(paths)
    settings = Settings.load(base_dir=tmp_path / "release")
    assert settings.database_path == library / "Data" / "connlab.sqlite3"
    assert settings.projects_dir == library / "Projects"


def test_relative_library_binding_is_rejected_consistently(monkeypatch, tmp_path):
    clear_paths(monkeypatch)
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT", "relative-business")
    with pytest.raises(ValueError, match="absolute"):
        Settings.load(base_dir=tmp_path / "source")
    paths = build_packaged_runtime_paths(app_root=tmp_path / "release", user_root=tmp_path / "user")
    with pytest.raises(ValueError, match="absolute"):
        apply_packaged_environment_defaults(paths)


def test_future_library_version_rejected_before_creating_config_or_database(monkeypatch, tmp_path):
    clear_paths(monkeypatch)
    root = tmp_path / "future"
    marker = root / ".connlab" / "library-format.json"
    marker.parent.mkdir(parents=True)
    marker.write_text(json.dumps({"format_version": 99, "database_relative_path": "Data/connlab.sqlite3"}), encoding="utf-8")
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT", str(root))
    with pytest.raises(ValueError, match="version"):
        Settings.load(base_dir=tmp_path / "program")
    assert not (tmp_path / "program" / "connlab.admin.toml").exists()
    assert not (root / "Data").exists()


def test_selected_library_has_one_writer_process_and_dispose_releases_it(monkeypatch, tmp_path):
    import subprocess
    import sys
    from backend.infrastructure.storage.database import create_database_engine
    clear_paths(monkeypatch)
    root = tmp_path / "business"
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT", str(root))
    settings = Settings.load(base_dir=tmp_path / "program")
    engine = create_database_engine(settings)
    code = (
        "from pathlib import Path; from backend.shared.config import Settings; "
        "from backend.infrastructure.storage.database import create_database_engine; "
        "s=Settings.load(base_dir=Path(" + repr(str(tmp_path / "program")) + ")); "
        "\ntry:\n e=create_database_engine(s);e.dispose();print('available')\n"
        "except ValueError:\n print('already-running')\n"
    )
    env = dict(os.environ)
    locked = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=20)
    assert locked.returncode == 0, locked.stderr
    assert locked.stdout.strip() == "already-running"
    engine.dispose()
    released = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=20)
    assert released.returncode == 0, released.stderr
    assert released.stdout.strip() == "available"
