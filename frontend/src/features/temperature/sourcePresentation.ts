import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';
import { columnLetter, SCANNER_UNIT_SUFFIX, sourceColumnKind, sourceColumns, type SourceColumnKind } from './sourceColumns';

type SourceValue = WorkbookTable['rows'][number][number];

export function formatSourceReading(value: SourceValue, kind: SourceColumnKind): string {
  const text = String(value ?? '');
  if (kind === 'source' || !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text.trim())) return text;
  const number = Number(text);
  if (!Number.isFinite(number)) return text;
  const rounded = number.toFixed(kind === 'temperature' ? 1 : 2);
  return /^-0\.0+$/.test(rounded) ? rounded.slice(1) : rounded;
}

export function sourceColumnOptions(table: WorkbookTable, selection: DataSelection, layout?: ChannelLayout | null) {
  return sourceColumns(table, selection.header_row).map(column => {
    const original = String(table.rows[selection.header_row - 1]?.[column.id - 1] ?? '');
    const clean = original.replace(SCANNER_UNIT_SUFFIX, '').trim();
    const parts = clean.match(/^(\d+)\s*<([^>]+)>\s*(.*)$/);
    const heading = parts ? [parts[1], `${parts[2]} ${parts[3]}`.trim()] : [clean];
    return { id: column.id, original, heading,
      label: `${columnLetter(column.id)} — ${heading.join(' ') || '(No Header)'}`,
      kind: sourceColumnKind(table, selection, column.id, layout) };
  });
}

// Estimate the displayed glyph widths once per imported data/role change, not on scroll or click.
// A small font allowance keeps full readings visible across Windows sans-serif fallback fonts.
function textWidth(text: string): number {
  let width = 0;
  for (const character of text) width += /[^\x00-\xff]/.test(character) ? 14 : /[ilI.,: ]/.test(character) ? 4.5 : 8;
  return Math.ceil(width);
}

export function sourcePresentation(table: WorkbookTable, selection: DataSelection, layout?: ChannelLayout | null) {
  return sourceColumnOptions(table, selection, layout).map(column => {
    let width = Math.max(column.id <= 2 ? 36 : 56, ...column.heading.map(text => textWidth(text) + 16));
    for (let row = selection.start_row; row <= selection.end_row; row++) {
      width = Math.max(width, textWidth(formatSourceReading(table.rows[row - 1]?.[column.id - 1] ?? null, column.kind)) + 16);
    }
    return { ...column, width };
  });
}
