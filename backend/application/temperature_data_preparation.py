"""Review scanner values and explicit operator selections before numerical analysis."""

from dataclasses import dataclass
from math import isfinite

from backend.domain.temperature_data import DataSelection, WorkbookTable, column_letter
from backend.domain.temperature_rise import Measurement


@dataclass(frozen=True)
class DataIssue:
    code: str
    severity: str
    source_row: int
    message: str


@dataclass(frozen=True)
class PreparedData:
    measurements: tuple[Measurement, ...]
    issues: tuple[DataIssue, ...]
    ready: bool


def prepare_data(table: WorkbookTable, selection: DataSelection, *, acknowledge_warnings: bool = False) -> PreparedData:
    _validate_selection(table, selection)
    measurements: list[Measurement] = []
    issues: list[DataIssue] = []
    excluded = set(selection.excluded_rows)
    columns = (selection.current_column, selection.ambient_column, *selection.temperature_columns)
    for number in range(selection.start_row, selection.end_row + 1):
        if number in excluded:
            continue
        row = table.rows[number - 1]
        values: list[float] = []
        for column in columns:
            try:
                values.append(_number(row[column - 1] if column <= len(row) else None))
            except ValueError:
                issues.append(DataIssue('invalid_reading', 'error', number,
                    f"Row {number}, column {column_letter(column)}: missing or non-numeric reading. Correct the mapping or exclude this row."))
        if len(values) != len(columns):
            continue
        current = values[0] * selection.current_multiplier
        if not isfinite(current) or current < 0:
            issues.append(DataIssue('invalid_current', 'error', number,
                f"Row {number}: current must be finite and nonnegative. Check the selected column and current scale."))
            continue
        measurement = Measurement(number, current, values[1], tuple(values[2:]))
        measurements.append(measurement)
        if current == 0:
            issues.append(DataIssue('zero_current', 'warning', number,
                f"Row {number}: current is zero. Confirm whether this is an interruption or a reading after switch-off."))
        if len(measurements) > 1:
            previous = measurements[-2]
            if 0 < current < previous.current * .99:
                issues.append(DataIssue('current_drop', 'warning', number,
                    f"Row {number}: current decreased by more than 1%. Confirm whether this stage belongs in the test."))
        if any(value < measurement.ambient - 1 for value in measurement.temperatures):
            issues.append(DataIssue('below_ambient', 'warning', number,
                f"Row {number}: a thermocouple reads more than 1°C below ambient. Check the selected channels."))
    if not measurements:
        issues.append(DataIssue('no_data', 'error', selection.start_row, "No usable rows remain. Restore rows or correct the mapping."))
    ready = not any(issue.severity == 'error' for issue in issues) and (not issues or acknowledge_warnings)
    return PreparedData(tuple(measurements), tuple(issues), ready)


def _number(value: object) -> float:
    if isinstance(value, bool) or value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError('Missing reading')
    try:
        numeric = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError('Non-numeric reading') from exc
    if not isfinite(numeric):
        raise ValueError('Non-finite reading')
    return numeric


def _validate_selection(table: WorkbookTable, selection: DataSelection) -> None:
    if not 1 <= selection.header_row < selection.start_row <= selection.end_row <= len(table.rows):
        raise ValueError("Choose a header row before the data, and a data range inside the selected sheet.")
    count = selection.thermocouples_per_sample
    if count < 1 or not selection.temperature_columns or len(selection.temperature_columns) % count:
        raise ValueError("Select complete samples with the same number of thermocouples per sample.")
    columns = (selection.ambient_column, selection.current_column, *selection.temperature_columns)
    if len(set(columns)) != len(columns) or any(not 1 <= col <= table.width for col in columns):
        raise ValueError("Assign each source column once: ambient, current and thermocouples must be distinct.")
    if not isfinite(selection.current_multiplier) or selection.current_multiplier <= 0:
        raise ValueError("Current scale must be a finite positive number.")
    if any(not selection.start_row <= row <= selection.end_row for row in selection.excluded_rows):
        raise ValueError("Excluded rows must be inside the selected data range.")


def suggest_selection(table: WorkbookTable) -> DataSelection:
    """Editable initial guesses, never a substitute for operator confirmation."""
    width = table.width
    if width < 3 or len(table.rows) < 2:
        raise ValueError("The sheet needs a header and numeric temperature, ambient and current columns.")
    start = 2
    for index, row in enumerate(table.rows[1:], 2):
        numeric = 0
        for cell in row:
            try:
                _number(cell)
                numeric += 1
            except ValueError:
                pass
        if numeric >= max(3, width // 2):
            start = index
            break
    header = table.rows[start - 2]
    def named_column(words: tuple[str, ...], fallback: int) -> int:
        return next((i for i, value in enumerate(header, 1)
                     if any(word in str(value).casefold() for word in words)), fallback)
    ambient = named_column(('ambient', '环境'), width - 1)
    current = named_column(('current', 'amp', '电流'), width)
    temperatures = tuple(i for i in range(1, width + 1)
                         if i not in (ambient, current)
                         and not any(word in str(header[i - 1] if i <= len(header) else '').casefold()
                                     for word in ('scan', 'time', 'date', '序号', '扫描', '时间')))
    per_sample = 4 if len(temperatures) % 4 == 0 else 1
    return DataSelection(start - 1, start, len(table.rows), ambient, current, temperatures, per_sample)
