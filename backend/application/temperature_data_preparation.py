"""Review scanner values and explicit operator selections before numerical analysis."""

from dataclasses import dataclass
from math import isfinite

from backend.domain.temperature_data import DataSelection, WorkbookTable, column_letter
from backend.domain.temperature_rise import Measurement
from backend.application.temperature_channel_layout import ChannelLayout, inspect_channel_layout


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
    retained_current_columns: tuple[int, ...] = ()


def prepare_data(table: WorkbookTable, selection: DataSelection, *, acknowledge_warnings: bool = False) -> PreparedData:
    layout = _validate_selection(table, selection)
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
        if abs(current) < .1:
            current = 0.
        if not isfinite(current) or current < 0:
            issues.append(DataIssue('invalid_current', 'error', number,
                f"Row {number}: current must be finite and nonnegative. Check the selected column and current scale."))
            continue
        measurement = Measurement(number, current, values[1], tuple(values[2:]))
        measurements.append(measurement)
        if current == 0:
            issues.append(DataIssue('zero_current', 'warning', number,
                f"Row {number}: |current| < 0.1 A is treated as unpowered. Review this row; other current columns may still be powered."))
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
    retained = tuple(column for column in layout.current_columns
                     if column not in (selection.current_column, selection.ambient_column, *selection.temperature_columns))
    return PreparedData(tuple(measurements), tuple(issues), ready, retained)


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


def _validate_selection(table: WorkbookTable, selection: DataSelection) -> ChannelLayout:
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
    layout = inspect_channel_layout(table, selection.header_row, selection.start_row, selection.end_row)
    if (selection.temperature_columns == layout.temperature_columns
            and count == layout.thermocouples_per_sample
            and any(len(group.columns) != count for group in layout.sample_groups)):
        raise ValueError('Sample channel counts differ. Explicitly adjust the channel assignments before confirming.')
    return layout


class DataRegionError(ValueError):
    """The workbook is readable, but no unique scanner region can be selected."""


_METADATA_WORDS = ('scan', 'time', 'date', '序号', '扫描', '时间')
_HEADER_WORDS = (*_METADATA_WORDS, 'ambient', 'current', 'amp', '环境', '电流',
                 'tc', 'thermocouple', 'temperature', '温度')


def _is_number(value: object) -> bool:
    try:
        _number(value)
        return True
    except ValueError:
        return False


def _is_header(row: tuple) -> bool:
    # Scanner channel-configuration rows also contain names, but have numeric/Boolean settings.
    if any(isinstance(value, bool) or _is_number(value) for value in row):
        return False
    labels = [str(value).strip().casefold() for value in row
              if isinstance(value, str) and value.strip() and not _is_number(value)]
    if any(label.endswith((':', '：')) for label in labels):
        return False  # Key/value metadata such as "Scan count:" is not a measurement header.
    return len(labels) >= 3 and any(word in label for label in labels for word in _HEADER_WORDS)


def suggest_selection(table: WorkbookTable) -> DataSelection:
    """Locate one labelled scanner block; never replace failed detection with row 2."""
    headers = [index for index, row in enumerate(table.rows, 1) if _is_header(row)]
    if len(headers) != 1 or headers[0] == len(table.rows):
        reason = 'Multiple possible data regions were found.' if len(headers) > 1 else 'No data region could be identified.'
        raise DataRegionError(reason + ' Check the sheet or set the header and data rows manually.')
    header_row = headers[0]
    choice = selection_for_region(table, header_row, header_row + 1, len(table.rows))
    readings = (*choice.temperature_columns, choice.ambient_column, choice.current_column)
    metadata = [column for column, label in enumerate(table.rows[header_row - 1], 1)
                if column not in readings and any(word in str(label).casefold() for word in _METADATA_WORDS)]
    last_record = None
    has_numeric_readings = False
    for row_number in range(choice.start_row, len(table.rows) + 1):
        row = table.rows[row_number - 1]
        values = [row[column - 1] if column <= len(row) else None for column in readings]
        has_numeric_readings |= sum(_is_number(value) for value in values) >= max(3, len(readings) // 2)
        # Keep incomplete records, interruptions and zero-current tails for explicit review.
        if any(value is not None and str(value).strip() for value in values) or any(
            column <= len(row) and row[column - 1] is not None
            and (_is_number(row[column - 1]) or ':' in str(row[column - 1])) for column in metadata
        ):
            last_record = row_number
    if not has_numeric_readings or last_record is None:
        raise DataRegionError('No data region could be identified. Check the sheet or set the header and data rows manually.')
    return selection_for_region(table, header_row, choice.start_row, last_record)


def selection_for_region(table: WorkbookTable, header_row: int, start_row: int, end_row: int) -> DataSelection:
    """Build editable column suggestions from an automatic or operator-selected region."""
    if not 1 <= header_row < start_row <= end_row <= len(table.rows):
        raise ValueError('Choose a header row before the data, and a data range inside the selected sheet.')
    header = table.rows[header_row - 1]
    width = len(header)
    if width < 3:
        raise ValueError('The header needs at least three columns for temperature, ambient and current.')
    layout = inspect_channel_layout(table, header_row, start_row, end_row)
    return DataSelection(header_row, start_row, end_row, layout.ambient_column,
                         layout.current_column, layout.temperature_columns, layout.thermocouples_per_sample)
