from pathlib import Path
from types import SimpleNamespace
import pytest
from backend.shared.config import Settings
from backend.domain import ExternalResourceType


def test_explicit_environment_defaults_are_lazy_and_keep_internal_storage(portable_tmp_path, monkeypatch):
    monkeypatch.setenv("CONNLAB_ENVIRONMENT", "release")
    for key in ["CONNLAB_DATA_DIR", "CONNLAB_PROJECTS_DIR", "CONNLAB_DATABASE_PATH", "CONNLAB_LOCAL_CONFIG_PATH", "CONNLAB_ADMIN_CONFIG_PATH"]:
        monkeypatch.delenv(key, raising=False)
    settings = Settings.load(base_dir=portable_tmp_path)
    assert settings.environment == "release"
    assert settings.projects_dir == Path("D:/ConnLab/Projects")
    assert settings.output_path("Materials") == Path("D:/ConnLab/Materials")
    assert settings.output_path("TemporaryMaterials") == Path("D:/ConnLab/TemporaryMaterials")
    assert settings.data_dir == portable_tmp_path / "data"
    assert settings.database_path == portable_tmp_path / "data/connlab.sqlite3"
    assert not (portable_tmp_path / "projects").exists()
    assert not (portable_tmp_path / "templates").exists()


def test_missing_default_is_created_once_but_configured_offline_is_not_recreated(portable_tmp_path):
    from backend.application.default_storage_locations import DefaultStorageLocations
    from backend.infrastructure.files.default_storage_directory import DefaultStorageDirectory
    class Resources:
        value = None
        def get_by_type(self, kind): return self.value
        def create_default_if_absent(self, value): self.value = self.value or value; return self.value
    resources = Resources()
    settings = Settings(data_dir=portable_tmp_path/"data", projects_dir=portable_tmp_path/"output/Projects", templates_dir=portable_tmp_path/"templates", database_path=portable_tmp_path/"data/db.sqlite3", output_root=portable_tmp_path/"output")
    defaults = DefaultStorageLocations(settings, resources, DefaultStorageDirectory())
    root = defaults.ensure(ExternalResourceType.TEMPORARY_MATERIALS_ROOT)
    assert root == portable_tmp_path/"output/TemporaryMaterials"
    assert root.is_dir()
    root.rmdir()
    with pytest.raises(ValueError, match="Settings"):
        defaults.ensure(ExternalResourceType.TEMPORARY_MATERIALS_ROOT)
    assert not root.exists()


def test_fresh_release_does_not_bootstrap_optional_administrator_file(portable_tmp_path, monkeypatch):
    monkeypatch.setenv("CONNLAB_ENVIRONMENT", "release")
    administrator = portable_tmp_path/"administrator/config/connlab.admin.toml"
    monkeypatch.setenv("CONNLAB_ADMIN_CONFIG_PATH", str(administrator))
    value=Settings.load(base_dir=portable_tmp_path)
    assert not administrator.exists()
    assert value.ltr_workbook.modify_password is None
    assert value.ltr_workbook.write_enabled is False


def test_release_without_readable_credentials_keeps_other_features_available_but_disables_workbook_writes(portable_tmp_path, monkeypatch):
    monkeypatch.setenv("CONNLAB_ENVIRONMENT", "release")
    monkeypatch.setenv("CONNLAB_ADMIN_CONFIG_PATH", str(portable_tmp_path/"missing/admin.toml"))
    config=portable_tmp_path/"local.toml"
    config.write_text('[ltr_workbook]\nwrite_enabled = true\nmode = "excel_com"\n',encoding="utf-8")
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH",str(config))
    value=Settings.load(base_dir=portable_tmp_path)
    assert not value.ltr_workbook.write_enabled
    assert value.data_dir.is_dir()


@pytest.mark.parametrize("first,second",[("development","release"),("release","development")])
def test_explicit_entries_replace_only_their_inherited_managed_defaults(first,second,monkeypatch,portable_tmp_path):
    from backend.shared.runtime_environment import apply_entry_defaults
    names=["CONNLAB_DATA_DIR","CONNLAB_DATABASE_PATH","CONNLAB_LOCAL_CONFIG_PATH","CONNLAB_LOGS_DIR"]
    for name in names:monkeypatch.delenv(name,raising=False)
    monkeypatch.delenv("CONNLAB_MANAGED_ENV_DEFAULTS",raising=False)
    old={name:portable_tmp_path/first/name for name in names}
    new={name:portable_tmp_path/second/name for name in names}
    apply_entry_defaults(first,old)
    apply_entry_defaults(second,new)
    import os
    assert all(os.environ[name]==str(value) for name,value in new.items())
    assert os.environ["CONNLAB_ENVIRONMENT"]==second
    explicit=portable_tmp_path/"operator-selected"
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH",str(explicit))
    apply_entry_defaults(first,old)
    assert os.environ["CONNLAB_LOCAL_CONFIG_PATH"]==str(explicit)


def test_real_entries_revoke_inherited_config_before_resolving_library(portable_tmp_path, monkeypatch):
    from backend.api.development import apply_development_environment_defaults
    from backend.desktop.runtime_paths import apply_packaged_environment_defaults, build_packaged_runtime_paths
    import os
    for key in list(os.environ):
        if key.startswith("CONNLAB_"): monkeypatch.delenv(key, raising=False)
    dev=portable_tmp_path/"dev"
    dev.mkdir()
    dev_library=portable_tmp_path/"dev-library"
    (dev/"connlab.local.toml").write_text('[paths]\nlibrary_root = "'+dev_library.as_posix()+'"\n', encoding="utf-8")
    release=build_packaged_runtime_paths(app_root=portable_tmp_path/"release", user_root=portable_tmp_path/"user")
    release.config_dir.mkdir(parents=True)
    release_library=portable_tmp_path/"release-library"
    release.local_config_path.write_text('[paths]\nlibrary_root = "'+release_library.as_posix()+'"\n', encoding="utf-8")
    apply_development_environment_defaults(dev)
    assert Settings.load(base_dir=dev).data_dir==dev_library/"Data"
    apply_packaged_environment_defaults(release)
    assert os.environ["CONNLAB_LOCAL_CONFIG_PATH"]==str(release.local_config_path)
    assert Settings.load(base_dir=release.app_root).data_dir==release_library/"Data"
    assert os.environ["CONNLAB_LIBRARY_ROOT"]==str(release_library)
    apply_development_environment_defaults(dev)
    assert Settings.load(base_dir=dev).data_dir==dev_library/"Data"
    assert os.environ["CONNLAB_LIBRARY_ROOT"]==str(dev_library)
    # An explicit operator override remains valid across entry preparation.
    explicit=portable_tmp_path/"explicit.toml"
    explicit.write_text('[paths]\nlibrary_root = "'+(portable_tmp_path/"explicit-library").as_posix()+'"\n', encoding="utf-8")
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH",str(explicit))
    apply_packaged_environment_defaults(release)
    assert Settings.load(base_dir=release.app_root).data_dir==portable_tmp_path/"explicit-library/Data"


def test_derived_projects_under_a_new_library_are_created_on_first_use(portable_tmp_path,monkeypatch):
    from backend.application.default_storage_locations import DefaultStorageLocations
    from backend.infrastructure.files.default_storage_directory import DefaultStorageDirectory
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from backend.infrastructure.storage.database import init_db
    from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository
    monkeypatch.setenv("CONNLAB_ENVIRONMENT","release")
    monkeypatch.setenv("CONNLAB_LIBRARY_ROOT",str(portable_tmp_path/"library"))
    settings=Settings.load(base_dir=portable_tmp_path)
    assert not settings.projects_dir.exists()
    engine=create_engine(f"sqlite:///{settings.database_path}");init_db(engine)
    try:
        with Session(engine) as session:
            resources=ExternalResourceRepository(session)
            locations=DefaultStorageLocations(settings,resources,DefaultStorageDirectory())
            root=locations.ensure(ExternalResourceType.PROJECT_OUTPUT_ROOT)
            assert root==settings.projects_dir and root.is_dir()
            session.commit()
        with Session(engine) as session:
            assert ExternalResourceRepository(session).get_by_type(ExternalResourceType.PROJECT_OUTPUT_ROOT).path==root
    finally:engine.dispose()


@pytest.mark.parametrize("failure",["drive_missing","permission"])
def test_default_directory_failure_is_actionable_and_never_falls_back(portable_tmp_path,monkeypatch,failure):
    from backend.infrastructure.files.default_storage_directory import DefaultStorageDirectory
    root=portable_tmp_path/"new-output/Materials"
    if failure=="drive_missing":
        original=Path.is_dir
        monkeypatch.setattr(Path,"is_dir",lambda path:False if path==Path(root.anchor) else original(path))
    else:
        original=Path.mkdir
        def mkdir(path,*args,**kwargs):
            if path==root: raise PermissionError("fixture unwritable")
            return original(path,*args,**kwargs)
        monkeypatch.setattr(Path,"mkdir",mkdir)
    with pytest.raises(ValueError,match="Settings"):
        DefaultStorageDirectory().create(root)
    assert not root.exists()


def test_release_unreadable_admin_configuration_does_not_block_other_features(portable_tmp_path,monkeypatch):
    monkeypatch.setenv("CONNLAB_ENVIRONMENT","release")
    admin=portable_tmp_path/"admin.toml";admin.write_text('[ltr_workbook]\nmodify_password="fixture-only"\n',encoding="utf-8")
    monkeypatch.setenv("CONNLAB_ADMIN_CONFIG_PATH",str(admin))
    before=admin.read_bytes()
    value=Settings.load(base_dir=portable_tmp_path)
    assert value.ltr_workbook.modify_password=="fixture-only" and admin.read_bytes()==before
    original=Path.open
    def deny(path,*args,**kwargs):
        if path==admin: raise PermissionError("fixture denied")
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,"open",deny)
    value=Settings.load(base_dir=portable_tmp_path)
    assert value.ltr_workbook.modify_password is None and not value.ltr_workbook.write_enabled
