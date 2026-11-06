"""Controlled evidence discovery/retention through real HTTP, files and SQLite."""
from hashlib import sha256
import json

import pytest

from backend.infrastructure.project_library.files import LibraryFiles
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
from tests.integration.test_internal_report_generation_api import lab, official_report


BASE = '/api/projects/P1/report-workspace/authoring'


def scan(lab):
    response = lab['client'].get(BASE + '/inventory')
    assert response.status_code == 200, response.text
    return response.json()


def item_for(snapshot, relative_path, role='evidence'):
    item = next(item for item in snapshot['items'] if item['relative_path'] == relative_path)
    assert item['status'] == 'candidate'
    return {'relative_path': relative_path, 'file_token': item['file_token'], 'role': role}


def retain(lab, snapshot, items, revision=0):
    return lab['client'].post(BASE + '/inventory/retain', json={
        'expected_revision': revision, 'root_token': snapshot['root_token'], 'items': items})


def material(lab, names):
    original, root = official_report(lab)
    paths = []
    for name, content in names:
        path = original.parent / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        paths.append(path)
    return root, paths


def test_unavailable_inventory_does_not_disable_existing_manual_upload(lab):
    result = scan(lab)
    assert result['available'] is False and result['items'] == []
    assert result['reason']
    uploaded = lab['client'].post(BASE + '/sources', data={'role': 'evidence', 'expected_revision': 0},
                                  files={'file': ('manual.csv', b'SN,value\nSN1,12\n')})
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()['sources'][0]['source_locator'] == ''
    assert scan(lab)['available'] is False


def test_retain_multiple_sources_preserves_exact_bytes_and_relative_origins(lab):
    root, files = material(lab, [('Test results/current.csv', b'SN,Current\nSN1,250\n'),
                               ('Test results/force.csv', b'SN,Force\nSN1,240\n')])
    originals = [(path.read_bytes(), path.stat().st_mtime_ns) for path in files]
    snapshot = scan(lab)
    assert snapshot['available'] is True
    assert str(root) not in json.dumps(snapshot)
    selections = [item_for(snapshot, path.relative_to(root).as_posix()) for path in files]
    response = retain(lab, snapshot, selections)
    assert response.status_code == 200, response.text
    state = response.json()
    assert len(state['sources']) == 2
    assert state['outputs'] == [] and state['results'] == [] and state['mappings'] == []
    assert lab['client'].get(BASE).json() == state
    for source, path, (content, modified) in zip(state['sources'], files, originals):
        assert source['source_locator'] == path.relative_to(root).as_posix()
        assert source['sha256'] == sha256(content).hexdigest()
        assert lab['client'].get(source['download_url']).content == content
        assert path.read_bytes() == content and path.stat().st_mtime_ns == modified
    repeated = retain(lab, snapshot, selections, state['revision'])
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == state


@pytest.mark.parametrize('relative', ['C:/outside.csv', '/outside.csv', '../outside.csv',
                                    'child/../../outside.csv', 'data.csv:private'])
def test_inventory_body_cannot_select_absolute_or_escaping_paths(lab, relative):
    _, files = material(lab, [('data.csv', b'untouched')])
    snapshot = scan(lab)
    response = retain(lab, snapshot, [{'relative_path': relative, 'file_token': '0' * 64, 'role': 'evidence'}])
    assert response.status_code == 422, response.text
    assert lab['client'].get(BASE).json()['revision'] == 0
    assert files[0].read_bytes() == b'untouched'
    extra = lab['client'].post(BASE + '/inventory/retain', json={
        'expected_revision': 0, 'root_token': snapshot['root_token'], 'root_path': str(lab['root']),
        'items': [{'relative_path': 'data.csv', 'file_token': '0' * 64, 'role': 'evidence'}]})
    assert extra.status_code == 422


@pytest.mark.parametrize('changed', ['file', 'root_token', 'manifest'])
def test_stale_second_source_or_foreign_folder_never_saves_first_source(lab, changed):
    root, files = material(lab, [('first.csv', b'first review'), ('second.csv', b'second review')])
    snapshot = scan(lab)
    selections = [item_for(snapshot, path.relative_to(root).as_posix()) for path in files]
    before = lab['client'].get(BASE).json()
    if changed == 'file':
        files[1].write_bytes(b'replaced second source')
    elif changed == 'root_token':
        snapshot['root_token'] = '0' * 64
    else:
        manifest_path = root / '.connlab' / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['project_id'] = 'foreign-project'
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    response = retain(lab, snapshot, selections)
    assert response.status_code in {409, 422}, response.text
    assert lab['client'].get(BASE).json() == before
    assert files[0].read_bytes() == b'first review'


def test_invalid_second_package_does_not_leave_a_partially_saved_request(lab):
    root, files = material(lab, [('first.csv', b'valid supporting data'),
                               ('Temperature_ReportResults.zip', b'not a valid Tools package')])
    snapshot = scan(lab)
    selections = [item_for(snapshot, files[0].relative_to(root).as_posix()),
                  item_for(snapshot, files[1].relative_to(root).as_posix(), 'tools_result_package')]
    before = lab['client'].get(BASE).json()
    response = retain(lab, snapshot, selections)
    assert response.status_code == 422, response.text
    assert lab['client'].get(BASE).json() == before


def confirm_mapping(lab, source, revision):
    response = lab['client'].post(BASE + '/mappings', json={
        'expected_revision': revision, 'source_id': source['source_id'], 'kind': 'specification',
        'source_locator': 'Row 2', 'label': 'Specification revision', 'value': 'Rev.2',
        'status': 'confirmed', 'reason': 'Reviewed this exact source record'})
    assert response.status_code == 200, response.text
    return response.json()


def test_same_filename_in_another_directory_does_not_supersede_confirmed_source(lab):
    root, files = material(lab, [('Group A/data.csv', b'Group A source'), ('Group B/data.csv', b'Group B source')])
    snapshot = scan(lab)
    state = retain(lab, snapshot, [item_for(snapshot, files[0].relative_to(root).as_posix())]).json()
    state = confirm_mapping(lab, state['sources'][0], state['revision'])
    response = retain(lab, snapshot, [item_for(snapshot, files[1].relative_to(root).as_posix())], state['revision'])
    assert response.status_code == 200, response.text
    state = response.json()
    assert len(state['sources']) == 2
    assert state['mappings'][0]['status'] == 'confirmed'
    files[0].write_bytes(b'Group A changed source')
    current = scan(lab)
    superseded = retain(lab, current, [item_for(current, files[0].relative_to(root).as_posix())], state['revision'])
    assert superseded.status_code == 200, superseded.text
    assert superseded.json()['mappings'][0]['status'] == 'pending'


def test_identical_bytes_at_two_locations_keep_both_source_origins(lab):
    root, files = material(lab, [('Group A/data.csv', b'exact same bytes'), ('Group B/data.csv', b'exact same bytes')])
    snapshot = scan(lab)
    response = retain(lab, snapshot, [item_for(snapshot, path.relative_to(root).as_posix()) for path in files])
    assert response.status_code == 200, response.text
    sources = response.json()['sources']
    assert len(sources) == 2
    assert len({source['source_id'] for source in sources}) == 2
    assert {source['source_locator'] for source in sources} == {path.relative_to(root).as_posix() for path in files}
    assert len({source['sha256'] for source in sources}) == 1


def test_reselecting_earlier_bytes_becomes_the_latest_source_version(lab):
    root, files = material(lab, [('data.csv', b'revision A')])
    path = files[0]
    state = lab['client'].get(BASE).json()
    versions = []
    for index, content in enumerate((b'revision A', b'revision B', b'revision A')):
        path.write_bytes(content)
        snapshot = scan(lab)
        response = retain(lab, snapshot, [item_for(snapshot, path.relative_to(root).as_posix())], state['revision'])
        assert response.status_code == 200, response.text
        state = response.json()
        versions.append(state['sources'][-1])
        assert lab['client'].get(versions[-1]['download_url']).content == content
        if index == 0:
            state = confirm_mapping(lab, versions[0], state['revision'])
        else:
            assert state['mappings'][0]['status'] == 'pending'
    assert len({source['source_id'] for source in versions}) == 3
    assert versions[0]['sha256'] == versions[2]['sha256']
    repeated = retain(lab, snapshot, [item_for(snapshot, path.relative_to(root).as_posix())], state['revision'])
    assert repeated.status_code == 200, repeated.text
    assert repeated.json() == state


def test_actual_library_membership_is_verified_before_source_retention(lab):
    root, files = material(lab, [('data.csv', b'controlled library evidence')])
    with lab['factory']() as session:
        member = ProjectLibraryRepository(session).add_member({
            'member_id': 'member-P1', 'project_id': 'P1', 'source_project_id': 'P1',
            'ltr_number': 'DL-2026-05-001', 'title': 'Isolated linked project',
            'folder_path': str(root), 'source_path': str(root), 'revision': 1,
            'created_at': '2026-11-07T00:00:00+00:00', 'disposition': 'working'})
    LibraryFiles(lab['settings']).write_marker(member)
    snapshot = scan(lab)
    assert snapshot['available'] is True
    selected = item_for(snapshot, files[0].relative_to(root).as_posix())
    marker_path = root / '.connlab' / 'library.json'
    marker = json.loads(marker_path.read_text(encoding='utf-8'))
    marker['member_id'] = 'another-library-member'
    marker_path.write_text(json.dumps(marker), encoding='utf-8')
    assert scan(lab)['available'] is False
    response = retain(lab, snapshot, [selected])
    assert response.status_code in {409, 422}, response.text
    assert lab['client'].get(BASE).json()['sources'] == []
