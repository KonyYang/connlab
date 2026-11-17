"""Finite migration uses synthetic folders and a test SQLite database only."""
from dataclasses import replace
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.shared.config import Settings
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel, ProjectOfficialWorkspaceRecordModel, FileAssetModel
from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel, MaterialArchiveFileModel
from backend.infrastructure.project_library.files import LibraryFiles, atomic_json, identity, inventory
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from scripts.migrate_local_development_materials import DevelopmentRelocation, Relocation


@pytest.fixture
def relocation(portable_tmp_path):
    root=portable_tmp_path
    data=root/"data";data.mkdir()
    settings=Settings(data,root/"old-projects",root/"templates",data/"test.sqlite3",output_root=root/"new")
    engine=create_engine(f"sqlite:///{settings.database_path}")
    init_db(engine)
    source=settings.projects_dir/"DL-2026-11-013"
    business=source/"DL-2026-11-013 files";business.mkdir(parents=True)
    (source/"Source Book").mkdir()
    (business/"人工记录.txt").write_text("human data",encoding="utf-8")
    with Session(engine) as session:
        session.add(ProjectModel(project_id="p",project_no="DL-2026-11-013",product_name="T3BIGM FBB to GPU(Power)",requestor="fixture",status="draft",registry_state="trash"))
        session.flush()
        session.add(ProjectOfficialWorkspaceRecordModel(workspace_id="w",project_id="p",dl_number="DL-2026-11-013",local_workspace_path=str(source),official_folder_path=str(business),source_book_path=str(source/"Source Book"),manifest_path=str(source/".connlab/manifest.json"),created_at="fixture"))
        session.add(FileAssetModel(asset_id="asset",project_id="p",asset_type="record",path=str(business/"人工记录.txt")))
        session.add(ProjectLibraryMemberModel(member_id="m",project_id="p",ltr_number="DL-2026-11-013",title="T3BIGM FBB to GPU(Power) Qualification test",folder_path=str(source),source_path="untouched-original",created_at="fixture"))
        session.commit()
        files=LibraryFiles(settings)
        files.write_marker(ProjectLibraryRepository(session).member("m"))
        atomic_json(source/".connlab/manifest.json",dict(project_id="p",dl_number="DL-2026-11-013",official_folder_identity=identity(business)))
        archive=root/"old-materials/旧资料";archive.mkdir(parents=True);(archive/"report.txt").write_text("archived",encoding="utf-8")
        store=MaterialArchiveRepository(session)
        store.register(archive.parent,archive,"old-number","Old title",folder_id="a")
        session.add(MaterialArchiveFileModel(catalog_key="archive:a",relative_path="report.txt",name="report.txt"));session.commit()
        MaterialReceiptRepository(session).configure(str(archive.parent))
    temp=root/"old-temp/临时资料";temp.mkdir(parents=True);(temp/"application.txt").write_bytes(b"draft")
    rows=[Relocation("project","m",source,root/"new/Projects"/source.name),Relocation("archive","a",archive,root/"new/Materials"/archive.name),Relocation("temporary","temp",temp,root/"new/TemporaryMaterials"/temp.name)]
    coordinator=DevelopmentRelocation(settings,engine,rows,root/"recovery")
    yield coordinator,settings,engine,rows
    engine.dispose()


def test_copy_rebind_keeps_business_identity_status_bytes_and_old_copies(relocation):
    coordinator,settings,engine,rows=relocation
    before={row.key:inventory(row.source) for row in rows}
    with pytest.raises(ValueError,match="writers"):
        coordinator.apply()
    result=coordinator.apply(writers_stopped=True)
    assert result["status"]=="completed"
    assert Path(result["database_backup"]).is_file()
    assert all(inventory(row.source)==before[row.key] for row in rows)
    with Session(engine) as session:
        project=session.get(ProjectModel,"p")
        member=session.get(ProjectLibraryMemberModel,"m")
        assert project.product_name=="T3BIGM FBB to GPU(Power)" and project.status=="draft" and project.registry_state=="trash"
        assert member.title=="T3BIGM FBB to GPU(Power) Qualification test"
        assert member.source_path=="untouched-original" and member.revision==2
        assert session.get(FileAssetModel,"asset").path==str(rows[0].target/"DL-2026-11-013 files/人工记录.txt")
        assert MaterialArchiveRepository(session).indexed_files("archive:a")[0]["relative_path"]=="report.txt"
        assert MaterialReceiptRepository(session).settings()["root_path"]==str(rows[1].target.parent)
    assert coordinator.apply(writers_stopped=True)["status"]=="completed"
    assert (rows[0].target/"DL-2026-11-013 files/人工记录.txt").read_text(encoding="utf-8")=="human data"


def test_existing_target_blocks_before_backup_or_reference_changes(relocation):
    coordinator,settings,engine,rows=relocation
    rows[0].target.mkdir(parents=True)
    (rows[0].target/"human.txt").write_bytes(b"existing")
    with pytest.raises(ValueError,match="Destination conflict"):
        coordinator.prepare()
    assert not coordinator.evidence.exists()
    with Session(engine) as session:
        assert session.get(ProjectLibraryMemberModel,"m").folder_path==str(rows[0].source)
    assert (rows[0].target/"human.txt").read_bytes()==b"existing"


def test_interrupted_location_publication_uses_original_plan_and_one_revision(relocation,monkeypatch):
    coordinator,settings,engine,rows=relocation
    original=LibraryFiles.publish_workspace_metadata
    def fail(*args): raise OSError("fixture interruption after DB commit")
    monkeypatch.setattr(LibraryFiles,"publish_workspace_metadata",fail)
    with pytest.raises(OSError,match="fixture interruption"):
        coordinator.apply(writers_stopped=True)
    plan=json.loads(coordinator.journal.read_text(encoding="utf-8"))["items"][0]["plan"]
    monkeypatch.setattr(LibraryFiles,"publish_workspace_metadata",original)
    coordinator.apply(writers_stopped=True)
    after=json.loads(coordinator.journal.read_text(encoding="utf-8"))["items"][0]["plan"]
    assert plan==after
    with Session(engine) as session: assert session.get(ProjectLibraryMemberModel,"m").revision==2



def test_interrupted_copy_never_adopts_an_existing_target_even_with_matching_bytes(relocation,monkeypatch):
    coordinator,settings,engine,rows=relocation
    import scripts.migrate_local_development_materials as migration
    original=migration.copy_verified
    def interrupted(*args):
        original(*args)
        raise OSError("fixture copy response lost before ownership checkpoint")
    monkeypatch.setattr(migration,"copy_verified",interrupted)
    with pytest.raises(OSError):coordinator.apply(writers_stopped=True)
    monkeypatch.setattr(migration,"copy_verified",original)
    with pytest.raises(ValueError,match="ownership"):
        coordinator.apply(writers_stopped=True)
    with Session(engine) as session:
        assert session.get(ProjectLibraryMemberModel,"m").folder_path==str(rows[0].source)
    assert (rows[0].target/"DL-2026-11-013 files/人工记录.txt").read_text(encoding="utf-8")=="human data"



def test_cold_coordinator_registers_complete_models_without_bootstrapping_schema(relocation):
    import hashlib
    import os
    import sqlite3
    from contextlib import closing
    import subprocess
    import sys
    coordinator,settings,engine,rows=relocation
    engine.dispose()
    def schema():
        with closing(sqlite3.connect(settings.database_path)) as connection:
            return connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
    def digest(): return hashlib.sha256(settings.database_path.read_bytes()).hexdigest()
    original_schema=schema()
    original_source={row.key:inventory(row.source) for row in rows}
    payload=dict(data=str(settings.data_dir),projects=str(settings.projects_dir),templates=str(settings.templates_dir),
        database=str(settings.database_path),output=str(settings.output_root),evidence=str(coordinator.evidence),
        rows=[dict(kind=row.kind,key=row.key,source=str(row.source),target=str(row.target)) for row in rows])
    code=r"""
import json,sys
from pathlib import Path
from sqlalchemy import event
from backend.shared.config import Settings
from backend.infrastructure.storage import database
from scripts.migrate_local_development_materials import DevelopmentRelocation,Relocation
p=json.loads(sys.argv[1]);phase=sys.argv[2]
settings=Settings(Path(p['data']),Path(p['projects']),Path(p['templates']),Path(p['database']),output_root=Path(p['output']))
def forbidden(*args,**kwargs):raise AssertionError('Cold relocation must never initialize or migrate the source schema.')
database.init_db=forbidden
database.Base.metadata.create_all=forbidden
engine=database.create_database_engine(settings)
statements=[]
@event.listens_for(engine,'before_cursor_execute')
def reject_source_writes(connection,cursor,statement,parameters,context,executemany):
 word=statement.lstrip().split(None,1)[0].upper()
 assert word not in {'CREATE','ALTER','DROP','VACUUM','REINDEX','ATTACH','DETACH'},statement
 if phase!='apply':assert word not in {'INSERT','UPDATE','DELETE','REPLACE'},statement
 statements.append(word)
try:
 rows=[Relocation(row['kind'],row['key'],Path(row['source']),Path(row['target'])) for row in p['rows']]
 coordinator=DevelopmentRelocation(settings,engine,rows,Path(p['evidence']))
 result=coordinator.prepare() if phase=='prepare' else coordinator.apply(writers_stopped=True) if phase=='apply' else coordinator.verify()
 with engine.connect() as connection:
  names=set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").scalars())
  sqlite_table_count=connection.exec_driver_sql("SELECT count(*) FROM sqlite_master WHERE type='table'").scalar_one()
 assert names.issubset(database.Base.metadata.tables)
 print(json.dumps(dict(phase=phase,status=result['status'],table_count=len(names),sqlite_table_count=sqlite_table_count,metadata_complete=True,source_statements=sorted(set(statements)))))
finally:engine.dispose()
"""
    environment={**os.environ,"PYTHONUTF8":"1","PYTHONDONTWRITEBYTECODE":"1"}
    results=[]
    for phase in ('prepare','apply','verify'):
        before=digest()
        run=subprocess.run([sys.executable,'-c',code,json.dumps(payload),phase],cwd=Path(__file__).resolve().parents[2],
            env=environment,capture_output=True,text=True,encoding='utf-8',timeout=60)
        assert run.returncode==0,run.stdout+run.stderr
        result=json.loads(run.stdout.strip().splitlines()[-1]);results.append(result)
        assert result['metadata_complete']
        assert schema()==original_schema
        if phase!='apply':assert digest()==before
        if phase=='prepare':
            assert result['status']=='prepared'
            assert Path(json.loads(coordinator.journal.read_text(encoding='utf-8'))['database_backup']).is_file()
            assert not any(row.target.exists() for row in rows)
        else:assert result['status']=='completed'
        assert all(inventory(row.source)==original_source[row.key] for row in rows)
    (coordinator.evidence/'cold-process-validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
