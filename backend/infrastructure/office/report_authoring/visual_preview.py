"""Bounded Word rendering of one private copy; no shared PDF cache or user Word."""
from io import BytesIO
import logging
from pathlib import Path
from queue import Queue, Empty
from tempfile import TemporaryDirectory
from threading import Thread, Lock, BoundedSemaphore
import re

import pdfplumber

from backend.infrastructure.office.word_document_gateway import WordDocumentGateway

logger = logging.getLogger(__name__)
_workers = BoundedSemaphore(1)


class WordReportPreview:
    def __init__(self, exporter=None, timeout_seconds=120):
        self.exporter = exporter or WordDocumentGateway().export_preview_pdf
        self.timeout_seconds = timeout_seconds

    def render(self, content, *, review):
        if not _workers.acquire(blocking=False):
            raise ValueError('Word preview is busy. Wait for the current render to finish before retrying.')
        result, lock, owned = Queue(maxsize=1), Lock(), {'handle': None, 'expired': False}

        def close_owned(terminate=False):
            with lock:
                handle = owned['handle']
                if handle is not None:
                    try:
                        if terminate:
                            import win32api
                            import win32event
                            if win32event.WaitForSingleObject(handle, 0) == 258:
                                win32api.TerminateProcess(handle, 1)
                    finally:
                        handle.Close()
                        owned['handle'] = None

        def capture_owned(pid):
            # The gateway supplies only a newly created Word PID. A live process
            # handle binds that instance even if Windows later recycles its PID.
            import win32api
            handle = win32api.OpenProcess(0x00100001, False, pid)
            with lock:
                if owned['expired']:
                    handle.Close()
                    raise TimeoutError('Preview expired before Word ownership was acquired.')
                owned['handle'] = handle

        def work():
            try:
                with TemporaryDirectory(prefix='connlab-word-preview-') as directory:
                    source, target = Path(directory) / 'working-copy.docx', Path(directory) / 'preview.pdf'
                    source.write_bytes(content)
                    self.exporter(source, target, on_owned_word=capture_owned)
                    payload = target.read_bytes()
                    if not payload.startswith(b'%PDF-'):
                        raise ValueError('Word did not return a readable PDF preview.')
                    pages = []
                    with pdfplumber.open(BytesIO(payload)) as pdf:
                        for index, page in enumerate(pdf.pages, 1):
                            pages.append({'page': index, 'width': float(page.width), 'height': float(page.height),
                                          'text': (page.extract_text() or '')[:20000]})
                    if not pages:
                        raise ValueError('Word returned a PDF with no pages.')
                    # Pagination can move following content after a local edit. A
                    # conservative whole-document extent is honest, unlike guessed
                    # paragraph-to-page locations from the OOXML source.
                    normalize = lambda text: re.sub(r'\s+', ' ', text).strip().casefold()
                    anchors = [normalize(text) for text in review.get('changed_text_anchors', []) if len(normalize(text)) >= 4]
                    locations = [{'text': anchor, 'pages': [page['page'] for page in pages if anchor in normalize(page['text'])]}
                                 for anchor in dict.fromkeys(anchors)]
                    affected = sorted({number for location in locations for number in location['pages']})
                    result.put({'content': payload, 'page_count': len(pages), 'pages': pages,
                        'affected_pages': affected or list(range(1, len(pages) + 1)), 'changed_locations': locations,
                        'affected_pages_reason': 'Changed text located in actual Word PDF; inspect these pages first and all pages for reflow.' if affected else 'Changed text could not be located reliably; review the full document.',
                        'renderer': 'Microsoft Word', 'render_policy': 'isolated-read-only-macros-disabled-no-link-update'})
            except Exception as exc:
                logger.exception('Isolated report Word preview failed')
                result.put(exc)
            finally:
                close_owned()
                _workers.release()

        Thread(target=work, name='connlab-word-preview', daemon=True).start()
        try:
            value = result.get(timeout=self.timeout_seconds)
        except Empty as exc:
            with lock:
                owned['expired'] = True
            close_owned(terminate=True)
            raise ValueError('Word preview timed out. Cleanup targets only a proven owned Word instance; existing documents are never terminated. Check Word installation/dialogs and retry.') from exc
        if isinstance(value, Exception):
            raise ValueError(f'Word preview failed. Check Microsoft Word and pywin32 on the server; no original was changed. {value}') from value
        return value
