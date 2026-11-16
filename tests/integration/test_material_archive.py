"""Archive contracts use synthetic folders and SQLite only."""
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.infrastructure.storage.database import init_db
from backend.shared.config import Settings

@pytest.fixture
def archive(tmp_path):
    from backend.application.project_library.material_archive import MaterialArchiveService
    from backend.infrastructure.project_library.material_archive_files import MaterialArchiveFiles
    from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
    data=tmp_path/'data'; data.mkdir(); root=tmp_path/'library'; root.mkdir()
    engine=create_engine(f"sqlite:///{data/'test.sqlite3'}")
    init_db(engine)
    with Session(engine) as session:
        store=MaterialArchiveRepository(session)
        store.receipts.configure(str(root))
        files=MaterialArchiveFiles(Settings(data_dir=data,projects_dir=tmp_path/'projects',templates_dir=tmp_path/'templates',database_path=data/'test.sqlite3'))
        class Catalog:
            def catalog(self): return store.catalog()
        service=MaterialArchiveService(store,files,Catalog())
        yield service,store,files,root
    engine.dispose()

def test_refresh_discovers_direct_child_without_a_fake_copy_operation(archive,tmp_path):
    service,store,files,root=archive
    folder=root/'DL-2020-01-001 Connector';folder.mkdir();(folder/'report.docx').write_bytes(b'manual')
    first=service.refresh();second=service.refresh()
    assert first['available'] and first['folders'][0]['key']==second['folders'][0]['key']
    assert first['folders'][0]['operation_id'] is None
    assert store.operations()==[]
    assert (folder/'report.docx').read_bytes()==b'manual'

def test_receive_once_preserves_structure_and_source_and_replay(archive,tmp_path):
    service,store,files,root=archive
    source=tmp_path/'Old connector';(source/'.connlab').mkdir(parents=True)
    (source/'.connlab'/'old.sqlite3').write_bytes(b'not parsed');(source/'manual.txt').write_bytes(b'human')
    plan=service.preview(str(source));assert plan['status']=='ready'
    assert not (root/source.name).exists()
    result=service.confirm(plan['plan_id'],plan['fingerprint'])
    assert result['status']=='completed'
    assert service.retry(result['batch_id'])==result
    assert (root/source.name/'manual.txt').read_bytes()==b'human'
    assert (root/source.name/'.connlab'/'old.sqlite3').read_bytes()==b'not parsed'
    assert (source/'manual.txt').read_bytes()==b'human'
    assert len(service.refresh()['folders'])==1

def test_same_name_never_compares_contents_and_independent_copy_is_explicit(archive,tmp_path):
    service,store,files,root=archive
    source=tmp_path/'Old';source.mkdir();(source/'a.txt').write_bytes(b'new')
    target=root/'Old';target.mkdir();(target/'a.txt').write_bytes(b'old')
    plan=service.preview(str(source));assert plan['status']=='conflict'
    copy=service.preview(str(source),independent=True)
    assert copy['target_path']!=str(target)
    service.confirm(copy['plan_id'],copy['fingerprint'])
    assert (target/'a.txt').read_bytes()==b'old'
    assert len(service.refresh()['folders'])==2


def fresh_process(service,files,plan,fault=None):
    import subprocess,sys,json,os
    code=r"""
import json,sys,os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.shared.config import Settings
from backend.application.project_library.material_archive import MaterialArchiveService
from backend.infrastructure.project_library.material_archive_files import MaterialArchiveFiles
from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
p=json.loads(sys.argv[1]);engine=create_engine(p['url'])
with Session(engine) as session:
 store=MaterialArchiveRepository(session)
 settings=Settings(data_dir=Path(p['data']),projects_dir=Path(p['projects']),templates_dir=Path(p['templates']),database_path=Path(p['database']))
 files=MaterialArchiveFiles(settings)
 class Catalog:
  def catalog(self):return store.catalog()
 service=MaterialArchiveService(store,files,Catalog())
 name={'stage':'new_stage','file':'publish','published':'publish_folder'}.get(p['fault'])
 if name:
  original=getattr(files,name)
  def crash(*args,**kwargs):
   value=original(*args,**kwargs);os._exit(31)
  setattr(files,name,crash)
 result=service.confirm(p['plan']['plan_id'],p['plan']['fingerprint'])
 if p['fault']=='response':os._exit(31)
 print(json.dumps(result))
"""
    payload=dict(url=str(service.store.session.bind.url),data=str(files.settings.data_dir),projects=str(files.settings.projects_dir),templates=str(files.settings.templates_dir),database=str(files.settings.database_path),plan=plan,fault=fault)
    result=subprocess.run([sys.executable,'-X','utf8','-c',code,json.dumps(payload)],capture_output=True,text=True,encoding='utf-8',cwd=Path(__file__).resolve().parents[2])
    assert result.returncode==(31 if fault else 0),result.stderr
    return json.loads(result.stdout) if not fault else None

@pytest.mark.parametrize('fault',['stage','file','published','response'])
def test_fresh_process_restart_keeps_one_final_copy_and_original_bytes(archive,tmp_path,fault):
    service,store,files,root=archive
    source=tmp_path/'Restart 中文';source.mkdir();(source/'a.txt').write_bytes(b'first');(source/'b.txt').write_bytes(b'second')
    plan=service.preview(str(source));fresh_process(service,files,plan,fault)
    op=store.operation(plan['batch_id'])
    stage=Path(op['stage_path']) if op['stage_path'] else None
    copied=stage/'a.txt' if stage and (stage/'a.txt').exists() else None
    copied_time=copied.stat().st_mtime_ns if copied else None
    result=fresh_process(service,files,plan)
    assert result['status']=='completed'
    final=Path(result['target_path'])
    assert (final/'a.txt').read_bytes()==b'first' and (final/'b.txt').read_bytes()==b'second'
    assert (source/'a.txt').read_bytes()==b'first'
    assert [path.name for path in root.iterdir() if path.name!='.connlab']==[source.name]
    if copied_time:assert (final/'a.txt').stat().st_mtime_ns==copied_time


def test_index_registration_failure_rolls_back_and_repairs_without_source_or_recopy(archive,tmp_path,monkeypatch):
    from backend.infrastructure.storage.models_project_library import MaterialArchiveFolderModel
    service,store,files,root=archive
    source=tmp_path/'Index repair';source.mkdir();(source/'a.txt').write_bytes(b'original')
    plan=service.preview(str(source));original=store.register
    def fail(*args,**kwargs):
        store.session.add(MaterialArchiveFolderModel(folder_id='bad',normalized_path='bad',library_root='',folder_path='',title=None))
        store.session.commit()
    monkeypatch.setattr(store,'register',fail)
    result=service.confirm(plan['plan_id'],plan['fingerprint'])
    assert result['status']=='incomplete' and result['phase']=='index_pending'
    final=Path(result['target_path']);stamp=(final/'a.txt').stat().st_mtime_ns
    source.rename(tmp_path/'disconnected-source')
    monkeypatch.setattr(store,'register',original)
    assert fresh_process(service,files,plan)['status']=='completed'
    assert (final/'a.txt').stat().st_mtime_ns==stamp


def test_partial_receipt_stays_visible_and_refresh_never_turns_it_into_a_complete_manual_entry(archive,tmp_path,monkeypatch):
    service,store,files,root=archive
    source=tmp_path/'Partial';source.mkdir();(source/'a.txt').write_bytes(b'a');(source/'b.txt').write_bytes(b'b')
    plan=service.preview(str(source));publish=files.publish
    def fail_one(source,target,item,identity):
        if item['relative_path']=='b.txt':raise OSError('Synthetic locked file')
        return publish(source,target,item,identity)
    monkeypatch.setattr(files,'publish',fail_one)
    op=service.confirm(plan['plan_id'],plan['fingerprint']);assert op['status']=='incomplete'
    rows=service.refresh()['folders'];assert len(rows)==1 and rows[0]['intake_status']=='incomplete'
    assert rows[0]['operation_id']==op['batch_id']
    monkeypatch.setattr(files,'publish',publish)
    assert fresh_process(service,files,plan)['status']=='completed'


def test_offline_root_keeps_records_and_does_not_change_setting(archive,tmp_path):
    service,store,files,root=archive
    (root/'Manual').mkdir();service.refresh();before=store.receipts.settings();key=store.catalog()[0]['key']
    root.rename(tmp_path/'offline')
    result=service.refresh()
    assert not result['available'] and len(result['warnings'])==1
    assert store.catalog()[0]['key']==key and store.receipts.settings()==before
    assert not root.exists()


def test_scan_and_copy_cancellation_are_effective_and_preserve_old_index(archive,tmp_path,monkeypatch):
    from threading import Event
    from backend.infrastructure.project_library.material_archive_files import ArchiveCancelled
    service,store,files,root=archive
    folder=root/'Manual';folder.mkdir();(folder/'a.txt').write_bytes(b'old');service.refresh()
    row=store.catalog()[0];before=store.indexed_files(row['key'])
    event=Event();event.set();files.cancellation=event
    with pytest.raises(ArchiveCancelled):service.refresh()
    assert store.indexed_files(row['key'])==before
    event.clear();source=tmp_path/'Large';source.mkdir();(source/'large.bin').write_bytes(b'x'*(8*1024*1024));plan=service.preview(str(source))
    check=files.check_cancel;calls=0
    def cancel_during_chunks():
        nonlocal calls
        calls+=1
        if calls==5:event.set()
        check()
    monkeypatch.setattr(files,'check_cancel',cancel_during_chunks)
    result=service.confirm(plan['plan_id'],plan['fingerprint'])
    assert result['status']=='incomplete' and not Path(result['target_path']).exists()
    assert (source/'large.bin').stat().st_size==8*1024*1024


def test_invalid_library_selection_and_nested_link_are_rejected(archive,tmp_path):
    service,store,files,root=archive
    folder=root/'Manual';(folder/'nested').mkdir(parents=True)
    for path in [root,folder/'nested',root.parent]:
        with pytest.raises(ValueError):service.preview(str(path))
    source=tmp_path/'Linked';source.mkdir();outside=tmp_path/'Outside';outside.mkdir();(outside/'private.txt').write_bytes(b'outside')
    try:(source/'redirect').symlink_to(outside,target_is_directory=True)
    except OSError:pytest.skip('Host does not allow symlink fixture')
    with pytest.raises(ValueError):service.preview(str(source))
    assert (outside/'private.txt').read_bytes()==b'outside'


def test_real_catalog_search_uses_lightweight_index_without_scan_or_availability_io(archive,tmp_path,monkeypatch):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
    from backend.infrastructure.project_library.search_files import SearchFiles
    service,store,files,root=archive
    folder=root/'DL-2020-01-001 Connector';(folder/'.connlab').mkdir(parents=True)
    (folder/'report.docx').write_bytes(b'doc');(folder/'old.sqlite3').write_bytes(b'db');(folder/'.connlab'/'secret.txt').write_bytes(b'internal')
    service.refresh()
    class Summaries:
        def list_rows(self):return []
    repo=LibrarySearchRepository(store.session,Summaries());disk=SearchFiles()
    def forbidden(*args):raise AssertionError('Queries must not scan or stat material folders')
    monkeypatch.setattr(disk,'scan',forbidden);monkeypatch.setattr(disk,'available',forbidden)
    search=LibrarySearchService(repo,disk,lambda path:None)
    assert [row['name'] for row in search.search('Connector report')['files']]==['report.docx']
    assert search.search('secret')['files']==[] and search.search('sqlite3')['files']==[]
    (folder/'report.docx').rename(folder/'new.docx')
    assert search.search('report')['files']
    service.refresh()
    assert search.search('report')['files']==[] and search.search('new.docx')['files']
    browse=SearchFiles().browse(folder,'')[1]
    assert [row['name'] for row in browse]==['new.docx']


def test_windows_directory_junction_is_not_followed(archive,tmp_path):
    import os,subprocess
    if os.name!='nt':pytest.skip('Windows junction contract')
    service,store,files,root=archive
    outside=tmp_path/'outside';outside.mkdir();(outside/'keep.txt').write_bytes(b'keep')
    source=tmp_path/'junction-source';source.mkdir();link=source/'junction'
    result=subprocess.run(['cmd','/c','mklink','/J',str(link),str(outside)],capture_output=True,text=True)
    if result.returncode:pytest.skip('Host cannot create junction fixture')
    with pytest.raises(ValueError):service.preview(str(source))
    assert (outside/'keep.txt').read_bytes()==b'keep'


def test_long_chinese_folder_name_is_preserved(archive,tmp_path):
    service,store,files,root=archive
    source=tmp_path/('旧项目完整名称-'+'Connector-'*13);source.mkdir();(source/'record.txt').write_bytes(b'record')
    plan=service.preview(str(source));result=service.confirm(plan['plan_id'],plan['fingerprint'])
    assert result['status']=='completed' and Path(result['target_path']).name==source.name


def test_worker_cancellation_remains_requested_until_work_actually_stops():
    from threading import Event
    from time import monotonic,sleep
    from backend.infrastructure.project_library.material_archive_files import ArchiveJobs,ArchiveCancelled
    jobs=ArchiveJobs();entered=Event();release=Event()
    def work(cancel):
        entered.set();release.wait(timeout=5)
        if cancel.is_set():raise ArchiveCancelled('cancelled')
        return {'finished':True}
    key=jobs.start(work)['job_id'];assert entered.wait(timeout=5)
    assert jobs.cancel(key)['status']=='cancellation_requested'
    assert jobs.get(key)['status']=='cancellation_requested'
    release.set();until=monotonic()+5
    while jobs.get(key)['status']=='cancellation_requested' and monotonic()<until:sleep(.01)
    assert jobs.get(key)['status']=='cancelled'
    jobs.pool.shutdown(wait=True)


def test_archive_long_work_does_not_hold_the_formal_library_lock(archive):
    from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles
    service,store,files,root=archive
    with files.lock():
        with MaterialReceiptFiles(files.settings).lock():
            assert store.receipts.settings()['root_path']==str(root)


def test_additive_archive_schema_preserves_old_settings_and_project_rows(archive):
    from backend.infrastructure.storage.models import ProjectModel
    from backend.infrastructure.storage.models_project_library import MaterialArchiveFolderModel,MaterialArchiveFileModel
    from sqlalchemy import select
    service,store,files,root=archive
    store.session.add(ProjectModel(project_id='retained',product_name='Existing connector',project_no='DL-2020-01-001',requestor='Lab',status='draft'))
    store.session.commit();before=store.receipts.settings();engine=store.session.bind
    MaterialArchiveFileModel.__table__.drop(engine);MaterialArchiveFolderModel.__table__.drop(engine)
    init_db(engine);init_db(engine)
    assert store.receipts.settings()==before
    assert store.session.get(ProjectModel,'retained').product_name=='Existing connector'
    assert store.catalog()==[]


def test_background_http_job_uses_injected_isolated_engine_and_does_not_block_other_requests(archive,tmp_path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_material_receipts import router,get_session,get_settings
    from time import monotonic,sleep
    service,store,files,root=archive
    folder=root/'Manual';folder.mkdir();(folder/'report.docx').write_bytes(b'doc')
    app=FastAPI();app.include_router(router)
    def sessions():
        with Session(store.session.bind) as session:yield session
    app.dependency_overrides[get_session]=sessions
    app.dependency_overrides[get_settings]=lambda:files.settings
    @app.get('/formal-work')
    def formal_work():return {'ready':True}
    with TestClient(app) as client:
        response=client.post('/api/material-receipts/archive/refresh');assert response.status_code==202
        assert client.get('/formal-work').json()=={'ready':True}
        key=response.json()['job_id'];until=monotonic()+10
        while monotonic()<until:
            result=client.get('/api/material-receipts/archive/jobs/'+key).json()
            if result['status'] not in {'working','cancellation_requested'}:break
            sleep(.01)
        assert result['status']=='done',result
        assert result['result']['root_path']==str(root)
        assert len(result['result']['folders'])==1


def test_reselecting_published_incomplete_folder_keeps_the_original_operation(archive,tmp_path,monkeypatch):
    service,store,files,root=archive
    source=tmp_path/'Pending registration';source.mkdir();(source/'report.txt').write_bytes(b'report')
    plan=service.preview(str(source));register=store.register
    def fail(*args,**kwargs):raise OSError('Synthetic registration failure')
    monkeypatch.setattr(store,'register',fail)
    op=service.confirm(plan['plan_id'],plan['fingerprint'])
    assert op['phase']=='index_pending'
    monkeypatch.setattr(store,'register',register)
    selected=service.preview(op['target_path'])
    assert selected['status']=='pending' and selected['operation']['batch_id']==op['batch_id']
    assert store.operation(op['batch_id'])['status']=='incomplete'


def test_index_search_includes_the_physical_folder_name_without_io(archive):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
    from backend.infrastructure.project_library.search_files import SearchFiles
    service,store,files,root=archive
    folder=root/'remember-this-folder';folder.mkdir();(folder/'report.txt').write_bytes(b'report')
    store.register(str(root),str(folder),None,'Older retained title');service.refresh()
    class Summaries:
        def list_rows(self):return []
    search=LibrarySearchService(LibrarySearchRepository(store.session,Summaries()),SearchFiles(),lambda path:None)
    assert len(search.search('remember-this-folder')['projects'])==1


def test_archive_entry_supports_open_browse_shortcuts_and_explicit_copy_but_never_a_target(archive,tmp_path):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.project_library.search_files import SearchFiles
    from backend.application.project_library.material_copy import MaterialCopyService
    from backend.application.project_library.copy_context import CopyContextRegistry
    from backend.application.project_library.report_shortcuts import ReportShortcutService
    from backend.infrastructure.storage.repositories.report_shortcuts import ReportShortcutRepository
    from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles
    service,store,files,root=archive
    source=root/'Legacy reports';source.mkdir();(source/'report.docx').write_bytes(b'reused report');service.refresh()
    row=store.catalog()[0];target=tmp_path/'formal-project';target.mkdir()
    class Catalog:
        def catalog(self):return store.catalog()+[dict(key='project:p1',project_id='p1',member_id=None,number='DL-1',title='Current',source='connlab',test_item='',folder_path=str(target))]
        def copy_target_eligible(self,project_id):return project_id=='p1'
    catalog=Catalog();opened=[]
    search=LibrarySearchService(catalog,SearchFiles(),opened.append)
    assert search.browse(row['key'])['items'][0]['name']=='report.docx'
    search.open(row['key'],'report.docx');assert opened==[source/'report.docx']
    disk=MaterialReceiptFiles(files.settings)
    reports=ReportShortcutService(ReportShortcutRepository(store.session),disk,catalog)
    assert reports.set(row['key'],'internal','report.docx',None)['items'][0]['available']
    contexts=CopyContextRegistry();copies=MaterialCopyService(store.receipts,disk,catalog,contexts)
    session_id=contexts.create()['session_id'];active=copies.update_context(session_id,1,'p1')
    context={'session_id':session_id,'token':active['token']}
    plan=copies.preview(row['key'],'report.docx',context)
    assert copies.confirm(plan['plan_id'],plan['fingerprint'],context)['status']=='completed'
    assert (target/'Reference materials'/'report.docx').read_bytes()==b'reused report'
    assert (source/'report.docx').read_bytes()==b'reused report'
    with pytest.raises(ValueError,match='existing ConnLab project'):copies._entry(row['key'],native=True)


def test_derived_materials_index_is_excluded_from_formal_project_snapshots(archive):
    from backend.infrastructure.storage.models import ProjectModel
    from backend.infrastructure.project_library.ownership import capture,typed_record
    service,store,files,root=archive
    (root/'Archive only').mkdir();service.refresh()
    store.session.add(ProjectModel(project_id='formal-snapshot',product_name='Current connector',requestor='Lab',status='draft'))
    store.session.commit()
    result=capture(store.session,'formal-snapshot')
    assert result['projects'][0]['project_id']=='formal-snapshot'
    for name in ['material_archive_files','material_archive_folders']:
        assert name not in result
        with pytest.raises(ValueError,match='unsupported record family'):typed_record(name,{})


def test_retry_preserves_manual_edits_to_received_partial_files(archive,tmp_path,monkeypatch):
    service,store,files,root=archive
    source=tmp_path/'Partial edited';source.mkdir();(source/'a.txt').write_bytes(b'original');(source/'b.txt').write_bytes(b'second')
    plan=service.preview(str(source));publish=files.publish
    def fail_one(source,target,item,identity):
        if item['relative_path']=='b.txt':raise OSError('Synthetic locked file')
        return publish(source,target,item,identity)
    monkeypatch.setattr(files,'publish',fail_one)
    op=service.confirm(plan['plan_id'],plan['fingerprint'])
    received=Path(op['stage_path'])/'a.txt';received.write_bytes(b'human edit')
    monkeypatch.setattr(files,'publish',publish)
    result=fresh_process(service,files,plan)
    assert result['status']=='incomplete' and result['counts']['retained_changed']==1
    assert received.read_bytes()==b'human edit' and (source/'a.txt').read_bytes()==b'original'
    assert (Path(op['stage_path'])/'b.txt').read_bytes()==b'second'
    assert not Path(op['target_path']).exists()


def existing_material_catalog(store,folder,kind):
    from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
    from backend.api.dependencies import get_project_registry_summary_service
    if kind=='receipt':
        store.receipts.add_entry(dict(receipt_id='retained-receipt',product_name='Retained connector',folder_path=str(folder),
            source_path='historical-origin',batch_id='historical-batch',created_at='2020-01-01'))
        key='receipt:retained-receipt'
    else:
        from backend.infrastructure.storage.models import ProjectModel,ProjectFolderRecordModel
        store.session.add(ProjectModel(project_id='retained-native',product_name='Retained connector',requestor='Lab',status='draft'))
        store.session.commit()
        store.session.add(ProjectFolderRecordModel(folder_id='retained-folder',project_id='retained-native',folder_path=str(folder)))
        store.session.commit();key='project:retained-native'
    return LibrarySearchRepository(store.session,get_project_registry_summary_service(store.session)),key


@pytest.mark.parametrize('kind',['receipt','native'])
def test_receiving_a_known_direct_child_returns_its_real_browsable_catalog_identity(archive,kind):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.project_library.search_files import SearchFiles
    service,store,files,root=archive
    folder=root/'Already registered';folder.mkdir();(folder/'report.txt').write_bytes(b'retained')
    catalog,key=existing_material_catalog(store,folder,kind);service.catalog=catalog
    result=service.preview(str(folder))
    assert result['status']=='existing' and result['target_key']==key
    search=LibrarySearchService(catalog,SearchFiles(),lambda path:None)
    assert search.browse(result['target_key'])['items'][0]['name']=='report.txt'
    selected=search.search(project=result['target_key'])
    assert [row['key'] for row in selected['projects']]==[key]
    assert [row['name'] for row in selected['files']]==['report.txt']
    assert [row['key'] for row in catalog.catalog()]==[key]
    assert store.operations()==[] and (folder/'report.txt').read_bytes()==b'retained'


@pytest.mark.parametrize('kind',['receipt','native'])
def test_existing_external_index_adopts_library_root_and_becomes_unavailable_when_root_is_offline(archive,tmp_path,kind):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.project_library.search_files import SearchFiles
    service,store,files,root=archive
    configured=tmp_path/'Later library';folder=configured/'Existing connector';folder.mkdir(parents=True)
    (folder/'report.txt').write_bytes(b'retained')
    catalog,key=existing_material_catalog(store,folder,kind);service.catalog=catalog
    service.refresh()
    before=store.indexed_files(key);assert before and store.indexed_available(str(folder))
    store.receipts.configure(str(configured));service.refresh()
    configured.rename(tmp_path/'Offline library')
    result=service.refresh()
    assert not result['available'] and len(result['warnings'])==1
    search=LibrarySearchService(catalog,SearchFiles(),lambda path:None).search()
    assert [row['key'] for row in search['projects']]==[key]
    assert not search['projects'][0]['available'] and search['files']==[]
    assert store.indexed_files(key)==before and store.receipts.settings()['root_path']==str(configured)


def test_receiving_a_child_does_not_select_an_overlapping_parent_catalog_entry(archive):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.project_library.search_files import SearchFiles
    service,store,files,root=archive
    folder=root/'Distinct child';folder.mkdir();(folder/'report.txt').write_bytes(b'child report')
    catalog,parent_key=existing_material_catalog(store,root,'receipt');service.catalog=catalog
    result=service.preview(str(folder))
    assert result['target_key']!=parent_key
    assert result['target_key'].startswith('archive:')
    assert LibrarySearchService(catalog,SearchFiles(),lambda path:None).browse(result['target_key'])['root']==str(folder)
