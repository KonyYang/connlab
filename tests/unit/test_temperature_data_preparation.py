from copy import deepcopy

import pytest

from backend.application.temperature_data_preparation import DataSelection, prepare_data, suggest_selection
from backend.domain.temperature_data import WorkbookTable


def table():
    return WorkbookTable('scanner.xlsx', ('Data',), 'Data', (
        ('Current', 'Broken', 'Ambient', 'Other', 'TC1', 'Spare'),
        (10, None, 20, 999, 24, 25), (10, None, 20, 999, 24, 25),
        (0, None, 20, 999, 20, 20), (20, None, 21, 999, 29, 30),
        (20, None, 21, 999, 29, 30), (0, None, 21, 999, 21, 21),
    ))


def selection(**changes):
    values = dict(header_row=1, start_row=2, end_row=7, ambient_column=3, current_column=1,
                  temperature_columns=(5, 6), thermocouples_per_sample=2,
                  excluded_rows=(), current_multiplier=1.)
    return DataSelection(**(values | changes))


def test_spare_channel_and_arbitrary_ambient_current_order_are_explicit_and_non_destructive():
    source = table()
    original = deepcopy(source)
    result = prepare_data(source, selection(excluded_rows=(4, 7)))
    assert result.ready
    assert result.issues == ()
    assert [row.source_row for row in result.measurements] == [2, 3, 5, 6]
    assert result.measurements[0].temperatures == (24, 25)
    assert source == original
    reordered = prepare_data(source, selection(temperature_columns=(6, 5), excluded_rows=(4, 7)))
    assert reordered.measurements[0].temperatures == (25, 24)


def test_suspicious_rows_are_retained_until_user_excludes_them():
    result = prepare_data(table(), selection())
    assert [row.source_row for row in result.measurements] == [2, 3, 4, 5, 6, 7]
    assert {issue.source_row for issue in result.issues if issue.code == 'zero_current'} == {4, 7}
    assert not result.ready
    assert prepare_data(table(), selection(), acknowledge_warnings=True).ready
    excluded = prepare_data(table(), selection(excluded_rows=(4, 7)))
    restored = prepare_data(table(), selection())
    assert len(excluded.measurements) == 4
    assert len(restored.measurements) == 6


def test_required_missing_data_cannot_be_acknowledged_away():
    result = prepare_data(table(), selection(temperature_columns=(5, 2)), acknowledge_warnings=True)
    assert not result.ready
    assert any(issue.severity == 'error' and issue.source_row == 2 for issue in result.issues)


@pytest.mark.parametrize('changes', [
    {'temperature_columns': (5, 5)}, {'temperature_columns': (5, 3)},
    {'temperature_columns': (5,)}, {'current_multiplier': 0}, {'start_row': 0},
    {'end_row': 9}, {'excluded_rows': (99,)}, {'ambient_column': 1},
])
def test_invalid_mapping_or_range_is_rejected(changes):
    with pytest.raises(ValueError):
        prepare_data(table(), selection(**changes))
def test_suggested_mapping_excludes_chinese_scanner_metadata():
    from backend.application.temperature_data_preparation import suggest_selection
    table = WorkbookTable('scanner.xlsm', ('Initial Data',), 'Initial Data', (
        ('扫描', '时间', 'TC1', 'TC2', 'TC3', 'TC4', 'Ambient T', 'Current (VDC)'),
        (1, '17:17', 25, 26, 27, 28, 20, 10),
    ))
    selection = suggest_selection(table)
    assert selection.temperature_columns == (3, 4, 5, 6)
    assert selection.thermocouples_per_sample == 4
    assert selection.current_multiplier == 1


def test_automatic_region_ignores_preamble_and_footer_but_keeps_suspicious_rows():
    source = WorkbookTable('scanner.xlsx', ('Data',), 'Data', (
        ('Scanner settings',),
        (101, 'Ambient T', 'Type T', 'C', 'Temp (Type T)#Auto', False, 1, 0),
        ('Scan count:', 'Start condition:', 'Immediate', 'Stop condition:', 'User stop'),
        ('扫描', '时间', 'TC1', 'Ambient', 'Current'),
        (1, '17:17', None, 20, 10), (2, '17:18', 25, 20, 10),
        (), (3, '17:19', 25, 20, 0),
        (4, '17:20', None, None, None), ('End of acquisition',), (),
    ))
    choice = suggest_selection(source)
    assert (choice.header_row, choice.start_row, choice.end_row) == (4, 5, 9)
    assert choice.excluded_rows == ()
    review = prepare_data(source, choice)
    assert any(issue.source_row == 5 and issue.code == 'invalid_reading' for issue in review.issues)
    assert any(issue.source_row == 8 and issue.code == 'zero_current' for issue in review.issues)
    assert not review.ready


@pytest.mark.parametrize('rows', [
    (('Notes', 'Only text', 'No readings'), ('more', 'notes', 'here')),
    (('TC1', 'Ambient', 'Current'), ('missing', None, None)),
    ((25, 20, 10), (26, 20, 10)),
    (('TC1', 'Ambient', 'Current'), (25, 20, 10), (),
     ('TC1', 'Ambient', 'Current'), (26, 20, 20)),
    (('TC1', 'Ambient', 'Current'), (25, 20, 10),
     ('TC1 error', 'Ambient error', 'Current error')),
    (('TC1', 'Ambient', 'Current'),
     ('TC1 error', 'Ambient error', 'Current error'), (25, 20, 10)),
])
def test_automatic_region_rejects_missing_or_ambiguous_data_instead_of_guessing_row_two(rows):
    source = WorkbookTable('scanner.xlsx', ('Data',), 'Data', rows)
    with pytest.raises(ValueError, match='data region'):
        suggest_selection(source)
