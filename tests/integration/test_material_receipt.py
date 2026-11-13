"""Receipt writes use isolated files and SQLite; originals are never opened by Office."""
from pathlib import Path
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles
from backend.application.project_library.material_receipt import MaterialReceiptService
from backend.shared.config import Settings


class Catalog:
    def __init__(self, store):
        self.store = store
        self.extra = []

    def catalog(self):
        return self.extra + self.store.catalog()


@pytest.fixture
def receipt(tmp_path):
    data = tmp_path / 'state'
    data.mkdir()
    engine = create_engine(f"sqlite:///{data / 'test.sqlite3'}")
    init_db(engine)
    with Session(engine) as session:
        store = MaterialReceiptRepository(session)
        settings = Settings(data_dir=data, projects_dir=tmp_path/'native', templates_dir=tmp_path/'templates', database_path=data/'test.sqlite3')
        files = MaterialReceiptFiles(settings)
        catalog = Catalog(store)
        service = MaterialReceiptService(store, files, catalog)
        root = tmp_path / 'received'
        root.mkdir()
        service.configure_root(str(root))
        yield service, store, files, catalog, session
    engine.dispose()


def test_preview_then_explicit_receive_preserves_every_byte_without_project_creation(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    (source/'.connlab'/'portable').mkdir(parents=True)
    (source/'empty').mkdir()
    (source/'.connlab'/'portable'/'snapshot.json').write_bytes(b'old snapshot: do not parse')
    (source/'old.sqlite3').write_bytes(b'old database')
    (source/'manual.docx').write_bytes(b'manual edits')
    plan = service.preview(str(source), 'DL-2026-08-079', 'Connector', 'temperature', material_state='completed')
    assert plan['status'] == 'ready'
    assert not Path(plan['target_path']).exists()
    assert store.catalog() == []
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'completed'
    target = Path(plan['target_path'])
    assert (target/'.connlab'/'portable'/'snapshot.json').read_bytes() == b'old snapshot: do not parse'
    assert (target/'old.sqlite3').read_bytes() == b'old database'
    assert (target/'empty').is_dir()
    assert (source/'manual.docx').read_bytes() == b'manual edits'
    assert session.scalar(select(func.count()).select_from(ProjectModel)) == 0
    assert len(store.catalog()) == 1
    assert service.confirm(plan['plan_id'], plan['fingerprint']) == result


def test_same_number_selection_supplements_and_skips_previously_archived_conflicts(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    target = tmp_path/'native'
    target.mkdir()
    (target/'report.docx').write_bytes(b'current edits')
    catalog.extra.append(dict(key='project:p1', project_id='p1', member_id=None, number='DL-2026-08-079',
        title='Native business product', test_item='Native test', source='connlab', folder_path=str(target)))
    source = tmp_path/'incoming'
    (source/'.connlab').mkdir(parents=True)
    (source/'.connlab'/'manifest.json').write_bytes(b'incoming control bytes')
    (source/'report.docx').write_bytes(b'incoming report')
    (source/'record.xlsx').write_bytes(b'new record')
    choice = service.preview(str(source), 'DL-2026-08-079', 'Do not replace native', 'Do not replace test')
    assert choice['status'] == 'choose_target'
    assert [r['key'] for r in choice['candidates']] == ['project:p1']
    plan = service.preview(str(source), 'DL-2026-08-079', 'Ignored', 'Ignored', 'project:p1')
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'completed'
    assert result['counts'] == dict(copied=1, supplemented=2, skipped=0, failed=0, retained_changed=0)
    assert (target/'report.docx').read_bytes() == b'current edits'
    assert not (target/'.connlab').exists()
    archived = next(row for row in result['items'] if row['relative_path'] == 'report.docx')
    assert archived['target_relative'].startswith('补充资料/')
    assert (target/archived['target_relative']).read_bytes() == b'incoming report'
    assert store.catalog() == []
    repeat = service.preview(str(source), 'DL-2026-08-079', '', '', 'project:p1')
    again = service.confirm(repeat['plan_id'], repeat['fingerprint'])
    assert again['counts'] == dict(copied=0, supplemented=0, skipped=3, failed=0, retained_changed=0)
    assert len(list((target/'补充资料').iterdir())) == 1
    assert catalog.extra[0]['title'] == 'Native business product'


def test_legacy_numbers_are_retained_and_duplicate_independence_is_explicit(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'Old project'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source), 'Legacy/2001-a', 'Old product', '')
    assert plan['number'] == 'Legacy/2001-a'
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert store.entry(result['receipt_id'])['number'] == 'Legacy/2001-a'
    assert service.preview(str(source), 'legacy/2001-A')['status'] == 'choose_target'
    with pytest.raises(ValueError, match='distinguishing'):
        service.preview(str(source), 'Legacy/2001-a', '', '', 'new')
    independent = service.preview(str(source), 'Legacy/2001-a', 'Other product', '', 'new', 'second specimen')
    service.confirm(independent['plan_id'], independent['fingerprint'])
    assert len(store.catalog()) == 2


@pytest.mark.parametrize('change', ['source', 'destination', 'binding'])
def test_changed_preview_blocks_before_receipt_writes(receipt, tmp_path, change):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source), '', 'Product')
    if change == 'source':
        (source/'a.txt').write_bytes(b'changed')
    elif change == 'destination':
        Path(plan['target_path']).mkdir()
        (Path(plan['target_path'])/'manual.txt').write_bytes(b'manual')
    else:
        root = tmp_path/'other-root'
        root.mkdir()
        service.configure_root(str(root))
    with pytest.raises(ValueError, match='changed'):
        service.confirm(plan['plan_id'], plan['fingerprint'])
    assert store.catalog() == []


def test_partial_failure_retry_uses_durable_results_and_preserves_manual_changes(receipt, tmp_path, monkeypatch):
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    (source/'b.txt').write_bytes(b'b')
    plan = service.preview(str(source), '', 'Product')
    publish = files.publish
    def fail_one(source, target, entry, identity):
        if entry['relative_path'] == 'a.txt':
            raise OSError('Synthetic locked file')
        return publish(source, target, entry, identity)
    monkeypatch.setattr(files, 'publish', fail_one)
    partial = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert partial['status'] == 'incomplete'
    assert partial['counts'] == dict(copied=1, supplemented=0, skipped=0, failed=1, retained_changed=0)
    target = Path(plan['target_path'])
    (target/'b.txt').write_bytes(b'later manual changes')
    monkeypatch.setattr(files, 'publish', publish)
    # Reconstruct service and Session to consume only durable receipt state.
    with Session(session.bind) as fresh:
        fresh_store = MaterialReceiptRepository(fresh)
        resumed = MaterialReceiptService(fresh_store, MaterialReceiptFiles(files.settings), Catalog(fresh_store))
        result = resumed.retry(partial['batch_id'])
    assert result['status'] == 'incomplete'
    assert result['counts']['retained_changed'] == 1
    assert (target/'a.txt').read_bytes() == b'a'
    assert (target/'b.txt').read_bytes() == b'later manual changes'


def test_linked_original_is_a_candidate_but_never_a_write_target(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    target = tmp_path/'linked'
    target.mkdir()
    source = tmp_path/'incoming'
    source.mkdir()
    catalog.extra.append(dict(key='linked:l1', number='DL-2026-08-079', project_id=None, member_id=None,
        title='Linked', source='linked', folder_path=str(target), test_item=''))
    candidate = service.preview(str(source), 'DL-2026-08-079')['candidates'][0]
    assert candidate['can_supplement'] is False
    with pytest.raises(ValueError, match='read-only'):
        service.preview(str(source), 'DL-2026-08-079', '', '', 'linked:l1')
    assert list(target.iterdir()) == []


def test_metadata_edit_does_not_rename_files_and_missing_root_remains_searchable(receipt, tmp_path):
    from backend.application.project_library.search import LibrarySearchService
    from backend.infrastructure.project_library.search_files import SearchFiles
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    (source/'original.docx').write_bytes(b'original')
    plan = service.preview(str(source), '', 'Product')
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    entry = service.detail(result['receipt_id'])
    service.edit(entry['receipt_id'], entry['revision'], 'Edited product', 'temperature vibration')
    assert (Path(entry['folder_path'])/'original.docx').read_bytes() == b'original'
    Path(entry['folder_path']).rename(tmp_path/'relocated')
    search = LibrarySearchService(catalog, SearchFiles(), lambda path: None)
    found = search.search('Edited vibration')['projects']
    assert len(found) == 1 and not found[0]['available']
    assert not Path(entry['folder_path']).exists()
    locate = service.locate_preview(entry['receipt_id'], str(tmp_path/'relocated'))
    service.locate(entry['receipt_id'], locate['plan_id'], locate['fingerprint'])
    assert service.detail(entry['receipt_id'])['available'] is True


def test_old_connlab_state_requires_explicit_materials_choice_without_restore(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    (source/'.connlab').mkdir(parents=True)
    (source/'.connlab'/'snapshot.json').write_bytes(b'not JSON')
    assert service.preview(str(source), '', 'Product')['status'] == 'choose_state'
    assert store.catalog() == []
    plan = service.preview(str(source), '', 'Product', material_state='ongoing')
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    entry = store.entry(result['receipt_id'])
    assert entry['material_state'] == 'ongoing'
    service.edit(entry['receipt_id'], entry['revision'], 'Product', 'keywords', 'completed')
    assert store.entry(result['receipt_id'])['material_state'] == 'completed'
    assert (Path(plan['target_path'])/'.connlab'/'snapshot.json').read_bytes() == b'not JSON'


def test_missing_previously_copied_file_is_not_recreated_on_retry(receipt, tmp_path, monkeypatch):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    (source/'b.txt').write_bytes(b'b')
    plan = service.preview(str(source))
    publish = files.publish
    def fail_b(source, target, entry, identity):
        if entry['relative_path'] == 'b.txt':
            raise OSError('Synthetic failure')
        return publish(source, target, entry, identity)
    monkeypatch.setattr(files, 'publish', fail_b)
    batch = service.confirm(plan['plan_id'], plan['fingerprint'])
    (Path(plan['target_path'])/'a.txt').unlink()
    monkeypatch.setattr(files, 'publish', publish)
    resumed = service.retry(batch['batch_id'])
    assert resumed['status'] == 'incomplete'
    assert resumed['counts']['retained_changed'] == 1
    assert not (Path(plan['target_path'])/'a.txt').exists()
    assert (Path(plan['target_path'])/'b.txt').read_bytes() == b'b'


def test_replaced_physical_target_and_modified_archive_block_stale_confirmation(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source, target = tmp_path/'incoming', tmp_path/'native'
    source.mkdir(); target.mkdir()
    (source/'report.docx').write_bytes(b'incoming')
    (target/'report.docx').write_bytes(b'current')
    catalog.extra.append(dict(key='project:p1', project_id='p1', member_id=None, number='DL-2026-08-079',
        title='Native', test_item='', source='connlab', folder_path=str(target)))
    plan = service.preview(str(source), 'DL-2026-08-079', target_key='project:p1')
    target.rename(tmp_path/'moved-native')
    target.mkdir()
    (target/'report.docx').write_bytes(b'current')
    with pytest.raises(ValueError, match='destination changed'):
        service.confirm(plan['plan_id'], plan['fingerprint'])
    current = service.preview(str(source), 'DL-2026-08-079', target_key='project:p1')
    result = service.confirm(current['plan_id'], current['fingerprint'])
    repeat = service.preview(str(source), 'DL-2026-08-079', target_key='project:p1')
    archived = next(r for r in result['items'] if r['relative_path'] == 'report.docx')
    (target/archived['target_relative']).write_bytes(b'manual archive edits')
    with pytest.raises(ValueError, match='destination changed'):
        service.confirm(repeat['plan_id'], repeat['fingerprint'])
    assert (target/archived['target_relative']).read_bytes() == b'manual archive edits'


def test_receipt_relocation_cannot_alias_original_or_another_owned_root(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    source.mkdir()
    plan = service.preview(str(source))
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    with pytest.raises(ValueError, match='original source'):
        service.locate_preview(result['receipt_id'], str(source))
    target = tmp_path/'linked'
    target.mkdir()
    catalog.extra.append(dict(key='linked:l1', project_id=None, member_id=None, number=None,
        title='Other', test_item='', source='linked', folder_path=str(target)))
    with pytest.raises(ValueError, match='another entry'):
        service.locate_preview(result['receipt_id'], str(target))
    new = tmp_path/'new'
    new.mkdir()
    locate = service.locate_preview(result['receipt_id'], str(new))
    catalog.extra.append(dict(key='project:p1', project_id='p1', member_id=None, number=None,
        title='Now owned', test_item='', source='connlab', folder_path=str(new)))
    with pytest.raises(ValueError, match='another entry'):
        service.locate(result['receipt_id'], locate['plan_id'], locate['fingerprint'])


def test_concurrent_confirmation_is_exclusive_and_retry_does_not_duplicate(receipt, tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source))
    entered, release = Event(), Event()
    original = MaterialReceiptFiles.publish
    def paused(self, source, target, entry, identity):
        entered.set()
        assert release.wait(5)
        return original(self, source, target, entry, identity)
    monkeypatch.setattr(MaterialReceiptFiles, 'publish', paused)
    def confirm():
        with Session(session.bind) as fresh:
            fresh_store = MaterialReceiptRepository(fresh)
            return MaterialReceiptService(fresh_store, MaterialReceiptFiles(files.settings), Catalog(fresh_store)).confirm(plan['plan_id'], plan['fingerprint'])
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(confirm)
        try:
            assert entered.wait(5)
            with pytest.raises(ValueError, match='already running'):
                confirm()
        finally:
            release.set()
        result = future.result(timeout=10)
    assert result['status'] == 'completed'
    assert confirm() == result
    assert len(store.catalog()) == 1


def test_empty_directory_failure_is_explicit_and_does_not_block_other_files(receipt, tmp_path, monkeypatch):
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    (source/'empty').mkdir(parents=True)
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source))
    original = files.publish
    def fail_directory(source, target, entry, identity):
        if entry['directory']:
            raise OSError('Synthetic empty-directory failure')
        return original(source, target, entry, identity)
    monkeypatch.setattr(files, 'publish', fail_directory)
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'incomplete'
    assert result['counts']['copied'] == 1
    assert result['directory_counts']['failed'] == 1


def test_api_receipt_and_legacy_batch_namespaces_do_not_overlap(receipt, tmp_path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_material_receipts import router, get_material_receipt_service
    from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
    service, store, files, catalog, session = receipt
    source = tmp_path/'old'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_material_receipt_service] = lambda: service
    with TestClient(app) as client:
        preview = client.post('/api/material-receipts/preview', json={'source': str(source), 'product_name': 'Product'})
        assert preview.status_code == 200
        plan = preview.json()
        assert not Path(plan['target_path']).exists()
        bad = client.post('/api/material-receipts/confirm', json={'plan_id': plan['plan_id'], 'fingerprint': '0'*64})
        assert bad.status_code == 409
        confirmed = client.post('/api/material-receipts/confirm', json={'plan_id': plan['plan_id'], 'fingerprint': plan['fingerprint']})
        assert confirmed.status_code == 200
        result = confirmed.json()
        assert client.get('/api/material-receipts/batches/'+result['batch_id']).json() == result
        assert client.get('/api/material-receipts/entries/'+result['receipt_id']).json()['product_name'] == 'Product'
        with pytest.raises(LookupError):
            ProjectLibraryRepository(session).batch(result['batch_id'])
    assert session.scalar(select(func.count()).select_from(ProjectModel)) == 0


def test_cold_database_initialization_registers_additive_receipt_tables(tmp_path):
    import subprocess
    import sys
    script = """
import sys
from sqlalchemy import create_engine, inspect
from backend.infrastructure.storage.database import init_db
engine = create_engine('sqlite:///'+sys.argv[1])
init_db(engine)
assert {'material_receipt_entries','material_receipt_settings','material_receipt_batches'}.issubset(inspect(engine).get_table_names())
engine.dispose()
"""
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path/'cold.sqlite3')], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_conflict_paths_keep_original_relative_structure_and_target_bytes(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    target = tmp_path/'native'
    target.mkdir()
    (target/'reports').write_bytes(b'existing file occupying directory name')
    source = tmp_path/'incoming'
    (source/'reports'/'nested').mkdir(parents=True)
    (source/'reports'/'nested'/'manual.docx').write_bytes(b'incoming')
    catalog.extra.append(dict(key='project:p1', project_id='p1', member_id=None, number='old-123',
        title='Native', test_item='', source='connlab', folder_path=str(target)))
    plan = service.preview(str(source), 'old-123', target_key='project:p1')
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'completed'
    row = next(r for r in result['items'] if r['relative_path'].endswith('manual.docx'))
    assert row['target_relative'].endswith('reports/nested/manual.docx')
    assert (target/row['target_relative']).read_bytes() == b'incoming'
    assert (target/'reports').read_bytes() == b'existing file occupying directory name'


def test_overlap_and_redirected_sources_cannot_be_received(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    root = Path(service.runtime()['root_path'])
    with pytest.raises(ValueError, match='overlap'):
        service.preview(str(tmp_path))
    external = tmp_path/'external'
    external.mkdir()
    (external/'a.txt').write_bytes(b'protected')
    source = tmp_path/'source'
    source.mkdir()
    try:
        (source/'redirect').symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip('Host does not permit creating test symlinks')
    with pytest.raises(ValueError, match='Redirected'):
        service.preview(str(source))
    assert list(root.iterdir()) == []


def test_source_change_during_receipt_reports_incomplete_and_preserves_originals(receipt, tmp_path, monkeypatch):
    service, store, files, catalog, session = receipt
    source = tmp_path/'source'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source))
    original = files.publish
    def add_source_file(source_path, target, entry, identity):
        status = original(source_path, target, entry, identity)
        (Path(source_path)/'late.txt').write_bytes(b'added during receipt')
        return status
    monkeypatch.setattr(files, 'publish', add_source_file)
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'incomplete'
    assert 'source changed' in result['message']
    assert not (Path(plan['target_path'])/'late.txt').exists()
    assert (source/'late.txt').read_bytes() == b'added during receipt'


def test_exclusive_file_publication_preserves_racing_manual_file(receipt, tmp_path, monkeypatch):
    import os
    import backend.infrastructure.project_library.material_receipt_files as module
    service, store, files, catalog, session = receipt
    source = tmp_path/'source'
    source.mkdir()
    (source/'a.txt').write_bytes(b'incoming')
    plan = service.preview(str(source))
    operation = 'rename' if os.name == 'nt' else 'link'
    original = getattr(module.os, operation)
    def occupy_before_publish(source_path, target_path, *args, **kwargs):
        if str(source_path).endswith('.tmp') and Path(source_path).name.startswith('.receipt-'):
            Path(target_path).write_bytes(b'racing manual file')
        return original(source_path, target_path, *args, **kwargs)
    monkeypatch.setattr(module.os, operation, occupy_before_publish)
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'incomplete'
    assert result['counts']['failed'] == 1
    assert (Path(plan['target_path'])/'a.txt').read_bytes() == b'racing manual file'
    assert (source/'a.txt').read_bytes() == b'incoming'


def test_historical_unbound_member_reconnects_without_touching_control_files(receipt, tmp_path):
    from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
    service, store, files, catalog, session = receipt
    source = tmp_path/'original'
    source.mkdir()
    moved = tmp_path/'moved'
    (moved/'.connlab').mkdir(parents=True)
    (moved/'.connlab'/'portable.json').write_bytes(b'original control bytes')
    session.add(ProjectLibraryMemberModel(member_id='m1', project_id=None, title='Historical', folder_path=str(tmp_path/'missing'),
        source_path=str(source), created_at='2026-11-14', revision=1))
    session.commit()
    with pytest.raises(ValueError, match='original source'):
        service.catalog_location_preview('member:m1', str(source))
    preview = service.catalog_location_preview('member:m1', str(moved))
    result = service.catalog_location('member:m1', preview['plan_id'], preview['fingerprint'])
    assert result['folder_path'] == str(moved)
    assert result['revision'] == 2
    assert (moved/'.connlab'/'portable.json').read_bytes() == b'original control bytes'
    assert session.scalar(select(func.count()).select_from(ProjectModel)) == 0
    assert store.catalog() == []


def test_business_bound_member_cannot_reconnect_through_plain_materials_route(receipt, tmp_path):
    from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
    service, store, files, catalog, session = receipt
    session.add(ProjectModel(project_id='p1', product_name='Native', requestor='Lab', status='draft'))
    session.commit()
    session.add(ProjectLibraryMemberModel(member_id='m1', project_id='p1', title='Native', folder_path=str(tmp_path/'native'),
        source_path=str(tmp_path/'source'), created_at='2026-11-14'))
    session.commit()
    with pytest.raises(ValueError, match='business project'):
        service.catalog_location_preview('member:m1', str(tmp_path))
