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


def test_real_process_exit_after_link_is_recovered_by_owned_identity(tmp_path):
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
    real_link(*args,**kwargs); os._exit(71)
os.link=crash_after_link
ReportPublicationGateway().publish_regenerated_current(source_path=Path(item['source']),expected_source_sha256=item['sha256'],current_path=Path(item['current']),expected_current_sha256=item['old_sha256'],target_path=Path(item['target']),history_root=Path(item['history_root']),persist=lambda _:None,receipt=store.item('P1','b'*32,'internal'))
"""
    child = subprocess.run([sys.executable, '-c', script, str(tmp_path/'receipts')], check=False)
    assert child.returncode == 71
    assert store.read('P1', 'b'*32)['items'][0]['status'] == 'publishing'
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
