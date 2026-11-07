"""Explicit result-row and appendix-table updates in an immutable Word copy."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.report_authoring.word_copy import NS, text
from backend.infrastructure.office.report_authoring.region_parts import remove_replaced_region_parts, R
from backend.infrastructure.office.report_authoring.pagination import protect_table_starts, reflow_headings, protect_reflow_headings


def node(name):
    return etree.Element(f'{{{NS["w"]}}}{name}')


def set_text(element, value):
    paragraph = element if element.tag == node('p').tag else element.find('w:p', NS)
    if paragraph is None:
        paragraph = node('p')
        element.append(paragraph)
    prototype = paragraph.find('w:r/w:rPr', NS)
    for child in list(paragraph):
        if child.tag != node('pPr').tag:
            paragraph.remove(child)
    run = node('r')
    if prototype is not None:
        run.append(deepcopy(prototype))
    label = node('t')
    label.text = str(value)
    label.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    run.append(label)
    paragraph.append(run)
    if element is not paragraph:
        for extra in list(element):
            if extra.tag in {node('p').tag, node('tbl').tag} and extra is not paragraph:
                element.remove(extra)


def _headers(table):
    row = table.find('w:tr', NS)
    return [text(cell).strip().casefold() for cell in row.findall('w:tc', NS)] if row is not None else []


def _parts(root, result):
    tables, result_rows, appendix_tables = [], [], []
    group, heading = '', None
    for block in root.find('w:body', NS):
        if block.tag == node('p').tag:
            label = ' '.join(text(block).split())
            match = re.fullmatch(r'Group\s+(.+?)\s+Test Results', label, re.I)
            if match:
                group = match.group(1).strip()
                heading = None
            elif re.match(r'Appendix\b', label, re.I):
                heading, group = block, ''
        nested = [block] if block.tag == node('tbl').tag else block.xpath('./w:sdtContent/w:tbl', namespaces=NS)
        for table in nested:
            index = len(tables)
            tables.append((table, heading))
            headers = _headers(table)
            if heading is not None:
                appendix_tables.append({'table_index': index, 'title': text(heading), 'headers': headers})
            if group.casefold() != str(result['target']['group_label']).strip().casefold():
                continue
            step_col = next((i for i, h in enumerate(headers) if re.sub(r'[^a-z]', '', h) in {'step', 'stepno', 'no'}), None)
            if step_col is None or 'result' not in headers or 'comment' not in headers:
                continue
            item_col = next((i for i, h in enumerate(headers) if h in {'test item', 'test'}), None)
            for row_index, row in enumerate(table.findall('w:tr', NS)[1:], 1):
                cells = row.findall('w:tc', NS)
                if step_col < len(cells) and text(cells[step_col]).strip() == str(result['target']['step_token']):
                    result_rows.append({'table_index': index, 'row_index': row_index,
                        'step': text(cells[step_col]), 'test_item': text(cells[item_col]) if item_col is not None and item_col < len(cells) else ''})
    return tables, result_rows, appendix_tables


def _temperature_evidence_blocks(root, result):
    if result.get('kind') not in {'temperature', 'linked_temperature'}:
        return []
    selected_group = str(result['target']['group_label']).strip().casefold()
    active, after_result, blocks = False, False, []
    for index, block in enumerate(root.find('w:body', NS)):
        label = ' '.join(text(block).split())
        heading = re.fullmatch(r'Group\s+(.+?)\s+Test Results', label, re.I) if block.tag == node('p').tag else None
        if heading:
            active, after_result = heading.group(1).strip().casefold() == selected_group, False
            continue
        if block.tag == node('p').tag and (re.match(r'^(?:\d+\s*\.\s*)?(?:EQUIPMENTS|REVISION RECORD|Appendix)\b', label, re.I) or 'End of Report' in label):
            active = False
        if not active:
            continue
        if block.tag == node('tbl').tag and {'result', 'comment'} <= set(_headers(block)):
            after_result = True
            continue
        if not after_result or block.tag == node('sectPr').tag:
            continue
        marker = block.find('w:sdtPr/w:tag', NS)
        owned = marker.get(f'{{{NS["w"]}}}val', '') if marker is not None else ''
        alias = block.find('w:sdtPr/w:alias', NS)
        identity = alias.get(f'{{{NS["w"]}}}val', '') if alias is not None else ''
        other_step = bool(owned.startswith('connlab-report-result:') and identity and identity != _step_identity(result))
        if owned.startswith('connlab-report-result:'):
            legacy = owned != 'connlab-report-result:' + result.get('result_id', '')
        elif block.tag == node('tbl').tag:
            normalized = re.sub(r'\s+', '', label).casefold()
            legacy = any(token in normalized for token in ('appliedcurrent', 'maxt-rise', 'avgofmax'))
        else:
            legacy = bool(re.search(r'(?:\bTable[\s-]*\d*.*Temperature.*(?:Rise|Measurement)|\bmaximum\b.*\brise\b|\bregression\b.*\btemperature\b)', label, re.I))
        blocks.append({'block_index': index, 'kind': etree.QName(block).localname, 'text': label[:1000],
            'drawing_count': len(block.xpath('.//w:drawing|.//w:pict', namespaces=NS)),
            'temperature_evidence': legacy and not other_step, 'protected_other_step': other_step,
            'owned_current_result': owned == 'connlab-report-result:' + result.get('result_id', '')})
    return blocks


class ReportResultsDocument:
    def __init__(self, protected=None, temperature_chart=None):
        self.protected = protected or ProtectedWordPackageGateway()
        self.temperature_chart = temperature_chart

    def inspect(self, source: Path, result):
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as package:
            root = etree.fromstring(package.read('word/document.xml'))
            return self.inspect_xml(root, result)

    def inspect_xml(self, root, result):
        _, rows, appendices = _parts(root, result)
        blocks = _temperature_evidence_blocks(root, result)
        return {'result_rows': rows, 'appendix_tables': appendices, 'evidence_blocks': blocks,
            'unreconciled_temperature_evidence': any(block['temperature_evidence'] for block in blocks)}

    def prepare_update(self, root, result, **target):
        """Resolve every original XML element before any batch member mutates the tree."""
        return prepare_result_update(root, result, **target)

    def update(self, source: Path, output: Path, result, **target):
        # Preserve the established single-update pagination behavior. A batch
        # explicitly limits its layout changes to the selected result tables.
        return self.update_many(source, output, [{'result': result, 'target': target}], paginate_all_groups=True)

    def update_many(self, source: Path, output: Path, updates, *, paginate_all_groups=False):
        """Reuse the single-item renderer while keeping original node references stable."""
        if output.exists():
            raise ValueError('The output already exists; source reports are never overwritten.')
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as package:
            root = etree.fromstring(package.read('word/document.xml'))
            prepared = [self.prepare_update(root, item['result'], **item['target']) for item in updates]
            flowing_headings = reflow_headings(root, {item['table'] for item in prepared}) if not paginate_all_groups else []
            for index, first in enumerate(prepared):
                for second in prepared[index + 1:]:
                    if any(left is right or left in right.iterancestors() or right in left.iterancestors()
                           for left in first['writes'] for right in second['writes']):
                        raise ValueError('Batch result targets overlap; review the mappings before writing.')
            removed_ids = set()
            for item in prepared:
                removed_ids.update(apply_prepared_result(root, item))
            pagination_groups = protect_table_starts(root,
                target_tables=None if paginate_all_groups else {item['table'] for item in prepared})
            protect_reflow_headings(flowing_headings)
            pagination_groups.extend(label for label, _ in flowing_headings if label not in pagination_groups)
            parts = {info.filename: package.read(info.filename) for info in package.infolist()}
            parts['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            parts = remove_replaced_region_parts(parts, removed_ids)
            buffer = BytesIO()
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as updated:
                for info in package.infolist():
                    if info.filename in parts:
                        updated.writestr(info, parts[info.filename])
        with TemporaryDirectory(prefix='connlab-result-') as directory:
            plain = Path(directory) / 'result.docx'
            plain.write_bytes(buffer.getvalue())
            for index, item in enumerate(updates):
                result = item['result']
                if result['kind'] == 'temperature':
                    if self.temperature_chart is None:
                        raise ValueError('The editable temperature curve writer is unavailable.')
                    charted = Path(directory) / f'charted-{index}.docx'
                    self.temperature_chart(plain, charted, result['data']['analysis'],
                        'connlab-report-result:' + result['result_id'])
                    plain = charted
                elif result['kind'] == 'linked_temperature':
                    from backend.infrastructure.office.report_authoring.linked_region import LinkedReportRegion
                    LinkedReportRegion().append(plain, result['data'], 'connlab-report-result:' + result['result_id'])
            protection = self.protected.stage_editable_copy(source, output)
            output.write_bytes(plain.read_bytes())
            self.protected.restore_password_protection(output, protection)
        return {'pagination_groups': pagination_groups}


def prepare_result_update(root, result, *, result_table, result_row, appendix_table, appendix_title,
                          evidence_start=None, evidence_end=None):
    region_selected = evidence_start is not None or evidence_end is not None
    if not region_selected:
        appendix_title = result_appendix_title(result, appendix_title)
    tables, rows, appendices = _parts(root, result)
    evidence = _temperature_evidence_blocks(root, result)
    if not region_selected and any(block['temperature_evidence'] for block in evidence):
        raise ValueError('Old temperature evidence exists in this Group. Select and replace its complete region instead of appending a competing appendix.')
    if not any(row['table_index'] == result_table and row['row_index'] == result_row for row in rows):
        raise ValueError('The selected result row does not match the confirmed Group and Step.')
    if appendix_table is not None and not any(item['table_index'] == appendix_table for item in appendices):
        raise ValueError('Choose an existing appendix table or explicitly add a new appendix.')
    if region_selected:
        allowed = {block['block_index']: block for block in evidence}
        if evidence_start is None or evidence_end is None or evidence_start > evidence_end or appendix_table is not None:
            raise ValueError('Select one complete temperature evidence region, not an appendix and a region together.')
        if any(index not in allowed for index in range(evidence_start, evidence_end + 1)):
            raise ValueError('The temperature evidence region must stay after this Group result table and before the next section.')
        if any(allowed[index]['protected_other_step'] for index in range(evidence_start, evidence_end + 1)):
            raise ValueError('The selected region includes another confirmed Step. Select only this Step evidence; complex multi-Step layouts require separate mapping.')
        if not any(allowed[index]['temperature_evidence'] or allowed[index]['owned_current_result'] for index in range(evidence_start, evidence_end + 1)):
            raise ValueError('Select the temperature measurement region, including its table, curve and associated old conclusion.')
        markers = [block['block_index'] for block in evidence if block['temperature_evidence']]
        if markers and (evidence_start > min(markers) or evidence_end < max(markers)):
            raise ValueError('The selected region must include the complete old temperature table, curve and conclusion, not a partial replacement.')
        if not any(allowed[index]['kind'] in {'tbl', 'sdt'} for index in range(evidence_start, evidence_end + 1)):
            raise ValueError('The temperature region must contain its measurement table or an existing generated result region.')
    table = tables[result_table][0]
    cells = table.findall('w:tr', NS)[result_row].findall('w:tc', NS)
    headers = _headers(table)
    if len(cells) < len(headers):
        raise ValueError('Merged result cells need manual mapping; no report was changed.')

    appendix = tables[appendix_table] if appendix_table is not None else None
    if appendix is not None and sum(item[1] is appendix[1] for item in tables) != 1:
        container = appendix[0].getparent()
        if container.tag != node('sdtContent').tag or any(
                item[1] is appendix[1] and item[0].getparent() is not container for item in tables):
            raise ValueError('This appendix heading covers several tables. Add a separate appendix instead of relabeling unrelated results.')
    blocks = list(root.find('w:body', NS))[evidence_start:evidence_end + 1] if region_selected else []
    writes = [cells[headers.index('result')], cells[headers.index('comment')]]
    if blocks:
        writes.extend(blocks)
    elif appendix is not None:
        old_table, heading = appendix
        container = old_table.getparent().getparent() if old_table.getparent().tag == node('sdtContent').tag else old_table
        writes.extend([container, heading])
    return {'result': result, 'table': table, 'cells': cells, 'headers': headers,
        'appendix': appendix, 'appendix_table': appendix_table, 'appendix_title': appendix_title,
        'region_selected': region_selected, 'blocks': blocks, 'writes': writes}


def apply_prepared_result(root, prepared):
    result, table, cells, headers = (prepared[key] for key in ('result', 'table', 'cells', 'headers'))
    appendix_table, appendix_title, region_selected = (
        prepared[key] for key in ('appendix_table', 'appendix_title', 'region_selected'))
    set_text(cells[headers.index('result')], summary(result))
    set_text(cells[headers.index('comment')], {'pass': 'Pass', 'fail': 'Fail', 'not_applicable': 'N/A', 'pending': ''}[result['outcome']])
    tag = 'connlab-report-result:' + result['result_id']
    section = node('sdt')
    properties = node('sdtPr')
    marker = node('tag')
    marker.set(f'{{{NS["w"]}}}val', tag)
    properties.append(marker)
    alias = node('alias'); alias.set(f'{{{NS["w"]}}}val', _step_identity(result)); properties.append(alias)
    section.append(properties)
    content = node('sdtContent')
    if region_selected:
        heading = node('p')
        set_text(heading, f"Temperature Rise Measurements — Group {result['target']['group_label']}, Step {result['target']['step_token']} (°C)")
        content.append(heading)
    if result['kind'] == 'mechanical_qualitative':
        for matrix in result['data']['tables']:
            heading = node('p'); set_text(heading, matrix['title']); content.append(heading)
            content.append(qualitative_table(matrix))
    else:
        content.append(measurement_table(result))
    for line in result_notes(result):
        paragraph = node('p'); set_text(paragraph, line); content.append(paragraph)
    section.append(content)
    style_generated_section(section, prepared['appendix'][0] if appendix_table is not None else table)
    body = root.find('w:body', NS)
    removed_ids = set()
    if region_selected:
        insertion = body.index(prepared['blocks'][0])
        for block in prepared['blocks']:
            removed_ids.update(value for item in block.iter() for key, value in item.attrib.items() if key.startswith('{'+R+'}'))
            body.remove(block)
        body.insert(insertion, section)
    elif appendix_table is None:
        heading = node('p')
        set_text(heading, appendix_title)
        paragraph_properties = node('pPr'); paragraph_properties.append(node('pageBreakBefore')); paragraph_properties.append(node('keepNext'))
        heading.insert(0, paragraph_properties)
        style_generated_section(heading, table)
        insertion = next((i for i, block in enumerate(body) if 'End of Report' in text(block)),
            len(body) - 1 if len(body) and body[-1].tag == node('sectPr').tag else len(body))
        body.insert(insertion, heading)
        body.insert(insertion + 1, section)
    else:
        old_table, heading = prepared['appendix']
        set_text(heading, appendix_title)
        parent = old_table.getparent()
        if parent.tag == node('sdtContent').tag:
            old_section = parent.getparent()
            old_section.getparent().replace(old_section, section)
        else:
            parent.replace(old_table, section)

    return removed_ids

def summary(result):
    data = result['data']
    if result['kind'] in {'external_reference', 'linked_temperature'}:
        return 'See the scoped related-report evidence and its explicit applicability statement.'
    if result['kind'] in {'electrical', 'resistance_stages'}:
        values = []
        for row in data['rows']:
            value = '' if row['value'] is None else f"{row.get('comparator') or ''}{row['value']} {row['unit']}"
            label = row.get('measurement', 'ΔR' if row.get('quantity') == 'delta' else 'Absolute R')
            values.append(f"{row['stage']} / {row['sample_id']} / {row.get('pair', '')}: {label} {value}".strip())
        return '; '.join(values)
    if result['kind'] == 'mechanical_qualitative':
        return '; '.join(matrix['title'] + ': ' + ', '.join(
            f"{sample} / {column}: {value}" for sample, row in zip(matrix['samples'], matrix['results'])
            for column, value in zip(matrix['columns'], row) if value)
            for matrix in data['tables'])
    if result['kind'] == 'temperature':
        measured = [p for p in data['analysis']['points'] if p['source_row'] is not None]
        return '; '.join(f"{p['current']:g} A: measured Max {p['maximum']:g} °C; Avg of Max {p['average']:g} °C" for p in measured)
    stats = data['summary']
    meaning = (f"{data['test_type']} force ({data['quantity']})" if result['kind'] == 'mechanical' else
               'ΔR' if data['quantity'] == 'delta' else 'Absolute contact resistance')
    return f"{meaning}: Min {stats['min']}; Max {stats['max']}; Avg {stats['average']} {data['unit']}"


def _step_identity(result):
    return f"Group {result['target']['group_label']} / Step {result['target']['step_token']}"


def measurement_table(result):
    data = result['data']
    if result['kind'] in {'external_reference', 'linked_temperature'}:
        adoption = data['adoption']
        return value_table(['Reference', 'Version', 'Source location', 'Adopted scope'], [[adoption[key] for key in ('report_identity', 'source_version', 'source_locator', 'adopted_scope')]])
    if result['kind'] == 'electrical':
        headers = ['Sample / pair', 'Stage', 'IR / DWV reading', 'Conditions', 'Breakdown', 'Source cells']
        values = [[f"{row['sample_id']}\n{row['pair']}", row['stage'], row['measurement'].upper() + '\n' +
            ('' if row['value'] is None else f"{row['comparator'] or ''}{row['value']} {row['unit']}"),
            '\n'.join([f"{row['voltage_v']} V" if row['voltage_v'] else '', f"{row['duration_s']} s" if row['duration_s'] else '']),
            {'not_recorded': '', 'not_applicable': '', 'no_breakdown': 'No breakdown', 'breakdown': 'Breakdown'}[row['breakdown']],
            '\n'.join(f'{key}: {value}' for key, value in row['source_cells'].items())] for row in data['rows']]
        table = value_table(headers, values)
        # A six-column layout keeps measured numbers legible in the common six-inch
        # body. Percent cell widths follow the target table; only reading cells do not wrap.
        widths = (850, 700, 950, 650, 850, 1000)
        for column, width in zip(table.find('w:tblGrid', NS), widths):
            column.set(f'{{{NS["w"]}}}w', str(width * 8640 // 5000))
        for row_index, row in enumerate(table.findall('w:tr', NS)):
            for column_index, (cell, width) in enumerate(zip(row.findall('w:tc', NS), widths)):
                properties = node('tcPr'); cell.insert(0, properties)
                preferred = node('tcW'); preferred.set(f'{{{NS["w"]}}}type', 'pct'); preferred.set(f'{{{NS["w"]}}}w', str(width)); properties.append(preferred)
                if row_index and column_index == 2: properties.append(node('noWrap'))
                if row_index:
                    lines = values[row_index - 1][column_index].split('\n')
                    set_text(cell, lines[0])
                    for line in lines[1:]:
                        paragraph = node('p'); set_text(paragraph, line); cell.append(paragraph)
        return table
    if result['kind'] == 'resistance_stages':
        headers = ['Sample', 'Pair', 'Stage', 'Quantity', 'Value (mΩ)', 'Baseline (mΩ)', 'Raw source value', 'Source cells']
        values = [[row['sample_id'], row['pair'], row['stage'], 'Absolute R' if row['quantity'] == 'absolute' else 'ΔR',
            row['value'] if row['value'] is not None else '', row['baseline_mohm'] or '',
            f"{row['raw_value']} {row['source_unit']}" if row['raw_value'] else '',
            ', '.join(f'{key}: {value}' for key, value in row['source_cells'].items())] for row in data['rows']]
        return value_table(headers, values)
    if result['kind'] == 'mechanical_qualitative':
        return qualitative_table(data['tables'][0])
    if result['kind'] == 'temperature':
        points = [p for p in data['analysis']['points'] if p['source_row'] is not None]
        channels = len(points[0]['rises']) if points else 0
        samples = len(points[0]['sample_maxima']) if points else 0
        headers = ['Measured rise / °C'] + [f"{p['current']:g} A" for p in points]
        identities = data.get('sample_ids') or [f'Sample group {index + 1}' for index in range(samples)]
        values = [['Source row', *[p['source_row'] for p in points]]]
        raw = {row['source_row']: row['values'] for row in data.get('raw_rows', [])}
        selection = data.get('selection')
        if selection:
            if any(point['source_row'] not in raw for point in points):
                raise ValueError('The complete measured temperature source rows are unavailable. Re-import before updating the report.')
            values += [['Ambient (°C)', *[raw[p['source_row']][selection['ambient_column'] - 1] for p in points]]]
            for index, column in enumerate(selection['temperature_columns']):
                values += [[f'Channel {index + 1} measured (°C)', *[raw[p['source_row']][column - 1] for p in points]]]
        values += [[f'Channel {index + 1} rise (°C)', *[p['rises'][index] for p in points]] for index in range(channels)]
        values += [[f'{identities[index]} Max', *[p['sample_maxima'][index] for p in points]] for index in range(samples)]
        values += [['Max', *[p['maximum'] for p in points]], ['Avg of Max', *[p['average'] for p in points]]]
    elif result['kind'] == 'cr':
        headers = ['Sample SN', 'Instrument record', 'Color', 'Voltage', 'Actual I (A)', 'Absolute R (mΩ)']
        keys = ['sample_id', 'record_id', 'color', 'voltage', 'current_a', 'resistance_mohm']
        if data['quantity'] == 'delta':
            headers += ['Initial R (mΩ)', 'ΔR (mΩ)']
            keys += ['initial_mohm', 'delta_mohm']
        values = [[(f"{row['voltage']} {row['voltage_unit']}" if key == 'voltage' else row.get(key, '')) for key in keys] for row in data['rows']]
    else:
        headers = ['Sample SN', 'Instrument record', 'Color', f"{data['test_type'].capitalize()} {data['quantity']} force (N)"]
        keys = ['sample_id', 'record_id', 'color', 'value']
        if any(row.get('part') for row in data['rows']):
            headers.insert(3, 'Part')
            keys.insert(3, 'part')
        if any(row.get('raw_value') is not None and row['raw_value'] != row['value'] for row in data['rows']):
            headers.append('Raw signed force (N)')
            keys.append('raw_value')
        if data['quantity'] == 'hold':
            headers.append('Hold (s)')
            keys.append('hold_seconds')
        values = [[row.get(key, '') for key in keys] for row in data['rows']]
    return value_table(headers, values)


def qualitative_table(matrix):
    headers = [matrix.get('row_heading') or 'Sample'] + [
        f"{matrix.get('column_heading', '')} {label}".strip() for label in matrix['columns']]
    values = [[sample, *row] for sample, row in zip(matrix['samples'], matrix['results'])]
    if matrix.get('curves'):
        headers.append('Source curve annotation (not sample identity)')
        values = [[*row, curve] for row, curve in zip(values, matrix['curves'])]
    return value_table(headers, values)


def value_table(headers, values):
    table = node('tbl')
    properties = node('tblPr')
    style = node('tblStyle'); style.set(f'{{{NS["w"]}}}val', 'TableGrid'); properties.append(style)
    width = node('tblW'); width.set(f'{{{NS["w"]}}}type', 'pct'); width.set(f'{{{NS["w"]}}}w', '5000'); properties.append(width)
    table.append(properties)
    grid = node('tblGrid')
    for _ in headers:
        column = node('gridCol'); column.set(f'{{{NS["w"]}}}w', str(9000//len(headers))); grid.append(column)
    table.append(grid)
    for index, values_row in enumerate([headers, *values]):
        row = node('tr')
        if index == 0:
            row_properties = node('trPr'); row_properties.append(node('tblHeader')); row.append(row_properties)
        for value in values_row:
            cell = node('tc'); set_text(cell, f'{value:g}' if isinstance(value, float) else value); row.append(cell)
        table.append(row)
    return table


def result_notes(result):
    if result['kind'] in {'external_reference', 'linked_temperature'}:
        return result['data']['adoption_notes']
    if result['kind'] in {'electrical', 'resistance_stages'}:
        return ['Blank measurements and breakdown observations are unrecorded, not zero or a passing result. Stage labels do not imply absolute R or ΔR.',
            *[f"Conditions: {row['stage']} / {row['sample_id']} — {row['condition_locator']}" for row in result['data']['rows'] if row.get('condition_locator')],
            *([f"Project acceptance evidence: {result['acceptance_reason']}"] if result.get('acceptance_reason') else [])]
    if result['kind'] == 'mechanical_qualitative':
        count = len(result['data'].get('raw_curves', []))
        return [f"{count} source curve(s) retained; not one curve per observation. Matrix cells are reviewed source observations, not independent instrument measurements.",
            'The report outcome is a separate project decision; matrix Pass labels do not automatically approve this Step.',
            *([f"Project acceptance evidence: {result['acceptance_reason']}"] if result.get('acceptance_reason') else [])]
    if result['kind'] != 'temperature':
        stats = result['data']['summary']
        return [f"Statistics ({result['data']['unit']}): Min {stats['min']}; Max {stats['max']}; Average {stats['average']}; Sample standard deviation {stats['stdev'] if stats['stdev'] is not None else 'not defined for one sample'}. Classifications and source coordinates are retained in the Workspace."]
    analysis = result['data']['analysis']
    lines = [f"Measured temperature rise is listed above. Regression model: ΔT = a·I² + b·I + c; zero-intercept: {'yes' if analysis['zero_intercept'] else 'no'}. The synthetic origin is not a measured reading."]
    for key, label in [('maximum_fit', 'Max'), ('average_fit', 'Avg of Max')]:
        fit = analysis[key]
        coefficients = fit.get('fitted_coefficients') or fit['coefficients']
        lines.append(f"{label} fit: a={float(coefficients['a']):.6g}; b={float(coefficients['b']):.6g}; c={float(coefficients['c']):.6g}; R²={float(fit['r_squared']):.6f}.")
    lines.append('Displayed coefficients are rounded for readability; the retained analysis and editable chart workbook keep the full calculation precision.')
    data = result['data']
    for key, label in [('effective_maximum_coefficients', 'Max'), ('effective_average_coefficients', 'Avg of Max')]:
        if key in data:
            coefficients = data[key]
            lines.append(f"Tools effective {label} coefficients for calculator/derating: a={float(coefficients['a']):.6g}; b={float(coefficients['b']):.6g}; c={float(coefficients['c']):.6g}. These are not the fitted chart curve or new measured readings.")
    if data.get('target_rise') is not None:
        lines.append(f"Retained Tools calculator target rise: {float(data['target_rise']):g} °C; not an automatically approved acceptance limit.")
    if data.get('derating'):
        parameters = data['derating']
        lines.append(f"Retained Tools derating inputs: maximum temperature {float(parameters['max_temperature']):g} °C; ambient point {float(parameters['ambient_point']):g} °C; step {float(parameters['step']):g} °C. See the retained Summary workbook for the Tools calculation.")
    return lines


def result_appendix_title(result, requested):
    match = re.match(r'^\s*Appendix\s+([A-Z]+|\d+)\b', requested, re.I)
    if not match:
        raise ValueError('Supply an Appendix identifier, for example Appendix C. The measurement title follows the confirmed data.')
    data = result['data']
    if result['kind'] == 'mechanical':
        colors = list(dict.fromkeys(row['color'] for row in data['rows'] if row.get('color')))
        label = f"{data['test_type'].capitalize()} Force — {data['quantity'].capitalize()} (N)"
        if colors:
            label += '; ' + ' and '.join(colors)
    elif result['kind'] == 'cr':
        label = ('Change in Contact Resistance (ΔR, mΩ)' if data['quantity'] == 'delta' else 'Absolute Contact Resistance (mΩ)')
    elif result['kind'] == 'mechanical_qualitative':
        label = 'Qualitative Observations — ' + '; '.join(matrix['title'] for matrix in data['tables'])
    elif result['kind'] == 'electrical':
        label = 'Electrical Measurements — IR / DWV'
    elif result['kind'] == 'resistance_stages':
        label = 'Contact Resistance by Stage — Absolute R and ΔR (mΩ)'
    elif result['kind'] == 'external_reference':
        label = 'Scoped Related Report Evidence'
    else:
        label = 'Temperature Rise Measurements (°C)'
    return f'Appendix {match.group(1).upper()}: {label}'


def style_generated_section(section, prototype=None):
    """Only new content receives explicit styling; no global style definitions are changed."""
    fonts = prototype.find('.//w:rFonts', NS) if prototype is not None else None
    size = prototype.find('.//w:sz', NS) if prototype is not None else None
    for run in section.xpath('.//w:r', namespaces=NS):
        properties = run.find('w:rPr', NS)
        if properties is None:
            properties = node('rPr'); run.insert(0, properties)
        for name in ('rFonts', 'sz', 'szCs'):
            old = properties.find('w:'+name, NS)
            if old is not None:
                properties.remove(old)
        chosen_fonts = deepcopy(fonts) if fonts is not None else node('rFonts')
        if fonts is None:
            for field in ('ascii', 'hAnsi', 'cs'):
                chosen_fonts.set(f'{{{NS["w"]}}}{field}', 'Arial')
        properties.append(chosen_fonts)
        chosen_size = deepcopy(size) if size is not None else node('sz')
        if size is None:
            chosen_size.set(f'{{{NS["w"]}}}val', '20')
        properties.append(chosen_size)
    for table in section.xpath('.//w:tbl', namespaces=NS):
        properties = table.find('w:tblPr', NS)
        borders = node('tblBorders')
        for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            border = node(edge)
            for key, value in (('val', 'single'), ('sz', '4'), ('color', '808080')):
                border.set(f'{{{NS["w"]}}}{key}', value)
            borders.append(border)
        properties.append(borders)
        first = table.find('w:tr', NS)
        for cell in first.findall('w:tc', NS):
            cell_properties = cell.find('w:tcPr', NS)
            if cell_properties is None:
                cell_properties = node('tcPr'); cell.insert(0, cell_properties)
            shading = node('shd'); shading.set(f'{{{NS["w"]}}}fill', 'E7E6E6'); cell_properties.append(shading)
            for run in cell.xpath('.//w:r', namespaces=NS):
                run.find('w:rPr', NS).append(node('b'))
