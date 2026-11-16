"""Isolated cleanup/recovery contracts; never point fixtures at business data."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import pytest

SPEC = importlib.util.spec_from_file_location("cleanup_tool", Path(__file__).parents[2] / "scripts/legacy_import_cleanup.py")
cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleanup)


@pytest.fixture
def cleanup_case(portable_tmp_path):
    root = portable_tmp_path / "copies"
    root.mkdir()
    source = portable_tmp_path / "original"
    source.mkdir()
    (source / "报告.txt").write_text("original", encoding="utf-8")
    target = root / "DL-2026-04-003"
    target.mkdir()
    (target / "报告.txt").write_text("original", encoding="utf-8")
    db = portable_tmp_path / "store.db"
    with sqlite3.connect(db) as conn:
        conn.executescript("""
        CREATE TABLE projects(project_id TEXT PRIMARY KEY, status TEXT);
        CREATE TABLE project_library_members(member_id TEXT PRIMARY KEY, project_id TEXT, folder_path TEXT, source_path TEXT, source_project_id TEXT, batch_id TEXT, revision INTEGER);
        CREATE TABLE project_library_batches(batch_id TEXT PRIMARY KEY,payload_json TEXT);
        CREATE TABLE project_official_workspace_records(workspace_id TEXT PRIMARY KEY, project_id TEXT, local_workspace_path TEXT);
        CREATE TABLE material_archive_folders(folder_id TEXT PRIMARY KEY,folder_path TEXT);
        CREATE TABLE material_archive_files(catalog_key TEXT,relative_path TEXT, PRIMARY KEY(catalog_key,relative_path));
        CREATE TABLE library_report_shortcuts(catalog_key TEXT,role TEXT,PRIMARY KEY(catalog_key,role));
        CREATE TABLE project_lifecycle_events(event_id TEXT PRIMARY KEY,project_id TEXT);
        """)
        conn.execute("INSERT INTO projects VALUES('p','draft')")
        conn.execute("INSERT INTO project_library_members VALUES('m','p',?,?,NULL,'b',1)", (str(target),str(source)))
        conn.execute("INSERT INTO project_library_batches VALUES('b',?)", (json.dumps({'status':'completed'}),))
        conn.execute("INSERT INTO project_official_workspace_records VALUES('w','p',?)",(str(target),))
        conn.execute("INSERT INTO material_archive_folders VALUES('f',?)",(str(target),))
        conn.execute("INSERT INTO material_archive_files VALUES('project:p','报告.txt')")
    unit={'folder':target.name,'path':str(target),'members':[{'member_id':'m','project_id':'p','folder_path':str(target),'source_path':str(source),'source_project_id':None,'batch_id':'b','revision':1}], 'project_ids':['p'],'projects':[{'project_id':'p','status':'draft'}],'workspaces':[{'workspace_id':'w','project_id':'p','local_workspace_path':str(target)}], 'archive_indexes':[{'folder_id':'f','folder_path':str(target)}], 'file_index_counts':{'project:p':1},'report_shortcuts':[], 'disk':{'status':'complete','files':{'报告.txt':{'relative_path':'报告.txt','size':8,'sha256':cleanup.digest(source/'报告.txt')}}},'comparisons':[{'source':{'path':str(source),'status':'complete','files':{'报告.txt':{'relative_path':'报告.txt','size':8,'sha256':cleanup.digest(source/'报告.txt')}}}}]}
    facts={'root':str(root),'database':str(db),'units':[unit]}
    return facts, target, source, db


def test_backup_precedes_unlink_and_recycle_and_original_is_untouched(portable_tmp_path, cleanup_case):
    facts,target,source,db=cleanup_case
    run=portable_tmp_path/'backup'
    # Fixtures exercise the same executor with their own bounded authorization.
    cleanup.prepare(facts, run, authorization={target.name:('m','p')})
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1
    recycled=[]
    def recycle(path, record):
        assert (run/'database.sqlite3').is_file()
        assert (run/'directories'/target.name/'报告.txt').read_text(encoding='utf-8')=='original'
        with sqlite3.connect(db) as conn:
            assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==0
        binpath=portable_tmp_path/'recycled'
        path.rename(binpath)
        record({'source':str(path),'recycled_path':str(binpath)})
        recycled.append(str(path))
    cleanup.apply(run, recycler=recycle)
    cleanup.apply(run, recycler=recycle)
    assert len(recycled)==1
    assert (source/'报告.txt').read_text(encoding='utf-8')=='original'
    assert cleanup.verify(run)['status']=='completed'
    cleanup.restore_associations(run)
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1
    with pytest.raises(cleanup.CleanupError):
        cleanup.restore_associations(run)


def test_windows_adapter_returns_real_system_recycle_item(portable_tmp_path):
    import os
    if os.name != "nt":
        pytest.skip("Windows Shell required")
    from backend.infrastructure.files.windows_recycle import recycle_directory
    target=portable_tmp_path/"系统回收隔离测试"
    target.mkdir()
    (target/"empty").mkdir()
    (target/"核验.txt").write_text("recycle probe",encoding="utf-8")
    receipts=[]
    recycle_directory(target, receipts.append)
    assert not target.exists()
    assert len(receipts)==1
    recycled=Path(receipts[0]['recycled_path'])
    assert "$recycle.bin" in str(recycled).casefold()
    assert (recycled/"核验.txt").read_text(encoding="utf-8")=="recycle probe"
    assert (recycled/"empty").is_dir()


@pytest.mark.parametrize("change", ["target", "source", "backup", "new_business", "new_path_reference"])
def test_stale_or_unverified_cleanup_retains_all_live_data(portable_tmp_path, cleanup_case, change):
    facts,target,source,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    if change=='target':
        (target/'报告.txt').write_text('manual edit',encoding='utf-8')
    elif change=='source':
        (source/'报告.txt').write_text('source edit',encoding='utf-8')
    elif change=='backup':
        (run/'directories'/target.name/'报告.txt').write_text('bad backup',encoding='utf-8')
    else:
        with sqlite3.connect(db) as conn:
            if change=='new_business':
                conn.execute('CREATE TABLE test_business(id TEXT PRIMARY KEY, project_id TEXT)')
                conn.execute("INSERT INTO test_business VALUES('important','p')")
            else:
                conn.execute('CREATE TABLE test_reference(id TEXT PRIMARY KEY, folder_path TEXT)')
                conn.execute('INSERT INTO test_reference VALUES(?,?)',('outside',str(target)))
    called=[]
    with pytest.raises(cleanup.CleanupError):
        cleanup.apply(run,recycler=lambda *args:called.append(args))
    assert not called
    assert target.exists()
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1


def test_database_failure_rolls_back_prior_deletes(portable_tmp_path, cleanup_case, monkeypatch):
    facts,target,_,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    real_connect=cleanup.connect
    def failing_connect(path,**kwargs):
        conn=real_connect(path,**kwargs)
        if kwargs.get('writable'):
            conn.set_authorizer(lambda action,arg1,*rest: sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_DELETE and arg1=='projects' else sqlite3.SQLITE_OK)
        return conn
    monkeypatch.setattr(cleanup,'connect',failing_connect)
    with pytest.raises(sqlite3.DatabaseError):
        cleanup.apply(run,recycler=lambda *args:pytest.fail('must not recycle'))
    assert target.exists()
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1
        assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==1


def test_recycle_failure_retains_backup_and_resume_keeps_other_project_updates(portable_tmp_path, cleanup_case):
    facts,target,source,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    def unavailable(*args):
        raise OSError('recycle unavailable')
    with pytest.raises(OSError):
        cleanup.apply(run,recycler=unavailable)
    assert target.exists()
    assert (run/'directories'/target.name/'报告.txt').read_text(encoding='utf-8')=='original'
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO projects VALUES('other','important concurrent write')")
    def finish(path,record):
        destination=portable_tmp_path/'test-bin'
        path.rename(destination)
        record({'source':str(path),'recycled_path':str(destination)})
    assert cleanup.apply(run,recycler=finish)['status']=='completed'
    cleanup.restore_associations(run)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT status FROM projects WHERE project_id='other'").fetchone()[0]=='important concurrent write'
        assert conn.execute('SELECT count(*) FROM projects').fetchone()[0]==2


def test_process_death_after_receipt_does_not_recycle_twice(portable_tmp_path, cleanup_case):
    import subprocess
    import sys
    facts,target,_,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    worker=portable_tmp_path/'crash_worker.py'
    worker.write_text("import sys,os,importlib.util\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nspec=importlib.util.spec_from_file_location('tool',Path(sys.argv[1])/'scripts/legacy_import_cleanup.py')\ntool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)\ndef recycle(path,record):\n destination=Path(sys.argv[3]);path.rename(destination);record({'source':str(path),'recycled_path':str(destination)});os._exit(73)\ntool.apply(Path(sys.argv[2]),recycler=recycle)\n",encoding='utf-8')
    result=subprocess.run([sys.executable,str(worker),str(Path(__file__).parents[2]),str(run),str(portable_tmp_path/'test-bin')],capture_output=True,text=True)
    assert result.returncode==73,result.stderr
    assert cleanup.apply(run,recycler=lambda *args:pytest.fail('receipt must suppress repeat'))['status']=='completed'
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==0


def test_new_lifecycle_audit_after_preview_must_not_be_deleted(portable_tmp_path, cleanup_case):
    facts,target,_,db=cleanup_case
    facts['units'][0]['db_counts']={'p':{'projects':1,'project_library_members':1,'project_official_workspace_records':1}}
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO project_lifecycle_events VALUES('new important audit','p')")
    with pytest.raises(cleanup.CleanupError,match='relation count'):
        cleanup.prepare(facts,portable_tmp_path/'backup',authorization={target.name:('m','p')})
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_lifecycle_events').fetchone()[0]==1


def test_deleted_database_state_must_not_ignore_a_new_folder_association(portable_tmp_path, cleanup_case):
    facts,target,source,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    with pytest.raises(OSError):
        cleanup.apply(run,recycler=lambda *args:(_ for _ in ()).throw(OSError('interrupted')))
    with sqlite3.connect(db) as conn:
        conn.execute('INSERT INTO material_archive_folders VALUES(?,?)',('new folder key',str(target)))
    with pytest.raises(cleanup.CleanupError,match='reference'):
        cleanup.apply(run,recycler=lambda *args:pytest.fail('do not recycle a newly associated folder'))
    assert target.exists()


def test_database_only_remainder_has_no_file_operation(portable_tmp_path, cleanup_case):
    facts,target,source,db=cleanup_case
    ghost=target.parent/'missing old registration'
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE project_library_members SET project_id=NULL,folder_path=?',(str(ghost),))
    unit=facts['units'][0]
    unit.update(folder=ghost.name,path=str(ghost),project_ids=[],projects=[],workspaces=[],archive_indexes=[],file_index_counts={'member:m':0},disk={'status':'missing','files':{}},comparisons=[])
    unit['members'][0].update(project_id=None,folder_path=str(ghost))
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={ghost.name:('m',None)})
    result=cleanup.apply(run,recycler=lambda *args:pytest.fail('ghost must not touch files'))
    assert result['directories_recycled']==0
    assert (target/'报告.txt').read_text(encoding='utf-8')=='original'
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM projects').fetchone()[0]==1
        assert conn.execute('SELECT count(*) FROM material_archive_files').fetchone()[0]==1


def test_backup_copy_failure_never_unlinks_database(portable_tmp_path, cleanup_case, monkeypatch):
    facts,target,source,db=cleanup_case
    def fail(*args):
        raise OSError('backup device unavailable')
    monkeypatch.setattr(cleanup,'copy_verified',fail)
    with pytest.raises(OSError):
        cleanup.prepare(facts,portable_tmp_path/'backup',authorization={target.name:('m','p')})
    assert target.exists()
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT count(*) FROM project_library_members').fetchone()[0]==1


def test_incoming_cascade_outside_approved_rows_blocks_cleanup(portable_tmp_path, cleanup_case):
    facts,target,source,db=cleanup_case
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE unrelated(child_id TEXT PRIMARY KEY, owner TEXT REFERENCES project_official_workspace_records(workspace_id) ON DELETE CASCADE)')
        conn.execute("INSERT INTO unrelated VALUES('keep me','w')")
    with pytest.raises(cleanup.CleanupError,match='foreign-key reference'):
        cleanup.prepare(facts,portable_tmp_path/'backup',authorization={target.name:('m','p')})
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT child_id FROM unrelated').fetchone()[0]=='keep me'


def test_existing_workspace_locks_block_cleanup(portable_tmp_path, cleanup_case):
    from backend.infrastructure.files.generation_journal import GenerationJournal
    facts,target,source,db=cleanup_case
    run=portable_tmp_path/'backup'
    cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    journal=GenerationJournal(db.parent/'project_library'/'locks')
    with journal.lock('materials-archive'):
        with pytest.raises(ValueError,match='already running'):
            cleanup.apply(run,recycler=lambda *args:pytest.fail('must not recycle while scanning'))
    assert target.exists()


def test_full_current_schema_lifecycle_audit_is_exported_and_selectively_restored(portable_tmp_path, cleanup_case):
    from sqlalchemy import create_engine
    from backend.infrastructure.storage.database import init_db
    facts,target,source,db=cleanup_case
    actual=portable_tmp_path/'actual-schema.db'
    engine=create_engine('sqlite:///'+actual.as_posix())
    init_db(engine)
    engine.dispose()
    with sqlite3.connect(actual) as conn:
        conn.execute("INSERT INTO projects(project_id,product_name,requestor,status,lifecycle_state) VALUES('p','fixture','operator','draft','active')")
        conn.execute("INSERT INTO project_library_members(member_id,project_id,title,folder_path,source_path,batch_id,revision,created_at) VALUES('m','p','fixture',?,?,'b',1,'now')",(str(target),str(source)))
        conn.execute("INSERT INTO project_library_batches VALUES('b',?)",(json.dumps({'status':'completed'}),))
        conn.execute("INSERT INTO project_official_workspace_records(workspace_id,project_id,dl_number,local_workspace_path,source_book_path,official_folder_path,manifest_path,created_at) VALUES('w','p','fixture',?,?,?,?,'now')",(str(target),str(target/'Source Book'),str(target/'official'),str(target/'.connlab/manifest.json')))
        conn.execute("INSERT INTO material_archive_folders(folder_id,normalized_path,library_root,folder_path,title,indexed_available) VALUES('f',?,'',?,'fixture',1)",(cleanup.norm(target),str(target)))
        conn.execute("INSERT INTO material_archive_files VALUES('project:p','报告.txt','报告.txt',NULL)")
        conn.execute("INSERT INTO project_lifecycle_events(event_id,project_id,event_type,previous_lifecycle_state,new_lifecycle_state,created_at,metadata_json) VALUES('audit','p','reopen','closed','active','now','{\"reason\":\"保留审计\"}')")
    facts['database']=str(actual)
    facts['units'][0]['db_counts']={'p':{'projects':1,'project_library_members':1,'project_official_workspace_records':1,'project_lifecycle_events':1}}
    run=portable_tmp_path/'backup'
    manifest=cleanup.prepare(facts,run,authorization={target.name:('m','p')})
    assert manifest['relations']['delete_rows']['project_lifecycle_events'][0]['metadata_json']=='{"reason":"保留审计"}'
    def recycle(path,record):
        destination=portable_tmp_path/'test-bin'
        path.rename(destination)
        record({'source':str(path),'recycled_path':str(destination)})
    assert cleanup.apply(run,recycler=recycle)['status']=='completed'
    cleanup.restore_associations(run)
    with sqlite3.connect(actual) as conn:
        assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert conn.execute('SELECT metadata_json FROM project_lifecycle_events').fetchone()[0]=='{"reason":"保留审计"}'
