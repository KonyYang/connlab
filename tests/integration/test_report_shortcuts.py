"""Ordinary report pointers use synthetic files and a dedicated SQLite database."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles
from backend.shared.config import Settings


@pytest.fixture
def library(tmp_path):
    from backend.application.project_library.report_shortcuts import ReportShortcutService
    from backend.infrastructure.storage.repositories.report_shortcuts import ReportShortcutRepository
    data = tmp_path/'data'
    data.mkdir()
    root = tmp_path/'project'
    root.mkdir()
    (root/'first.docx').write_bytes(b'first')
    (root/'second.pdf').write_bytes(b'second')
    engine = create_engine(f"sqlite:///{data/'db.sqlite3'}", connect_args={"check_same_thread": False})
    init_db(engine)
    rows = [dict(key='project:p1', project_id='p1', member_id='m1', number='DL-1', title='Product',
                 source='connlab', test_item='', folder_path=str(root))]
    class Catalog:
        def catalog(self):
            return rows
        def copy_target_eligible(self, project_id):
            return any(row.get('project_id') == project_id for row in rows)
    with Session(engine) as session:
        files = MaterialReceiptFiles(Settings(data_dir=data, projects_dir=tmp_path/'projects', templates_dir=tmp_path/'templates', database_path=data/'db.sqlite3'))
        service = ReportShortcutService(ReportShortcutRepository(session), files, Catalog())
        yield service, session, root, rows, files, Catalog()
    engine.dispose()


def test_report_shortcuts_set_replace_clear_without_changing_files(library):
    service, session, root, rows, files, catalog = library
    assert service.list('member:m1')['items'] == []
    first = service.set('member:m1', 'internal', 'first.docx', None)
    assert first['key'] == 'project:p1'
    assert first['items'][0]['relative_path'] == 'first.docx'
    both = service.set('project:p1', 'customer', 'first.docx', None)
    assert len(both['items']) == 2
    with pytest.raises(ValueError, match='Confirm replacement'):
        service.set('project:p1', 'internal', 'second.pdf', 'first.docx')
    replaced = service.set('project:p1', 'internal', 'second.pdf', 'first.docx', True)
    assert next(row for row in replaced['items'] if row['role'] == 'internal')['relative_path'] == 'second.pdf'
    with pytest.raises(ValueError, match='changed'):
        service.set('project:p1', 'internal', 'first.docx', 'first.docx', True)
    cleared = service.clear('member:m1', 'internal', 'second.pdf')
    assert [row['role'] for row in cleared['items']] == ['customer']
    assert (root/'first.docx').read_bytes() == b'first'
    assert (root/'second.pdf').read_bytes() == b'second'


def test_report_pointer_follows_same_path_edits_and_root_location_without_hashing(library, tmp_path, monkeypatch):
    import os
    import backend.infrastructure.project_library.files as operations
    service, session, root, rows, files, catalog = library
    def forbidden(*args, **kwargs):
        raise AssertionError('Report shortcuts must not hash or inventory files')
    monkeypatch.setattr(operations, 'file_hash', forbidden)
    monkeypatch.setattr(operations, 'inventory', forbidden)
    monkeypatch.setattr('backend.infrastructure.project_library.material_receipt_files.file_hash', forbidden)
    monkeypatch.setattr('backend.infrastructure.project_library.material_receipt_files.inventory', forbidden)
    service.set('project:p1', 'internal', 'first.docx', None)
    original = service.list('project:p1')['items'][0]
    (root/'first.docx').write_bytes(b'edited in place')
    os.utime(root/'first.docx', (1900000000, 1900000000))
    refreshed = service.list('project:p1')['items'][0]
    assert refreshed['relative_path'] == 'first.docx' and refreshed['modified_at'] != original['modified_at']
    (root/'first.docx').unlink()
    assert not service.list('project:p1')['items'][0]['available']
    (root/'first.docx').write_bytes(b'replacement at same name')
    assert service.list('project:p1')['items'][0]['available']
    moved = tmp_path/'moved'
    root.rename(moved)
    assert not service.list('project:p1')['items'][0]['available']
    rows[0]['folder_path'] = str(moved)
    assert service.list('project:p1')['items'][0]['available']
    assert (moved/'first.docx').read_bytes() == b'replacement at same name'
    rows.append({**rows[0], 'key':'project:p2', 'project_id':'p2', 'member_id':None})
    assert service.list('project:p2')['items'] == []


def test_report_pointer_excludes_global_metadata_from_portable_contract(library):
    from backend.infrastructure.storage.models import ProjectModel
    from backend.infrastructure.project_library.ownership import capture, typed_record
    service, session, root, rows, files, catalog = library
    service.set('project:p1', 'customer', 'second.pdf', None)
    session.add(ProjectModel(project_id='p1', product_name='Product', requestor='Lab', status='draft'))
    session.commit()
    assert 'library_report_shortcuts' not in capture(session, 'p1')
    with pytest.raises(ValueError, match='unsupported record family'):
        typed_record('library_report_shortcuts', {})
    assert service.list('project:p1')['items'][0]['relative_path'] == 'second.pdf'


def test_report_pointer_rejects_escape_and_missing_file_but_can_clear_missing(library):
    service, session, root, rows, files, catalog = library
    for path in ('../outside.docx','first.docx:stream','C:/first.docx','/first.docx','missing.docx',''):
        with pytest.raises(ValueError):
            service.set('project:p1','internal',path,None)
    service.set('project:p1','internal','first.docx',None)
    (root/'first.docx').unlink()
    assert service.clear('project:p1','internal','first.docx')['items'] == []


def test_distinct_member_root_keeps_its_own_shortcuts_despite_shared_project_id(library, tmp_path):
    service, session, root, rows, files, catalog = library
    separate = tmp_path/'member-copy'
    separate.mkdir()
    (separate/'first.docx').write_bytes(b'distinct received report')
    rows.append({**rows[0], 'key':'member:m1', 'folder_path':str(separate), 'source':'received'})
    service.set('member:m1','customer','first.docx',None)
    assert service.list('member:m1')['key'] == 'member:m1'
    assert service.list('member:m1')['items'][0]['relative_path'] == 'first.docx'
    assert service.list('project:p1')['items'] == []
    assert (root/'first.docx').read_bytes() == b'first'
    assert (separate/'first.docx').read_bytes() == b'distinct received report'


def test_copying_a_marked_file_does_not_inherit_the_shortcut(library, tmp_path):
    from backend.application.project_library.material_receipt import MaterialReceiptService
    service, session, root, rows, files, catalog = library
    service.set('project:p1','internal','first.docx',None)
    target = tmp_path/'target-project'
    target.mkdir()
    rows.append({**rows[0], 'key':'project:p2', 'project_id':'p2', 'member_id':None, 'folder_path':str(target)})
    copies = MaterialReceiptService(MaterialReceiptRepository(session),files,catalog)
    session_id = copies.create_copy_context()['session_id']
    active = copies.update_copy_context(session_id,1,'p2')
    context = {'session_id':session_id,'token':active['token']}
    plan = copies.copy_preview('project:p1','first.docx',context)
    copies.copy_confirm(plan['plan_id'],plan['fingerprint'],context)
    assert service.list('project:p2')['items'] == []
    assert service.list('project:p1')['items'][0]['relative_path'] == 'first.docx'
    assert (target/'Reference materials'/'first.docx').read_bytes() == b'first'


def test_shortcut_http_requires_explicit_replacement_and_preserves_only_metadata(library):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_report_shortcuts import router, get_report_shortcut_service
    service, session, root, rows, files, catalog = library
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_report_shortcut_service] = lambda: service
    with TestClient(app) as client:
        base='/api/project-library/report-shortcuts'
        first=client.post(base+'/set',json={'key':'member:m1','role':'internal','relative_path':'first.docx'})
        assert first.status_code == 200 and first.json()['key'] == 'project:p1'
        change={'key':'project:p1','role':'internal','relative_path':'second.pdf','expected_path':'first.docx'}
        assert client.post(base+'/set',json=change).status_code == 409
        assert client.post(base+'/set',json={**change,'replacement_confirmed':True}).status_code == 200
        (root/'second.pdf').unlink()
        assert not client.get(base,params={'key':'project:p1'}).json()['items'][0]['available']
        cleared=client.post(base+'/clear',json={'key':'project:p1','role':'internal','expected_path':'second.pdf'})
        assert cleared.status_code == 200 and cleared.json()['items'] == []
    assert (root/'first.docx').read_bytes() == b'first'


def test_redirected_report_path_is_rejected(library, tmp_path):
    service, session, root, rows, files, catalog = library
    try:
        (root/'link.docx').symlink_to(root/'first.docx')
    except OSError:
        pytest.skip('Host does not allow creating test symlinks')
    with pytest.raises(ValueError, match='Redirected'):
        service.set('project:p1','internal','link.docx',None)


def test_retained_temporary_registry_project_cannot_become_live_copy_context(library):
    from backend.application.project_library.material_receipt import MaterialReceiptService
    from backend.infrastructure.storage.models import ProjectModel, ProjectFolderRecordModel
    from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
    from backend.infrastructure.storage.repositories.library_search import LibrarySearchRepository
    from backend.api.dependencies import get_project_registry_summary_service
    service, session, root, rows, files, catalog = library
    session.add(ProjectModel(project_id='temporary',product_name='Retained work',requestor='Lab',status='draft'))
    session.commit()
    session.add(ProjectFolderRecordModel(folder_id='retained-root',project_id='temporary',folder_path=str(root)))
    session.commit()
    summaries=get_project_registry_summary_service(session)
    assert summaries.get_row('temporary').display_project_id_kind == 'temporary'
    real_catalog=LibrarySearchRepository(session,summaries)
    copies=MaterialReceiptService(MaterialReceiptRepository(session),files,real_catalog)
    browser=copies.create_copy_context()['session_id']
    with pytest.raises(ValueError,match='temporary'):
        copies.update_copy_context(browser,1,'temporary')
    session.add(ProjectLibraryMemberModel(member_id='imported',project_id='temporary',ltr_number='Historical-1',title='Imported history',folder_path=str(root),source_path='old source',created_at='2026-11-14'))
    session.commit()
    assert summaries.get_row('temporary').display_project_id_kind == 'imported'
    active=copies.update_copy_context(browser,2,'temporary')
    assert active['target']['project_id'] == 'temporary'
    session.get(ProjectModel,'temporary').registry_state='trash'
    session.commit()
    with pytest.raises((LookupError,ValueError)):
        copies.copy_preview('project:temporary','first.docx',{'session_id':browser,'token':active['token']})
    assert (root/'first.docx').read_bytes() == b'first'
