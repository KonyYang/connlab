"""Read instrument PDF uploads without modifying their source bytes."""

from io import BytesIO

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

from backend.application.mechanical_summary import parse_pdf_rows


def inspect_pdf(content: bytes, kind: str) -> dict:
    try:
        with pdfplumber.open(BytesIO(content)) as document:
            if not document.pages or len(document.pages) > 50:
                raise ValueError('Select a PDF with between 1 and 50 pages.')
            texts = [page.extract_text() or '' for page in document.pages]
    except (OSError, EOFError, PdfminerException) as exc:
        raise ValueError('The PDF cannot be read.') from exc
    rows = []
    seen = set()
    for text in texts:
        for row in parse_pdf_rows(text, kind):
            if row['curve'] in seen:
                raise ValueError('Duplicate curve identifier across PDF pages; review the instrument record.')
            seen.add(row['curve'])
            rows.append(row)
    if not rows:
        raise ValueError('No supported result rows found. Check the selected test type and PDF.')
    source_text = '\n\n'.join(f'Page {i + 1}\n{text}' for i, text in enumerate(texts))
    return {'rows': rows, 'source_text': source_text, 'requires_review': True}
