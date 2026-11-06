"""Read selected folder bytes; no filesystem paths or source writes are accepted."""
from hashlib import sha256
from io import BytesIO
from pathlib import PurePosixPath
import re

import pdfplumber
from openpyxl.utils import get_column_letter
from backend.application.mechanical_summary import parse_pdf_rows
from backend.application.mechanical_summary_folder import PROJECT, KINDS, sample_parts, source_information, section_issues
from backend.infrastructure.office.mechanical_summary_workbook import inspect_workbook

_EXCLUDED = {'source', 'source book', 'history', 'backup', 'backups', 'archive', 'archives', '.git', 'node_modules'}


def ignore_reason(name: str) -> str:
    path = PurePosixPath(name.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in name:
        raise ValueError('Select files using relative folder names.')
    if any(part.lower() in _EXCLUDED for part in path.parts[:-1]):
        return 'Reference or history folder'
    if path.name.startswith('~$') or re.search(r'mechanical[ _-]*(?:force[ _-]*)?summary', path.name, re.I):
        return 'Existing summary or temporary file'
    if path.suffix.lower() not in {'.pdf', '.xls', '.xlsx'}:
        return 'Not an instrument PDF or workbook'
    return ''


def _kind(name: str, text: str) -> str:
    combined = (name + '\n' + text).lower()
    if 'polarisation' in combined or 'polarization' in combined or 'mis-mating' in combined:
        return 'polarisation'
    if re.search(r'protection.*electric shock', combined):
        return 'protection'
    if re.search(r'\bMF\s*[/ ]?\s*UMF\b', combined, re.I):
        return 'mating'
    if 'end section' in combined:
        return 'clamp' if 'cable clamp' in combined else 'hold'
    if 'retention' in combined and re.search(r'\bmax\b|Fmax', combined, re.I):
        return 'retention'
    return ''


def _worksheet_metadata(rows: list[list]) -> str:
    from datetime import date, datetime
    labels = {'operator': 'Tester', 'tester': 'Tester', 'tested by': 'Tested By',
              'test date': 'Test Date', 'test condition': 'Test Condition',
              'temperature/humidity': 'Temperature/humidity', 'test equipment id': 'Test Equipment ID',
              'equipment id': 'Equipment ID', 'test group': 'Test Group', 'ltr no': 'LTR No'}
    lines = []
    for row in rows:
        for i, value in enumerate(row):
            key = str(value or '').strip().rstrip(':：').strip().lower()
            if key not in labels:
                continue
            following = next((v for v in row[i+1:] if v not in ('', None)), None)
            if following is None or re.search(r'[:：]\s*$', str(following)):
                continue
            if isinstance(following, (datetime, date)):
                following = following.strftime('%Y-%m-%d')
            # A labelled Excel date stored only as an untyped serial needs its
            # workbook date system; do not guess that system from the number.
            if key == 'test date' and not isinstance(following, str):
                continue
            lines.append(f'{labels[key]} : {following}')
    return '\n'.join(lines)


def _effective_cells(rows: list[list]) -> tuple[list[dict], list[str]]:
    header = next((i for i, row in enumerate(rows) if any(str(v).strip() == '[N]' for v in row)), None)
    if header is None or header == 0:
        raise ValueError('Measurement headings and units could not be identified.')
    measurement_columns = [j for j, value in enumerate(rows[header]) if re.fullmatch(r'\[(?:N|mm)\]', str(value).strip())]
    selected = [header - 1, header]
    curves = []
    for i in range(header + 1, len(rows)):
        row = rows[i]
        label = str(row[0]).strip() if row else ''
        has_values = any(j < len(row) and row[j] not in ('', None) for j in measurement_columns)
        if re.fullmatch(r'\d+(?:\.\d+)?', label) and has_values:
            curves.append(label); selected.append(i)
        elif label.lower() in {'maxi', 'mini', 'rang', 'avrg', 'sdev', 'cpk'} and has_values:
            selected.append(i)
    if not curves:
        raise ValueError('No effective instrument measurements were found.')
    cells = []
    for dest, i in enumerate(selected, 3):
        for j, value in enumerate(rows[i]):
            if j not in {0, *measurement_columns} or value in ('', None):
                continue
            if i == header - 1 and j == 0 and str(value).lower() == 'specification':
                continue
            cells.append({'source': f'{get_column_letter(j+1)}{i+1}', 'row': dest, 'column': j+1, 'value': value})
    return cells, curves


def _pdf_section(name: str, content: bytes) -> dict | None:
    with pdfplumber.open(BytesIO(content)) as document:
        if not 1 <= len(document.pages) <= 50:
            raise ValueError('Each instrument PDF must have between 1 and 50 pages.')
        texts = [page.extract_text() or '' for page in document.pages]
    text = '\n'.join(texts)
    kind = _kind(name, text)
    if not kind or kind in {'polarisation', 'protection'}:
        if re.search(r'retention|MFUMF|cable clamp|polarisation|electric shock', name, re.I):
            raise ValueError('Mechanical record format is not recognized. Supply a readable instrument export or exclude this file explicitly.')
        return None
    parse_kind = 'hold' if kind == 'clamp' else kind
    rows = [row for page in texts for row in parse_pdf_rows(page, parse_kind)]
    if not rows:
        raise ValueError('The test was recognized but its result rows could not be read.')
    counts = {int(n) for n in re.findall(r'\bn\s*=\s*(\d+)', text)}
    if counts and counts != {len(rows)}:
        raise ValueError('Extracted row count does not match the instrument sample count. Review the original export.')
    if len({row['curve'] for row in rows}) != len(rows):
        raise ValueError('Duplicate curve identifiers need separate test-stage records.')
    for row in rows:
        row.update(sample_parts(row['sample']))
    fields = []
    if kind in {'hold', 'clamp'}:
        other = [row for page in texts for row in parse_pdf_rows(page, 'hold_end1')]
        for row, end1 in zip(rows, other):
            row['end_section'] = row['value']; row['end_section1'] = end1['value']
        fields = ['FEnd section', 'FEnd section 1']
    return {'kind': kind, 'rows': rows, 'source_text': text, 'raw_cells': [], 'tables': [],
            'force_fields': fields, 'force_field': '', 'sheet': None}


def analyze_folder(files: list[tuple[str, bytes]]) -> dict:
    if not files or len(files) > 200:
        raise ValueError('Select a folder containing between 1 and 200 PDF/Excel files.')
    if sum(len(content) for _, content in files) > 150 * 1024 * 1024:
        raise ValueError('Select a smaller test-results folder (up to 150 MB).')
    sections, ignored, errors, projects = [], [], [], set()
    seen = set()
    paths = [name.replace('\\', '/').casefold() for name, _ in files]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate relative file names found. Select each source only once.')
    for name, content in files:
        reason = ignore_reason(name)
        if reason:
            ignored.append({'file': name, 'reason': reason}); continue
        digest = sha256(content).hexdigest()
        if digest in seen:
            ignored.append({'file': name, 'reason': 'Identical source already included'}); continue
        seen.add(digest)
        if not content or len(content) > 25 * 1024 * 1024:
            errors.append({'file': name, 'message': 'Each source must be nonempty and smaller than 25 MB.'}); continue
        try:
            if name.lower().endswith('.pdf'):
                section = _pdf_section(name, content)
                candidates = [section] if section else []
            else:
                kind = _kind(name, '')
                if not kind and re.search(r'LLCR|IR[& ]*DWV|T[- ]?Rise|fee form', name, re.I):
                    ignored.append({'file': name, 'reason': 'Non-mechanical record'}); continue
                book = inspect_workbook(content, name)
                candidates = []
                for index, sheet in enumerate(book['sheets'], 1):
                    sheet_kind = kind or _kind(sheet['name'], '') or 'qualitative'
                    try:
                        cells, curves = _effective_cells(sheet['rows'])
                    except ValueError:
                        ignored.append({'file': name + ' / ' + sheet['name'], 'reason': 'No supported instrument measurement region on this worksheet'})
                        continue
                    candidates.append({'kind': sheet_kind, 'sheet': index, 'rows': [], 'raw_cells': cells,
                                       'raw_curves': curves, 'tables': [], 'source_text': _worksheet_metadata(sheet['rows']), 'force_fields': [], 'force_field': '', 'type_required': sheet_kind == 'qualitative'})
                if not candidates and kind:
                    raise ValueError('The named mechanical workbook has no recognizable measurement region.')
            if not candidates:
                ignored.append({'file': name, 'reason': 'No supported mechanical results recognized'}); continue
            for section in candidates:
                ids = {m.upper() for m in PROJECT.findall(name + '\n' + section['source_text'])}
                if len(ids) > 1:
                    raise ValueError('Conflicting project identifiers in source and folder.')
                projects.update(ids)
                project = next(iter(ids), '')
                section.update({'id': digest + ':' + str(section['sheet'] or 0), 'sha256': digest,
                                'source': name, 'project': project, 'name': KINDS[section['kind']],
                                'information': source_information(section['source_text'], project, section['kind']),
                                'withdraw_magnitude': False})
                section['issues'] = section_issues(section)
                sections.append(section)
        except Exception as exc:
            # A malformed selected record stays visible and blocks incomplete output.
            errors.append({'file': name, 'message': str(exc)[:300] or 'Source could not be read.'})
    if len(projects) > 1:
        raise ValueError('Multiple project identifiers found. Select one project test-results folder.')
    if not sections and not errors:
        raise ValueError('No supported mechanical records found. Select the test-results folder.')
    project = next(iter(projects), '')
    for section in sections:
        if not section['project'] and project:
            section['project'] = project
            section['information']['LTR'] = project
    order = {'polarisation': 0, 'clamp': 1, 'mating': 2, 'retention': 3, 'hold': 4, 'hold_end1': 4, 'protection': 5}
    sections.sort(key=lambda s: (order.get(s['kind'], 99), s['source'].casefold(), s['sheet'] or 0))
    return {'project': project, 'sections': sections, 'ignored': ignored, 'errors': errors,
            'ready': bool(sections) and not errors and all(not s['issues'] for s in sections)}
