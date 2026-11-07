"""Explicit measured quantities; chronology and acceptance are separate facts."""
from decimal import Decimal, InvalidOperation
import re


def number(value):
    if isinstance(value, bool):
        raise ValueError('Boolean cells are not measurements.')
    try:
        result = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f'Unsupported measurement: {value}. Select the source cell and unit explicitly.') from exc
    if not result.is_finite():
        raise ValueError('Measurements must be finite.')
    return result


def display(value):
    return format(value.normalize(), 'f')


def electrical_measurement(measurement, raw, unit, breakdown, voltage, duration):
    raw = '' if raw is None else str(raw).strip()
    match = re.fullmatch(r'(>=|<=|>|<|≥|≤|=)?\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(MΩ|GΩ|Ω|µA|μA|uA|mA|nA)?', raw) if raw else None
    if raw and match is None:
        raise ValueError('Select a numeric electrical cell (an inequality is allowed) and its unit separately.')
    units = {'MΩ': Decimal(1), 'GΩ': Decimal(1000), 'Ω': Decimal('0.000001')} if measurement == 'ir' else {
        'µA': Decimal(1), 'μA': Decimal(1), 'uA': Decimal(1), 'mA': Decimal(1000), 'nA': Decimal('0.001')}
    if unit not in units:
        raise ValueError('Confirm an explicit supported electrical unit.')
    aliases = {'μA': 'µA', 'uA': 'µA'}
    if match and match[3] and aliases.get(match[3], match[3]) != aliases.get(unit, unit):
        raise ValueError('The source cell unit conflicts with the selected unit; review the original without rewriting it.')
    value = number(match[2]) * units[unit] if match else None
    if value is not None and value < 0:
        raise ValueError('Negative insulation resistance or leakage requires source review.')
    marker = str(breakdown or '').strip().casefold()
    states = {'': 'not_recorded', 'no breakdown': 'no_breakdown', '未击穿': 'no_breakdown',
              'breakdown': 'breakdown', '击穿': 'breakdown'}
    if measurement == 'dwv' and marker not in states:
        raise ValueError('DWV breakdown must explicitly say breakdown or no breakdown; Pass alone is not that observation.')
    conditions = {}
    for name, supplied in (('voltage_v', voltage), ('duration_s', duration)):
        value_condition = number(supplied) if supplied is not None and str(supplied).strip() else None
        if value_condition is not None and value_condition <= 0:
            raise ValueError('Test voltage and duration must be positive when recorded.')
        conditions[name] = display(value_condition) if value_condition is not None else None
    return {'measurement': measurement, 'raw_value': raw, 'source_unit': unit,
        'comparator': (match[1] or '=') if match else None,
        'value': display(value) if value is not None else None, 'unit': 'MΩ' if measurement == 'ir' else 'µA',
        'breakdown': states.get(marker, 'not_recorded') if measurement == 'dwv' else 'not_applicable',
        'missing': value is None or (measurement == 'dwv' and states[marker] == 'not_recorded') or any(v is None for v in conditions.values()),
        **conditions}


def resistance_measurement(stage, quantity, raw, unit, baseline):
    if not stage.strip():
        raise ValueError('Confirm the test stage separately from absolute R or ΔR.')
    if unit not in {'mΩ', 'Ω'} or quantity not in {'absolute', 'delta', 'delta_from_absolute'}:
        raise ValueError('Confirm the resistance quantity and unit.')
    factor = Decimal(1000) if unit == 'Ω' else Decimal(1)
    raw = '' if raw is None else raw
    value = number(raw) * factor if str(raw).strip() else None
    if value is not None and quantity != 'delta' and value < 0:
        raise ValueError('Absolute resistance cannot be negative.')
    reference = None
    if quantity == 'delta_from_absolute':
        if baseline is None or not str(baseline).strip():
            raise ValueError('Select the corresponding absolute baseline before computing ΔR.')
        reference = number(baseline) * factor
        if reference < 0:
            raise ValueError('The absolute baseline cannot be negative.')
        if value is not None:
            value -= reference
    return {'stage': stage, 'quantity': 'delta' if quantity != 'absolute' else 'absolute',
        'input_quantity': quantity, 'raw_value': str(raw), 'source_unit': unit,
        'value': display(value) if value is not None else None, 'unit': 'mΩ',
        'baseline_mohm': display(reference) if reference is not None else None, 'missing': value is None}
