import type { DataSelection, TemperatureReportMetadata, WorkbookTable } from '../../api/temperature';

export type ReportInfoFields = Omit<TemperatureReportMetadata, 'relative_humidity'> & { relative_humidity: string };
export const emptyReportInfo: ReportInfoFields = {
  ltr_number: '', tested_by: '', test_date: '', ambient_temperature: '', relative_humidity: '',
  equipment_id: '', test_condition: '', remark: '',
};

function recordedDate(value: unknown): string | null {
  const match = String(value ?? '').trim().match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?=$|[T\s])/);
  if (!match) return null;
  const [, year, month, day] = match;
  const date = new Date(`${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T00:00:00Z`);
  if (!Number.isFinite(date.getTime()) || date.getUTCMonth() + 1 !== Number(month) || date.getUTCDate() !== Number(day)) return null;
  return date.toISOString().slice(0, 10);
}

export function sourceReportDefaults(table: WorkbookTable | null, selection: DataSelection | null): Partial<ReportInfoFields> {
  if (!table || !selection) return {};
  const headers = table.rows[selection.header_row - 1] ?? [];
  const timeColumn = headers.findIndex(value => /^(time|date|date\s*time|timestamp|时间|日期|日期时间)$/i.test(String(value ?? '').trim()));
  const excluded = new Set(selection.excluded_rows);
  const dates = new Set<string>();
  let allDatesKnown = timeColumn >= 0;
  let minimum = Infinity, maximum = -Infinity;
  for (let row = selection.start_row; row <= selection.end_row; row++) {
    if (excluded.has(row)) continue;
    const values = table.rows[row - 1] ?? [];
    const date = recordedDate(values[timeColumn]);
    if (date) dates.add(date);
    else allDatesKnown = false;
    const raw = values[selection.ambient_column - 1];
    const reading = typeof raw === 'number' || typeof raw === 'string' && raw.trim() ? Number(raw) : NaN;
    if (Number.isFinite(reading)) { minimum = Math.min(minimum, reading); maximum = Math.max(maximum, reading); }
  }
  const orderedDates = [...dates].sort();
  const start = orderedDates[0], end = orderedDates.at(-1);
  const low = minimum.toFixed(1), high = maximum.toFixed(1);
  return {
    test_date: allDatesKnown && start ? start === end ? start : `${start} ~ ${end}` : '',
    ambient_temperature: Number.isFinite(minimum) ? low === high ? low : `${low}–${high}` : '',
  };
}

export function reportHumidityIssue(value: string): string | null {
  if (!value.trim()) return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 && number <= 100 ? null : 'Enter relative humidity between 0 and 100 %RH.';
}

export function reportMetadata(fields: ReportInfoFields): TemperatureReportMetadata {
  const issue = reportHumidityIssue(fields.relative_humidity);
  if (issue) throw new Error(issue);
  return { ...fields, relative_humidity: fields.relative_humidity.trim() ? Number(fields.relative_humidity) : null };
}
