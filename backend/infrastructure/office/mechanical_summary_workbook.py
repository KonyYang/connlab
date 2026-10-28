"""Read-only preview of uploaded instrument workbook values."""

from io import BytesIO
from pathlib import PurePath
from zipfile import BadZipFile

import xlrd
from openpyxl import load_workbook


def inspect_workbook(content: bytes, filename: str) -> dict:
    if not content or len(content) > 25 * 1024 * 1024:
        raise ValueError('Select a nonempty workbook smaller than 25 MB.')
    suffix = PurePath(filename).suffix.lower()
    sheets = []
    if suffix == '.xls':
        try:
            book = xlrd.open_workbook(file_contents=content, on_demand=True)
        except (xlrd.XLRDError, OSError, EOFError) as exc:
            raise ValueError('The workbook cannot be read. Select a valid XLS file.') from exc
        try:
            for sheet in book.sheets():
                if sheet.nrows > 20000 or sheet.ncols > 256:
                    raise ValueError('Workbook exceeds the supported size.')
                sheets.append({'name': sheet.name, 'rows': [sheet.row_values(i) for i in range(sheet.nrows)]})
        finally:
            book.release_resources()
    elif suffix == '.xlsx':
        try:
            book = load_workbook(BytesIO(content), read_only=True, data_only=False, keep_links=False)
        except (BadZipFile, OSError, EOFError) as exc:
            raise ValueError('The workbook cannot be read. Select a valid XLSX file.') from exc
        try:
            for sheet in book:
                if sheet.max_row > 20000 or sheet.max_column > 256:
                    raise ValueError('Workbook exceeds the supported size.')
                sheets.append({'name': sheet.title, 'rows': [list(row) for row in sheet.iter_rows(values_only=True)]})
        finally:
            book.close()
    else:
        raise ValueError('Select an XLS or XLSX workbook.')
    return {'sheets': sheets, 'requires_review': True}
