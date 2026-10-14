import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';
import { sampleGroups } from './sampleGroups';

export function columnLetter(index: number): string {
  let value = '';
  while (index > 0) { index -= 1; value = String.fromCharCode(65 + index % 26) + value; index = Math.floor(index / 26); }
  return value;
}

export function sourceColumns(table: WorkbookTable, headerRow: number) {
  const width = table.rows.reduce((maximum, row) => Math.max(maximum, row.length), 0);
  return Array.from({ length: width }, (_, index) => ({ id: index + 1,
    label: `${columnLetter(index + 1)} — ${table.rows[headerRow - 1]?.[index] ?? '(No Header)'}` }));
}

export type SourceColumnKind = 'temperature' | 'current' | 'source';
export const SCANNER_UNIT_SUFFIX = /\s*[（(]\s*(?:°?C|℃|VDC|V|m?A)\s*[）)]\s*$/i;

export function sourceColumnKind(table: WorkbookTable, selection: DataSelection, column: number, layout?: ChannelLayout | null): SourceColumnKind {
  if (column <= 2) return 'source';
  const header = String(table.rows[selection.header_row - 1]?.[column - 1] ?? '');
  if (/[（(]\s*(?:°?C|℃)\s*[）)]\s*$/i.test(header)) return 'temperature';
  if (/[（(]\s*(?:VDC|V|m?A)\s*[）)]\s*$/i.test(header)) return 'current';
  if (/ambient|环境|\bTC\d*\b|thermocouple|temperature|温度/i.test(header)) return 'temperature';
  // Keep older, untagged workbooks usable with their confirmed/imported role suggestions.
  if (column === selection.current_column || layout?.current_columns.includes(column)) return 'current';
  if (column === selection.ambient_column || selection.temperature_columns.includes(column)
    || layout?.temperature_columns.includes(column)) return 'temperature';
  return 'source';
}

export function isTemperatureColumn(table: WorkbookTable, selection: DataSelection, column: number, layout?: ChannelLayout | null) {
  return column > 2 && column !== selection.ambient_column && column !== selection.current_column
    && sourceColumnKind(table, selection, column, layout) !== 'current'
    && (selection.temperature_columns.includes(column) || layout?.temperature_columns.includes(column)
      || !/scan|time|date|序号|扫描|时间/i.test(String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')));
}

export function incompleteSampleGroups(selection: DataSelection, layout?: ChannelLayout | null) {
  const count = selection.thermocouples_per_sample;
  if (!Number.isInteger(count) || count < 1 || !selection.temperature_columns.length
    || selection.temperature_columns.length % count !== 0) return true;
  const groups = sampleGroups(selection, layout);
  if (selection.sample_count != null && (!Number.isInteger(selection.sample_count) || selection.sample_count < 1
    || selection.sample_count > 254 || groups.length !== selection.sample_count)) return true;
  return groups.some(group => group.length !== count)
    || groups.flat().join(',') !== selection.temperature_columns.join(',');
}
