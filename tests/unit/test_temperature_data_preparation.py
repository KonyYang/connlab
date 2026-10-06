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


def grouped_scanner():
    labels = ['扫描', '时间']
    # Hardware channel IDs need not encode the sample number; names do.
    for sample, first in ((1, 101), (2, 111), (3, 201)):
        labels.extend(f'{first + index} <{sample}_T{index + 1}> (C)' for index in range(10))
    labels.extend(['313 <ambient> (C)', '315 <High Power> (VDC)',
                   '316 <Low Power> (VDC)', '317 <A4_B4 Signal> (VDC)', '318 <Others Signal> (VDC)'])
    rows = [tuple(labels)]
    for index, current in enumerate((.009999, .011427, 10, 10.01, 20, 20.01), 1):
        rows.append((index, '17:17', *((25 + sample) for sample in range(30)),
                     20, 125 + index * .001, current, 3.001, 1.02))
    return WorkbookTable('scanner.csv', ('Initial Data',), 'Initial Data', tuple(rows))


def test_sample_names_group_three_samples_and_choose_only_the_variable_current():
    source = grouped_scanner()
    choice = suggest_selection(source)
    assert choice.temperature_columns == tuple(range(3, 33))
    assert choice.thermocouples_per_sample == 10
    assert choice.ambient_column == 33
    assert choice.current_column == 35
    assert choice.excluded_rows == ()
    assert len(source.rows[0]) == 37  # Other currents remain in the source.


def test_near_zero_current_is_reviewed_as_unpowered_without_deleting_or_rounding_source():
    source = grouped_scanner()
    original = deepcopy(source)
    choice = DataSelection(1, 2, 7, 33, 35, tuple(range(3, 33)), 10)
    review = prepare_data(source, choice)
    assert [row.current for row in review.measurements[:3]] == [0, 0, 10]
    assert {issue.source_row for issue in review.issues if issue.code == 'zero_current'} == {2, 3}
    assert not review.ready
    assert len(review.measurements) == 6
    assert source == original


@pytest.mark.parametrize('current, expected', [(-.099, 0), (.099, 0), (.1, .1), (.100001, .100001)])
def test_unpowered_threshold_uses_absolute_current_and_keeps_boundary_values(current, expected):
    source = WorkbookTable('data.xlsx', ('Data',), 'Data', (('TC1', 'Ambient', 'Current'), (25, 20, current)))
    review = prepare_data(source, DataSelection(1, 2, 2, 2, 3, (1,), 1))
    assert review.measurements[0].current == expected
    assert any(issue.code == 'zero_current' for issue in review.issues) == (expected == 0)


def test_unequal_named_groups_cannot_silently_be_split_even_when_total_is_divisible():
    source = WorkbookTable('groups.xlsx', ('Data',), 'Data', (
        ('Scan', '101 <1_A> (C)', '102 <1_B> (C)', '111 <2_A> (C)',
         '201 <3_A> (C)', '202 <3_B> (C)', '203 <3_C> (C)', 'Ambient', 'Current'),
        (1, 25, 26, 25, 25, 26, 27, 20, 10), (2, 25, 26, 25, 25, 26, 27, 20, 10),
    ))
    choice = suggest_selection(source)
    assert choice.thermocouples_per_sample == 2
    with pytest.raises(ValueError, match='Sample channel counts differ'):
        prepare_data(source, choice, acknowledge_warnings=True)


def test_stable_current_default_is_not_triggered_by_zero_or_missing_auxiliary_readings():
    from backend.application.temperature_channel_layout import inspect_channel_layout
    source = WorkbookTable('data.xlsx', ('Data',), 'Data', (
        ('Scan', 'TC1', 'Ambient', 'Current', 'Aux current'),
        (1, 25, 20, 10, 0), (2, 30, 20, 20, 0),
    ))
    layout = inspect_channel_layout(source, 1, 2, 3)
    assert layout.stable_current_columns == ()
    assert layout.zero_intercept_default is True


def test_sample_names_group_noncontiguous_source_channels_and_keep_spare_available():
    source = WorkbookTable('data.xlsx', ('Data',), 'Data', (
        ('Scan', '101 <1_A> (C)', '201 <2_A> (C)', '102 <1_B> (C)',
         '202 <2_B> (C)', 'Ambient', 'Current', '999 <spare> (C)'),
        (1, 25, 26, 27, 28, 20, 10, 29), (2, 25, 26, 27, 28, 20, 10, 29),
    ))
    choice = suggest_selection(source)
    assert choice.temperature_columns == (2, 4, 3, 5)
    assert choice.thermocouples_per_sample == 2
    assert len(source.rows[0]) == 8


def test_ambiguous_current_warning_is_separate_from_sample_mapping_issues():
    from backend.application.temperature_channel_layout import inspect_channel_layout
    source = WorkbookTable('data.xlsx', ('Data',), 'Data', (
        ('1_A (C)', 'Ambient', 'Current', 'Aux current'),
        (25, 20, 10, 5), (30, 20, 20, 7),
    ))
    layout = inspect_channel_layout(source, 1, 2, 3)
    assert layout.issues == ()
    assert 'Confirm the current column' in layout.current_issue
