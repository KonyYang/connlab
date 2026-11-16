"""Single-item cleanup contracts against isolated directories and the current schema."""
import json
from pathlib import Path
import sqlite3

import pytest
from scripts import legacy_import_cleanup as engine


FOLDER = "DL-2026-11-013 [56cdd25d]"
MEMBER = "33043ab04dfb4bb484e2d9f30a0422ca"
CACHE = "9b8d61be32ba41ef8186b172edb4256f"
BATCH = "3cf6adc1df33432686200577226889b6"


@pytest.fixture
def single_copy(portable_tmp_path):
    from sqlalchemy import create_engine
    from backend.infrastructure.storage.database import init_db
    root = portable_tmp_path / "copies"
    root.mkdir()
    source = portable_tmp_path / "original"
    source.mkdir()
    target = root / FOLDER
    target.mkdir()
    (target / ".connlab").mkdir()
    (target / ".connlab/library.json").write_text(json.dumps({"member_id": MEMBER, "project_id": None}), encoding="utf-8")
    for n in range(26):
        name = f"资料{n:02}.txt"
        (source/name).write_text(f"original {n}", encoding="utf-8")
        (target/name).write_text(f"original {n}", encoding="utf-8")
    (source/"additional-report.txt").write_text("source only", encoding="utf-8")
    peer = root/"DL-2026-11-013"
    peer.mkdir()
    (peer/"retain.txt").write_text("keep unsuffixed directory", encoding="utf-8")
    db = portable_tmp_path/"store.db"
    sql_engine = create_engine("sqlite:///"+db.as_posix())
    init_db(sql_engine)
    sql_engine.dispose()
    payload = json.dumps({"status":"completed", "items":[{"member_id":MEMBER,"status":"added"}]})
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO projects(project_id,product_name,requestor,status,lifecycle_state) VALUES('keep-project','fixture','operator','draft','active')")
        conn.execute("INSERT INTO project_library_members(member_id,title,folder_path,source_path,batch_id,revision,created_at) VALUES(?,?,?, ?,?,1,'now')", (MEMBER,'fixture',str(target),str(source),BATCH))
        conn.execute("INSERT INTO project_library_batches VALUES(?,?)", (BATCH,payload))
        conn.execute("INSERT INTO material_archive_folders(folder_id,normalized_path,library_root,folder_path,title,indexed_available) VALUES(?,?,'',?,'fixture',1)", (CACHE,engine.norm(target),str(target)))
        conn.executemany("INSERT INTO material_archive_files VALUES(?,?,?,NULL)", [("member:"+MEMBER,f"资料{n:02}.txt",f"资料{n:02}.txt") for n in range(26)])
    with engine.connect(db) as conn:
        member=engine.rows(conn,"project_library_members")[0]
        cache=engine.rows(conn,"material_archive_folders")[0]
    def files(path):
        return {e['relative_path'].casefold():e for e in engine.inventory(path) if not e['directory']}
    unit={"folder":FOLDER,"path":str(target),"members":[member],"project_ids":[],"projects":[],"workspaces":[],
          "archive_indexes":[cache],"file_index_counts":{"member:"+MEMBER:26},"report_shortcuts":[],
          "disk":{"status":"complete","files":files(target)},
          "comparisons":[{"source":{"path":str(source),"status":"complete","files":files(source)}}]}
    return {"root":str(root),"database":str(db),"units":[unit]}, target, source, peer, db, payload


def test_actual_authorization_is_retained_in_checksummed_manifest(portable_tmp_path, single_copy):
    facts,target,*_=single_copy
    run=portable_tmp_path/"backup"
    manifest=engine.prepare(facts,run,authorization={FOLDER:(MEMBER,None)},audit_authorization="Only this independently approved copy")
    assert manifest['audit_authorization']=="Only this independently approved copy"
    assert (run/'authorization.txt').read_text(encoding='utf-8')=="Only this independently approved copy"
    assert engine.load_run(run)[0]['audit_authorization']=="Only this independently approved copy"


def test_single_copy_backup_unlink_recycle_and_resume_preserve_other_data(portable_tmp_path, single_copy):
    from scripts import renamed_import_cleanup as tool
    facts,target,source,peer,db,payload=single_copy
    run=portable_tmp_path/'backup'
    manifest=tool.prepare(facts,run)
    assert manifest['audit_authorization']==tool.AUDIT_AUTHORIZATION
    assert len(manifest['directories'])==1
    assert len(manifest['relations']['delete_rows']['material_archive_files'])==26
    assert (run/'directories'/FOLDER/'.connlab/library.json').is_file()
    calls=[]
    def recycle(path, record):
        with sqlite3.connect(db) as conn:
            assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==0
            assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==0
        destination=portable_tmp_path/'isolated-bin'
        path.rename(destination)
        record({'source':str(path),'recycled_path':str(destination)})
        calls.append(str(path))
    assert tool.apply(run,recycler=recycle)['directories_recycled']==1
    assert tool.apply(run,recycler=recycle)['status']=='completed'
    assert calls==[str(target)]
    assert (peer/'retain.txt').read_text(encoding='utf-8')=='keep unsuffixed directory'
    assert (source/'additional-report.txt').read_text(encoding='utf-8')=='source only'
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT project_id FROM projects').fetchall()==[('keep-project',)]
        assert conn.execute('SELECT payload_json FROM project_library_batches').fetchone()[0]==payload
    assert tool.verify(run)['status']=='completed'


@pytest.mark.parametrize("change", ["member", "cache", "batch", "project", "count", "folder", "extra_unit"])
def test_outside_approved_single_identity_is_rejected_before_backup(portable_tmp_path, single_copy, change):
    from copy import deepcopy
    from scripts import renamed_import_cleanup as tool
    facts,target,_,_,db,_=single_copy
    facts=deepcopy(facts)
    unit=facts['units'][0]
    if change=='member': unit['members'][0]['member_id']='other-member'
    elif change=='cache': unit['archive_indexes'][0]['folder_id']='other-cache'
    elif change=='batch': unit['members'][0]['batch_id']='other-batch'
    elif change=='project': unit['members'][0]['project_id']='keep-project'
    elif change=='count': unit['file_index_counts']['member:'+MEMBER]=27
    elif change=='folder': unit['folder']='DL-2026-11-013'
    else: facts['units'].append(deepcopy(unit))
    run=portable_tmp_path/'must-not-exist'
    with pytest.raises(engine.CleanupError,match='approved single'):
        tool.prepare(facts,run)
    assert not run.exists()
    assert target.is_dir()
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==26


def test_legacy_authorization_run_cannot_be_reused_by_new_entry(portable_tmp_path, single_copy):
    from scripts import renamed_import_cleanup as tool
    facts,target,_,_,db,_=single_copy
    run=portable_tmp_path/'legacy-run'
    manifest=engine.prepare(facts,run,authorization={FOLDER:(MEMBER,None)})
    assert manifest['audit_authorization']==engine.AUDIT_AUTHORIZATION
    with pytest.raises(engine.CleanupError,match='separately approved single-copy'):
        tool.apply(run,recycler=lambda *args:pytest.fail('must not recycle a legacy run'))
    assert target.is_dir()
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1


def test_changed_authorization_record_stops_before_unlink(portable_tmp_path, single_copy):
    from scripts import renamed_import_cleanup as tool
    facts,target,_,_,db,_=single_copy
    run=portable_tmp_path/'backup'
    tool.prepare(facts,run)
    (run/'authorization.txt').write_text('different scope',encoding='utf-8')
    with pytest.raises(engine.CleanupError,match='authorization record changed'):
        tool.apply(run,recycler=lambda *args:pytest.fail('must not recycle'))
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==26
    assert target.is_dir()


def test_selective_restore_keeps_unrelated_concurrent_project_work(portable_tmp_path, single_copy):
    from scripts import renamed_import_cleanup as tool
    facts,target,_,_,db,payload=single_copy
    run=portable_tmp_path/'backup'
    tool.prepare(facts,run)
    def unavailable(*args): raise OSError('isolated recycle unavailable')
    with pytest.raises(OSError): tool.apply(run,recycler=unavailable)
    assert target.is_dir()
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE projects SET product_name='concurrent user work' WHERE project_id='keep-project'")
    tool.restore_associations(run)
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT product_name FROM projects').fetchone()[0]=='concurrent user work'
        assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==26
        assert conn.execute('SELECT payload_json FROM project_library_batches').fetchone()[0]==payload
    with pytest.raises(engine.CleanupError,match='restored'):
        tool.apply(run,recycler=lambda *args:pytest.fail('restored run cannot be reused'))


def test_new_entry_resumes_durable_receipt_in_a_fresh_process(portable_tmp_path, single_copy):
    from scripts import renamed_import_cleanup as tool
    import subprocess
    import sys
    facts,target,_,_,db,_=single_copy
    run=portable_tmp_path/'backup'
    tool.prepare(facts,run)
    worker=portable_tmp_path/'worker.py'
    worker.write_text("import os,sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom scripts import renamed_import_cleanup as tool\ndef recycle(path,record):\n dest=Path(sys.argv[3]);path.rename(dest);record({'source':str(path),'recycled_path':str(dest)});os._exit(73)\ntool.apply(Path(sys.argv[2]),recycler=recycle)\n",encoding='utf-8')
    result=subprocess.run([sys.executable,str(worker),str(Path(__file__).parents[2]),str(run),str(portable_tmp_path/'isolated-bin')],capture_output=True,text=True)
    assert result.returncode==73,result.stderr
    assert tool.apply(run,recycler=lambda *args:pytest.fail('same receipt must suppress replay'))['status']=='completed'
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==0


def test_cli_refuses_other_database_or_root_before_any_backup(portable_tmp_path, single_copy, monkeypatch):
    from scripts import renamed_import_cleanup as tool
    import sys
    facts,target,*_=single_copy
    preview=portable_tmp_path/'preview.json'
    preview.write_text(json.dumps(facts),encoding='utf-8')
    run=portable_tmp_path/'must-not-exist'
    monkeypatch.setattr(sys,'argv',['renamed_import_cleanup.py','prepare','--preview',str(preview),'--run',str(run)])
    with pytest.raises(engine.CleanupError,match='production root/database'):
        tool.main()
    assert not run.exists()
    assert target.is_dir()
