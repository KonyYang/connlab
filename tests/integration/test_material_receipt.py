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

    def copy_target_eligible(self, project_id):
        return any(row.get('project_id') == project_id and row['source'] != 'linked' for row in self.extra)

    def catalog(self):
        return self.extra + self.store.catalog()


@pytest.fixture
def receipt(tmp_path, request):
    data = tmp_path / 'state'
    data.mkdir()
    engine = create_engine(f"sqlite:///{data / 'test.sqlite3'}")
    init_db(engine)
    with Session(engine) as session:
        store = MaterialReceiptRepository(session)
        settings = Settings(data_dir=data, projects_dir=tmp_path/'native', templates_dir=tmp_path/'templates', database_path=data/'test.sqlite3', output_root=tmp_path/'default-output')
        files = MaterialReceiptFiles(settings)
        catalog = Catalog(store)
        service = MaterialReceiptService(store, files, catalog)
        if getattr(request, 'param', True):
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
assert {'material_receipt_entries','material_receipt_settings','material_receipt_batches','library_report_shortcuts'}.issubset(inspect(engine).get_table_names())
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


def test_same_number_candidates_distinguish_unassociated_from_missing_locations(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    catalog.extra.extend([
        dict(key='project:new', project_id='new', member_id=None, number='same-number',
             title='Planning', test_item='', source='connlab', folder_path=''),
        dict(key='project:lost', project_id='lost', member_id=None, number='same-number',
             title='Registered missing', test_item='', source='connlab', folder_path=str(tmp_path/'missing')),
    ])
    choices = service.preview(str(source), 'same-number')['candidates']
    assert choices[0]['location_state'] == 'unassociated'
    assert 'not linked' in choices[0]['reason']
    assert choices[1]['location_state'] == 'unavailable'
    assert 'unavailable' in choices[1]['reason']
    assert not any(row['can_supplement'] for row in choices)
    assert not list(source.iterdir())


@pytest.mark.parametrize('kind', ['connlab', 'linked', 'received'])
def test_receive_root_cannot_be_inside_an_owned_material_folder(receipt, tmp_path, kind):
    service, store, files, catalog, session = receipt
    owned = tmp_path/'owned'
    nested = owned/'nested'
    nested.mkdir(parents=True)
    (owned/'manual.txt').write_bytes(b'original')
    catalog.extra.append(dict(key='owned:1', project_id=None, member_id=None, number='OLD',
        title='Existing', test_item='', source=kind, folder_path=str(owned)))
    for root in (owned, nested):
        with pytest.raises(ValueError, match='owned'):
            service.configure_root(str(root))
    assert service.runtime()['root_path'] == str(tmp_path/'received')
    assert (owned/'manual.txt').read_bytes() == b'original'


def test_new_receipt_rechecks_newly_registered_target_ownership(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    plan = service.preview(str(source))
    catalog.extra.append(dict(key='project:p1', project_id='p1', member_id=None, number='OTHER',
        title='Reserved business folder', test_item='', source='connlab', folder_path=plan['target_path']))
    with pytest.raises(ValueError, match='owned'):
        service.confirm(plan['plan_id'], plan['fingerprint'])
    assert not Path(plan['target_path']).exists()
    assert store.catalog() == []
    with pytest.raises(ValueError, match='owned'):
        service.preview(str(source))


def test_incomplete_receipt_retry_rejects_changed_registration(receipt, tmp_path, monkeypatch):
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    (source/'b.txt').write_bytes(b'b')
    plan = service.preview(str(source))
    publish = files.publish
    def fail_one(source, target, entry, identity):
        if entry['relative_path'] == 'b.txt':
            raise OSError('Synthetic locked file')
        return publish(source, target, entry, identity)
    monkeypatch.setattr(files, 'publish', fail_one)
    partial = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert partial['status'] == 'incomplete'
    moved = tmp_path/'moved-copy'
    moved.mkdir()
    (moved/'a.txt').write_bytes(b'a')
    location = service.locate_preview(partial['receipt_id'], str(moved))
    service.locate(partial['receipt_id'], location['plan_id'], location['fingerprint'])
    monkeypatch.setattr(files, 'publish', publish)
    with pytest.raises(ValueError, match='entry changed'):
        service.retry(partial['batch_id'])
    assert not (Path(plan['target_path'])/'b.txt').exists()
    assert not (moved/'b.txt').exists()
    assert store.entry(partial['receipt_id'])['folder_path'] == str(moved)


def test_relocated_receipt_keeps_history_and_skips_preserved_conflict(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'incoming'
    source.mkdir()
    (source/'a.txt').write_bytes(b'original')
    first = service.preview(str(source), 'OLD-1')
    received = service.confirm(first['plan_id'], first['fingerprint'])
    key = received['target_key']
    (source/'a.txt').write_bytes(b'incoming update')
    second = service.preview(str(source), 'OLD-1', target_key=key)
    supplemented = service.confirm(second['plan_id'], second['fingerprint'])
    archive = next(row['target_relative'] for row in supplemented['items'] if row['relative_path'] == 'a.txt')
    moved = tmp_path/'moved-copy'
    Path(first['target_path']).rename(moved)
    location = service.locate_preview(received['receipt_id'], str(moved))
    detail = service.locate(received['receipt_id'], location['plan_id'], location['fingerprint'])
    assert len(detail['history']) == 2
    repeat = service.preview(str(source), 'OLD-1', target_key=key)
    assert repeat['items'][0]['action'] == 'skip'
    assert repeat['items'][0]['target_relative'] == archive
    result = service.confirm(repeat['plan_id'], repeat['fingerprint'])
    assert result['counts']['skipped'] == 1
    assert (moved/'a.txt').read_bytes() == b'original'
    assert (moved/archive).read_bytes() == b'incoming update'
    assert len(list((moved/'补充资料').iterdir())) == 1


def test_unnumbered_materials_allow_explicit_supplement_without_automatic_matching(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'original'
    source.mkdir()
    (source/'a.txt').write_bytes(b'a')
    first = service.preview(str(source))
    received = service.confirm(first['plan_id'], first['fingerprint'])
    incoming = tmp_path/'supplement'
    incoming.mkdir()
    (incoming/'b.txt').write_bytes(b'b')
    separate = service.preview(str(incoming))
    assert not separate['supplement']
    assert separate['candidates'] == []
    plan = service.preview(str(incoming), target_key=received['target_key'])
    assert plan['supplement']
    assert plan['target_path'] == first['target_path']
    result = service.confirm(plan['plan_id'], plan['fingerprint'])
    assert result['status'] == 'completed'
    assert len(store.catalog()) == 1
    assert (Path(first['target_path'])/'a.txt').read_bytes() == b'a'
    assert (Path(first['target_path'])/'b.txt').read_bytes() == b'b'
    stale = service.preview(str(incoming), target_key=received['target_key'])
    entry = service.detail(received['receipt_id'])
    service.edit(received['receipt_id'], entry['revision'], 'Changed description', '')
    with pytest.raises(ValueError, match='selected entry changed'):
        service.confirm(stale['plan_id'], stale['fingerprint'])
    with pytest.raises(ValueError, match='selected same-number entry changed'):
        service.preview(str(incoming), 'DIFFERENT-NUMBER', target_key=received['target_key'])


def test_selected_file_copy_requires_confirmation_and_only_copies_that_file(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source = tmp_path/'linked-original'
    (source/'Reports').mkdir(parents=True)
    (source/'Reports'/'chosen.docx').write_bytes(b'chosen report')
    (source/'Reports'/'other.docx').write_bytes(b'other report')
    target = tmp_path/'native-project'
    target.mkdir()
    catalog.extra.extend([
        dict(key='linked:old', project_id=None, member_id=None, number='OLD', title='Original',
             test_item='', source='linked', folder_path=str(source)),
        dict(key='project:p1', project_id='p1', member_id=None, number='CURRENT', title='Current',
             test_item='', source='connlab', folder_path=str(target))])
    context = activate_test_context(service)
    plan = service.copy_preview('linked:old', 'Reports/chosen.docx', context, 'Reference materials/Reports')
    assert plan['status'] == 'ready'
    assert list(target.iterdir()) == []
    assert len(plan['items']) == 1
    result = service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    assert result['status'] == 'completed'
    assert result['counts']['copied'] == 1
    assert (target/'Reference materials'/'Reports'/'chosen.docx').read_bytes() == b'chosen report'
    assert not (target/'Reference materials'/'Reports'/'other.docx').exists()
    assert (source/'Reports'/'chosen.docx').read_bytes() == b'chosen report'
    assert (source/'Reports'/'other.docx').read_bytes() == b'other report'
    assert store.catalog() == []
    assert session.scalar(select(func.count()).select_from(ProjectModel)) == 0
    assert service.copy_confirm(plan['plan_id'], plan['fingerprint'], context) == result


@pytest.fixture
def copy_materials(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    source, target = tmp_path/'original', tmp_path/'current'
    source.mkdir()
    target.mkdir()
    (source/'report.docx').write_bytes(b'incoming')
    catalog.extra.extend([
        dict(key='linked:old', project_id=None, member_id=None, number='OLD', title='Original',
             test_item='', source='linked', folder_path=str(source)),
        dict(key='project:p1', project_id='p1', member_id='m1', number='CURRENT', title='Current',
             test_item='', source='received', folder_path=str(target))])
    return service, store, files, catalog, session, source, target, activate_test_context(service)


def test_selected_copy_archives_conflicts_and_repeat_skips_actual_preserved_file(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    (target/'Reference materials').mkdir()
    original = target/'Reference materials'/'report.docx'
    original.write_bytes(b'manual target')
    plan = service.copy_preview('linked:old', 'report.docx', context)
    assert plan['items'][0]['action'] == 'supplement'
    result = service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    archived = target/result['items'][0]['target_relative']
    assert archived.read_bytes() == b'incoming'
    assert original.read_bytes() == b'manual target'
    repeat = service.copy_preview('linked:old', 'report.docx', context)
    assert repeat['items'][0]['action'] == 'skip'
    assert service.copy_confirm(repeat['plan_id'], repeat['fingerprint'], context)['counts']['skipped'] == 1
    archived.write_bytes(b'human archive edit')
    new_plan = service.copy_preview('linked:old', 'report.docx', context)
    assert new_plan['items'][0]['action'] == 'supplement'
    service.copy_confirm(new_plan['plan_id'], new_plan['fingerprint'], context)
    assert archived.read_bytes() == b'human archive edit'
    assert original.read_bytes() == b'manual target'


@pytest.mark.parametrize('change', ['source_bytes', 'source_registration', 'target_bytes', 'target_registration', 'target_identity'])
def test_selected_copy_rejects_stale_confirmation(copy_materials, tmp_path, change):
    service, store, files, catalog, session, source, target, context = copy_materials
    plan = service.copy_preview('linked:old', 'report.docx', context)
    if change == 'source_bytes':
        (source/'report.docx').write_bytes(b'changed')
    elif change == 'source_registration':
        catalog.extra[0]['title'] = 'Changed source'
    elif change == 'target_registration':
        catalog.extra[1]['folder_path'] = str(source)
    elif change == 'target_identity':
        target.rename(tmp_path/'previous-target')
        target.mkdir()
    else:
        (target/'manual.txt').write_bytes(b'changed target')
    with pytest.raises(ValueError, match='changed'):
        service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    assert not (target/'Reference materials').exists()


def test_selected_copy_rejects_unsafe_paths_and_nonbusiness_targets(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    for relative in ('../report.docx', '/report.docx', 'report.docx:stream', 'C:/report.docx', ''):
        with pytest.raises(ValueError):
            service.copy_preview('linked:old', relative, context)
    for directory in ('../outside', '/outside', 'C:/outside', 'Reports:stream', 'a/../b', 'CON'):
        with pytest.raises(ValueError):
            service.copy_preview('linked:old', 'report.docx', context, directory)
    with pytest.raises(LookupError):
        service.update_copy_context(service.create_copy_context()['session_id'], 1, 'old')
    assert list(target.iterdir()) == []


def test_selected_copy_control_data_is_archived_without_activation(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    (source/'.connlab').mkdir()
    (source/'.connlab'/'snapshot.json').write_bytes(b'original unparsed snapshot')
    plan = service.copy_preview('linked:old', '.connlab/snapshot.json', context, '.connlab')
    assert 'archived' in plan['items'][0]['reason']
    result = service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    assert result['counts']['supplemented'] == 1
    assert not (target/'.connlab').exists()
    assert (target/result['items'][0]['target_relative']).read_bytes() == b'original unparsed snapshot'


def test_selected_copy_failure_retry_preserves_manual_collision(copy_materials, monkeypatch):
    service, store, files, catalog, session, source, target, context = copy_materials
    plan = service.copy_preview('linked:old', 'report.docx', context)
    publish = files.publish
    def fail(*args):
        raise OSError('Synthetic locked destination')
    monkeypatch.setattr(files, 'publish', fail)
    result = service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    assert result['status'] == 'incomplete' and result['counts']['failed'] == 1
    (target/'Reference materials').mkdir()
    (target/'Reference materials'/'report.docx').write_bytes(b'later manual file')
    monkeypatch.setattr(files, 'publish', publish)
    with Session(session.bind) as fresh:
        fresh_store = MaterialReceiptRepository(fresh)
        fresh_catalog = Catalog(fresh_store)
        fresh_catalog.extra = catalog.extra
        resumed = MaterialReceiptService(fresh_store, MaterialReceiptFiles(files.settings), fresh_catalog)
        retried = resumed.retry(result['batch_id'], context)
    assert retried['status'] == 'incomplete' and retried['counts']['failed'] == 1
    assert (target/'Reference materials'/'report.docx').read_bytes() == b'later manual file'
    assert (source/'report.docx').read_bytes() == b'incoming'


def test_selected_copy_api_uses_durable_batch_namespace_and_explicit_confirmation(copy_materials):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_material_receipts import router, get_material_receipt_service
    service, store, files, catalog, session, source, target, context = copy_materials
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_material_receipt_service] = lambda: service
    with TestClient(app) as client:
        response = client.post('/api/material-receipts/copy-preview', json={
            'source_key': 'linked:old', 'relative_path': 'report.docx', 'context': context})
        assert response.status_code == 200, response.text
        plan = response.json()
        assert list(target.iterdir()) == []
        assert client.post('/api/material-receipts/copy-confirm', json={
            'plan_id': plan['plan_id'], 'fingerprint': '0'*64, 'context': context}).status_code == 409
        response = client.post('/api/material-receipts/copy-confirm', json={
            'plan_id': plan['plan_id'], 'fingerprint': plan['fingerprint'], 'context': context})
        assert response.status_code == 200, response.text
        result = response.json()
        assert result['operation'] == 'copy_file' and result['counts']['copied'] == 1
        history = client.get('/api/material-receipts/catalog-history', params={'key': 'project:p1'})
        assert history.status_code == 200, history.text
        assert history.json()['items'][0]['batch_id'] == result['batch_id']
        assert history.json()['items'][0]['counts']['copied'] == 1
        assert client.get('/api/material-receipts/catalog-history', params={'key': 'project:missing'}).status_code == 404
        assert client.post('/api/material-receipts/batches/'+result['batch_id']+'/retry').status_code == 409
        assert client.post('/api/material-receipts/batches/'+result['batch_id']+'/retry', json={'context': context}).json() == result
        assert client.get('/api/material-receipts/batches/'+result['batch_id']).json() == result


def test_selected_copy_concurrent_confirm_is_exclusive(copy_materials, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    service, store, files, catalog, session, source, target, context = copy_materials
    plan = service.copy_preview('linked:old', 'report.docx', context)
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
            fresh_catalog = Catalog(fresh_store)
            fresh_catalog.extra = catalog.extra
            fresh_service = MaterialReceiptService(fresh_store, MaterialReceiptFiles(files.settings), fresh_catalog)
            return fresh_service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
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
    assert (target/'Reference materials'/'report.docx').read_bytes() == b'incoming'


def test_selected_copy_rejects_reparse_source_and_destination(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    try:
        (source/'redirect.docx').symlink_to(source/'report.docx')
        (target/'redirect').symlink_to(source, target_is_directory=True)
    except OSError:
        pytest.skip('Host does not allow creating test symlinks')
    with pytest.raises(ValueError, match='Redirected'):
        service.copy_preview('linked:old', 'redirect.docx', context)
    with pytest.raises(ValueError, match='Redirected'):
        service.copy_preview('linked:old', 'report.docx', context, 'redirect')


def test_whole_folder_receipt_does_not_skip_file_copied_to_another_relative_directory(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    copy = service.copy_preview('linked:old', 'report.docx', context)
    service.copy_confirm(copy['plan_id'], copy['fingerprint'], context)
    assert (target/'Reference materials'/'report.docx').read_bytes() == b'incoming'
    assert not (target/'report.docx').exists()
    whole = service.preview(str(source), 'CURRENT', target_key='project:p1')
    assert whole['items'][0]['action'] == 'copy'
    assert whole['items'][0]['target_relative'] == 'report.docx'
    result = service.confirm(whole['plan_id'], whole['fingerprint'])
    assert result['counts']['copied'] == 1
    assert (target/'report.docx').read_bytes() == b'incoming'
    assert (target/'Reference materials'/'report.docx').read_bytes() == b'incoming'
    assert (source/'report.docx').read_bytes() == b'incoming'


def test_whole_folder_receipt_reuses_selected_copy_archive_for_same_relative_destination(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    (target/'report.docx').write_bytes(b'manual target')
    copy = service.copy_preview('linked:old', 'report.docx', context, '')
    copied = service.copy_confirm(copy['plan_id'], copy['fingerprint'], context)
    archived = copied['items'][0]['target_relative']
    whole = service.preview(str(source), 'CURRENT', target_key='project:p1')
    assert whole['items'][0]['action'] == 'skip'
    assert whole['items'][0]['target_relative'] == archived
    result = service.confirm(whole['plan_id'], whole['fingerprint'])
    assert result['counts']['skipped'] == 1
    assert (target/'report.docx').read_bytes() == b'manual target'
    assert (target/archived).read_bytes() == b'incoming'


def test_catalog_history_exposes_durable_native_copy_and_receipt_results(copy_materials, tmp_path):
    service, store, files, catalog, session, source, target, context = copy_materials
    copy = service.copy_preview('linked:old', 'report.docx', context)
    copied = service.copy_confirm(copy['plan_id'], copy['fingerprint'], context)
    whole = service.preview(str(source), 'CURRENT', target_key='project:p1')
    received = service.confirm(whole['plan_id'], whole['fingerprint'])
    history = service.catalog_history('project:p1')
    assert {row['batch_id'] for row in history['items']} == {copied['batch_id'], received['batch_id']}
    assert all(row['status'] == 'completed' and row['source_path'] == str(source) for row in history['items'])
    assert service.catalog_history('member:m1') == history
    assert service.catalog_history('linked:old')['items'] == []
    target.rename(tmp_path/'moved-current')
    assert service.catalog_history('project:p1') == history
    with pytest.raises(LookupError):
        service.catalog_history('project:missing')
    assert (tmp_path/'moved-current'/'report.docx').read_bytes() == b'incoming'


def test_receipt_global_records_do_not_enter_legacy_project_portable_contract(receipt, tmp_path):
    from sqlalchemy import text
    from backend.infrastructure.project_library.ownership import capture, typed_record
    service, store, files, catalog, session = receipt
    source = tmp_path/'original'
    source.mkdir()
    (source/'record.txt').write_bytes(b'original material')
    preview = service.preview(str(source), 'HISTORICAL')
    received = service.confirm(preview['plan_id'], preview['fingerprint'])
    session.add(ProjectModel(project_id='business-project', product_name='Native product', requestor='Lab', status='draft'))
    session.commit()
    before = (store.settings(), store.entry(received['receipt_id']), store.batch(received['batch_id']))
    project_rows = capture(session, 'business-project')
    assert [row['project_id'] for row in project_rows['projects']] == ['business-project']
    for family in ('material_receipt_settings', 'material_receipt_entries', 'material_receipt_batches'):
        assert family not in project_rows
        with pytest.raises(ValueError, match='unsupported record family'):
            typed_record(family, {})
    assert (store.settings(), store.entry(received['receipt_id']), store.batch(received['batch_id'])) == before
    assert (source/'record.txt').read_bytes() == b'original material'
    session.execute(text('CREATE TABLE unknown_future_records (id TEXT PRIMARY KEY)'))
    session.commit()
    with pytest.raises(ValueError, match='not covered by the portable contract'):
        capture(session, 'business-project')


def activate_test_context(service):
    session_id = service.create_copy_context()['session_id']
    active = service.update_copy_context(session_id, 1, 'p1')
    return {'session_id': session_id, 'token': active['token']}


def test_copy_context_is_required_for_preview_confirm_and_generic_retry(copy_materials):
    service, store, files, catalog, session, source, target, context = copy_materials
    plan = service.copy_preview('linked:old', 'report.docx', context)
    service.update_copy_context(context['session_id'], 2, None)
    with pytest.raises(ValueError, match='Workbench'):
        service.copy_confirm(plan['plan_id'], plan['fingerprint'], context)
    assert not (target/'Reference materials').exists()
    replacement = service.update_copy_context(context['session_id'], 3, 'p1')
    renewed = {'session_id': context['session_id'], 'token': replacement['token']}
    with pytest.raises(ValueError, match='context changed'):
        service.copy_confirm(plan['plan_id'], plan['fingerprint'], renewed)
    current = service.copy_preview('linked:old', 'report.docx', renewed)
    result = service.copy_confirm(current['plan_id'], current['fingerprint'], renewed)
    service.update_copy_context(context['session_id'], 4, None)
    assert service.batch(result['batch_id']) == result
    with pytest.raises(ValueError, match='Workbench'):
        service.retry(result['batch_id'], renewed)
    with pytest.raises(ValueError, match='Workbench'):
        service.retry(result['batch_id'])
    with pytest.raises(ValueError, match='Workbench'):
        service.copy_preview('linked:old', 'report.docx', None)


def test_copy_http_never_accepts_target_only_or_stale_context(copy_materials):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_material_receipts import router, get_material_receipt_service
    service, store, files, catalog, session, source, target, context = copy_materials
    app=FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_material_receipt_service]=lambda:service
    with TestClient(app) as client:
        base='/api/material-receipts'
        legacy={'source_key':'linked:old','relative_path':'report.docx','target_key':'project:p1'}
        assert client.post(base+'/copy-preview',json=legacy).status_code == 422
        valid={'source_key':'linked:old','relative_path':'report.docx','context':context}
        assert client.post(base+'/copy-preview',json={**valid,'target_key':'project:p1'}).status_code == 422
        plan=client.post(base+'/copy-preview',json=valid).json()
        confirm={'plan_id':plan['plan_id'],'fingerprint':plan['fingerprint']}
        assert client.post(base+'/copy-confirm',json=confirm).status_code == 422
        cleared=client.post(base+'/copy-context',json={'session_id':context['session_id'],'intent':3,'project_id':None})
        assert cleared.status_code == 200 and cleared.json()['target'] is None
        stale=client.post(base+'/copy-context',json={'session_id':context['session_id'],'intent':2,'project_id':'p1'})
        assert stale.status_code == 409
        assert client.post(base+'/copy-confirm',json={**confirm,'context':context}).status_code == 409
        assert client.post(base+'/copy-preview',json=valid).status_code == 409
    assert list(target.iterdir()) == []


@pytest.mark.parametrize('receipt', [False], indirect=True)
@pytest.mark.parametrize('already_exists', [False, True])
def test_unconfigured_material_library_is_lazy_and_keeps_its_saved_location(receipt, tmp_path, monkeypatch, already_exists):
    from backend.infrastructure.project_library import material_receipt_files
    service, store, files, catalog, session = receipt
    documents = tmp_path / 'Redirected Documents'
    documents.mkdir()
    original = documents / 'personal.txt'
    original.write_bytes(b'personal document retained')
    files.settings = __import__('dataclasses').replace(files.settings, output_root=documents / 'ConnLab')
    expected = documents / 'ConnLab' / 'Materials'
    if already_exists:
        expected.mkdir(parents=True)
        (expected / 'retained.txt').write_bytes(b'existing materials')
    preview_runtime = service.runtime()
    assert preview_runtime['root_path'] == str(expected)
    assert not preview_runtime['configured']
    runtime = service.runtime(ensure_default=True)
    assert runtime['root_path'] == str(expected)
    assert runtime['configured'] and runtime['available']
    assert expected.is_dir()
    if already_exists:
        assert (expected / 'retained.txt').read_bytes() == b'existing materials'
    else:
        assert list(expected.iterdir()) == []
    assert original.read_bytes() == b'personal document retained'
    saved = store.settings()
    files.settings = __import__('dataclasses').replace(files.settings, output_root=tmp_path / 'Different Documents')
    with Session(session.bind) as fresh:
        fresh_store = MaterialReceiptRepository(fresh)
        fresh_service = MaterialReceiptService(fresh_store, MaterialReceiptFiles(files.settings), Catalog(fresh_store))
        assert fresh_service.runtime() == runtime
        assert fresh_store.settings() == saved
    assert not (tmp_path / 'Different Documents').exists()
    assert store.catalog() == []


@pytest.mark.parametrize('receipt', [False], indirect=True)
def test_first_receipt_preview_can_use_default_library_without_changing_source(receipt, tmp_path, monkeypatch):
    from backend.infrastructure.project_library import material_receipt_files
    service, store, files, catalog, session = receipt
    documents = tmp_path / 'Documents'
    documents.mkdir()
    files.settings = __import__('dataclasses').replace(files.settings, output_root=documents / 'ConnLab')
    source = tmp_path / 'incoming'
    source.mkdir()
    (source / 'manual.txt').write_bytes(b'manual content')
    plan = service.preview(str(source), product_name='Connector')
    assert Path(plan['target_path']).parent == documents / 'ConnLab' / 'Materials'
    assert not Path(plan['target_path']).exists()
    assert (source / 'manual.txt').read_bytes() == b'manual content'
    assert store.catalog() == []


@pytest.mark.parametrize('offline', [False, True])
def test_existing_library_is_never_replaced_by_the_default(receipt, tmp_path, monkeypatch, offline):
    from backend.infrastructure.project_library import material_receipt_files
    service, store, files, catalog, session = receipt
    before = store.settings()
    root = Path(before['root_path'])
    (root / 'manual.txt').write_bytes(b'human edit')
    moved = tmp_path / 'moved-by-user' if offline else root
    if offline:
        root.rename(moved)
    def unexpected_default():
        raise AssertionError('Existing config must win')
    monkeypatch.setattr(files, 'default_root', unexpected_default)
    runtime = service.runtime()
    assert runtime['root_path'] == before['root_path']
    assert runtime['configured'] and runtime['available'] is not offline
    assert store.settings() == before
    assert root.exists() is not offline
    assert (moved / 'manual.txt').read_bytes() == b'human edit'


@pytest.mark.parametrize('receipt', [False], indirect=True)
def test_default_library_does_not_claim_a_registered_project_directory(receipt, tmp_path, monkeypatch):
    from backend.infrastructure.project_library import material_receipt_files
    service, store, files, catalog, session = receipt
    documents = tmp_path / 'Documents'
    documents.mkdir()
    files.settings = __import__('dataclasses').replace(files.settings, output_root=documents / 'ConnLab')
    catalog.extra.append(dict(key='project:p1', project_id='p1', source='connlab', folder_path=str(documents)))
    with pytest.raises(ValueError, match='separate'):
        service.runtime(ensure_default=True)
    assert store.settings() == {'root_path': '', 'revision': 0}
    assert not (documents / 'ConnLab').exists()


@pytest.mark.parametrize('receipt', [False], indirect=True)
def test_default_library_creation_failure_does_not_save_a_setting(receipt, tmp_path):
    service, store, files, catalog, session = receipt
    documents = tmp_path / 'Documents'
    documents.mkdir()
    files.settings = __import__('dataclasses').replace(files.settings, output_root=documents / 'ConnLab')
    expected = documents / 'ConnLab' / 'Materials'
    expected.parent.write_bytes(b'existing user file')
    with pytest.raises(ValueError, match='Settings'):
        service.runtime(ensure_default=True)
    assert store.settings() == {'root_path': '', 'revision': 0}
    assert not expected.exists()
    assert expected.parent.read_bytes() == b'existing user file'


@pytest.mark.parametrize('receipt', [False], indirect=True)
def test_default_library_stays_separate_from_internal_data(receipt, tmp_path, monkeypatch):
    from backend.infrastructure.project_library import material_receipt_files
    service, store, files, catalog, session = receipt
    files.settings = __import__('dataclasses').replace(files.settings, output_root=files.settings.data_dir.parent)
    monkeypatch.setattr(files, 'default_root', lambda: files.settings.data_dir)
    with pytest.raises(ValueError, match='separate'):
        service.runtime(ensure_default=True)
    assert store.settings() == {'root_path': '', 'revision': 0}
    assert not (files.settings.data_dir / 'ConnLab').exists()
