import { act, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as api from '../api/temperature';
import { TemperatureRisePage } from './TemperatureRisePage';
import { AppShell } from '../components/layout/AppShell';

vi.mock('../api/temperature', () => ({
  importTemperatureWorkbook: vi.fn(), prepareTemperatureData: vi.fn(), analyzeTemperatureData: vi.fn(),
  calculateTemperatureCurrent: vi.fn(), generateTemperatureDerating: vi.fn(), downloadTemperatureWorkbook: vi.fn(),
}));
const imported = {
  region_issue: null,
  table: { file_name: 'scanner.xlsx', sheet_names: ['Data'], sheet_name: 'Data', rows: [
    ['Scan', 'Time', 'TC1', 'TC2', 'Ambient', 'Current', 'Spare'],
    [1, '18:00', 24, 25, 20, 10, 26], [2, '18:01', 24, 25, 20, 10, 26],
    [3, '18:02', 29, 30, 20, 20, 31], [4, '18:03', 29, 30, 20, 20, 31],
  ] },
  selection: { header_row: 1, start_row: 2, end_row: 5, ambient_column: 5, current_column: 6,
    temperature_columns: [3, 4], thermocouples_per_sample: 2, excluded_rows: [], current_multiplier: 1 },
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
const derating: api.DeratingAnalysis = {
  points: [{ ambient: 0, basic: 100, derated: 80 }, { ambient: 105, basic: 0, derated: 0 }],
  annotation: { ambient: 75, basic: 60, derated: 48 }, coefficients, max_temperature: 105, step: 2.5,
};

async function upload() {
  fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [new File(['x'], 'scanner.xlsx')] } });
  await screen.findByRole('button', { name: 'Confirm Data' });
}

describe('temperature preparation and calculation workflow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue(structuredClone(imported));
    vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [] });
    vi.mocked(api.analyzeTemperatureData).mockResolvedValue(analysis);
    vi.mocked(api.calculateTemperatureCurrent).mockResolvedValue({ current: 30 });
    vi.mocked(api.generateTemperatureDerating).mockResolvedValue(derating);
  });

  it('generates both charts after one successful confirmation using the new rounded AVG fit and chosen settings', async () => {
    const user = userEvent.setup();
    let finishReview!: (value: api.PreparedData) => void;
    let finishRise!: (value: api.TemperatureAnalysis) => void;
    vi.mocked(api.prepareTemperatureData).mockReturnValueOnce(new Promise(done => { finishReview = done; }));
    vi.mocked(api.analyzeTemperatureData).mockReturnValueOnce(new Promise(done => { finishRise = done; }));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.change(screen.getByLabelText('Max Working Temp (°C)'), { target: { value: '125' } });
    fireEvent.change(screen.getByLabelText('Step (°C)'), { target: { value: '5' } });
    fireEvent.change(screen.getByLabelText('Ambient Point (°C)'), { target: { value: '80' } });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    await act(async () => finishReview({ ready: true, issues: [], measurements: [] }));
    expect(screen.getByText('Generating T-riseChart...')).toBeTruthy();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    await act(async () => finishRise({ ...analysis, average_fit: { ...analysis.average_fit,
      coefficients: { a: .00987649, b: .12345649, c: 0 } } }));
    expect(await screen.findByRole('img', { name: 'Temperature Rise vs Current' })).toBeTruthy();
    expect(await screen.findByRole('img', { name: 'Current vs Ambient Temperature' })).toBeTruthy();
    expect(api.analyzeTemperatureData).toHaveBeenCalledOnce();
    expect(api.generateTemperatureDerating).toHaveBeenCalledExactlyOnceWith(
      { a: .009876, b: .123456, c: 0 }, { max_temperature: 125, step: 5, ambient_point: 80 });
    expect(api.calculateTemperatureCurrent).not.toHaveBeenCalled();
    expect(api.downloadTemperatureWorkbook).not.toHaveBeenCalled();
  });

  it('automatically generates only temperature rise when Zero Intercept is off', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByLabelText('Zero Intercept'));
    vi.mocked(api.analyzeTemperatureData).mockResolvedValueOnce({ ...analysis, zero_intercept: false,
      average_fit: { ...analysis.average_fit, coefficients: { ...coefficients, c: 2 } } });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(await screen.findByRole('img', { name: 'Temperature Rise vs Current' })).toBeTruthy();
    expect(screen.getByText(/Avg Of Max ΔT = .*2\.000000/)).toBeTruthy();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Generate Derating' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it.each(['prepare', 'rise', 'derating'] as const)('stops automatic generation on a %s failure and allows a focused retry', async stage => {
    const user = userEvent.setup();
    if (stage === 'prepare') vi.mocked(api.prepareTemperatureData).mockRejectedValueOnce(new Error('Check the data.'));
    if (stage === 'rise') vi.mocked(api.analyzeTemperatureData).mockRejectedValueOnce(new Error('Check the fit.'));
    if (stage === 'derating') vi.mocked(api.generateTemperatureDerating).mockRejectedValueOnce(new Error('Check the derating settings.'));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect((await screen.findByRole('alert')).textContent).toContain(stage === 'prepare' ? 'Check the data.' : stage === 'rise' ? 'Check the fit.' : 'Check the derating settings.');
    expect(screen.queryByRole('img', { name: 'Current vs Ambient Temperature' })).toBeNull();
    if (stage !== 'derating') expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    if (stage === 'prepare') expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    if (stage === 'derating') expect(screen.getByRole('img', { name: 'Temperature Rise vs Current' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: stage === 'prepare' ? 'Confirm Data' : stage === 'rise' ? 'Generate T-riseChart' : 'Generate Derating' }));
    expect(await screen.findByRole('img', { name: stage === 'derating' ? 'Current vs Ambient Temperature' : 'Temperature Rise vs Current' })).toBeTruthy();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it.each(['prepare', 'derating'] as const)('does not continue or restore an obsolete automatic %s operation after a new upload', async stage => {
    const user = userEvent.setup();
    let finishReview!: (value: api.PreparedData) => void;
    let finishDerating!: (value: api.DeratingAnalysis) => void;
    if (stage === 'prepare') vi.mocked(api.prepareTemperatureData).mockReturnValueOnce(new Promise(done => { finishReview = done; }));
    else vi.mocked(api.generateTemperatureDerating).mockReturnValueOnce(new Promise(done => { finishDerating = done; }));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText(stage === 'prepare' ? 'Checking Data...' : 'Generating Derating...');
    await upload();
    await act(async () => stage === 'prepare'
      ? finishReview({ ready: true, issues: [], measurements: [] }) : finishDerating(derating));
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.queryByRole('img', { name: 'Current vs Ambient Temperature' })).toBeNull();
    expect(screen.queryByText('Data Confirmed')).toBeNull();
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
    if (stage === 'prepare') {
      expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
      expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    }
  });

  it('does not start automatic analysis after confirmation resolves on an unmounted page', async () => {
    const user = userEvent.setup();
    let finishReview!: (value: api.PreparedData) => void;
    vi.mocked(api.prepareTemperatureData).mockReturnValueOnce(new Promise(done => { finishReview = done; }));
    const view = render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    view.unmount();
    await act(async () => finishReview({ ready: true, issues: [], measurements: [] }));
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
  });

  it('keeps coefficients out of the page while calculating and exporting the generated fits', async () => {
    const user = userEvent.setup();
    const average = { a: .009876, b: .123456, c: 0 };
    vi.mocked(api.analyzeTemperatureData).mockResolvedValueOnce({ ...analysis,
      average_fit: { ...analysis.average_fit, coefficients: average } });
    vi.mocked(api.downloadTemperatureWorkbook).mockResolvedValue({ blob: new Blob(['xlsx']), fileName: 'automatic.xlsx' });
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:test'), revokeObjectURL: vi.fn() });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    try {
      render(<TemperatureRisePage onBack={() => undefined} />);
      expect(screen.queryByText(/Polynomial Coefficients/)).toBeNull();
      expect(screen.queryByLabelText(/Coefficient [abc]/)).toBeNull();
      await upload();
      await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
      await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
      expect(screen.queryByText(/Polynomial Coefficients/)).toBeNull();
      expect(screen.queryByLabelText(/Coefficient [abc]/)).toBeNull();
      expect(screen.getByText(/Max ΔT = 0\.010000/)).toBeTruthy();
      expect(screen.getByText(/Avg Of Max ΔT = 0\.009876/)).toBeTruthy();
      await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
      expect(api.calculateTemperatureCurrent).toHaveBeenCalledWith(coefficients, 30);
      expect(api.generateTemperatureDerating).toHaveBeenCalledWith(average, {
        max_temperature: 105, step: 2.5, ambient_point: 75,
      });
      expect(screen.queryByRole('button', { name: 'Get Coefficients' })).toBeNull();
      expect((screen.getByRole('button', { name: 'Calculate Current' }) as HTMLButtonElement).disabled).toBe(false);
      expect((screen.getByRole('button', { name: 'Generate Derating' }) as HTMLButtonElement).disabled).toBe(false);
      await user.click(screen.getByRole('button', { name: 'Download Excel' }));
      await screen.findByText('automatic.xlsx');
      expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
        maximum_coefficients: coefficients, average_coefficients: average,
      }));
      expect(click).toHaveBeenCalledOnce();
    } finally { click.mockRestore(); vi.unstubAllGlobals(); }
  });

  it('refreshes nonzero-intercept fits on regeneration and invalidates calculations when data changes', async () => {
    const user = userEvent.setup();
    const maximum = { a: .012345, b: .234567, c: 1.234567 };
    const average = { a: .009876, b: .123456, c: .987654 };
    vi.mocked(api.analyzeTemperatureData).mockResolvedValue({ ...analysis, zero_intercept: false,
      maximum_fit: { ...analysis.maximum_fit, coefficients: maximum },
      average_fit: { ...analysis.average_fit, coefficients: average } });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByLabelText('Zero Intercept'));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(screen.getByText(/Max ΔT = .*1\.234567/)).toBeTruthy();
    const regenerated = { a: .015678, b: .345678, c: 2 };
    vi.mocked(api.analyzeTemperatureData).mockResolvedValueOnce({ ...analysis, zero_intercept: false,
      maximum_fit: { ...analysis.maximum_fit, coefficients: regenerated },
      average_fit: { ...analysis.average_fit, coefficients: average } });
    await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
    expect(screen.getByText(/Max ΔT = 0\.015678.*2\.000000/)).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
    expect(api.calculateTemperatureCurrent).toHaveBeenLastCalledWith(regenerated, 30);
    await user.selectOptions(screen.getByLabelText('Ambient Column'), '3');
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.queryByText(/Max ΔT =/)).toBeNull();
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    expect((screen.getByRole('button', { name: 'Calculate Current' }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('does not populate coefficients from a late analysis after another upload', async () => {
    const user = userEvent.setup();
    let resolve!: (value: api.TemperatureAnalysis) => void;
    vi.mocked(api.analyzeTemperatureData).mockReturnValueOnce(new Promise(done => { resolve = done; }));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Generating T-riseChart...');
    await upload();
    await act(async () => resolve(analysis));
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.queryByText(/Max ΔT =/)).toBeNull();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Calculate Current' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('filters ambient/current choices by scanner units without rounding the submitted data', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    source.table.rows[0] = ['Scan', 'Time', 'TC1 (C)', 'TC2 (C)', 'Ambient (C)', 'High Power (VDC)', 'Spare (C)', 'Aux (VDC)', 'Status'];
    source.table.rows[1] = [1, '18:00', 24.987654, 25.123456, 20.625, 17.596362, 26, 3, 'OK'];
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    const ambient = screen.getByLabelText('Ambient Column');
    const current = screen.getByLabelText('Current Column');
    expect(within(ambient).getAllByRole('option').map(option => (option as HTMLOptionElement).value)).toEqual(['3', '4', '5', '7']);
    expect(within(current).getAllByRole('option').map(option => (option as HTMLOptionElement).value)).toEqual(['6', '8']);
    expect(within(ambient).getByRole('option', { name: 'E — Ambient' })).toBeTruthy();
    expect(within(current).getByRole('option', { name: 'F — High Power' })).toBeTruthy();
    expect(screen.queryByLabelText('Select Column H')).toBeNull();
    expect(screen.getByRole('columnheader', { name: 'H — Aux (A)' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ table: expect.objectContaining({ rows: source.table.rows }) }));
    await user.selectOptions(current, '8');
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.current_column).toBe(8);
  });

  it('requires correcting a suggested current role that conflicts with an explicit temperature unit', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    source.table.rows[0] = ['Scan', 'Time', 'TC1 (C)', 'TC2 (C)', 'Ambient (C)', 'Current (VDC)', 'Spare (C)'];
    source.selection.current_column = 4;
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByLabelText('Current Column') as HTMLSelectElement).value).toBe('');
    expect(screen.getByRole('alert').textContent).toContain('Current Column');
    await user.selectOptions(screen.getByLabelText('Current Column'), '6');
    expect(screen.queryByRole('alert')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.current_column).toBe(6);
  });

  it('loads initial data through a keyboard-accessible button and keeps it when selection is cancelled', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    expect(screen.queryByText('Excel File')).toBeNull();
    const button = screen.getByRole('button', { name: 'Load Initial Data' });
    const input = screen.getByLabelText('Load Initial Data');
    const picker = vi.spyOn(input as HTMLInputElement, 'click');
    button.focus();
    await user.keyboard('{Enter}');
    expect(picker).toHaveBeenCalledOnce();
    const file = new File(['x'], 'scanner.xlsx');
    await user.upload(input, file);
    await screen.findByRole('button', { name: 'Confirm Data' });
    expect(screen.getByText('scanner.xlsx')).toBeTruthy();
    expect(api.importTemperatureWorkbook).toHaveBeenCalledWith(file, undefined);
    fireEvent.change(input, { target: { files: [] } });
    expect(screen.getByText('scanner.xlsx')).toBeTruthy();
    expect(api.importTemperatureWorkbook).toHaveBeenCalledOnce();
    await user.upload(input, file);
    expect(api.importTemperatureWorkbook).toHaveBeenCalledTimes(2);
  });

  it('summarizes regular groups without per-channel controls and defaults off for extra stable currents', async () => {
    const user = userEvent.setup();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce({
      ...structuredClone(imported), channel_layout: {
        temperature_columns: [3, 4], current_columns: [6, 7], stable_current_columns: [7],
        sample_groups: [{ sample_id: '1', columns: [3, 4] }], thermocouples_per_sample: 2,
        ambient_column: 5, current_column: 6, issues: [], zero_intercept_default: false,
      },
    });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(screen.getByText('1 Sample · 2 TC/Sample · 2 Channels')).toBeTruthy();
    expect(screen.queryByLabelText('Sample 1 / TC 1')).toBeNull();
    expect(screen.queryByRole('button', { name: /Earlier|Later/ })).toBeNull();
    expect((screen.getByLabelText('Zero Intercept') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByLabelText('Zero Intercept'));
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect((screen.getByLabelText('Zero Intercept') as HTMLInputElement).checked).toBe(true);
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ zero_intercept: true }));
  });

  it('blocks an incomplete sample until a spare is moved into position and can undo both operations', async () => {
    const user = userEvent.setup();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce({ ...structuredClone(imported), channel_layout: {
      temperature_columns: [3, 4], current_columns: [6], stable_current_columns: [], sample_groups: [],
      thermocouples_per_sample: 2, ambient_column: 5, current_column: 6, issues: [], zero_intercept_default: true,
      current_issue: 'Confirm the current column used for this curve.',
    } });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(true);
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    fireEvent.contextMenu(screen.getByLabelText('Select Column G').closest('th')!);
    await user.selectOptions(screen.getByLabelText('Move Before'), '4');
    await user.click(screen.getByRole('button', { name: 'Move' }));
    expect(screen.getByText('Confirm the current column used for this curve.')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.temperature_columns).toEqual([3, 7]);
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.temperature_columns).toEqual([3, 4]);
  });

  it('returns through an accessible icon in the Tools header, without a duplicate content button', async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    const view = render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={onBack} /></AppShell>);
    const banner = screen.getByRole('banner');
    expect(within(banner).getByRole('heading', { name: 'Temperature Rise' })).toBeTruthy();
    expect(screen.queryByRole('heading', { name: 'Temperature Rise & Derating' })).toBeNull();
    expect(screen.queryByRole('heading', { name: 'Initial Data' })).toBeNull();
    expect(within(banner).getByRole('button', { name: 'Load Initial Data' })).toBeTruthy();
    expect(within(screen.getByRole('main')).queryByRole('button', { name: 'Load Initial Data' })).toBeNull();
    const back = within(banner).getByRole('button', { name: 'Back To Tools' });
    expect(back.textContent).toBe('');
    expect(back.getAttribute('title')).toBe('Back To Tools');
    expect(within(screen.getByRole('main')).queryByRole('button', { name: 'Back To Tools' })).toBeNull();
    back.focus();
    await user.keyboard('{Enter}');
    expect(onBack).toHaveBeenCalledOnce();
    view.unmount();
    expect(screen.queryByRole('button', { name: 'Back To Tools' })).toBeNull();
  });

  it('loads CSV from the header without bypassing column and row confirmation', async () => {
    const user = userEvent.setup();
    const data = structuredClone(imported);
    data.table.file_name = 'scanner.csv';
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(data);
    render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    const button = within(screen.getByRole('banner')).getByRole('button', { name: 'Load Initial Data' });
    const input = screen.getByLabelText('Load Initial Data');
    const picker = vi.spyOn(input as HTMLInputElement, 'click');
    await user.click(button);
    expect(picker).toHaveBeenCalledOnce();
    const file = new File(['Scan,Time,TC1,Ambient,Current\n1,18:00,25,20,3.0010263'], 'scanner.csv', { type: 'text/csv' });
    await user.upload(input, file);
    await screen.findByRole('button', { name: 'Confirm Data' });
    expect(api.importTemperatureWorkbook).toHaveBeenCalledWith(file, undefined);
    expect(screen.getByText('scanner.csv')).toBeTruthy();
    expect(screen.getByLabelText('Ambient Column')).toBeTruthy();
    expect(screen.getByLabelText('Current Column')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Generate T-riseChart' }).hasAttribute('disabled')).toBe(true);
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
  });

  it('uses the detected region without showing row settings or success notices', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    for (const label of ['Header Row', 'First Data Row', 'Last Data Row']) {
      expect(screen.queryByLabelText(label)).toBeNull();
    }
    expect(screen.queryByRole('alert')).toBeNull();
    expect(screen.getByLabelText('Ambient Column')).toBeTruthy();
    expect(screen.getByLabelText('Current Column')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      selection: expect.objectContaining({ header_row: 1, start_row: 2, end_row: 5 }),
    }));
  });

  it('shows row correction only when detection fails and requires confirmation after recovery', async () => {
    const user = userEvent.setup();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce({
      table: structuredClone(imported.table), selection: null,
      region_issue: 'No data region could be identified. Check the sheet or set the header and data rows manually.',
    });
    render(<TemperatureRisePage onBack={() => undefined} />);
    fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [new File(['x'], 'scanner.xlsx')] } });
    await screen.findByRole('alert');
    expect(screen.getByLabelText('Sheet Name')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Confirm Data' })).toBeNull();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByLabelText('Header Row') as HTMLInputElement).value).toBe('');
    expect(screen.getByRole('region', { name: 'Source Rows' }).textContent).toContain('TC1');
    expect((screen.getByRole('button', { name: 'Apply Data Rows' }) as HTMLButtonElement).disabled).toBe(true);
    await user.type(screen.getByLabelText('Header Row'), '1');
    await user.type(screen.getByLabelText('First Data Row'), '2');
    await user.type(screen.getByLabelText('Last Data Row'), '5');
    await user.click(screen.getByRole('button', { name: 'Apply Data Rows' }));
    await screen.findByRole('button', { name: 'Confirm Data' });
    expect(api.importTemperatureWorkbook).toHaveBeenLastCalledWith(expect.any(File), 'Data', {
      header_row: 1, start_row: 2, end_row: 5,
    });
    expect(screen.queryByLabelText('Header Row')).toBeNull();
    expect(screen.queryByRole('alert')).toBeNull();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(false);
  });

  it('uses decimal current and ambient values directly without an extra conversion setting', async () => {
    const user = userEvent.setup();
    const decimal = structuredClone(imported);
    decimal.table.rows[1] = [1, '18:00', 24.987654, 25.123456, 20.625, 17.596362, 26];
    decimal.selection.current_multiplier = .001; // A legacy suggestion must not apply a hidden conversion.
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(decimal);
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(screen.queryByLabelText('Scale To Amperes')).toBeNull();
    expect(screen.queryByText(/Use 1 for readings already in A/)).toBeNull();
    expect(screen.queryByRole('button', { name: /conversion|scale/i })).toBeNull();
    expect(screen.getByLabelText('Ambient Column')).toBeTruthy();
    expect(screen.getByLabelText('Current Column')).toBeTruthy();
    expect(screen.getByLabelText('Thermocouples/Sample')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      table: expect.objectContaining({ rows: decimal.table.rows }),
      selection: expect.objectContaining({ current_column: 6, ambient_column: 5, current_multiplier: 1 }),
    }));
    expect(api.analyzeTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      table: expect.objectContaining({ rows: decimal.table.rows }),
      selection: expect.objectContaining({ current_multiplier: 1 }),
    }));
  });

  it('requires confirmation, supports whole-column moves and row restoration, and invalidates downstream results', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    fireEvent.contextMenu(screen.getByLabelText('Select Column G').closest('th')!);
    await user.selectOptions(screen.getByLabelText('Move Before'), '4');
    await user.click(screen.getByRole('button', { name: 'Move' }));
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection).toMatchObject({
      temperature_columns: [3, 7], excluded_rows: [2],
    });
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
    expect((await screen.findByLabelText('Calculated Current')).textContent).toContain('30.00 A');
    await user.click(screen.getByRole('button', { name: 'Restore All Rows' }));
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('retains correction entries after a failed request and ignores its late response after another upload', async () => {
    const user = userEvent.setup();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce({
      table: structuredClone(imported.table), selection: null, region_issue: 'Multiple possible data regions were found.',
    }).mockRejectedValueOnce(new Error('The header needs at least three columns.'));
    render(<TemperatureRisePage onBack={() => undefined} />);
    fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [new File(['x'], 'ambiguous.xlsx')] } });
    await screen.findByLabelText('Header Row');
    await user.type(screen.getByLabelText('Header Row'), '1');
    await user.type(screen.getByLabelText('First Data Row'), '2');
    await user.type(screen.getByLabelText('Last Data Row'), '5');
    await user.click(screen.getByRole('button', { name: 'Apply Data Rows' }));
    await screen.findByText('The header needs at least three columns.');
    expect((screen.getByLabelText('Header Row') as HTMLInputElement).value).toBe('1');
    expect(screen.queryByRole('button', { name: 'Confirm Data' })).toBeNull();
    let resolve!: (value: api.WorkbookImportResult) => void;
    vi.mocked(api.importTemperatureWorkbook).mockReturnValueOnce(new Promise(done => { resolve = done; }));
    await user.click(screen.getByRole('button', { name: 'Apply Data Rows' }));
    const next = structuredClone(imported);
    next.table.file_name = 'next.xlsx';
    next.table.rows[0][2] = 'New TC';
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(next);
    fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [new File(['new'], 'next.xlsx')] } });
    await screen.findByRole('button', { name: 'Confirm Data' });
    await act(async () => resolve(imported));
    expect(screen.getByRole('region', { name: 'Scanner Data Preview' }).textContent).toContain('New TC');
    expect(screen.queryByText('View Channels')).toBeNull();
    expect(screen.queryByLabelText('Header Row')).toBeNull();
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('keeps flagged readings until an explicit review choice', async () => {
    const user = userEvent.setup();
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [],
      issues: [{ code: 'zero_current', severity: 'warning', source_row: 2, message: 'Row 2: current is zero.' }] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan 1: current is zero.');
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
    await user.click(screen.getByRole('button', { name: 'Select Unpowered Rows' }));
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText('Select Scan 2') as HTMLInputElement).checked).toBe(false);
    expect(api.prepareTemperatureData).toHaveBeenCalledTimes(1);
    await user.click(screen.getByLabelText('Keep Flagged Rows'));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].acknowledge_warnings).toBe(true);
    expect(await screen.findByRole('img', { name: 'Current vs Ambient Temperature' })).toBeTruthy();
  });

  it('uses A-column scan IDs for review and selects the matching source rows without renumbering them', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    source.table.rows[1][0] = '00774';
    source.table.rows[2][0] = 800;
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [], issues: [
      { code: 'zero_current', severity: 'warning', source_row: 2, message: 'Row 2: current is zero.' },
      { code: 'invalid_reading', severity: 'error', source_row: 3, message: 'Row 3, column C: missing reading.' },
      { code: 'no_data', severity: 'error', source_row: 2, message: 'No usable rows remain.' },
    ] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan 00774: current is zero.');
    expect(screen.getByText('Scan 800, column C: missing reading.')).toBeTruthy();
    expect(screen.getByText('No usable rows remain.')).toBeTruthy();
    const review = screen.getByRole('region', { name: 'Data Needs Review' });
    expect(review.textContent).not.toMatch(/Row [23]/);
    await user.click(screen.getByRole('button', { name: 'Select Unpowered Rows' }));
    expect((screen.getByLabelText('Select Scan 00774') as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText('Select Scan 800') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.excluded_rows).toEqual([2]);
  });

  it('shows scan IDs in analysis errors and stage results while preserving the synthetic origin', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    source.table.rows[2][0] = 800;
    source.table.rows[4][0] = '00850';
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    vi.mocked(api.analyzeTemperatureData).mockRejectedValueOnce(new Error('Row 3: replace missing readings.'));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan 800: replace missing readings.');
    await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByText('Stage Results', { exact: true }));
    const stageTable = screen.getByRole('columnheader', { name: 'Scan', exact: true }).closest('table')!;
    expect(within(stageTable).getByRole('cell', { name: 'Origin', exact: true })).toBeTruthy();
    expect(within(stageTable).getByRole('cell', { name: '800', exact: true })).toBeTruthy();
    expect(within(stageTable).getByRole('cell', { name: '00850', exact: true })).toBeTruthy();
    expect(screen.queryByRole('columnheader', { name: 'Original Row' })).toBeNull();
  });

  it('does not invent a scan ID when the A-column value is missing', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    source.table.rows[1][0] = '';
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [], issues: [
      { code: 'invalid_reading', severity: 'error', source_row: 2, message: 'Row 2: missing reading.' },
    ] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan unavailable: missing reading.');
    expect(screen.queryByText('Row 2: missing reading.')).toBeNull();
  });

  it('ignores a completed import after leaving the page', async () => {
    let resolve!: (value: typeof imported) => void;
    vi.mocked(api.importTemperatureWorkbook).mockReturnValue(new Promise(done => { resolve = done; }));
    const view = render(<TemperatureRisePage onBack={() => undefined} />);
    fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [new File(['x'], 'scanner.xlsx')] } });
    view.unmount();
    await act(async () => resolve(imported));
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.downloadTemperatureWorkbook).not.toHaveBeenCalled();
  });

  it('reorders and restores channels and never acknowledges invalid readings', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.contextMenu(screen.getByLabelText('Select Column D').closest('th')!);
    await user.selectOptions(screen.getByLabelText('Move Before'), '3');
    await user.click(screen.getByRole('button', { name: 'Move' }));
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [],
      issues: [{ code: 'invalid_reading', severity: 'error', source_row: 2, message: 'Row 2: missing reading.' }] });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.temperature_columns).toEqual([4, 3]);
    await screen.findByText('Scan 1: missing reading.');
    expect(screen.queryByLabelText('Keep Flagged Rows')).toBeNull();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('clears affected calculations when parameters change and exports generated fits with the chosen settings', async () => {
    const user = userEvent.setup();
    const legacy = structuredClone(imported);
    legacy.selection.current_multiplier = .001;
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(legacy);
    vi.mocked(api.downloadTemperatureWorkbook).mockResolvedValue({ blob: new Blob(['xlsx']), fileName: 'curves.xlsx' });
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:test'), revokeObjectURL: vi.fn() });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    try {
      render(<TemperatureRisePage onBack={() => undefined} />);
      await upload();
      await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
      await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
      await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
      fireEvent.change(screen.getByLabelText('Max Working Temp (°C)'), { target: { value: '125' } });
      expect(screen.queryByRole('img', { name: 'Current vs Ambient Temperature' })).toBeNull();
      expect(screen.getByLabelText('Calculated Current').textContent).toContain('30.00');
      await user.click(screen.getByRole('button', { name: 'Generate Derating' }));
      expect(api.generateTemperatureDerating).toHaveBeenLastCalledWith(coefficients, {
        max_temperature: 125, step: 2.5, ambient_point: 75,
      });
      fireEvent.change(screen.getByLabelText('Target Rise (°C)'), { target: { value: '40' } });
      expect(screen.queryByLabelText('Calculated Current')).toBeNull();
      expect(screen.getByRole('img', { name: 'Current vs Ambient Temperature' })).toBeTruthy();
      await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
      expect(api.calculateTemperatureCurrent).toHaveBeenLastCalledWith(coefficients, 40);
      await user.click(screen.getByRole('button', { name: 'Download Excel' }));
      await screen.findByText('curves.xlsx');
      expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
        selection: expect.objectContaining({ current_multiplier: 1 }),
        maximum_coefficients: coefficients, average_coefficients: coefficients, target_rise: 40,
        derating: { max_temperature: 125, step: 2.5, ambient_point: 75 },
      }));
      expect(click).toHaveBeenCalledOnce();
      await user.click(screen.getByLabelText('Zero Intercept'));
      expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
      expect(screen.queryByLabelText('Calculated Current')).toBeNull();
      expect((screen.getByRole('button', { name: 'Generate Derating' }) as HTMLButtonElement).disabled).toBe(true);
    } finally { click.mockRestore(); vi.unstubAllGlobals(); }
  });
});
