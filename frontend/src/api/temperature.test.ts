import { afterEach, expect, it, vi } from 'vitest';
import { downloadTemperatureWorkbook, importTemperatureWorkbook } from './temperature';

afterEach(() => vi.unstubAllGlobals());

it('uploads manual recovery rows and sheet as multipart without changing the source file', async () => {
  const response = { table: { rows: [['Probe', 'Room', 'Supply'], [25, 20, 10]] }, selection: null, region_issue: 'Check rows.' };
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { headers: { 'Content-Type': 'application/json' } }));
  vi.stubGlobal('fetch', fetch);
  const file = new File(['original source'], 'scanner.xlsx');
  expect(await importTemperatureWorkbook(file, 'Data', { header_row: 1, start_row: 2, end_row: 5 })).toEqual(response);
  const options = fetch.mock.calls[0][1];
  expect(options.body).toBeInstanceOf(FormData);
  expect(options.body.get('file').name).toBe(file.name);
  expect(options.body.get('sheet_name')).toBe('Data');
  expect(options.body.get('header_row')).toBe('1');
  expect(options.body.get('start_row')).toBe('2');
  expect(options.body.get('end_row')).toBe('5');
  expect(new Headers(options.headers).get('Content-Type')).toBeNull();
});

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
