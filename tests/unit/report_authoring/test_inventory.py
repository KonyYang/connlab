from hashlib import sha256
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.report_authoring.inventory import ReportInventory
from backend.infrastructure.files.report_evidence_inventory import ReportEvidenceInventory
from backend.infrastructure.project_library.files import LibraryFiles, identity


class ProjectStore:
    """Project-library persistence seam, isolated from the operator database."""

    def __init__(self, workspace):
        self.value = workspace
        self.registry_state = 'active'
        self.member_value = None

    def project_context(self, project_id):
        if project_id != 'project-1':
            raise LookupError('Project not found.')
        return {'registry_state': self.registry_state, 'registry_revision': 1,
                'workspace': self.value, 'folder_paths': [], 'numbers': []}

    def imported_identity(self, project_id):
        return {'member_id': self.member_value['member_id']} if self.member_value else None

    def member(self, member_id):
        return self.member_value


@pytest.fixture
def inventory(tmp_path):
    root = tmp_path / 'projects' / 'DL-2026-09-032'
    business = root / 'DL-2026-09-032 Example'
    business.mkdir(parents=True)
    (root / 'Source Book').mkdir()
    metadata = root / '.connlab'
    metadata.mkdir()
    workspace = {'project_id': 'project-1', 'dl_number': 'DL-2026-09-032',
                 'local_workspace_path': str(root), 'official_folder_path': str(business),
                 'source_book_path': str(root / 'Source Book'), 'manifest_path': str(metadata / 'manifest.json')}
    manifest = {**workspace, 'schema_version': 1, 'official_project_folder_path': str(business),
                'official_folder_identity': identity(business)}
    (metadata / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    settings = SimpleNamespace(data_dir=tmp_path / 'app', projects_dir=tmp_path / 'projects', library_root=None)
    store = ProjectStore(workspace)
    gateway = ReportEvidenceInventory(LibraryFiles(settings), store)
    return ReportInventory(gateway), root, business, store


def test_scan_is_metadata_only_and_selection_returns_exact_bytes_without_changing_source(inventory, monkeypatch):
    service, root, business, _ = inventory
    source = business / 'Temperature_ReportResults.zip'
    source.write_bytes(b'exact retained package bytes')
    original = source.stat()
    open_file = Path.open

    def no_source_read(path, *args, **kwargs):
        if path == source:
            pytest.fail('The inventory must not parse or hash business files.')
        return open_file(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, 'open', no_source_read)
        snapshot = service.scan('project-1')
    assert snapshot['available'] is True
    assert str(root) not in json.dumps(snapshot)
    item = next(item for item in snapshot['items'] if item['status'] == 'candidate')
    assert item['relative_path'] == 'DL-2026-09-032 Example/Temperature_ReportResults.zip'
    assert item['suggested_role'] == 'tools_result_package'
    assert item['status'] == 'candidate'
    selected = service.read_selected('project-1', root_token=snapshot['root_token'],
                                     relative_path=item['relative_path'], file_token=item['file_token'])
    assert selected['content'] == b'exact retained package bytes'
    assert selected['sha256'] == sha256(b'exact retained package bytes').hexdigest()
    assert selected['source_locator'] == item['relative_path']
    assert source.stat().st_mtime_ns == original.st_mtime_ns


def test_missing_controlled_folder_is_explained_without_disabling_manual_upload(inventory):
    service, _, _, store = inventory
    store.value = None
    result = service.scan('project-1')
    assert result['available'] is False
    assert result['items'] == []
    assert 'upload' in result['reason'].lower()


def test_history_temporary_and_unsupported_sources_are_visible_but_not_selectable(inventory):
    service, root, business, _ = inventory
    for name in ('History/old.csv', 'temp/scratch.csv', '~$Report.docx', 'raw.xls', 'mail.msg', 'data.csv'):
        path = business / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'not parsed during discovery')
    snapshot = service.scan('project-1')
    by_name = {item['name']: item for item in snapshot['items']}
    assert by_name['History']['status'] == by_name['temp']['status'] == 'excluded'
    assert 'old.csv' not in by_name and 'scratch.csv' not in by_name
    assert by_name['~$Report.docx']['status'] == 'excluded'
    assert by_name['raw.xls']['status'] == by_name['mail.msg']['status'] == 'unsupported'
    assert by_name['data.csv']['status'] == 'candidate'
    for name in ('History', '~$Report.docx', 'raw.xls', 'mail.msg'):
        item = by_name[name]
        with pytest.raises(ValueError):
            service.read_selected('project-1', root_token=snapshot['root_token'],
                                  relative_path=item['relative_path'], file_token=item['file_token'])


def test_same_filename_candidates_remain_distinct_and_require_source_review(inventory):
    service, root, business, _ = inventory
    first = business / 'data.csv'
    second = root / 'Source Book' / 'data.csv'
    first.write_bytes(b'first source')
    second.write_bytes(b'second source')
    snapshot = service.scan('project-1')
    candidates = [item for item in snapshot['items'] if item['status'] == 'candidate']
    assert len(candidates) == 2
    assert all(item['duplicate_name'] for item in candidates)
    assert len({item['relative_path'] for item in candidates}) == 2
    assert {service.read_selected('project-1', root_token=snapshot['root_token'],
                                 relative_path=item['relative_path'], file_token=item['file_token'])['content']
            for item in candidates} == {b'first source', b'second source'}


def selected_item(service, business):
    source = business / 'measurement.csv'
    source.write_bytes(b'sample,value\nSN1,12.5\n')
    snapshot = service.scan('project-1')
    item = next(item for item in snapshot['items'] if item['status'] == 'candidate')
    arguments = {'root_token': snapshot['root_token'], 'relative_path': item['relative_path'], 'file_token': item['file_token']}
    return source, arguments


def test_changed_source_is_not_silently_adopted_from_an_old_inventory(inventory):
    service, _, business, _ = inventory
    source, arguments = selected_item(service, business)
    source.write_bytes(b'sample,value\nSN1,99.1\n')
    with pytest.raises(ValueError, match='changed'):
        service.read_selected('project-1', **arguments)


@pytest.mark.parametrize('path', ['../outside.csv', '/outside.csv', 'C:/outside.csv',
                                 'child/../../outside.csv', 'Source Book\\data.csv', 'file.csv:secret'])
def test_client_paths_cannot_escape_the_registered_project(inventory, path):
    service, _, business, _ = inventory
    _, arguments = selected_item(service, business)
    with pytest.raises(ValueError):
        service.read_selected('project-1', **{**arguments, 'relative_path': path})


@pytest.mark.parametrize('change', ['project', 'ltr', 'business_identity', 'registry'])
def test_changed_project_identity_invalidates_read_and_discovery(inventory, change):
    service, root, business, store = inventory
    _, arguments = selected_item(service, business)
    manifest_path = root / '.connlab' / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if change == 'registry':
        store.registry_state = 'trash'
    elif change == 'project':
        manifest['project_id'] = 'another-project'
    elif change == 'ltr':
        manifest['dl_number'] = 'DL-2026-09-999'
    else:
        manifest['official_folder_identity'] = [99, 999]
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    assert service.scan('project-1')['available'] is False
    with pytest.raises(ValueError):
        service.read_selected('project-1', **arguments)


def test_redirected_candidate_is_reported_but_never_read_or_traversed(inventory, tmp_path):
    service, _, business, _ = inventory
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'secret.csv').write_bytes(b'outside source')
    redirected = business / 'linked'
    try:
        if os.name == 'nt':
            import _winapi
            _winapi.CreateJunction(str(outside), str(redirected))
        else:
            redirected.symlink_to(outside, target_is_directory=True)
    except OSError as error:
        pytest.skip(f'Isolated symbolic-link creation unavailable: {error}')
    snapshot = service.scan('project-1')
    blocked = next(item for item in snapshot['items'] if item['name'] == 'linked')
    assert blocked['status'] == 'blocked'
    assert not any('secret.csv' in item['relative_path'] for item in snapshot['items'])
    with pytest.raises(ValueError):
        service.read_selected('project-1', root_token=snapshot['root_token'],
                              relative_path=blocked['relative_path'] + '/secret.csv', file_token='ignored')


def test_regular_file_replacement_during_open_is_rejected(inventory, monkeypatch):
    service, _, business, _ = inventory
    source, arguments = selected_item(service, business)
    original_open = Path.open
    replaced = False

    def changing_open(path, *args, **kwargs):
        nonlocal replaced
        if path == source and args and args[0] == 'rb' and not replaced:
            replaced = True
            temporary = business / 'replacement.csv'
            temporary.write_bytes(b'unreviewed replacement')
            os.replace(temporary, source)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', changing_open)
    with pytest.raises(ValueError, match='changed'):
        service.read_selected('project-1', **arguments)


def test_empty_source_is_not_presented_as_ready_to_retain(inventory):
    service, _, business, _ = inventory
    (business / 'empty.csv').touch()
    item = next(item for item in service.scan('project-1')['items'] if item['name'] == 'empty.csv')
    assert item['status'] == 'unsupported'
    assert 'empty' in item['reason'].lower()


@pytest.mark.parametrize('metadata, payload', [('library.json', []), ('library.json', {'format_version': 99}),
                                             ('manifest.json', []), ('manifest.json', {'schema_version': 99})])
def test_malformed_or_newer_identity_metadata_is_explained_without_an_internal_error(inventory, metadata, payload):
    service, root, _, _ = inventory
    (root / '.connlab' / metadata).write_text(json.dumps(payload), encoding='utf-8')
    result = service.scan('project-1')
    assert result['available'] is False
    assert result['reason']
    assert str(root) not in result['reason']


def test_imported_project_without_official_workspace_reuses_library_membership(inventory):
    service, root, business, store = inventory
    store.value = None
    store.member_value = {'member_id': 'member-1', 'project_id': 'project-1', 'source_project_id': None,
                          'ltr_number': 'DL-2026-09-032', 'folder_path': str(root), 'revision': 2, 'is_history': False}
    marker = {'format_version': 1, 'member_id': 'member-1', 'project_id': 'project-1',
              'ltr_number': 'DL-2026-09-032', 'business_relative_path': business.name, 'business_identity': identity(business)}
    marker_path = root / '.connlab' / 'library.json'
    marker_path.write_text(json.dumps(marker), encoding='utf-8')
    source, arguments = selected_item(service, business)
    assert service.read_selected('project-1', **arguments)['content'] == source.read_bytes()
    marker['member_id'] = 'other-member'
    marker_path.write_text(json.dumps(marker), encoding='utf-8')
    assert service.scan('project-1')['available'] is False
    with pytest.raises(ValueError):
        service.read_selected('project-1', **arguments)
