"""Physical meaning is independent from report layout and result chronology."""
import pytest

from backend.domain.report_result_semantics import electrical_measurement, resistance_measurement


def test_ir_comparison_and_unit_are_preserved_without_inventing_a_limit():
    result = electrical_measurement('ir', '>1', 'GΩ', '', '500', '60')
    assert result['raw_value'] == '>1'
    assert result['comparator'] == '>' and result['value'] == '1000'
    assert result['unit'] == 'MΩ' and result['missing'] is False
    assert 'outcome' not in result
    embedded = electrical_measurement('ir', '>1000 MΩ', 'MΩ', '', '500', '60')
    assert embedded['value'] == '1000' and embedded['raw_value'] == '>1000 MΩ'
    with pytest.raises(ValueError, match='conflicts'):
        electrical_measurement('ir', '>1000 MΩ', 'GΩ', '', '500', '60')


def test_missing_electrical_readings_are_neither_zero_nor_no_breakdown():
    result = electrical_measurement('dwv', '', 'µA', '', '', '')
    assert result['value'] is None and result['breakdown'] == 'not_recorded'
    assert result['missing'] is True
    result = electrical_measurement('dwv', '1', 'mA', 'No breakdown', '4000', '60')
    assert result['value'] == '1000' and result['unit'] == 'µA'
    assert result['breakdown'] == 'no_breakdown'
    with pytest.raises(ValueError, match='positive'):
        electrical_measurement('dwv', '1', 'µA', 'No breakdown', 0, '60')


def test_stage_and_quantity_are_independent_and_delta_requires_selected_baseline():
    final = resistance_measurement('Final', 'absolute', '2.4', 'mΩ', '')
    assert final['stage'] == 'Final' and final['value'] == '2.4' and final['quantity'] == 'absolute'
    with pytest.raises(ValueError, match='baseline'):
        resistance_measurement('Post humidity', 'delta_from_absolute', '2.4', 'mΩ', '')
    delta = resistance_measurement('Post humidity', 'delta_from_absolute', '2.4', 'mΩ', '1.1')
    assert delta['value'] == '1.3' and delta['quantity'] == 'delta'
    direct = resistance_measurement('Final', 'delta', '-0.2', 'mΩ', '')
    assert direct['value'] == '-0.2'
    assert resistance_measurement('Initial', 'absolute', 0, 'mΩ', '')['value'] == '0'
