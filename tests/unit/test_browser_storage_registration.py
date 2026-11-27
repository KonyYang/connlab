from pathlib import Path

import pytest

from backend.desktop.browser_storage import register_browser_storage, uses_legacy_defaults
from backend.domain import ExternalResource, ExternalResourceType as Kind
from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.shared.config import Settings


@pytest.fixture
def install(tmp_path):
    settings = Settings(data_dir=tmp_path / "internal", database_path=tmp_path / "db.sqlite3",
                        projects_dir=tmp_path / "legacy/projects", templates_dir=tmp_path / "legacy/template",
                        environment="release", output_root=tmp_path / "legacy")
    engine = create_database_engine(settings)
    init_db(engine)
    try:
        yield settings, create_session_factory(engine)
    finally:
        engine.dispose()


def test_first_use_pins_all_four_paths_even_after_moving_program(tmp_path, install):
    settings, sessions = install
    root = tmp_path / "first/ConnLabFiles"
    result = register_browser_storage(settings, sessions, root, {})
    assert result.warnings == []
    assert result.common_root == root
    assert set(result.locations) == {"Projects", "TemporaryProjects", "Template", "Library"}
    assert all(path == root / purpose and path.is_dir() for purpose, path in result.locations.items())
    another = tmp_path / "second/ConnLabFiles"
    original = result.locations["Library"]
    original.rmdir()
    result = register_browser_storage(settings, sessions, another, {})
    assert result.locations["Library"] == original and not original.exists()
    assert any(str(original) in warning for warning in result.warnings)
    assert not another.exists()


def test_partial_install_keeps_offline_registration_and_template_override(tmp_path, install):
    settings, sessions = install
    old_template = tmp_path / "approved"
    old_template.mkdir()
    offline = tmp_path / "offline/projects"
    with sessions.begin() as session:
        ExternalResourceRepository(session).upsert(ExternalResource("keep-id", Kind.PROJECT_OUTPUT_ROOT, offline))
    result = register_browser_storage(settings, sessions, tmp_path / "ConnLabFiles", {"Template": old_template})
    assert result.locations["Projects"] == offline
    assert result.locations["Template"] == old_template
    assert result.common_root is None and not offline.exists()
    with sessions() as session:
        assert ExternalResourceRepository(session).get_by_type(Kind.PROJECT_OUTPUT_ROOT).resource_id == "keep-id"
        assert Path(MaterialReceiptRepository(session).settings()["root_path"]) == result.locations["Library"]



def test_upgrade_reuses_populated_previous_defaults_only_for_unregistered_paths(tmp_path, install):
    settings, sessions = install
    legacy = {"Projects": settings.projects_dir, "Library": settings.output_path("Materials"),
              "TemporaryProjects": settings.output_path("TemporaryMaterials")}
    for path in legacy.values():
        path.mkdir(parents=True)
        (path / "sentinel").write_bytes(b"keep")
    settings.templates_dir.mkdir(parents=True)
    root = tmp_path / "ConnLabFiles"
    result = register_browser_storage(settings, sessions, root, {}, upgrading=True)
    assert result.locations == {**legacy, "Template": root / "Template"}
    assert result.warnings == []
    assert all((p / "sentinel").read_bytes() == b"keep" for p in legacy.values())


def test_fresh_install_ignores_unrelated_old_default(tmp_path, install):
    settings, sessions = install
    settings.projects_dir.mkdir(parents=True)
    (settings.projects_dir / "sentinel").write_bytes(b"other installation")
    root = tmp_path / "ConnLabFiles"
    result = register_browser_storage(settings, sessions, root, {})
    assert result.locations["Projects"] == root / "Projects"
    assert (settings.projects_dir / "sentinel").read_bytes() == b"other installation"



def test_interrupted_fresh_setup_cannot_adopt_unrelated_legacy_paths_on_retry(tmp_path):
    data = tmp_path / "data"
    settings = Settings(data_dir=data, database_path=data / "fresh.sqlite3", projects_dir=tmp_path / "old",
                        templates_dir=tmp_path / "legacy-template", environment="release")
    data.mkdir()
    assert not uses_legacy_defaults(settings)
    # The previous launch created the database schema before failing to create the requested folders.
    settings.database_path.touch()
    assert not uses_legacy_defaults(settings)
    from dataclasses import replace
    old_database = data / "previous.sqlite3"
    old_database.touch()
    assert uses_legacy_defaults(replace(settings, database_path=old_database))



def test_explicit_per_file_overrides_match_generation_precedence(tmp_path, install):
    from dataclasses import replace
    from backend.shared.config import TestRecordSettings
    settings, sessions = install
    word = tmp_path / "custom-document.docx"
    settings = replace(settings, test_record=TestRecordSettings(template_path=word))
    root = tmp_path / "ConnLabFiles"
    ir = tmp_path / "approved" / "override.xlsx"
    with sessions.begin() as session:
        ExternalResourceRepository(session).upsert(ExternalResource("ir", Kind.IR_DWV_RECORD_TEMPLATE, ir))
    storage = register_browser_storage(settings, sessions, root, {})
    assert storage.template_overrides == {"test_record": word, "ir_dwv": ir}
    with sessions.begin() as session:
        discovered = storage.locations["Template"] / "FDQF-E-033 template.xlsx"
        ExternalResourceRepository(session).upsert(ExternalResource("ir", Kind.IR_DWV_RECORD_TEMPLATE, discovered))
    assert register_browser_storage(settings, sessions, root, {}).template_overrides == {"test_record": word}



def test_operator_template_junction_remains_unavailable_even_if_settings_resolved_it(tmp_path, install, monkeypatch):
    import os
    import subprocess
    from dataclasses import replace
    from backend.desktop.packaged_server import _browser_storage_overrides

    if os.name != "nt":
        pytest.skip("Windows junction")
    settings, sessions = install
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "field-template"
    sentinel.write_bytes(b"preserve")
    link = tmp_path / "linked-template"
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], check=True, capture_output=True)
    try:
        config = tmp_path / "connlab.local.toml"
        config.write_text('[paths]\ntemplates_dir = "' + link.as_posix() + '"\n', encoding="utf-8")
        monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config))
        monkeypatch.setenv("CONNLAB_TEMPLATES_DIR", str(link))
        overrides = _browser_storage_overrides(replace(settings, templates_dir=link.resolve()))
        storage = register_browser_storage(settings, sessions, tmp_path / "ConnLabFiles", overrides)
        assert storage.locations["Template"] == link
        assert "Template" in storage.unavailable
        assert any(str(link) in warning for warning in storage.warnings)
        assert list(outside.iterdir()) == [sentinel] and sentinel.read_bytes() == b"preserve"
    finally:
        link.rmdir()
