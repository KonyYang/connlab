"""Resolve explicit source coordinates before applying pure measurement rules."""
import re
from backend.domain.report_result_semantics import electrical_measurement, resistance_measurement


def read_cell(table, address, *, required=False):
    if not address:
        if required:
            raise ValueError('Select the source cell for this identity.')
        return ''
    match = re.fullmatch(r'([A-Za-z]{1,3})([1-9][0-9]{0,4})', address)
    if not match:
        raise ValueError('Use a single Excel cell address, for example C22.')
    column = 0
    for letter in match[1].upper():
        column = column * 26 + ord(letter) - 64
    row = int(match[2])
    if row > len(table.rows) or column > len(table.rows[row - 1]):
        raise ValueError(f'Source cell {address} is outside the selected sheet.')
    value = table.rows[row - 1][column - 1]
    if required and (value is None or not str(value).strip()):
        raise ValueError(f'Source identity cell {address} is blank.')
    return value if value is not None else ''


def preview_measurements(table, kind, selection):
    if not selection or selection['type'] != kind:
        raise ValueError('Choose the matching measurement selection.')
    rows, identities = [], set()
    for record in selection['records']:
        cells = record['cells']
        sample = str(read_cell(table, cells.get('sample'), required=True)).strip()
        pair = str(read_cell(table, cells.get('pair'), required=kind == 'electrical')).strip()
        measurement = record.get('measurement', 'absolute' if record.get('quantity') == 'absolute' else 'delta')
        key = (sample, pair, record['stage'], measurement)
        if key in identities:
            raise ValueError('Duplicate sample / pair / stage / measurement selection. Review the source mapping.')
        identities.add(key)
        if kind == 'electrical':
            data = electrical_measurement(record['measurement'], read_cell(table, cells.get('value')),
                record['unit'], read_cell(table, cells.get('breakdown')),
                record.get('voltage_v', ''), record.get('duration_s', ''))
        else:
            data = resistance_measurement(record['stage'], record['quantity'], read_cell(table, cells.get('value')),
                record['unit'], read_cell(table, cells.get('baseline')))
        rows.append({**data, 'sample_id': sample, 'pair': pair, 'stage': record['stage'],
            'source_cells': cells, 'condition_locator': record.get('condition_locator', '')})
    return {'sheet_name': table.sheet_name, 'quantity': kind, 'unit': '', 'rows': rows,
        'missing': any(row['missing'] for row in rows), 'selection_confirmed': selection['selection_confirmed']}
