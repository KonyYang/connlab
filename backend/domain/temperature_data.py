"""Workbook values without a dependency on their Office file representation."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from math import isfinite
import re

CellValue = str | float | int | bool | None


def round_current(value: float, decimals: int = 0, *, multiplier: float = 1.) -> float:
    """Quantize amperes like Excel ROUND, not Python's ties-to-even round."""
    if not isinstance(decimals, int) or isinstance(decimals, bool) or not 0 <= decimals <= 4:
        raise ValueError('Current decimals must be an integer from 0 to 4.')
    if not isfinite(value) or not isfinite(multiplier):
        raise ValueError('Current must be finite.')
    number = Decimal(str(value))
    scale = Decimal(str(multiplier))
    with localcontext() as context:
        context.prec = max(50, number.adjusted() + scale.adjusted() + decimals + 4)
        rounded = (number * scale).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return float(rounded) if rounded else 0.


def current_number_format(decimals: int) -> str:
    return '0' + ('.' + '0' * decimals if decimals else '')


@dataclass(frozen=True)
class WorkbookTable:
    file_name: str
    sheet_names: tuple[str, ...]
    sheet_name: str
    rows: tuple[tuple[CellValue, ...], ...]

    @property
    def width(self) -> int:
        return max((len(row) for row in self.rows), default=0)


@dataclass(frozen=True)
class DataSelection:
    """Source positions are one-based and remain stable after exclusions."""

    header_row: int
    start_row: int
    end_row: int
    ambient_column: int
    current_column: int
    temperature_columns: tuple[int, ...]
    thermocouples_per_sample: int
    excluded_rows: tuple[int, ...] = ()
    current_multiplier: float = 1.
    sample_groups: tuple[tuple[int, ...], ...] | None = None
    channel_names: tuple[tuple[int, str], ...] = ()
    sample_count: int | None = None
    current_decimals: int = 0


def measurement_name(table: WorkbookTable, selection: DataSelection, column: int) -> str:
    """Display/export metadata never replaces the source-position identity or grouping."""
    names = dict(selection.channel_names)
    if column in names:
        return names[column].strip()
    header = str(table.rows[selection.header_row - 1][column - 1] or '')
    clean = re.sub(r'\s*[（(]\s*(?:°?C|℃|VDC|V|m?A)\s*[）)]\s*$', '', header, flags=re.I).strip()
    match = re.fullmatch(r'\d+\s*<([^>]+)>\s*(.*)', clean)
    return f'{match[1]} {match[2]}'.strip() if match else clean


def column_letter(index: int) -> str:
    letters = ''
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters
