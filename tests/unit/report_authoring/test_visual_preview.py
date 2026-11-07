from io import BytesIO
from pathlib import Path
import time

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
    def hung(*args, **kwargs):
        time.sleep(.2)
    started = time.monotonic()
    with pytest.raises(ValueError, match='timed out'):
        WordReportPreview(exporter=hung, timeout_seconds=.01).render(b'copy', review={})
    assert time.monotonic() - started < .15
