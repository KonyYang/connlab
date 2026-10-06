"""Workbook values without a dependency on their Office file representation."""

from dataclasses import dataclass

CellValue = str | float | int | bool | None
UNPOWERED_CURRENT_THRESHOLD = .1


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


def column_letter(index: int) -> str:
    letters = ''
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters
