"""Native Excel writer for evidence-bound folder summaries; inputs are never saved."""
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import re

import pdfplumber
from backend.application.mechanical_summary_folder import INFO_FIELDS


def _text(cell, value):
    cell.NumberFormat = '@'
    cell.Value2 = str(value)


def _range(sheet, row, column, last_row, last_column):
    return sheet.Range(sheet.Cells(row, column), sheet.Cells(last_row, last_column))


def _merge_text(sheet, row, column, last_row, last_column, value):
    area = _range(sheet, row, column, last_row, last_column)
    if last_row != row or last_column != column:
        area.Merge()
    _text(sheet.Cells(row, column), value)
    return area


def _table_style(area, *, header=False, statistics=False):
    area.Font.Name = 'Arial'
    area.Font.Size = 11
    area.HorizontalAlignment = -4108
    area.VerticalAlignment = -4108
    area.WrapText = True
    area.Borders.LineStyle = 1
    area.Borders.Weight = 2
    if header:
        area.Interior.Color = 0xBFBFBF
        area.Font.Bold = True
    elif statistics:
        area.Interior.Color = 0xF3EEDA


def _information(sheet, info, row, column=8):
    for offset, label in enumerate(INFO_FIELDS):
        r = row + offset
        _merge_text(sheet, r, column, r, column + 2, label + ':').Font.Bold = True
        area = _merge_text(sheet, r, column + 3, r, column + 5, info.get(label, 'Not recorded'))
        if label == 'Test Date' and info.get(label) not in (None, '', 'Not recorded'):
            # Excel serial avoids locale-dependent COM string-to-date interpretation.
            value = datetime.strptime(info[label], '%Y-%m-%d')
            area.NumberFormat = 'yyyy/mm/dd'
            sheet.Cells(r, column + 3).Value2 = (value - datetime(1899, 12, 30)).days
        width = sum(sheet.Columns(c).ColumnWidth for c in range(column + 3, column + 6))
        length = max(len(str(info.get(label, 'Not recorded'))), len(label))
        sheet.Rows(r).RowHeight = max(32, math.ceil(length / max(18, width * 0.8)) * 14 + 8)
    area = _range(sheet, row, column, row + 7, column + 5)
    area.Interior.Color = 0xFFE5D3
    area.Font.Color = 0x602000
    area.Font.Size = 10
    area.HorizontalAlignment = -4131
    area.WrapText = True
    area.VerticalAlignment = -4108


def _quantitative(sheet, section):
    rows = section['rows']
    descriptors = ['sample']
    if any(row['colour'] for row in rows):
        descriptors.append('colour')
    if any(row['part'] for row in rows):
        descriptors.append('part')
    forces = ['mating', 'withdraw'] if section['kind'] == 'mating' else ['value']
    labels = {'sample': 'SN', 'colour': 'Colour', 'part': 'Part', 'mating': 'Mating', 'withdraw': 'Withdraw',
              'value': 'Retention Force' if section['kind'] == 'retention' else 'Hold Force'}
    fields = descriptors + forces
    first, last = 9, 8 + len(fields)
    _merge_text(sheet, 3, first, 4, first + len(descriptors) - 1, 'Unit: N')
    process = section['information'].get('Item/Process', '')
    match = re.search(r'\bGroup\s+[^/;]+', process, re.I)
    group = match[0].strip() if match else 'Group: Not recorded'
    _merge_text(sheet, 3, first + len(descriptors), 4, last, group)
    _text(sheet.Cells(5, 8), 'Curve')
    for col, key in enumerate(fields, first):
        _text(sheet.Cells(5, col), labels[key])
    for r, record in enumerate(rows, 6):
        _text(sheet.Cells(r, 8), record['curve'])
        for col, key in enumerate(fields, first):
            if key in descriptors:
                _text(sheet.Cells(r, col), record[key])
            else:
                value = record[key]
                if key == 'withdraw' and section.get('withdraw_magnitude'):
                    value = abs(value)
                sheet.Cells(r, col).Value2 = value
                places = max(0, -Decimal(str(value)).normalize().as_tuple().exponent)
                sheet.Cells(r, col).NumberFormat = '0' + ('.' + '0' * places if places else '')
    final_data = 5 + len(rows)
    _table_style(_range(sheet, 5, first, final_data, last))
    _table_style(_range(sheet, 3, first, 5, last), header=True)
    if len(descriptors) > 1:
        start = 6
        for r in range(7, final_data + 2):
            if r > final_data or rows[r-6]['sample'] != rows[start-6]['sample']:
                if r - start > 1:
                    _merge_text(sheet, start, first, r-1, first, rows[start-6]['sample'])
                start = r
    for offset, (label, function) in enumerate((('Min', 'MIN'), ('Max', 'MAX'), ('Avg', 'AVERAGE'), ('Stdev', 'STDEV')), final_data + 1):
        _merge_text(sheet, offset, first, offset, first + len(descriptors) - 1, label)
        for col in range(first + len(descriptors), last + 1):
            if function == 'STDEV' and len(rows) < 2:
                _text(sheet.Cells(offset, col), 'N/A')
            else:
                address = _range(sheet, 6, col, final_data, col).Address.replace('$', '')
                sheet.Cells(offset, col).Formula = f'={function}({address})'
                sheet.Cells(offset, col).NumberFormat = '0.00'
        _table_style(_range(sheet, offset, first, offset, last), statistics=True)
    _information(sheet, section['information'], final_data + 8)
    return final_data + 17


def _single_row_table(sheet, table, top, first):
    columns = table['columns']
    _merge_text(sheet, top, first, top+1, first, table['title'])
    _merge_text(sheet, top, first+1, top, first+len(columns), table.get('column_heading', ''))
    for j, column in enumerate(columns, first+1):
        _text(sheet.Cells(top+1, j), column)
    _text(sheet.Cells(top+2, first), table.get('row_heading') or table['samples'][0])
    for j, value in enumerate(table['results'][0], first+1):
        _text(sheet.Cells(top+2, j), value)
    _table_style(_range(sheet, top, first, top+1, first+len(columns)), header=True)
    _table_style(_range(sheet, top+2, first, top+2, first+len(columns)))
    sheet.Rows(top+2).RowHeight = max(32, math.ceil(len(table.get('row_heading', '')) / 11)*14+8)
    if table.get('curves'):
        _text(sheet.Cells(top+1, first+len(columns)+2), 'Curve')
        _text(sheet.Cells(top+2, first+len(columns)+2), table['curves'][0])
    return top+5


def _qualitative_table(sheet, table, top, first=8):
    if len(table['samples']) == 1 and not table.get('diagonal'):
        return _single_row_table(sheet, table, top, first)
    columns, samples = table['columns'], table['samples']
    count = len(columns)
    _merge_text(sheet, top, first, top, first + count + 1, table['title']).Font.Bold = True
    groups = [label.split(' / ', 1) for label in columns]
    grouped = all(len(parts) == 2 for parts in groups)
    _merge_text(sheet, top+1, first, top+2, first+1, 'S/N')
    if grouped:
        start = 0
        for j in range(1, count + 1):
            if j == count or groups[j][0] != groups[start][0]:
                _merge_text(sheet, top+1, first+2+start, top+1, first+1+j, groups[start][0])
                start = j
    else:
        _merge_text(sheet, top+1, first+2, top+1, first+count+1, table.get('column_heading', ''))
    for j, label in enumerate(columns, first+2):
        _text(sheet.Cells(top+2, j), groups[j-first-2][1] if grouped else label)
    _table_style(_range(sheet, top+1, first, top+2, first+count+1), header=True)
    end = top+2+len(samples)
    heading_height = math.ceil(len(table.get('row_heading', '')) / 11) * 14 + 8
    for r in range(top+3, end+1):
        sheet.Rows(r).RowHeight = max(sheet.Rows(r).RowHeight, math.ceil(heading_height / len(samples)), 25)
    for i, sample in enumerate(samples):
        row = top+3+i
        _text(sheet.Cells(row, first+1), sample)
        for j, result in enumerate(table['results'][i], first+2):
            _text(sheet.Cells(row, j), result)
    _merge_text(sheet, top+3, first, end, first, table.get('row_heading', ''))
    _table_style(_range(sheet, top+3, first, end, first+count+1))
    if table.get('diagonal'):
        for i in range(len(samples)):
            for j in range(count):
                if i != j:
                    sheet.Cells(top+3+i, first+2+j).Borders(5).LineStyle = 1
    if table.get('curves'):
        _text(sheet.Cells(top+2, first+count+3), 'Curve')
        for i, curve in enumerate(table['curves'], top+3):
            _text(sheet.Cells(i, first+count+3), curve)
    return end+3


def _prepare_original(sheet, section):
    # Native shapes/charts remain on the copied worksheet. Raw cell coordinates
    # stay unchanged so chart series do not point at a compacted/reordered range.
    sheet.UsedRange.UnMerge()
    keep = {cell['source'] for cell in section['raw_cells']}
    used = sheet.UsedRange
    for row in range(used.Row, used.Row + used.Rows.Count):
        for col in range(used.Column, used.Column + used.Columns.Count):
            cell = sheet.Cells(row, col)
            if cell.Address.replace('$', '') not in keep:
                cell.Clear()
    sheet.Cells.Font.Name = 'Arial'
    sheet.Cells.Font.Size = 11
    # Retained cells are the native copies, including formulas and number formats.
    return max(sheet.Range(c['source']).Row for c in section['raw_cells'])


def _position_shapes(sheet, start_row):
    top = sheet.Cells(start_row, 8).Top
    for i in range(1, sheet.Shapes.Count + 1):
        shape = sheet.Shapes(i)
        width, height = float(shape.Width), float(shape.Height)
        shape.Placement = 3
        shape.Left = sheet.Cells(start_row, 8).Left
        shape.Top = top
        if width > 650:
            shape.Width = 650
            shape.Height = height * 650 / width
        top += float(shape.Height) + 20
    return top


def _pdf_images(sheet, content, root, index):
    top = sheet.Cells(3, 1).Top
    with pdfplumber.open(BytesIO(content)) as document:
        for p, page in enumerate(document.pages):
            words = page.extract_words()
            headings = [w['top'] for w in words if any(label in w['text'] for label in ('试验结果', '序列曲线', '数据统计'))]
            # A continuation page can start with the curve before its statistics.
            crop_top = max(0, min(headings)-4) if headings else 0
            # Preserve original curve pixels and instrument statistics. Remove only
            # the introductory form above the first result, curve or statistics heading.
            content_bottoms = [w['bottom'] for w in words if crop_top <= w['top'] < page.height - 50]
            content_bottoms += [item['bottom'] for item in page.images if item['top'] >= crop_top]
            crop_bottom = min(page.height, max(content_bottoms) + 14) if content_bottoms else page.height
            crop = page.crop((0, crop_top, page.width, max(crop_top+1, crop_bottom)))
            rendered = crop.to_image(resolution=160).original
            path = root / f'curve_{index}_{p}.png'
            rendered.save(path)
            width = 360.0
            height = width * rendered.height / rendered.width
            sheet.Shapes.AddPicture(str(path), False, True, sheet.Cells(3, 1).Left, top, width, height)
            top += height + 16
    return top


def generate_folder_workbook(files: list[tuple[str, bytes]], analysis: dict) -> bytes:
    if not analysis.get('ready'):
        raise ValueError('Complete the unresolved source mappings and report results before generating.')
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    excel = target = source = None
    try:
        with TemporaryDirectory(prefix='connlab-mechanical-folder-') as temp:
            root = Path(temp)
            excel = win32com.client.DispatchEx('Excel.Application')
            excel.Visible = False; excel.DisplayAlerts = False; excel.EnableEvents = False
            excel.AutomationSecurity = 3
            target = excel.Workbooks.Add()
            placeholders = target.Worksheets.Count
            contents = dict(files)
            for index, section in enumerate(analysis['sections']):
                content = contents[section['source']]
                if section.get('sheet'):
                    path = root / f'source_{index}{Path(section["source"]).suffix}'
                    path.write_bytes(content)
                    source = excel.Workbooks.Open(str(path), UpdateLinks=0, ReadOnly=True, AddToMru=False)
                    source.Worksheets(section['sheet']).Copy(After=target.Worksheets(target.Worksheets.Count))
                    source.Close(SaveChanges=False); source = None
                    sheet = target.Worksheets(target.Worksheets.Count)
                    raw_end = _prepare_original(sheet, section)
                else:
                    sheet = target.Worksheets.Add(After=target.Worksheets(target.Worksheets.Count))
                    raw_end = 0
                base = re.sub(r'[\[\]:*?/\\]', '_', section['name'])[:31]
                names = {target.Worksheets(i).Name for i in range(1, target.Worksheets.Count+1) if target.Worksheets(i).Name != sheet.Name}
                name, suffix = base, 2
                while name in names:
                    name = f'{base[:27]} {suffix}'; suffix += 1
                sheet.Name = name
                sheet.Cells.Font.Name = 'Arial'; sheet.Cells.Font.Size = 11
                sheet.Rows.RowHeight = 22
                sheet.Columns('A:G').ColumnWidth = 9
                sheet.Columns('H:U').ColumnWidth = 13
                if section['kind'] in {'polarisation', 'protection'}:
                    row = side_row = 3
                    beside = (any(t.get('diagonal') for t in section['tables']) and
                              all(len(t['columns']) <= 3 for t in section['tables']))
                    for table in section['tables']:
                        if beside and not table.get('diagonal'):
                            side_row = _qualitative_table(sheet, table, side_row, 17)
                        else:
                            row = _qualitative_table(sheet, table, row)
                    row = max(row, side_row)
                    _information(sheet, section['information'], max(raw_end+3, row+2), 1)
                    _position_shapes(sheet, row+2)
                else:
                    _quantitative(sheet, section)
                    _pdf_images(sheet, content, root, index)
                sheet.PageSetup.Orientation = 2
                sheet.PageSetup.PaperSize = 8
                sheet.PageSetup.Zoom = False
                sheet.PageSetup.FitToPagesWide = 1
                sheet.PageSetup.FitToPagesTall = False
                bottom = sheet.UsedRange.Row + sheet.UsedRange.Rows.Count - 1
                right = sheet.UsedRange.Column + sheet.UsedRange.Columns.Count - 1
                for shape in sheet.Shapes:
                    bottom = max(bottom, shape.BottomRightCell.Row)
                    right = max(right, shape.BottomRightCell.Column)
                sheet.PageSetup.PrintArea = _range(sheet, 1, 1, bottom+1, right+1).Address
                sheet.PageSetup.LeftMargin = 18; sheet.PageSetup.RightMargin = 18
                sheet.PageSetup.TopMargin = 18; sheet.PageSetup.BottomMargin = 18
                sheet.Activate()
                excel.ActiveWindow.DisplayGridlines = False
                sheet.Range('A1').Select()
            for _ in range(placeholders):
                target.Worksheets(1).Delete()
            target.Worksheets(1).Activate()
            excel.CalculateFull()
            output = root / 'Mechanical Force Summary.xlsx'
            target.SaveAs(str(output), FileFormat=51, AddToMru=False)
            target.Close(SaveChanges=False); target = None
            return output.read_bytes()
    finally:
        try:
            if source is not None: source.Close(SaveChanges=False)
            if target is not None: target.Close(SaveChanges=False)
        finally:
            try:
                if excel is not None: excel.Quit()
            finally:
                pythoncom.CoUninitialize()
