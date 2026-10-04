import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as api from '../api/temperature';
import { TemperatureRisePage } from './TemperatureRisePage';

vi.mock('../api/temperature', () => ({
  importTemperatureWorkbook: vi.fn(), prepareTemperatureData: vi.fn(), analyzeTemperatureData: vi.fn(),
  calculateTemperatureCurrent: vi.fn(), generateTemperatureDerating: vi.fn(), downloadTemperatureWorkbook: vi.fn(),
}));
const imported = {
  table: { file_name: 'scanner.xlsx', sheet_names: ['Data'], sheet_name: 'Data', rows: [
    ['Scan', 'TC1', 'TC2', 'Ambient', 'Current', 'Spare'],
    [1, 24, 25, 20, 10, 26], [2, 24, 25, 20, 10, 26], [3, 29, 30, 20, 20, 31], [4, 29, 30, 20, 20, 31],
  ] },
  selection: { header_row: 1, start_row: 2, end_row: 5, ambient_column: 4, current_column: 5,
    temperature_columns: [2, 3], thermocouples_per_sample: 2, excluded_rows: [], current_multiplier: 1 },
};
const coefficients = { a: .01, b: .2, c: 0 };
const analysis: api.TemperatureAnalysis = {
  points: [{ source_row: null, current: 0, maximum: 0, average: 0, rises: [0, 0], sample_maxima: [0] },
    { source_row: 3, current: 10, maximum: 5, average: 5, rises: [4, 5], sample_maxima: [5] },
    { source_row: 5, current: 20, maximum: 10, average: 10, rises: [9, 10], sample_maxima: [10] }],
  maximum_fit: { coefficients, fitted_coefficients: coefficients, r_squared: .999 },
  average_fit: { coefficients, fitted_coefficients: coefficients, r_squared: .999 },
  zero_intercept: true, thermocouples_per_sample: 2,
};

async function upload() {
  fireEvent.change(screen.getByLabelText('Excel File'), { target: { files: [new File(['x'], 'scanner.xlsx')] } });
  await screen.findByRole('button', { name: 'Confirm Data' });
}

describe('temperature preparation and calculation workflow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue(structuredClone(imported));
    vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [] });
    vi.mocked(api.analyzeTemperatureData).mockResolvedValue(analysis);
    vi.mocked(api.calculateTemperatureCurrent).mockResolvedValue({ current: 30 });
  });

  it('requires confirmation, supports replacement and row restoration, and invalidates downstream results', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    await user.selectOptions(screen.getByLabelText('Sample 1 / TC 2'), '6');
    await user.click(screen.getByLabelText('Select Row 2'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected Rows' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection).toMatchObject({
      temperature_columns: [2, 6], excluded_rows: [2],
    });
    await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByRole('button', { name: 'Get Coefficients' }));
    await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
    expect((await screen.findByLabelText('Calculated Current')).textContent).toContain('30.00 A');
    await user.click(screen.getByRole('button', { name: 'Restore All Rows' }));
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('keeps flagged readings until an explicit review choice', async () => {
    const user = userEvent.setup();
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [],
      issues: [{ code: 'zero_current', severity: 'warning', source_row: 2, message: 'Row 2: current is zero.' }] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Row 2: current is zero.');
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    await user.click(screen.getByLabelText('Keep Flagged Rows'));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].acknowledge_warnings).toBe(true);
  });

  it('ignores a completed import after leaving the page', async () => {
    let resolve!: (value: typeof imported) => void;
    vi.mocked(api.importTemperatureWorkbook).mockReturnValue(new Promise(done => { resolve = done; }));
    const view = render(<TemperatureRisePage onBack={() => undefined} />);
    fireEvent.change(screen.getByLabelText('Excel File'), { target: { files: [new File(['x'], 'scanner.xlsx')] } });
    view.unmount();
    await act(async () => resolve(imported));
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.downloadTemperatureWorkbook).not.toHaveBeenCalled();
  });

  it('reorders and restores channels and never acknowledges invalid readings', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Move Sample 1 / TC 2 Earlier' }));
    expect((screen.getByLabelText('Sample 1 / TC 1') as HTMLSelectElement).value).toBe('3');
    await user.click(screen.getByRole('button', { name: 'Exclude Sample 1 / TC 1' }));
    await user.click(screen.getByRole('button', { name: 'Restore Column C' }));
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [],
      issues: [{ code: 'invalid_reading', severity: 'error', source_row: 2, message: 'Row 2: missing reading.' }] });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.temperature_columns).toEqual([3, 2]);
    await screen.findByText('Row 2: missing reading.');
    expect(screen.queryByLabelText('Keep Flagged Rows')).toBeNull();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('clears affected calculations when coefficients change and exports the chosen values', async () => {
    const user = userEvent.setup();
    vi.mocked(api.generateTemperatureDerating).mockResolvedValue({
      points: [{ ambient: 0, basic: 100, derated: 80 }, { ambient: 105, basic: 0, derated: 0 }],
      annotation: { ambient: 75, basic: 60, derated: 48 }, coefficients, max_temperature: 105, step: 2.5,
    });
    vi.mocked(api.downloadTemperatureWorkbook).mockResolvedValue({ blob: new Blob(['xlsx']), fileName: 'curves.xlsx' });
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:test'), revokeObjectURL: vi.fn() });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    try {
      render(<TemperatureRisePage onBack={() => undefined} />);
      await upload();
      await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
      await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
      await user.click(screen.getByRole('button', { name: 'Get Coefficients' }));
      await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
      await user.click(screen.getByRole('button', { name: 'Generate Derating' }));
      await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
      fireEvent.change(screen.getByLabelText('AVG Coefficient a'), { target: { value: '.02' } });
      expect(screen.queryByRole('img', { name: 'Current vs Ambient Temperature' })).toBeNull();
      expect(screen.getByLabelText('Calculated Current').textContent).toContain('30.00');
      await user.click(screen.getByRole('button', { name: 'Generate Derating' }));
      await user.click(screen.getByRole('button', { name: 'Download Excel' }));
      await screen.findByText('curves.xlsx');
      expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
        average_coefficients: { a: .02, b: .2, c: 0 }, target_rise: 30,
        derating: { max_temperature: 105, step: 2.5, ambient_point: 75 },
      }));
      expect(click).toHaveBeenCalledOnce();
      fireEvent.change(screen.getByLabelText('MAX Coefficient a'), { target: { value: '.03' } });
      expect(screen.queryByLabelText('Calculated Current')).toBeNull();
      await user.click(screen.getByLabelText('Zero Intercept'));
      expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
      expect((screen.getByRole('button', { name: 'Generate Derating' }) as HTMLButtonElement).disabled).toBe(true);
    } finally { click.mockRestore(); vi.unstubAllGlobals(); }
  });
});
