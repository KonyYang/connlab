from hashlib import sha256
import subprocess
import sys

import pytest

from backend.infrastructure.files.report_delivery_receipt import ReportDeliveryReceipts
from backend.infrastructure.files.report_publication_gateway import ReportPublicationGateway


def test_saved_report_survives_metadata_failure_and_resume_does_not_rearchive(tmp_path):
    folder = tmp_path / 'project'; folder.mkdir()
    source = tmp_path / 'source.docx'; source.write_bytes(b'reviewed new report')
    target = folder / 'DL-2026-09-032 Internal Report.docx'; target.write_bytes(b'old manual report')
    files = ReportPublicationGateway()
    receipts = ReportDeliveryReceipts(tmp_path / 'data')
    expected = sha256(source.read_bytes()).hexdigest()
    receipt = receipts.begin('P1', 'a' * 32, {'signature': 'reviewed'}, [{
        'role': 'internal', 'source': str(source), 'sha256': expected,
        'target': str(target), 'current': str(target), 'old_sha256': files.fingerprint(target),
        'history_root': str(folder / 'History' / 'Report')}])
    def unavailable(_):
        raise RuntimeError('database unavailable')
    with pytest.raises(RuntimeError, match='database unavailable'):
        files.publish_regenerated_current(source_path=source, expected_source_sha256=expected,
            current_path=target, expected_current_sha256=receipt['items'][0]['old_sha256'],
            target_path=target, history_root=folder/'History'/'Report', persist=unavailable,
            receipt=receipts.item('P1', 'a' * 32, 'internal'))
    assert target.read_bytes() == b'reviewed new report'
    assert [p.read_bytes() for p in (folder/'History'/'Report').glob('*.docx')] == [b'old manual report']
    saved = []
    files.publish_regenerated_current(source_path=source, expected_source_sha256=expected,
        current_path=target, expected_current_sha256=receipt['items'][0]['old_sha256'],
        target_path=target, history_root=folder/'History'/'Report', persist=saved.append,
        receipt=receipts.item('P1', 'a' * 32, 'internal'))
    assert len(saved) == 1
    assert len(list((folder/'History'/'Report').glob('*.docx'))) == 1
    assert source.read_bytes() == b'reviewed new report'


@pytest.mark.parametrize('crash_phase', ['archiving', 'publishing'])
def test_real_process_exit_after_link_is_recovered_by_owned_identity(tmp_path, crash_phase):
    folder = tmp_path / 'project'; folder.mkdir()
    source = tmp_path / 'source.docx'; source.write_bytes(b'new reviewed')
    target = folder / 'Report.docx'; target.write_bytes(b'old reviewed')
    files = ReportPublicationGateway(); store = ReportDeliveryReceipts(tmp_path/'receipts')
    digest = files.fingerprint(source); old = files.fingerprint(target)
    store.begin('P1', 'b'*32, {'signature': 'approved'}, [{
        'role': 'internal', 'source': str(source), 'sha256': digest, 'target': str(target),
        'current': str(target), 'old_sha256': old, 'history_root': str(folder/'History')}])
    script = """
import os,sys
from pathlib import Path
from backend.infrastructure.files.report_delivery_receipt import ReportDeliveryReceipts
from backend.infrastructure.files.report_publication_gateway import ReportPublicationGateway
store=ReportDeliveryReceipts(Path(sys.argv[1])); item=store.read('P1','b'*32)['items'][0]
real_link=os.link
def crash_after_link(*args,**kwargs):
    real_link(*args,**kwargs)
    if store.read('P1','b'*32)['items'][0]['status'] == sys.argv[2]:
        os._exit(71)
os.link=crash_after_link
ReportPublicationGateway().publish_regenerated_current(source_path=Path(item['source']),expected_source_sha256=item['sha256'],current_path=Path(item['current']),expected_current_sha256=item['old_sha256'],target_path=Path(item['target']),history_root=Path(item['history_root']),persist=lambda _:None,receipt=store.item('P1','b'*32,'internal'))
"""
    child = subprocess.run([sys.executable, '-c', script, str(tmp_path/'receipts'), crash_phase], check=False)
    assert child.returncode == 71
    assert store.read('P1', 'b'*32)['items'][0]['status'] == crash_phase
    assert [p.read_bytes() for p in (folder/'History').glob('*.docx')] == [b'old reviewed']
    files.publish_regenerated_current(source_path=source, expected_source_sha256=digest,
        current_path=target, expected_current_sha256=old, target_path=target, history_root=folder/'History',
        persist=lambda _: None, receipt=store.item('P1', 'b'*32, 'internal'))
    assert target.read_bytes() == b'new reviewed'
    assert [p.read_bytes() for p in (folder/'History').glob('*.docx')] == [b'old reviewed']
    # Same bytes in a different file do not prove that this operation owns it.
    target.unlink(); target.write_bytes(b'new reviewed')
    with pytest.raises(RuntimeError, match='changed outside'):
        files.publish_regenerated_current(source_path=source, expected_source_sha256=digest,
            current_path=target, expected_current_sha256=old, target_path=target, history_root=folder/'History',
            persist=lambda _: None, receipt=store.item('P1', 'b'*32, 'internal'))


def test_receipt_rejects_changed_immutable_intent_or_uncontrolled_staging(tmp_path):
    import json
    folder = tmp_path/'project'; folder.mkdir()
    source = tmp_path/'source.docx'; source.write_bytes(b'new')
    target = folder/'Report.docx'; target.write_bytes(b'old')
    store = ReportDeliveryReceipts(tmp_path/'receipts'); files = ReportPublicationGateway()
    original = store.begin('P1', 'c'*32, {'signature': 'approved'}, [{
        'role': 'internal', 'source': str(source), 'sha256': files.fingerprint(source), 'target': str(target),
        'current': str(target), 'old_sha256': files.fingerprint(target), 'history_root': str(folder/'History')}])
    receipt_path = next((tmp_path/'receipts').rglob('c'*32 + '.json'))
    tampered = json.loads(receipt_path.read_text(encoding='utf-8'))
    tampered['items'][0]['target'] = str(tmp_path/'unowned.docx')
    receipt_path.write_text(json.dumps(tampered), encoding='utf-8')
    with pytest.raises(RuntimeError, match='invalid'):
        store.read('P1', 'c'*32)
    tampered = json.loads(json.dumps(original))
    tampered['items'][0].update(status='staged', staging=str(tmp_path/'.report-unowned.stage'))
    receipt_path.write_text(json.dumps(tampered), encoding='utf-8')
    with pytest.raises(RuntimeError, match='invalid'):
        store.read('P1', 'c'*32)
    assert target.read_bytes() == b'old'


def test_projection_read_never_creates_missing_database_or_parent(tmp_path):
    from types import SimpleNamespace
    from backend.infrastructure.storage.repositories.report_authoring import ReportAuthoringRepository
    missing = tmp_path/'absent'/'connlab.sqlite3'
    with pytest.raises(OSError, match='unavailable'):
        ReportAuthoringRepository.read_delivery_projection(SimpleNamespace(database_path=missing), 'P1')
    assert not missing.parent.exists()


def test_foreign_edit_during_metadata_commit_is_not_reported_saved(tmp_path):
    folder = tmp_path/'project'; folder.mkdir()
    source = tmp_path/'source.docx'; source.write_bytes(b'new reviewed')
    target = folder/'Report.docx'; target.write_bytes(b'old reviewed')
    files = ReportPublicationGateway(); store = ReportDeliveryReceipts(tmp_path/'receipts')
    old_hash = files.fingerprint(target); new_hash = files.fingerprint(source)
    store.begin('P1', 'd'*32, {'signature': 'approved'}, [{'role': 'internal', 'source': str(source),
        'sha256': new_hash, 'target': str(target), 'current': str(target), 'old_sha256': old_hash,
        'history_root': str(folder/'History')}])
    def foreign_write(_):
        target.write_bytes(b'foreign manual edit during commit')
    with pytest.raises(RuntimeError, match='changed outside'):
        files.publish_regenerated_current(source_path=source, expected_source_sha256=new_hash,
            current_path=target, expected_current_sha256=old_hash, target_path=target,
            history_root=folder/'History', persist=foreign_write, receipt=store.item('P1','d'*32,'internal'))
    assert target.read_bytes() == b'foreign manual edit during commit'
    assert store.read('P1','d'*32)['items'][0]['status'] == 'published'
    assert [p.read_bytes() for p in (folder/'History').glob('*.docx')] == [b'old reviewed']


def test_staged_receipt_write_failure_reuses_reserved_paths_without_empty_history(tmp_path, monkeypatch):
    folder = tmp_path/'project'; folder.mkdir()
    source = tmp_path/'source.docx'; source.write_bytes(b'new reviewed')
    target = folder/'Report.docx'; target.write_bytes(b'old reviewed')
    files = ReportPublicationGateway(); store = ReportDeliveryReceipts(tmp_path/'receipts')
    old_hash = files.fingerprint(target); new_hash = files.fingerprint(source)
    store.begin('P1', 'e'*32, {'signature': 'approved'}, [{'role': 'internal', 'source': str(source),
        'sha256': new_hash, 'target': str(target), 'current': str(target), 'old_sha256': old_hash,
        'history_root': str(folder/'History')}])
    write = store._write; failed = [False]
    def disk_full(project_id, data):
        if data['items'][0]['status'] == 'staged' and not failed[0]:
            failed[0] = True
            raise OSError('one staged receipt write failed')
        write(project_id, data)
    monkeypatch.setattr(store, '_write', disk_full)
    arguments = dict(source_path=source, expected_source_sha256=new_hash, current_path=target,
        expected_current_sha256=old_hash, target_path=target, history_root=folder/'History',
        persist=lambda _: None, receipt=store.item('P1','e'*32,'internal'))
    with pytest.raises(OSError, match='one staged receipt'):
        files.publish_regenerated_current(**arguments)
    assert target.read_bytes() == b'old reviewed'
    assert not list((folder/'History').glob('*.docx'))
    staged = list(folder.glob('.report-*.stage'))
    assert len(staged) == 1
    inode, stamp = staged[0].stat().st_ino, staged[0].stat().st_mtime_ns
    files.publish_regenerated_current(**arguments)
    assert target.read_bytes() == b'new reviewed' and target.stat().st_ino == inode
    assert target.stat().st_mtime_ns == stamp
    assert [p.read_bytes() for p in (folder/'History').glob('*.docx')] == [b'old reviewed']
    assert not list(folder.glob('.report-*.stage'))


def test_stage_created_without_durable_identity_is_retained_and_blocks_retry(tmp_path, monkeypatch):
    folder = tmp_path/'project'; folder.mkdir()
    source = tmp_path/'source.docx'; source.write_bytes(b'new reviewed')
    target = folder/'Report.docx'; target.write_bytes(b'old reviewed')
    files = ReportPublicationGateway(); store = ReportDeliveryReceipts(tmp_path/'receipts')
    old_hash = files.fingerprint(target); new_hash = files.fingerprint(source)
    store.begin('P1', 'f'*32, {'signature': 'approved'}, [{'role': 'internal', 'source': str(source),
        'sha256': new_hash, 'target': str(target), 'current': str(target), 'old_sha256': old_hash,
        'history_root': str(folder/'History')}])
    write = store._write
    def identity_record_unavailable(project_id, data):
        if data['items'][0]['status'] == 'copying':
            raise OSError('identity receipt unavailable')
        write(project_id, data)
    monkeypatch.setattr(store, '_write', identity_record_unavailable)
    arguments = dict(source_path=source, expected_source_sha256=new_hash, current_path=target,
        expected_current_sha256=old_hash, target_path=target, history_root=folder/'History',
        persist=lambda _: None, receipt=store.item('P1','f'*32,'internal'))
    with pytest.raises(OSError, match='identity receipt'):
        files.publish_regenerated_current(**arguments)
    staged = list(folder.glob('.report-*.stage'))
    assert len(staged) == 1 and staged[0].read_bytes() == b''
    inode = staged[0].stat().st_ino
    monkeypatch.setattr(store, '_write', write)
    with pytest.raises(RuntimeError, match='no recorded ownership'):
        files.publish_regenerated_current(**arguments)
    assert staged[0].stat().st_ino == inode
    assert target.read_bytes() == b'old reviewed'
    assert not list((folder/'History').glob('*.docx'))
