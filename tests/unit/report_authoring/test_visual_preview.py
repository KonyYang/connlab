from io import BytesIO
from pathlib import Path
import time
from threading import Event, enumerate as threads
from types import SimpleNamespace
import sys

import pytest

from backend.infrastructure.office.report_authoring.visual_preview import WordReportPreview


def test_word_preview_is_immutable_version_bound_and_reports_all_pages(tmp_path):
    from reportlab.pdfgen import canvas
    payload = BytesIO()
    document = canvas.Canvas(payload)
    document.drawString(30, 700, 'Figure 1 New caption')
    document.showPage()
    document.drawString(30, 700, 'End of Report')
    document.save()
    def export(source, target, **kwargs):
        assert source.read_bytes() == b'isolated input'
        assert source.parent == target.parent
        target.write_bytes(payload.getvalue())
    preview = WordReportPreview(exporter=export).render(b'isolated input', review={'regions': [], 'numbering': {}})
    assert preview['page_count'] == 2
    assert len(preview['pages']) == 2
    assert preview['content'] == payload.getvalue()
    assert preview['affected_pages'] == [1, 2]


def test_hung_word_reports_timeout_without_waiting_indefinitely():
    release, completed = Event(), Event()
    def hung(*args, **kwargs):
        try:
            release.wait(2)
        finally:
            completed.set()
    started = time.monotonic()
    try:
        with pytest.raises(ValueError, match='timed out'):
            WordReportPreview(exporter=hung, timeout_seconds=.01).render(b'copy', review={})
        assert time.monotonic() - started < .15
    finally:
        release.set()
        assert completed.wait(2)
        for worker in threads():
            if worker.name == 'connlab-word-preview':
                worker.join(2)
                assert not worker.is_alive()


def test_timeout_terminates_only_captured_owned_process_handle(monkeypatch):
    release, acquired = Event(), Event()
    actions = []
    handle = SimpleNamespace(Close=lambda: actions.append('close-owned'))
    def open_process(access, inherit, pid):
        assert pid == 999
        return handle
    monkeypatch.setitem(sys.modules, 'win32api', SimpleNamespace(OpenProcess=open_process,
        TerminateProcess=lambda candidate, code: actions.append(('terminate', candidate is handle))))
    monkeypatch.setitem(sys.modules, 'win32event', SimpleNamespace(WaitForSingleObject=lambda *_: 258))
    def export(*args, on_owned_word):
        on_owned_word(999); acquired.set(); release.wait(2)
    try:
        with pytest.raises(ValueError, match='timed out'):
            WordReportPreview(exporter=export, timeout_seconds=.1).render(b'isolated', review={})
        assert acquired.is_set()
        assert actions == [('terminate', True), 'close-owned']
    finally:
        release.set()
        for worker in threads():
            if worker.name == 'connlab-word-preview':
                worker.join(2)
                assert not worker.is_alive()
