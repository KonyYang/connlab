import { afterEach, expect, it, vi } from 'vitest';
import { downloadTemperatureWorkbook } from './temperature';

afterEach(() => vi.unstubAllGlobals());

it('sends the Excel download request as JSON rather than text', async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(new Blob(['xlsx']), {
    headers: { 'Content-Disposition': "attachment; filename*=UTF-8''curves.xlsx" },
  }));
  vi.stubGlobal('fetch', fetch);
  const result = await downloadTemperatureWorkbook({
    table: { file_name: 'scanner.xlsx', sheet_names: ['Data'], sheet_name: 'Data', rows: [] },
    selection: { header_row: 1, start_row: 2, end_row: 3, ambient_column: 2, current_column: 3,
      temperature_columns: [1], thermocouples_per_sample: 1, excluded_rows: [], current_multiplier: 1 },
    acknowledge_warnings: false, zero_intercept: true, maximum_coefficients: null,
    average_coefficients: null, target_rise: null, derating: null,
  });
  expect(new Headers(fetch.mock.calls[0][1].headers).get('Content-Type')).toBe('application/json');
  expect(result.fileName).toBe('curves.xlsx');
});
