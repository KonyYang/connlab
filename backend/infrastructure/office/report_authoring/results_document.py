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
from backend.infrastructure.office.report_authoring.pagination import protect_table_starts


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
    if result.get('kind') != 'temperature':
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
            _, rows, appendices = _parts(root, result)
            blocks = _temperature_evidence_blocks(root, result)
        return {'result_rows': rows, 'appendix_tables': appendices, 'evidence_blocks': blocks,
            'unreconciled_temperature_evidence': any(block['temperature_evidence'] for block in blocks)}

    def update(self, source: Path, output: Path, result, *, result_table, result_row, appendix_table, appendix_title,
               evidence_start=None, evidence_end=None):
        if output.exists():
            raise ValueError('The output already exists; source reports are never overwritten.')
        region_selected = evidence_start is not None or evidence_end is not None
        if not region_selected:
            appendix_title = result_appendix_title(result, appendix_title)
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as package:
            root = etree.fromstring(package.read('word/document.xml'))
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
            content.append(measurement_table(result))
            for line in result_notes(result):
                paragraph = node('p'); set_text(paragraph, line); content.append(paragraph)
            section.append(content)
            style_generated_section(section, tables[appendix_table][0] if appendix_table is not None else table)
            body = root.find('w:body', NS)
            removed_ids = set()
            if region_selected:
                for block in list(body)[evidence_start:evidence_end + 1]:
                    removed_ids.update(value for item in block.iter() for key, value in item.attrib.items() if key.startswith('{'+R+'}'))
                    body.remove(block)
                body.insert(evidence_start, section)
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
                old_table, heading = tables[appendix_table]
                if sum(item[1] is heading for item in tables) != 1:
                    raise ValueError('This appendix heading covers several tables. Add a separate appendix instead of relabeling unrelated results.')
                set_text(heading, appendix_title)
                parent = old_table.getparent()
                if parent.tag == node('sdtContent').tag:
                    old_section = parent.getparent()
                    old_section.getparent().replace(old_section, section)
                else:
                    parent.replace(old_table, section)
            pagination_groups = protect_table_starts(root)
            buffer = BytesIO()
            parts = {info.filename: package.read(info.filename) for info in package.infolist()}
            parts['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            parts = remove_replaced_region_parts(parts, removed_ids)
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as updated:
                for info in package.infolist():
                    if info.filename in parts:
                        updated.writestr(info, parts[info.filename])
        with TemporaryDirectory(prefix='connlab-result-') as directory:
            plain = Path(directory)/'result.docx'
            plain.write_bytes(buffer.getvalue())
            if result['kind'] == 'temperature':
                if self.temperature_chart is None:
                    raise ValueError('The editable temperature curve writer is unavailable.')
                charted = Path(directory)/'charted.docx'
                self.temperature_chart(plain, charted, result['data']['analysis'], tag)
                plain = charted
            protection = self.protected.stage_editable_copy(source, output)
            output.write_bytes(plain.read_bytes())
            self.protected.restore_password_protection(output, protection)
        return {'pagination_groups': pagination_groups}


def summary(result):
    data = result['data']
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
        if data['quantity'] == 'hold':
            headers.append('Hold (s)')
            keys.append('hold_seconds')
        values = [[row.get(key, '') for key in keys] for row in data['rows']]
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
