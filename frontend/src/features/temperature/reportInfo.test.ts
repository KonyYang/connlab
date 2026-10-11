import { describe, expect, it } from 'vitest';
import { reportHumidityIssue, sourceReportDefaults } from './reportInfo';
import type { DataSelection, WorkbookTable } from '../../api/temperature';

const table: WorkbookTable = { file_name: 'source.xlsx', sheet_names: ['Data'], sheet_name: 'Data', rows: [
  ['Scan', '时间', 'TC', 'Ambient', 'Current'],
  [1, '2026/9/10 17:10:16:391', 30, '22.04', 10],
  [2, '2026-09-11T09:00:00', 35, 23.51, 20],
  [3, '2026/9/12 10:00:00', 40, 99, 30],
] };
const selection: DataSelection = { header_row: 1, start_row: 2, end_row: 4, temperature_columns: [3],
  thermocouples_per_sample: 1, ambient_column: 4, current_column: 5, current_multiplier: 1, excluded_rows: [4] };

describe('report suggestions from retained source readings', () => {
  it('uses retained row dates and temperature range, without inventing humidity', () => {
    expect(sourceReportDefaults(table, selection)).toEqual({ test_date: '2026-09-10 ~ 2026-09-11', ambient_temperature: '22.0–23.5' });
    expect(sourceReportDefaults(table, { ...selection, excluded_rows: [3, 4] })).toEqual({ test_date: '2026-09-10', ambient_temperature: '22.0' });
  });
  it.each(['18:00', '2026-02-30 08:00', '09/10/2026 08:00', ''])('leaves unknown or ambiguous dates for manual entry: %s', value => {
    const partial = { ...table, rows: [table.rows[0], [1, value, 30, 22, 10], ...table.rows.slice(2)] };
    expect(sourceReportDefaults(partial, selection).test_date).toBe('');
  });
  it('clears suggestions when all readings are excluded', () => {
    expect(sourceReportDefaults(table, { ...selection, excluded_rows: [2, 3, 4] })).toEqual({ test_date: '', ambient_temperature: '' });
  });
  it('never treats empty, boolean or nonfinite temperature cells as zero', () => {
    const invalid = { ...table, rows: [table.rows[0], [1, '2026-09-10', 30, false, 10], [2, '2026-09-10', 30, '', 10]] };
    expect(sourceReportDefaults(invalid, { ...selection, end_row: 3, excluded_rows: [] }).ambient_temperature).toBe('');
  });
  it.each(['-1', '101', 'Infinity', 'nan'])('rejects invalid report humidity: %s', value => {
    expect(reportHumidityIssue(value)).toContain('0 and 100');
  });
  it.each(['', '0', '100', '60.9'])('permits blank or physical humidity: %s', value => {
    expect(reportHumidityIssue(value)).toBeNull();
  });
});
