import { describe, expect, it } from 'vitest';
import type { DataIssue, WorkbookTable } from '../../api/temperature';
import { reviewMessages } from './sourceScan';

describe('compact scan review messages', () => {
  const suffix = ': current rounds to 0 at 0 decimal places (this current column).';
  it.each([
    { scans: [51, 52, 53], labels: ['Scan 51~53'] },
    { scans: [51, 53], labels: ['Scan 51', 'Scan 53'] },
    { scans: [51, 51], labels: ['Scan 51', 'Scan 51'] },
    { scans: [53, 52], labels: ['Scan 53', 'Scan 52'] },
    { scans: ['0051', '0052'], labels: ['Scan 0051~0052'] },
    { scans: [null, 52], labels: ['Scan unavailable', 'Scan 52'] },
    { scans: ['test-51', 'test-52'], labels: ['Scan test-51', 'Scan test-52'] },
    { scans: [51.1, 52.1], labels: ['Scan 51.1', 'Scan 52.1'] },
  ])('uses actual scan IDs and merges only an ascending consecutive run: $scans', ({ scans, labels }) => {
    const table: WorkbookTable = { file_name: 'scanner.csv', sheet_name: 'Data', sheet_names: ['Data'],
      rows: [['Scan'], ...scans.map(scan => [scan])] };
    const issues: DataIssue[] = scans.map((_, index) => ({ code: 'zero_current', severity: 'warning',
      source_row: index + 2, message: `Row ${index + 2}: current is zero.` }));
    const original = structuredClone(issues);
    expect(reviewMessages(table, issues)).toEqual(labels.map(label => ({ severity: 'warning', message: label + suffix })));
    expect(issues).toEqual(original);
  });

  it('preserves intervening errors and does not merge across unreported source rows', () => {
    const table: WorkbookTable = { file_name: 'scanner.csv', sheet_name: 'Data', sheet_names: ['Data'],
      rows: [['Scan'], [51], [52], [53], [54]] };
    const zero = (source_row: number): DataIssue => ({ code: 'zero_current', severity: 'warning', source_row, message: 'Unpowered' });
    expect(reviewMessages(table, [zero(2), { code: 'invalid_reading', severity: 'error', source_row: 3,
      message: 'Row 3: missing reading.' }, zero(3), zero(5)])).toEqual([
      { severity: 'warning', message: 'Scan 51' + suffix },
      { severity: 'error', message: 'Scan 52: missing reading.' },
      { severity: 'warning', message: 'Scan 52' + suffix },
      { severity: 'warning', message: 'Scan 54' + suffix },
    ]);
    expect(reviewMessages(null, [{ code: 'zero_current', severity: 'error', source_row: 2, message: 'Unexpected current error.' }]))
      .toEqual([{ severity: 'error', message: 'Unexpected current error.' }]);
  });
});
