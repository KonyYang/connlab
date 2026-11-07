"""Read bounded Word semantics and prepare exact, local figure-number edits."""
from hashlib import sha256
from pathlib import Path
from io import BytesIO
import re
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree

from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.report_authoring.photo_slots import inspect_photo_slots, photo_occurrences
from backend.infrastructure.office.report_authoring.word_copy import ReportCopyWriter, _paragraph_text, _paragraph_nodes, _text_part, fact_target_matches

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
FIGURE = re.compile(r'\b(?:Figures?|Fig\.?)\s+(\d+(?:\s*(?:&|,|~|–|\-|and|to)\s*\d+)*)\b', re.I)
CAPTION = re.compile(r'^\s*' + FIGURE.pattern, re.I)
ROLES = [('authorization_date', r'authori[sz](?:ation|ed).*date|date.*authori[sz]'),
         ('revision_date', r'(?:rev(?:ision)?\.?\s*\w*|issue).*date|date.*rev(?:ision)?'),
         ('specification', r'\bspecification\b|\btest standard\b|\bIEC\s*\d|\bEIA-'),
         ('samples', r'\bsample description\b|\bpart\s*(?:number|#)|\bserial\b|\bsample\s*(?:SN|ID)'),
         ('conclusions', r'\bconclusions?\b'), ('purpose', r'\bpurpose\b'),
         ('appendix', r'^\s*appendix\b'), ('results', r'\btest results?\b'),
         ('identity', r'\bDL-\d{4}-\d{2}-\d{3}\w*\b')]


def _target(part, index, paragraph):
    return {'part': part, 'paragraph': index,
            'sha256': sha256(etree.tostring(paragraph, method='c14n')).hexdigest()}


def _visible(paragraph):
    return not paragraph.xpath('ancestor::w:del | ancestor::w:moveFrom', namespaces=NS)


def _value(paragraph):
    # Text-box children are separately inventoried paragraphs, not a prefix of
    # their hosting caption (e.g. floating "Mated / Unmated" arrow labels).
    return _paragraph_text(paragraph).strip()


def _numbers(label):
    values = [int(value) for value in re.findall(r'\d+', label)]
    if re.search(r'~|–|\-|\bto\b', label, re.I):
        if len(values) != 2 or values[1] < values[0] or values[1] - values[0] > 100:
            raise ValueError('Ambiguous figure range; review its caption.')
        return list(range(values[0], values[1] + 1))
    return values


class ReportDocumentInspector:
    def __init__(self, protected=None):
        self.protected = protected or ProtectedWordPackageGateway()

    def inspect(self, source):
        regions, figures, references, issues = [], [], [], []
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as archive:
            if len(archive.infolist()) > 5000 or sum(item.file_size for item in archive.infolist()) > 200 * 1024 * 1024:
                raise ValueError('The report is too large to inspect safely.')
            slots = [vars(slot) for slot in inspect_photo_slots(readable)]
            for name in archive.namelist():
                if not _text_part(name):
                    continue
                root = etree.fromstring(archive.read(name), parser=etree.XMLParser(resolve_entities=False, no_network=True))
                occurrences = photo_occurrences(root) if name == 'word/document.xml' else {}
                by_paragraph = {}
                for slot_id, node in occurrences.items():
                    parents = node.xpath('ancestor::w:p[1]', namespaces=NS)
                    if parents:
                        by_paragraph.setdefault(parents[0], []).append(slot_id)
                pending_photos, section, group_id, group_title = [], 'unclassified', f'group:{name}:0', 'Front matter / unclassified content'
                paragraphs = root.xpath('//w:p', namespaces=NS)
                for index, paragraph in enumerate(paragraphs):
                    if not _visible(paragraph):
                        continue
                    value = _value(paragraph)
                    target = _target(name, index, paragraph)
                    role = next((kind for kind, pattern in ROLES if re.search(pattern, value, re.I)), None)
                    if role and role not in {'identity', 'revision_date', 'authorization_date'}:
                        section = role
                    heading = len(value) < 180 and re.match(r'^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?(?:purpose|conclusions?|sample description|test specifications?|group\b.*test results?|appendix\b|test results?\s*$)', value, re.I)
                    style = paragraph.xpath('./w:pPr/w:pStyle/@w:val', namespaces=NS)
                    if value and (heading or any(str(item).lower().startswith('heading') for item in style)):
                        group_id, group_title = f'group:{name}:{index}', value
                    # A region is one actual paragraph, including table cells. No claimed
                    # complete template understanding is inferred from a heading alone.
                    if value:
                        regions.append({'region_id': f'{name}:{index}', 'kind': role or section,
                            'group_id': group_id, 'group_title': group_title,
                            'text': value, 'target': target, 'sha256': target['sha256'],
                            'has_fields': bool(paragraph.xpath('.//w:fldChar|.//w:fldSimple|.//w:instrText', namespaces=NS)),
                            'owned_result': next(iter(paragraph.xpath('ancestor::w:sdt/w:sdtPr/w:tag/@w:val', namespaces=NS)), '')})
                    if paragraph.xpath('ancestor::w:txbxContent', namespaces=NS):
                        continue
                    photos = by_paragraph.get(paragraph, [])
                    if photos:
                        pending_photos.extend(photos)
                    caption = CAPTION.match(value) if name == 'word/document.xml' else None
                    if caption:
                        # Floating vector arrows are annotations, not photographs.
                        # Only actual image occurrences can make photo order unclear.
                        floats = any(occurrences[slot_id].xpath('ancestor::wp:anchor', namespaces=NS)
                                     for slot_id in pending_photos)
                        complex_fields = bool(paragraph.xpath('.//w:fldChar|.//w:fldSimple|.//w:instrText', namespaces=NS))
                        numbers = _numbers(caption.group(1))
                        figures.append({'figure_id': f'figure-{index}', 'number': numbers[0], 'numbers': numbers,
                            'caption': value, 'target': target, 'slot_ids': list(pending_photos),
                            'automatic_order': bool(pending_photos) and not floats and not complex_fields,
                            'reason': 'Review floating order or field-based caption in Word.' if floats or complex_fields else
                                      ('No adjacent photograph; this may be a chart or a text reference.' if not pending_photos else '')})
                        pending_photos = []
                    elif value and not photos:
                        pending_photos = []
                    for match in FIGURE.finditer(value):
                        if caption and match.start() == caption.start():
                            continue
                        references.append({'number': _numbers(match.group(1))[0], 'numbers': _numbers(match.group(1)), 'text': value, 'target': target,
                            'editable': not bool(paragraph.xpath('.//w:fldChar|.//w:fldSimple|.//w:instrText', namespaces=NS))})
                bookmarks = set(root.xpath('//w:bookmarkStart/@w:name', namespaces=NS))
                for instruction in root.xpath('//w:instrText/text()|//w:fldSimple/@w:instr', namespaces=NS):
                    match = re.search(r'\b(?:REF|PAGEREF)\s+"?([^\s"\\]+)', instruction, re.I)
                    if match and match.group(1) not in bookmarks:
                        issues.append({'code': 'dangling_bookmark_reference', 'message': f'Missing reference target: {match.group(1)}', 'location': name})
                if name == 'word/document.xml' and root.xpath('//w:cols[@w:num > 1]', namespaces=NS):
                    for figure in figures:
                        figure.update(automatic_order=False, reason='Multiple-column reading order requires Word review.')
            numbered = {}
            for figure in figures:
                for number in figure['numbers']:
                    numbered.setdefault(number, []).append(figure)
            for number, entries in numbered.items():
                if len(entries) > 1:
                    issues.append({'code': 'duplicate_figure_number', 'message': f'Figure {number} labels more than one caption.', 'location': entries[0]['figure_id']})
            for reference in references:
                if any(number not in numbered for number in reference['numbers']):
                    issues.append({'code': 'dangling_figure_reference', 'message': f"Figure {reference['number']} is referenced without a caption.", 'location': str(reference['target']['paragraph'])})
        return {'regions': regions, 'figures': figures, 'references': references, 'slots': slots, 'issues': issues}

    def numbering(self, source):
        review = self.inspect(source)
        issues = list(review['issues'])
        selected = [figure for figure in review['figures'] if figure['slot_ids']]
        for figure in selected:
            if not figure['automatic_order']:
                issues.append({'code': 'figure_order_unconfirmed', 'message': figure['reason'], 'location': figure['figure_id']})
        # Non-photo captions keep their numbers; do not accidentally renumber a
        # temperature curve while leaving its field references stale.
        fixed_numbers = {number for figure in review['figures'] if not figure['slot_ids'] for number in figure['numbers']}
        numbering, number = {}, 1
        for figure in selected:
            for old_number in figure['numbers']:
                while number in fixed_numbers:
                    number += 1
                numbering[old_number] = number
                number += 1
        replacements = []
        for item in [*selected, *review['references']]:
            value = item.get('caption', item.get('text', ''))
            for match in FIGURE.finditer(value):
                old = match.group(0)
                prefix = old[:match.start(1) - match.start()]
                new = prefix + re.sub(r'\d+', lambda digit: str(numbering.get(int(digit.group()), int(digit.group()))), match.group(1))
                if old == new:
                    continue
                if item.get('editable') is False:
                    issues.append({'code': 'field_reference_requires_word_review', 'message': 'A figure reference is a Word field; update its field explicitly before renumbering.', 'location': str(item['target']['paragraph'])})
                replacements.append({'old': old, 'new': new, 'target': item['target']})
        unique = {(item['target']['part'], item['target']['paragraph'], item['old']): item for item in replacements}
        return {'ready': not issues, 'issues': issues, 'replacements': list(unique.values()),
                'source_sha256': sha256(Path(source).read_bytes()).hexdigest()}

    def apply_numbering(self, source, output, plan):
        if Path(output).exists():
            raise FileExistsError('Numbering requires a new report copy.')
        if plan != self.numbering(source) or not plan['ready']:
            raise ValueError('Figure numbering changed or has unresolved references; inspect again.')
        protection = self.protected.stage_editable_copy(source, output)
        with ZipFile(output) as archive:
            changed = {}
            for part in archive.namelist():
                selected = [item for item in plan['replacements'] if item['target']['part'] == part]
                if not selected:
                    continue
                root = etree.fromstring(archive.read(part))
                for index, paragraph in enumerate(root.xpath('//w:p', namespaces=NS)):
                    items = [item for item in selected if fact_target_matches(part, index, paragraph, item['target'])]
                    edits = []
                    text = _paragraph_text(paragraph)
                    for item in items:
                        old_digits, new_digits = list(re.finditer(r'\d+', item['old'])), re.findall(r'\d+', item['new'])
                        for label in FIGURE.finditer(text):
                            if label.group() != item['old']:
                                continue
                            edits += [(label.start() + digit.start(), label.start() + digit.end(), new)
                                      for digit, new in zip(old_digits, new_digits, strict=True) if digit.group() != new]
                    # Original offsets, right-to-left. Only digit runs are edited;
                    # prefix, caption styling, hyperlinks and drawings are intact.
                    for start, stop, new in sorted(set(edits), reverse=True):
                        offset, inserted = 0, False
                        for node in _paragraph_nodes(paragraph):
                            value = node.text or ''
                            end = offset + len(value)
                            if offset < stop and end > start:
                                node.text = value[:max(0, start - offset)] + (new if not inserted else '') + value[max(0, stop - offset):]
                                inserted = True
                            offset = end
                changed[part] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            data = BytesIO()
            with ZipFile(data, 'w', ZIP_DEFLATED) as destination:
                for info in archive.infolist():
                    destination.writestr(info, changed.get(info.filename, archive.read(info.filename)))
        Path(output).write_bytes(data.getvalue())
        self.protected.restore_password_protection(output, protection)
