"""Copy instrument workbook sheets through Excel so native drawings survive."""

from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from contextlib import nullcontext
from io import BytesIO
import math
import re
import pdfplumber

_INFO = ('LTR', 'Test Date', 'Tested By', 'Amb Temp. and Rel. Hum.',
         'Test Equipment ID', 'Test Condition', 'Item/Process', 'Remark')


def _text(cell, value):
    # User text is data, not a formula, even if it begins with '=', '+', '-' or '@'.
    cell.NumberFormat = '@'
    cell.Value = str(value or 'Not recorded')


def add_reviewed_results(content: bytes, sections: list[dict], *, remove_placeholder: bool = False) -> bytes:
    """Add user-reviewed result tables while preserving copied native drawings."""
    if not sections or len(sections) > 20:
        raise ValueError('Select between 1 and 20 reviewed results.')
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    excel = workbook = None
    temporary = TemporaryDirectory(prefix='connlab-mechanical-results-')
    try:
        with nullcontext(Path(temporary.name)) as root:
            source = root / 'source.xlsx'
            source.write_bytes(content)
            excel = win32com.client.gencache.EnsureDispatch(win32com.client.DispatchEx('Excel.Application'))
            excel.Visible = False
            excel.DisplayAlerts = False
            excel.EnableEvents = False
            excel.AutomationSecurity = 3
            workbook = excel.Workbooks.Open(Filename=str(source), UpdateLinks=0, ReadOnly=False, AddToMru=False)
            for index, section in enumerate(sections):
                kind = section.get('kind')
                rows = section.get('rows')
                if kind not in {'hold', 'hold_end1', 'retention', 'mating', 'qualitative'} or not isinstance(rows, list) or not 1 <= len(rows) <= 500:
                    raise ValueError('Review the test type and result rows before generating.')
                target_index = section.get('target_sheet_index')
                if target_index is not None:
                    if type(target_index) is not int or not 1 <= target_index <= workbook.Worksheets.Count:
                        raise ValueError('Select a valid source sheet.')
                    sheet = workbook.Worksheets(target_index)
                    last_column = sheet.UsedRange.Column + sheet.UsedRange.Columns.Count - 1
                    for shape_index in range(1, sheet.Shapes.Count + 1):
                        last_column = max(last_column, sheet.Shapes(shape_index).BottomRightCell.Column)
                    first_column = last_column + 2
                else:
                    sheet = workbook.Worksheets.Add(After=workbook.Worksheets(workbook.Worksheets.Count))
                    name = re.sub(r'[\[\]:*?/\\]', '_', str(section.get('name') or f'Result {index + 1}'))[:26]
                    existing = {workbook.Worksheets(i).Name.casefold() for i in range(1, workbook.Worksheets.Count + 1) if workbook.Worksheets(i).Name != sheet.Name}
                    base = name or 'Result'
                    name = base
                    n = 2
                    while name.casefold() in existing:
                        name = f'{base[:25]} {n}'
                        n += 1
                    sheet.Name = name
                    first_column = 1
                _text(sheet.Cells(1, first_column), section.get('source', 'Source not recorded'))
                _text(sheet.Cells(2, first_column), f"Group: {section.get('group') or 'Not recorded'}")
                headers = ['Curve', 'Sample', 'Mating (N)', 'Withdraw (N)'] if kind == 'mating' else ['Curve', 'Sample', {'hold': 'FEnd section (N)', 'hold_end1': 'FEnd section 1 (N)', 'retention': 'Retention Force (N)', 'qualitative': 'Result'}[kind]]
                for column, header in enumerate(headers, first_column):
                    _text(sheet.Cells(3, column), header)
                result_header = sheet.Range(sheet.Cells(3, first_column + 1), sheet.Cells(3, first_column + len(headers) - 1))
                result_header.Font.Bold = True
                result_header.Interior.Color = 0xBFBFBF
                fields = ('mating', 'withdraw') if kind == 'mating' else ('value',)
                for offset, row in enumerate(rows, 4):
                    if not isinstance(row, dict) or not str(row.get('curve', '')).strip() or not str(row.get('sample', '')).strip():
                        raise ValueError('Each result needs a reviewed curve and sample.')
                    _text(sheet.Cells(offset, first_column), row['curve'])
                    _text(sheet.Cells(offset, first_column + 1), row['sample'])
                    if kind == 'qualitative':
                        if row.get('result') not in {'Pass', 'Fail', 'N/A'}:
                            raise ValueError('Each qualitative result must be explicitly selected.')
                        _text(sheet.Cells(offset, first_column + 2), row['result'])
                        continue
                    for column, field in enumerate(fields, first_column + 2):
                        value = row.get(field)
                        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                            raise ValueError('Each measurement must be a finite number.')
                        sheet.Cells(offset, column).Value = value
                start = 4 + len(rows) + 1
                for i, (label, formula) in enumerate(() if kind == 'qualitative' else (('Min', 'MIN'), ('Max', 'MAX'), ('Avg', 'AVERAGE'), ('Stdev', 'STDEV'))):
                    _text(sheet.Cells(start + i, first_column + 1), label)
                    for column in range(first_column + 2, first_column + len(headers)):
                        if formula == 'STDEV' and len(rows) < 2:
                            continue
                        address = sheet.Range(sheet.Cells(4, column), sheet.Cells(3 + len(rows), column)).Address.replace('$', '')
                        sheet.Cells(start + i, column).Formula = f'={formula}({address})'
                if kind != 'qualitative':
                    sheet.Range(sheet.Cells(start, first_column + 1), sheet.Cells(start + 3, first_column + len(headers) - 1)).Interior.Color = 0xF3EEDA
                information = section.get('information') or {}
                for i, label in enumerate(_INFO, start + 5):
                    _text(sheet.Cells(i, first_column), label)
                    _text(sheet.Cells(i, first_column + 1), information.get(label))
                info_range = sheet.Range(sheet.Cells(start + 5, first_column), sheet.Cells(start + 12, first_column + 1))
                info_range.Interior.Color = 0xFFE5D3
                info_range.Font.Color = 0x602000
                sheet.Range(sheet.Cells(start + 5, first_column), sheet.Cells(start + 12, first_column)).Font.Bold = True
                sheet.Columns(first_column).ColumnWidth = 25
                for column in range(first_column + 1, first_column + len(headers)):
                    sheet.Columns(column).ColumnWidth = 20
                sheet.Cells(1, first_column).WrapText = True
                if target_index is None:
                    sheet.PageSetup.Zoom = False
                    sheet.PageSetup.FitToPagesWide = 1
                    sheet.PageSetup.FitToPagesTall = False
                else:
                    # Instrument charts can span many columns; shrinking them and
                    # the adjacent results onto one page makes the text unreadable.
                    sheet.PageSetup.Zoom = 100
                sheet.PageSetup.Orientation = 2
                pdf_content = section.get('pdf_content')
                if pdf_content:
                    # Retain each original PDF page as an image, including its original curves.
                    # Start each page on a separate printed page so that a curve is
                    # not split across sheets or shrunk together with the results.
                    sheet.PageSetup.Orientation = 1
                    sheet.PageSetup.Zoom = 100
                    with pdfplumber.open(BytesIO(pdf_content)) as document:
                        image_row = start + len(_INFO) + 7
                        for page_index, page in enumerate(document.pages):
                            rendered = page.to_image(resolution=120).original
                            image_path = root / f'pdf_{index}_{page_index}.png'
                            rendered.save(image_path)
                            width = min(430.0, 600.0 * rendered.width / rendered.height)
                            height = width * rendered.height / rendered.width
                            anchor = sheet.Cells(image_row, first_column)
                            sheet.HPageBreaks.Add(Before=anchor)
                            sheet.Shapes.AddPicture(str(image_path), False, True, anchor.Left, anchor.Top, width, height)
                            image_row += math.ceil(height / sheet.StandardHeight) + 3
            if remove_placeholder:
                workbook.Worksheets(1).Delete()
            workbook.Application.CalculateFull()
            output = root / 'summary.xlsx'
            workbook.SaveAs(Filename=str(output), FileFormat=51, AddToMru=False)
            workbook.Close(SaveChanges=False)
            workbook = None
            return output.read_bytes()
    finally:
        if workbook is not None:
            workbook.Close(SaveChanges=False)
        if excel is not None:
            excel.Quit()
        pythoncom.CoUninitialize()
        temporary.cleanup()


def copy_instrument_workbooks(files: list[tuple[str, bytes]]) -> bytes:
    if not files or len(files) > 20:
        raise ValueError('Select between 1 and 20 instrument workbooks.')
    for name, content in files:
        if PurePath(name).suffix.lower() not in {'.xls', '.xlsx'} or not content or len(content) > 25 * 1024 * 1024:
            raise ValueError('Use nonempty XLS or XLSX workbooks smaller than 25 MB.')

    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    excel = None
    target = None
    source = None
    temporary = TemporaryDirectory(prefix='connlab-mechanical-')
    try:
        with nullcontext(Path(temporary.name)) as root:
            excel = win32com.client.gencache.EnsureDispatch(win32com.client.DispatchEx('Excel.Application'))
            excel.Visible = False
            excel.DisplayAlerts = False
            excel.EnableEvents = False
            excel.AutomationSecurity = 3  # Disable macros in uploaded instrument files.
            target = excel.Workbooks.Add()
            placeholder = target.Worksheets(1)
            for index, (name, content) in enumerate(files):
                path = root / f'source_{index}{PurePath(name).suffix.lower()}'
                path.write_bytes(content)
                source = excel.Workbooks.Open(Filename=str(path), UpdateLinks=0, ReadOnly=True, AddToMru=False)
                try:
                    for sheet_index in range(1, source.Worksheets.Count + 1):
                        source.Worksheets(sheet_index).Copy(After=target.Worksheets(target.Worksheets.Count))
                finally:
                    source.Close(SaveChanges=False)
                    source = None
            placeholder.Delete()
            output = root / 'instrument_copy.xlsx'
            target.SaveAs(Filename=str(output), FileFormat=51, AddToMru=False)
            target.Close(SaveChanges=False)
            target = None
            return output.read_bytes()
    finally:
        if source is not None:
            source.Close(SaveChanges=False)
        if target is not None:
            target.Close(SaveChanges=False)
        if excel is not None:
            excel.Quit()
        pythoncom.CoUninitialize()
        temporary.cleanup()
