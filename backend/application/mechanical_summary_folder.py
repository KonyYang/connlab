"""Evidence rules shared by folder analysis, review and generation."""
from datetime import datetime
import re

INFO_FIELDS = ('LTR', 'Test Date', 'Tested By', 'Amb Temp. and Rel. Hum.',
               'Test Equipment ID', 'Test Condition', 'Item/Process', 'Remark')
PROJECT = re.compile(r'DL-\d{4}-\d{2}-\d{3}[A-Za-z]?', re.I)
KINDS = {'qualitative': 'Mechanical result', 'mating': 'Mating&Withdraw', 'retention': 'Contact Retention',
         'hold': 'Retention Hold', 'hold_end1': 'Retention Hold', 'clamp': 'Cable Clamp Pull',
         'polarisation': 'Polarisation & Mis-mating', 'protection': 'Protection electric shock'}
_LABEL = re.compile(r'^(LTR No|Test Date|Tested By|Tester|Temperature\s*/\s*humidity|'
                    r'Amb Temp\. and Rel\. Hum\.|Test Equipment ID|Equipment ID|'
                    r'Test Condition|Test Group(?: and Items/Process)?|Title|标题|'
                    r'Test standard|Product name|Customer|Load cell|Specimen grips)\s*[:：]\s*(.*)$', re.I)


def source_information(text: str, project: str, kind: str) -> dict:
    """Read labelled values, including PDF columns emitted as labels then values."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    found = {}
    i = 0
    while i < len(lines):
        match = _LABEL.match(lines[i])
        if not match:
            i += 1
            continue
        if match[2]:
            found[match[1].lower()] = match[2]
            i += 1
            continue
        labels = []
        j = i
        while j < len(lines):
            item = _LABEL.match(lines[j])
            if not item or item[2]:
                break
            labels.append(item[1].lower()); j += 1
        values = lines[j:j + len(labels)]
        column = dict(zip(labels, values))
        has_date_anchor = bool(re.fullmatch(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', column.get('test date', '')))
        if len(labels) > 2 and len(values) == len(labels) and has_date_anchor and not any(_LABEL.match(v) for v in values):
            found.update(zip(labels, values)); i = j + len(labels)
        else:
            i += 1
    info = {key: 'Not recorded' for key in INFO_FIELDS}
    info['LTR'] = project or 'Not recorded'
    info['Item/Process'] = KINDS.get(kind, kind)
    info['Remark'] = 'N'
    for labels, field in [(('test date',), 'Test Date'), (('tested by', 'tester'), 'Tested By'),
                          (('test equipment id', 'equipment id'), 'Test Equipment ID'),
                          (('test condition',), 'Test Condition')]:
        for label in labels:
            if found.get(label):
                info[field] = found[label]; break
    date = info['Test Date']
    if date != 'Not recorded':
        try:
            info['Test Date'] = datetime.strptime(date.replace('/', '-'), '%Y-%m-%d').date().isoformat()
        except ValueError:
            info['Test Date'] = 'Not recorded'
    environment = next((v for k, v in found.items() if k.startswith(('temperature', 'amb temp'))), '')
    env = re.fullmatch(r'\s*([+-]?\d+(?:\.\d+)?)\s*(?:°?\s*C|℃)\s*[@&,/ ]+\s*(\d+(?:\.\d+)?)\s*%\s*RH\s*', environment, re.I)
    if env:
        info['Amb Temp. and Rel. Hum.'] = f'{env[1]} °C / {env[2]}% RH'
    # An explicitly labelled equipment ID is usable; capacity/model alone is not.
    equipment = re.search(r'\bEquipm(?:ent)?\s+(?:ID\s*[:：]?\s*)?([A-Z]+-[A-Z0-9-]*\d)\b', found.get('load cell', ''), re.I)
    if equipment and info['Test Equipment ID'] == 'Not recorded':
        info['Test Equipment ID'] = equipment[1]
    group = found.get('test group and items/process', found.get('test group', ''))
    if group:
        info['Item/Process'] += f' / {group}'
    return info


def sample_parts(value: str) -> dict:
    """Split only explicit labels; never assign by curve order or count."""
    match = re.fullmatch(r'(#?\d+#?)[- _]+(Orange|Black|Rec|Receptacle|Header|Plug|Busbar|Board)', value, re.I)
    if not match:
        return {'sample': value, 'colour': '', 'part': ''}
    label = match[2].capitalize()
    return {'sample': '#' + match[1].strip('#'),
            'colour': label if label in {'Orange', 'Black'} else '',
            'part': ('Receptacle' if label == 'Rec' else label) if label not in {'Orange', 'Black'} else ''}


def section_issues(section: dict) -> list[str]:
    issues = list(section.get('errors', []))
    if section['kind'] in {'qualitative', 'polarisation', 'protection'}:
        if section['kind'] == 'qualitative':
            issues.append('Select the test type for this instrument worksheet.')
        if not section.get('tables'):
            issues.append('Confirm the sample/part layout and qualitative results.')
    else:
        missing = [row['curve'] for row in section['rows'] if not row['sample'].strip()]
        if missing:
            issues.append('Enter the sample for curve ' + ', '.join(missing) + '.')
        if section.get('kind') in {'hold', 'hold_end1', 'clamp'} and not section.get('force_field'):
            issues.append('Select the recorded hold-force field: FEnd section or FEnd section 1.')
    return issues


def _review_text(value, *, optional=False):
    if not isinstance(value, str) or len(value) > 500 or (not optional and not value.strip()):
        raise ValueError('Enter a nonempty label of up to 500 characters.')
    return value.strip()


def _review_tables(tables, raw_curves):
    if not isinstance(tables, list) or not 1 <= len(tables) <= 12:
        raise ValueError('Confirm between 1 and 12 report tables.')
    for table in tables:
        if not isinstance(table, dict) or set(table) - {'title', 'row_heading', 'column_heading', 'columns', 'samples', 'results', 'diagonal', 'curves'}:
            raise ValueError('Invalid report table fields.')
        for key in ('title', 'row_heading', 'column_heading'):
            _review_text(table.get(key, ''), optional=key != 'title')
        for key in ('columns', 'samples'):
            labels = table.get(key)
            if not isinstance(labels, list) or not 1 <= len(labels) <= (12 if key == 'columns' else 100):
                raise ValueError('Enter the report column labels and sample labels.')
            for label in labels:
                _review_text(label)
        if type(table.get('diagonal', False)) is not bool:
            raise ValueError('Invalid diagonal table selection.')
        results = table.get('results')
        if not isinstance(results, list) or len(results) != len(table['samples']):
            raise ValueError('Confirm results for every report sample.')
        if table.get('diagonal') and len(table['samples']) != len(table['columns']):
            raise ValueError('Polarisation diagonal tables need matching row and column counts.')
        for i, row in enumerate(results):
            if not isinstance(row, list) or len(row) != len(table['columns']):
                raise ValueError('Confirm every report result column.')
            for j, value in enumerate(row):
                allowed = {''} if table.get('diagonal') and i != j else {'Pass', 'Fail', 'N/A'}
                if value not in allowed:
                    raise ValueError('Select Pass, Fail or N/A; leave invalid diagonal combinations blank.')
        curves = table.get('curves', [])
        if not isinstance(curves, list) or (curves and len(curves) != len(table['samples'])):
            raise ValueError('Curve annotations must align with report rows, or remain empty.')
        if any(curve not in raw_curves for curve in curves):
            raise ValueError('Curve annotations must refer to actual source curves.')
    return tables


def apply_review(analysis: dict, review: dict | None) -> dict:
    """Apply explicit labels/conclusions, never client-supplied measured values."""
    from copy import deepcopy
    result = deepcopy(analysis)
    if not review:
        return result
    if not isinstance(review, dict) or set(review) - {'project', 'sections'} or review.get('project') != analysis['project']:
        raise ValueError('Review belongs to a different project. Review the selected folder again.')
    patches = review.get('sections', {})
    if not isinstance(patches, dict) or set(patches) - {s['id'] for s in result['sections']}:
        raise ValueError('Source changed since review. Review the selected files again.')
    for section in result['sections']:
        patch = patches.get(section['id'], {})
        allowed = {'kind', 'rows', 'information', 'force_field', 'withdraw_magnitude', 'tables', 'qualitative_confirmed'}
        if not isinstance(patch, dict) or set(patch) - allowed:
            raise ValueError('Invalid review fields; measurements cannot be edited.')
        if 'kind' in patch:
            kind = patch['kind']
            if section['kind'] not in {'qualitative', kind} or kind not in {'polarisation', 'protection'}:
                raise ValueError('Select polarisation/mis-mating or electric-shock protection for the unidentified workbook.')
            section['kind'] = kind
            section['name'] = KINDS[kind]
            if section['information'].get('Item/Process') == 'Mechanical result':
                section['information']['Item/Process'] = KINDS[kind]
        if 'rows' in patch:
            rows = patch['rows']
            expected = {row['curve']: row for row in section['rows']}
            if not isinstance(rows, list) or len(rows) != len(expected):
                raise ValueError('Keep every source curve when confirming sample mappings.')
            seen = set()
            for row in rows:
                if not isinstance(row, dict) or set(row) - {'curve', 'sample', 'colour', 'part'}:
                    raise ValueError('Review fields cannot replace source measurements.')
                curve = row.get('curve')
                if curve not in expected or curve in seen:
                    raise ValueError('Keep original curve identifiers without duplicates.')
                seen.add(curve)
                for key in ('sample', 'colour', 'part'):
                    expected[curve][key] = _review_text(row.get(key, ''), optional=key != 'sample')
        if 'information' in patch:
            info = patch['information']
            if not isinstance(info, dict) or set(info) - set(INFO_FIELDS):
                raise ValueError('Invalid test information field.')
            for key, value in info.items():
                section['information'][key] = _review_text(value, optional=True) or 'Not recorded'
            ltr = section['information'].get('LTR', 'Not recorded')
            if analysis['project'] and ltr != analysis['project']:
                raise ValueError('Test information must retain the selected project LTR.')
            date = section['information'].get('Test Date', 'Not recorded')
            if date != 'Not recorded':
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError as exc:
                    raise ValueError('Use YYYY-MM-DD for Test Date, or Not recorded.') from exc
        if 'force_field' in patch:
            field = patch['force_field']
            if field not in section.get('force_fields', []):
                raise ValueError('Select a hold-force field present in the original record.')
            section['force_field'] = field
            for row in section['rows']:
                row['value'] = row['end_section1' if field == 'FEnd section 1' else 'end_section']
        if 'withdraw_magnitude' in patch:
            if type(patch['withdraw_magnitude']) is not bool:
                raise ValueError('Confirm the withdraw-force display convention.')
            section['withdraw_magnitude'] = patch['withdraw_magnitude']
        if 'tables' in patch:
            if section['kind'] not in {'polarisation', 'protection'} or patch.get('qualitative_confirmed') is not True:
                raise ValueError('Explicitly confirm the qualitative report layout and conclusions.')
            section['tables'] = _review_tables(patch['tables'], section['raw_curves'])
            section['qualitative_confirmed'] = True
        section['issues'] = section_issues(section)
    result['ready'] = bool(result['sections']) and not result['errors'] and all(not s['issues'] for s in result['sections'])
    return result
