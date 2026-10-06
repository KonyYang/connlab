"""Suggest scanner column roles and sample groups without editing source values."""

from collections import Counter
from dataclasses import dataclass
from math import isfinite
import re

from backend.domain.temperature_data import WorkbookTable


@dataclass(frozen=True)
class SampleChannels:
    sample_id: str
    columns: tuple[int, ...]


@dataclass(frozen=True)
class ChannelLayout:
    temperature_columns: tuple[int, ...]
    current_columns: tuple[int, ...]
    stable_current_columns: tuple[int, ...]
    sample_groups: tuple[SampleChannels, ...]
    thermocouples_per_sample: int
    ambient_column: int
    current_column: int
    issues: tuple[str, ...]
    zero_intercept_default: bool
    current_issue: str | None = None


def inspect_channel_layout(table: WorkbookTable, header_row: int, start_row: int, end_row: int) -> ChannelLayout:
    header = table.rows[header_row - 1]
    labels = {index: str(value or '').strip() for index, value in enumerate(header, 1)}
    labelled = {index: label for index, label in labels.items() if label}
    width = max(labelled, default=len(header))
    ambient = next((index for index, label in labelled.items()
                    if re.search(r'ambient|环境', label, re.I)), max(1, width - 1))
    currents = tuple(index for index, label in labelled.items() if index != ambient
                     and re.search(r'current|电流|\bamps?\b|\bVDC\b|\((?:m?A)\)', label, re.I))
    stable = tuple(column for column in currents if _stable_energized_column(table, column, start_row, end_row))
    variable = [column for column in currents if column not in stable]
    named_current = next((index for index in currents if re.search(r'current|电流|\bamps?\b', labels[index], re.I)), None)
    current = variable[0] if len(variable) == 1 else named_current or (currents[-1] if currents else width)
    candidates = tuple(index for index, label in labelled.items()
                       if index not in (ambient, current) and index not in currents
                       and not re.search(r'scan|time|date|序号|扫描|时间', label, re.I))
    temperature_labels = tuple(index for index in candidates
                               if re.search(r'\((?:°?C|℃)\)|\bTC\d*\b|thermocouple|温度', labels[index], re.I))
    temperatures = temperature_labels or candidates
    groups: dict[str, list[int]] = {}
    unassigned = []
    for column in temperatures:
        match = re.search(r'(?:<\s*|^)\s*(\d+)\s*[_#-]', labels[column])
        if match:
            groups.setdefault(match[1], []).append(column)
        else:
            unassigned.append(column)
    issues = []
    if groups:
        # Unnamed spare probes stay available for replacement, not silently added as samples.
        temperatures = tuple(column for columns in groups.values() for column in columns)
        count = Counter(map(len, groups.values())).most_common(1)[0][0]
        if any(len(columns) != count for columns in groups.values()):
            issues.append('Sample channel counts differ. Replace, exclude or reassign channels before confirming.')
        if unassigned:
            issues.append('Additional temperature channels have no sample number. Use them as replacements or add them explicitly if needed.')
    else:
        count = 4 if temperatures and len(temperatures) % 4 == 0 else 1
    current_issue = ('Multiple varying electrical columns were found. Confirm the current column used for this curve.'
                     if len(variable) > 1 else None)
    return ChannelLayout(temperatures, currents, stable,
                         tuple(SampleChannels(sample, tuple(columns)) for sample, columns in groups.items()),
                         count, ambient, current, tuple(issues), not any(column != current for column in stable), current_issue)


def _stable_energized_column(table: WorkbookTable, column: int, start: int, end: int) -> bool:
    readings = []
    for row in table.rows[start - 1:end]:
        value = row[column - 1] if column <= len(row) else None
        if isinstance(value, bool) or value is None:
            return False
        try:
            number = float(value)
        except (ValueError, TypeError):
            return False
        if not isfinite(number) or number < .1:
            return False
        readings.append(number)
    # Require sustained powered readings within the existing 1% current-stability rule.
    return len(readings) >= 2 and (max(readings) - min(readings)) / min(readings) <= .01
