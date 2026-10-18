import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as api from '../api/temperature';
import * as projectApi from '../api/client';
import { TemperatureRisePage } from './TemperatureRisePage';
import { AppShell } from '../components/layout/AppShell';
import * as profileApi from '../api/localIdentity';
import { refreshCurrentProfile } from '../currentUser';

vi.mock('../api/temperature', () => ({
  importTemperatureWorkbook: vi.fn(), prepareTemperatureData: vi.fn(), analyzeTemperatureData: vi.fn(),
  calculateTemperatureCurrent: vi.fn(), generateTemperatureDerating: vi.fn(), downloadTemperatureWorkbook: vi.fn(),
}));
vi.mock('../api/client', async original => ({
  ...await original<typeof import('../api/client')>(),
  listProjectRegistryRows: vi.fn(), getProjectBasicInformation: vi.fn(),
}));
vi.mock('../api/localIdentity', async original => ({ ...await original<typeof import('../api/localIdentity')>(),
  getLocalProfile: vi.fn(), saveLocalProfile: vi.fn() }));
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
function columnHeader(letter: string) { return screen.getByRole('columnheader', { name: new RegExp(`^Source Column ${letter.charCodeAt(0) - 64}: `) }); }

describe('temperature preparation and calculation workflow', () => {
  beforeEach(async () => {
    vi.resetAllMocks();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue(structuredClone(imported));
    vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [] });
    vi.mocked(api.analyzeTemperatureData).mockResolvedValue(analysis);
    vi.mocked(api.calculateTemperatureCurrent).mockResolvedValue({ current: 30 });
    vi.mocked(api.generateTemperatureDerating).mockResolvedValue(derating);
    vi.mocked(projectApi.listProjectRegistryRows).mockResolvedValue([]);
    vi.mocked(profileApi.getLocalProfile).mockResolvedValue({ profile: null });
    await refreshCurrentProfile();
  });

  it('keeps the source tooltip and groups confirmation before download after the header parameters', async () => {
    render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    await upload();
    const sheet = screen.getByLabelText('Sheet Name');
    expect(sheet.title).toBe('scanner.xlsx');
    expect(screen.queryByText('scanner.xlsx', { exact: true })).toBeNull();
    const confirm = screen.getByRole('button', { name: 'Confirm Data' });
    const download = screen.getByRole('button', { name: 'Download Excel' });
    const actions = within(screen.getByRole('banner')).getByRole('group', { name: 'Data actions' });
    expect(within(actions).getAllByRole('button')).toEqual([confirm, download]);
    expect(screen.getByLabelText('Current Decimals').compareDocumentPosition(confirm) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(download.closest('footer')).toBeNull();
    expect((download as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(confirm);
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect((confirm as HTMLButtonElement).disabled).toBe(true);
    expect((download as HTMLButtonElement).disabled).toBe(false);
    expect(screen.getByText('Data Confirmed').closest('footer')).not.toBeNull();
    fireEvent.change(screen.getByLabelText('Current Decimals'), { target: { value: '1' } });
    expect((confirm as HTMLButtonElement).disabled).toBe(false);
    expect((download as HTMLButtonElement).disabled).toBe(true);
    expect(screen.queryByText('Data Confirmed')).toBeNull();
  });

  it('switches worksheets from an unlabelled header selector immediately after Load Initial Data', async () => {
    const user = userEvent.setup();
    const first = structuredClone(imported);
    first.table.sheet_names = ['Data', 'Other'];
    const second = structuredClone(first);
    second.table.sheet_name = 'Other';
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(first).mockResolvedValueOnce(second);
    render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    const header = within(screen.getByRole('banner'));
    expect(header.queryByRole('combobox', { name: 'Sheet Name' })).toBeNull();
    await upload();
    const sheet = header.getByRole('combobox', { name: 'Sheet Name' });
    const load = header.getByRole('button', { name: 'Load Initial Data' });
    expect(load.nextElementSibling).toBe(sheet);
    expect(screen.queryByText('Sheet Name', { exact: true })).toBeNull();
    expect(sheet.title).toBe('scanner.xlsx');
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.selectOptions(sheet, 'Other');
    await waitFor(() => expect((header.getByRole('combobox', { name: 'Sheet Name' }) as HTMLSelectElement).value).toBe('Other'));
    expect(api.importTemperatureWorkbook).toHaveBeenLastCalledWith(expect.objectContaining({ name: 'scanner.xlsx' }), 'Other');
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Confirm Data' }).hasAttribute('disabled')).toBe(false);
    expect(screen.getByRole('button', { name: 'Download Excel' }).hasAttribute('disabled')).toBe(true);
  });

  it('offers a bounded current decimal spinner and invalidates results without excluding rows or changing samples', async () => {
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    const input = screen.getByRole('spinbutton', { name: 'Current Decimals' }) as HTMLInputElement;
    expect(input.value).toBe('0');
    expect([input.min, input.max, input.step]).toEqual(['0', '4', '1']);
    fireEvent.change(input, { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(api.analyzeTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      selection: expect.objectContaining({ current_decimals: 1, excluded_rows: [], temperature_columns: [3, 4] }),
    }));
    expect(screen.getByLabelText('Calculated Current').textContent).toBe('30.0 A');
    fireEvent.change(input, { target: { value: '2' } });
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText('4 Included / 0 Excluded Rows')).toBeTruthy();
  });

  it('edits all data parameters to the right of the header import action without duplicating them in the page', async () => {
    const data = structuredClone(imported);
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue({ ...data, selection: { ...data.selection, sample_count: 1 } });
    render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    await upload();
    const header = within(screen.getByRole('banner'));
    const parameters = header.getByRole('group', { name: 'Data parameters' });
    const load = header.getByRole('button', { name: 'Load Initial Data' });
    expect(load.compareDocumentPosition(parameters) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    for (const name of ['Ambient Column', 'Current Column', 'Samples', 'Current Decimals']) {
      expect(within(parameters).getByLabelText(name)).toBeTruthy();
      expect(within(screen.getByRole('main')).queryByLabelText(name)).toBeNull();
    }
    expect((within(parameters).getByLabelText('Ambient Column') as HTMLSelectElement).title).toBe('Ambient');
    expect((within(parameters).getByLabelText('Current Column') as HTMLSelectElement).title).toBe('Current');
    const thermocouples = within(parameters).getByText('2 TC/Sample');
    const decimals = within(parameters).getByLabelText('Current Decimals').closest('label')!;
    expect(thermocouples.nextElementSibling).toBe(decimals);
    fireEvent.change(within(parameters).getByLabelText('Samples'), { target: { value: '2' } });
    fireEvent.change(within(parameters).getByLabelText('Current Decimals'), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(api.analyzeTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ selection: expect.objectContaining({
      sample_count: 2, current_decimals: 1, ambient_column: 5, current_column: 6, excluded_rows: [],
    }) }));
  });

  it('uses precision-aware auxiliary power detection when choosing the automatic fit mode', async () => {
    vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [], stable_auxiliary_current_columns: [7] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.change(screen.getByLabelText('Current Decimals'), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(api.analyzeTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ zero_intercept: false }));
    expect((screen.getByLabelText('Zero Intercept') as HTMLInputElement).checked).toBe(false);
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
  });

  it('shows editable sample count, preserves all channels and only confirms complete groups', async () => {
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue({ ...structuredClone(imported), selection: {
      ...imported.selection, sample_count: 3, thermocouples_per_sample: 1,
    } });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText('TC/Sample: pending')).toBeTruthy();
    expect(screen.queryByLabelText('Thermocouples/Sample')).toBeNull();
    fireEvent.change(screen.getByLabelText('Samples'), { target: { value: '1' } });
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await waitFor(() => expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      selection: expect.objectContaining({ sample_count: 1, thermocouples_per_sample: 2, temperature_columns: [3, 4], sample_groups: [[3, 4]] }),
    })));
  });

  it('hides Tested By and exports the local project leader fallback', async () => {
    const user = userEvent.setup();
    render(<AppShell activeRoute="tools"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    await upload();
    expect(screen.getByRole('button', { name: 'Project Leader' }).title).toBe('Project Leader: Lab User');
    expect(screen.queryByLabelText('Tested By')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Default tester payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Default tester payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      report_metadata: expect.objectContaining({ tested_by: 'Lab User' }),
    }));
  });

  it('exports the latest name saved from the avatar without reimporting or recalculating', async () => {
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    vi.mocked(profileApi.getLocalProfile).mockResolvedValue({ profile: { display_name: 'Alice' } });
    await refreshCurrentProfile();
    const user = userEvent.setup();
    render(<AppShell activeRoute="tools"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    await upload();
    expect(screen.queryByLabelText('Tested By')).toBeNull();
    fireEvent.change(screen.getByLabelText('LTR'), { target: { value: 'Manual LTR' } });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    const chart = screen.getByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByRole('button', { name: 'Project Leader' }));
    const dialog = screen.getByRole('dialog', { name: 'Project Leader' });
    fireEvent.change(within(dialog).getByRole('textbox', { name: 'Project Leader' }), { target: { value: 'Bob' } });
    vi.mocked(profileApi.saveLocalProfile).mockResolvedValue({ profile: { display_name: 'Bob' } });
    await user.click(within(dialog).getByRole('button', { name: 'Save' }));
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(screen.getByRole('button', { name: 'Project Leader' }).title).toBe('Project Leader: Bob');
    expect(screen.getByRole('img', { name: 'Temperature Rise vs Current' })).toBe(chart);
    expect(api.importTemperatureWorkbook).toHaveBeenCalledTimes(1);
    expect(api.analyzeTemperatureData).toHaveBeenCalledTimes(1);
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Project leader payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Project leader payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      report_metadata: expect.objectContaining({ tested_by: 'Bob', ltr_number: 'Manual LTR' }),
    }));
  });

  it('shows all report fields for manual entry and exports them without project lookup or resetting the chart', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(screen.queryByLabelText('Project (optional)')).toBeNull();
    expect(screen.queryByText('More Information')).toBeNull();
    expect(screen.queryByText('Test Info', { exact: true })).toBeNull();
    const fields = { LTR: 'DL-2026-09-002A',
      'Test Equipment ID': 'DG-Q-0801/0269', 'Test Condition': '40 A' };
    const reportFields = within(screen.getByRole('group', { name: 'Report information' }));
    for (const [label, value] of Object.entries(fields)) {
      const input = reportFields.getByLabelText(label) as HTMLInputElement;
      expect(input.disabled).toBe(false);
      fireEvent.change(input, { target: { value } });
    }
    expect(screen.queryByLabelText('Rel. Hum. (%RH)')).toBeNull();
    expect(screen.queryByLabelText('Remark')).toBeNull();
    expect(screen.queryByLabelText('Test Date')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    expect(screen.queryByLabelText('Amb Temp. (°C)')).toBeNull();
    expect(screen.getByRole('img', { name: 'Temperature Rise vs Current' })).toBeTruthy();
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Metadata payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Metadata payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      report_metadata: { ltr_number: 'DL-2026-09-002A', tested_by: 'Lab User',
        test_date: '', ambient_temperature: '23', relative_humidity: 50,
        equipment_id: 'DG-Q-0801/0269', test_condition: '40 A', remark: '' },
    }));
    expect(projectApi.listProjectRegistryRows).not.toHaveBeenCalled();
    expect(projectApi.getProjectBasicInformation).not.toHaveBeenCalled();
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({
      selection: expect.objectContaining({ ambient_column: 5 }),
      table: expect.objectContaining({ rows: imported.table.rows }),
    }));
  });

  it('exports the latest included date automatically and updates it after row exclusion while retaining manual entries', async () => {
    const user = userEvent.setup();
    const dated = structuredClone(imported);
    ['2026/10/12 18:00', '2026/10/11 18:01', '2026/10/14 18:02', '2026/10/13 18:03']
      .forEach((value, index) => { dated.table.rows[index + 1][1] = value; });
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(dated);
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(screen.queryByLabelText('Test Date')).toBeNull();
    expect(screen.queryByLabelText('Amb Temp. (°C)')).toBeNull();
    expect((screen.getByLabelText('LTR') as HTMLInputElement).value).toBe('');
    expect(screen.queryByLabelText('Tested By')).toBeNull();
    fireEvent.change(screen.getByLabelText('LTR'), { target: { value: 'Explicit LTR' } });
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValue(new Error('Automatic date payload checked'));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Automatic date payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenLastCalledWith(expect.objectContaining({
      report_metadata: expect.objectContaining({ test_date: '2026-10-14', tested_by: 'Lab User', ltr_number: 'Explicit LTR' }),
    }));
    await user.click(screen.getByLabelText('Select Scan 3'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Automatic date payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenLastCalledWith(expect.objectContaining({
      report_metadata: expect.objectContaining({ test_date: '2026-10-13', tested_by: 'Lab User', ltr_number: 'Explicit LTR' }),
    }));
    expect(screen.queryByLabelText('Amb Temp. (°C)')).toBeNull();
    expect((screen.getByLabelText('LTR') as HTMLInputElement).value).toBe('Explicit LTR');
  });

  it('keeps hidden report environment defaults through source changes without blocking manual report downloads', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.change(screen.getByLabelText('LTR'), { target: { value: 'Manual LTR' } });
    const replacement = structuredClone(imported);
    replacement.table.rows.slice(1).forEach(row => { row[4] = 18; });
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(replacement);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    expect(screen.queryByLabelText('Rel. Hum. (%RH)')).toBeNull();
    expect(screen.queryByLabelText('Amb Temp. (°C)')).toBeNull();
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByLabelText('LTR') as HTMLInputElement).value).toBe('Manual LTR');
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Fixed environment payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Fixed environment payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      table: expect.objectContaining({ rows: replacement.table.rows }),
      report_metadata: expect.objectContaining({ ltr_number: 'Manual LTR', ambient_temperature: '23', relative_humidity: 50 }),
    }));
  });

  it('automatically calculates the default target from MAX and exports it without an extra click', async () => {
    const user = userEvent.setup();
    const maximum = { a: .012345, b: .234567, c: 0 };
    vi.mocked(api.analyzeTemperatureData).mockResolvedValueOnce({ ...analysis,
      maximum_fit: { ...analysis.maximum_fit, coefficients: maximum } });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(api.calculateTemperatureCurrent).not.toHaveBeenCalled();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect((await screen.findByLabelText('Calculated Current')).textContent).toContain('30 A');
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    expect(api.calculateTemperatureCurrent).toHaveBeenCalledExactlyOnceWith(maximum, 30);
    expect(api.generateTemperatureDerating).toHaveBeenCalledWith(coefficients, expect.anything());
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Export payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Export payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      target_rise: 30, maximum_coefficients: maximum,
    }));
    fireEvent.change(screen.getByLabelText('Target Rise (°C)'), { target: { value: '40' } });
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
    await screen.findByLabelText('Calculated Current');
    expect(api.calculateTemperatureCurrent).toHaveBeenLastCalledWith(coefficients, 40);
  });

  it('retains the chart on automatic current failure and allows a focused calculation retry', async () => {
    const user = userEvent.setup();
    vi.mocked(api.calculateTemperatureCurrent).mockRejectedValueOnce(new Error('No positive current for this target.'));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('No positive current for this target.');
    expect(screen.getByRole('img', { name: 'Temperature Rise vs Current' })).toBeTruthy();
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
    await screen.findByLabelText('Calculated Current');
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it.each(['upload', 'leave'] as const)('ignores a late automatic current after %s without continuing Derating', async action => {
    const user = userEvent.setup();
    let finishCurrent!: (value: { current: number }) => void;
    vi.mocked(api.calculateTemperatureCurrent).mockReturnValueOnce(new Promise(done => { finishCurrent = done; }));
    const view = render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await waitFor(() => expect(api.calculateTemperatureCurrent).toHaveBeenCalledOnce());
    expect((screen.getByRole('button', { name: 'Download Excel' }) as HTMLButtonElement).disabled).toBe(true);
    if (action === 'upload') await upload();
    else view.unmount();
    await act(async () => finishCurrent({ current: 84.3 }));
    expect(screen.queryByLabelText('Calculated Current')).toBeNull();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
  });

  it('restores a temperature after an ambient roundtrip without reviving an explicitly excluded channel', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.selectOptions(screen.getByLabelText('Ambient Column'), '3');
    await user.selectOptions(screen.getByLabelText('Ambient Column'), '5');
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(false);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.selectOptions(screen.getByLabelText('Ambient Column'), '4');
    await user.selectOptions(screen.getByLabelText('Ambient Column'), '5');
    await user.click(columnHeader('D'));
    expect((screen.getByRole('button', { name: 'Restore', exact: true }) as HTMLButtonElement).disabled).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Restore', exact: true }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ selection: expect.objectContaining({
      temperature_columns: [3, 4], thermocouples_per_sample: 2, sample_groups: [[3, 4]],
    }) }));
  });

  it('edits measurement names independently of source readings and sends them with the download', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    const header = columnHeader('C');
    expect(within(header).queryByText('C', { exact: true })).toBeNull();
    const name = within(header).getByRole('textbox', { name: 'Measurement Name, Source 3' });
    await user.clear(name);
    await user.type(name, 'Tail-R');
    expect(header.getAttribute('aria-selected')).toBe('false');
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Download name check'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Download name check');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      table: imported.table,
      selection: expect.objectContaining({ channel_names: { 3: 'Tail-R' }, temperature_columns: [3, 4] }),
    }));
    expect(imported.table.rows[0][2]).toBe('TC1');
  });

  it('blocks uneven exclusions even when the remaining total is divisible and sends balanced groups through confirmation and download', async () => {
    const source = { ...structuredClone(imported), table: { ...imported.table, rows: [
      ['Scan', 'Time', '101 <1_A> (C)', '102 <1_B> (C)', 'Ambient (C)', 'Current (VDC)',
        '103 <2_A> (C)', '104 <2_B> (C)'],
      [1, '18:00', 24, 25, 20, 10, 34, 35], [2, '18:01', 24, 25, 20, 10, 34, 35],
    ] }, selection: { ...imported.selection, end_row: 3, temperature_columns: [3, 4, 7, 8] }, channel_layout: {
      temperature_columns: [3, 4, 7, 8], current_columns: [6], stable_current_columns: [],
      sample_groups: [{ sample_id: '1', columns: [3, 4] }, { sample_id: '2', columns: [7, 8] }],
      thermocouples_per_sample: 2, ambient_column: 5, current_column: 6, issues: [], zero_intercept_default: true,
    } };
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    for (const letter of ['C', 'D']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByRole('alert').textContent).toContain('Incomplete sample group');
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    for (const letter of ['D', 'H']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect((screen.getByLabelText('Thermocouples/Sample') as HTMLInputElement).value).toBe('1');
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ selection: expect.objectContaining({
      temperature_columns: [3, 7], thermocouples_per_sample: 1, sample_groups: [[3], [7]],
    }) }));
    // Reject at the download boundary after observing its payload; no browser download is needed here.
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Download check'));
    fireEvent.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Download check');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({ selection: expect.objectContaining({
      temperature_columns: [3, 7], thermocouples_per_sample: 1, sample_groups: [[3], [7]],
    }) }));
  });

  it('generates both charts after one successful confirmation using the new rounded AVG fit and chosen settings', async () => {
    const user = userEvent.setup();
    let finishReview!: (value: api.PreparedData) => void;
    let finishRise!: (value: api.TemperatureAnalysis) => void;
    vi.mocked(api.prepareTemperatureData).mockReturnValueOnce(new Promise(done => { finishReview = done; }));
    vi.mocked(api.analyzeTemperatureData).mockReturnValueOnce(new Promise(done => { finishRise = done; }));
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.change(screen.getByLabelText('Max work Temp (°C)'), { target: { value: '125' } });
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
    expect(api.calculateTemperatureCurrent).toHaveBeenCalledExactlyOnceWith(coefficients, 30);
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
    expect((screen.getByRole('button', { name: 'Derating' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('shows the missing-baseline warning and measured-only stages until the mode changes', async () => {
    const warning = 'No pre-energization zero-current reading. No artificial origin added; the intercept is extrapolated from measured stages.';
    const user = userEvent.setup();
    vi.mocked(api.analyzeTemperatureData).mockResolvedValueOnce({ ...analysis,
      zero_intercept: false, points: analysis.points.slice(1), warnings: [warning] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByLabelText('Zero Intercept'));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    const message = await screen.findByText(warning);
    expect(message.title).toBe(warning);
    const plot = screen.getByRole('img', { name: 'Temperature Rise vs Current' });
    const firstMeasuredX = Number(plot.querySelector('circle')!.getAttribute('cx'));
    for (const line of plot.querySelectorAll('polyline')) {
      expect(Number(line.getAttribute('points')!.split(',')[0])).toBe(firstMeasuredX);
    }
    await user.click(screen.getByText('Stage Results'));
    expect(screen.queryByRole('cell', { name: 'Origin', exact: true })).toBeNull();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Derating' }) as HTMLButtonElement).disabled).toBe(true);
    await user.click(screen.getByLabelText('Zero Intercept'));
    expect(screen.queryByText(warning)).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Generate T-riseChart' }));
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByText('Stage Results'));
    expect(screen.getByRole('cell', { name: 'Origin', exact: true })).toBeTruthy();
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
    await user.click(screen.getByRole('button', { name: stage === 'prepare' ? 'Confirm Data' : stage === 'rise' ? 'Generate T-riseChart' : 'Derating' }));
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
      expect((screen.getByRole('button', { name: 'Derating' }) as HTMLButtonElement).disabled).toBe(false);
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
    expect(within(ambient).getByRole('option', { name: 'Ambient' })).toBeTruthy();
    expect(within(current).getByRole('option', { name: 'High Power' })).toBeTruthy();
    expect(screen.queryByLabelText('Select Column H')).toBeNull();
    expect(screen.getByRole('columnheader', { name: 'Source Column 8: Aux (A)' })).toBeTruthy();
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
    expect(screen.getByTitle('scanner.xlsx')).toBeTruthy();
    expect(api.importTemperatureWorkbook).toHaveBeenCalledWith(file, undefined);
    fireEvent.change(input, { target: { files: [] } });
    expect(screen.getByTitle('scanner.xlsx')).toBeTruthy();
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
    expect((screen.getByLabelText('Thermocouples/Sample') as HTMLInputElement).value).toBe('2');
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

  it('adjusts a single sample count, accepts a whole spare move and can undo both operations', async () => {
    const user = userEvent.setup();
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce({ ...structuredClone(imported), channel_layout: {
      temperature_columns: [3, 4], current_columns: [6], stable_current_columns: [], sample_groups: [],
      thermocouples_per_sample: 2, ambient_column: 5, current_column: 6, issues: [], zero_intercept_default: true,
      current_issue: 'Confirm the current column used for this curve.',
    } });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect((screen.getByRole('button', { name: 'Confirm Data' }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByLabelText('Thermocouples/Sample') as HTMLInputElement).value).toBe('1');
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    fireEvent.contextMenu(columnHeader('G'));
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'TC2' }));
    expect((screen.getByLabelText('Thermocouples/Sample') as HTMLInputElement).value).toBe('1');
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
    expect(screen.getByTitle('scanner.csv')).toBeTruthy();
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
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    fireEvent.contextMenu(columnHeader('G'));
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'TC2' }));
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection).toMatchObject({
      temperature_columns: [3, 7], excluded_rows: [2],
    });
    await screen.findByRole('img', { name: 'Temperature Rise vs Current' });
    await user.click(screen.getByRole('button', { name: 'Calculate Current' }));
    expect((await screen.findByLabelText('Calculated Current')).textContent).toContain('30 A');
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Restore', exact: true }));
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
    expect(within(screen.getByRole('region', { name: 'Scanner Data Preview' })).getByDisplayValue('New TC')).toBeTruthy();
    expect(screen.queryByText('View Channels')).toBeNull();
    expect(screen.queryByLabelText('Header Row')).toBeNull();
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    expect((screen.getByRole('button', { name: 'Generate T-riseChart' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('shows all review details in a compact footer hover without weakening validation or row highlighting', async () => {
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [], issues: [
      { code: 'zero_current', severity: 'warning', source_row: 2, message: 'Row 2: current is zero.' },
      { code: 'invalid_reading', severity: 'error', source_row: 3, message: 'Row 3: missing reading.' },
    ] });
    render(<AppShell activeRoute="tools" topBarTitle="Temperature Rise"><TemperatureRisePage onBack={() => undefined} /></AppShell>);
    await upload();
    fireEvent.click(screen.getByRole('button', { name: 'Confirm Data' }));
    const review = await screen.findByRole('region', { name: 'Data Needs Review' });
    expect(review.closest('footer')).not.toBeNull();
    expect(review.title).toBe('Scan 1: current rounds to 0 at 0 decimal places (this current column).\nScan 2: missing reading.');
    expect(screen.queryByRole('heading', { name: 'Data Needs Review' })).toBeNull();
    expect(within(review.closest('footer')!).queryByRole('button')).toBeNull();
    expect(screen.getByLabelText('Select Scan 1').closest('tr')?.getAttribute('aria-label')).toBe('Scan 1 · Needs Review');
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Download Excel' }).hasAttribute('disabled')).toBe(true);
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ selection: expect.objectContaining({ excluded_rows: [] }) }));
    fireEvent.change(screen.getByLabelText('Current Decimals'), { target: { value: '1' } });
    expect(screen.queryByRole('region', { name: 'Data Needs Review' })).toBeNull();
  });

  it('keeps warnings highlighted without extra acknowledgement or footer actions and uses the top row controls', async () => {
    const user = userEvent.setup();
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: true, measurements: [],
      issues: [{ code: 'zero_current', severity: 'warning', source_row: 2, message: 'Row 2: current is zero.' }] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    expect(api.prepareTemperatureData).not.toHaveBeenCalled();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan 1: current rounds to 0 at 0 decimal places (this current column).');
    expect(screen.queryByLabelText('Keep Flagged Rows')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Select Unpowered Rows' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Restore All Rows' })).toBeNull();
    const warnedRow = screen.getByLabelText('Select Scan 1').closest('tr')!;
    expect(warnedRow.getAttribute('aria-label')).toBe('Scan 1 · Needs Review');
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(false);
    expect(await screen.findByRole('img', { name: 'Current vs Ambient Temperature' })).toBeTruthy();
    expect(api.prepareTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ acknowledge_warnings: true }));
    expect(api.analyzeTemperatureData).toHaveBeenCalledWith(expect.objectContaining({ acknowledge_warnings: true }));
    await user.click(screen.getByLabelText('Select Scan 1'));
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText('Select Scan 2') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(screen.queryByRole('button', { name: 'Restore All Rows' })).toBeNull();
    expect(screen.queryByRole('img', { name: 'Temperature Rise vs Current' })).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    expect(api.prepareTemperatureData).toHaveBeenLastCalledWith(expect.objectContaining({
      selection: expect.objectContaining({ excluded_rows: [2] }),
    }));
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Restore', exact: true }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    vi.mocked(api.downloadTemperatureWorkbook).mockRejectedValueOnce(new Error('Review payload checked'));
    await user.click(screen.getByRole('button', { name: 'Download Excel' }));
    await screen.findByText('Review payload checked');
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(expect.objectContaining({
      acknowledge_warnings: true, selection: expect.objectContaining({ excluded_rows: [] }),
    }));
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
    await screen.findByText('Scan 00774: current rounds to 0 at 0 decimal places (this current column).');
    expect(screen.getByText('Scan 800, column C: missing reading.')).toBeTruthy();
    expect(screen.getByText('No usable rows remain.')).toBeTruthy();
    const review = screen.getByRole('region', { name: 'Data Needs Review' });
    expect(review.textContent).not.toMatch(/Row [23]/);
    await user.click(screen.getByLabelText('Select Scan 00774'));
    expect((screen.getByLabelText('Select Scan 00774') as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText('Select Scan 800') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.excluded_rows).toEqual([2]);
  });

  it('compacts consecutive unpowered scans without losing row selection or other warnings', async () => {
    const user = userEvent.setup();
    const source = structuredClone(imported);
    [51, 52, 53, 55].forEach((scan, index) => { source.table.rows[index + 1][0] = scan; });
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValueOnce(source);
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: true, measurements: [], issues: [
      ...[2, 3, 4].map(source_row => ({ code: 'zero_current', severity: 'warning', source_row,
        message: `Row ${source_row}: |current| < 0.1 A is treated as unpowered. Review this row; other current columns may still be powered.` })),
      { code: 'current_drop', severity: 'warning', source_row: 4, message: 'Row 4: current decreased by more than 1%.' },
      { code: 'zero_current', severity: 'warning', source_row: 5, message: 'Row 5: current is zero.' },
    ] });
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    await screen.findByText('Scan 51~53: current rounds to 0 at 0 decimal places (this current column).');
    expect(screen.getByText('Scan 55: current rounds to 0 at 0 decimal places (this current column).')).toBeTruthy();
    expect(screen.getByText('Scan 53: current decreased by more than 1%.')).toBeTruthy();
    const review = screen.getByRole('region', { name: 'Data Needs Review' });
    expect(within(review).getAllByRole('paragraph')).toHaveLength(3);
    expect(review.textContent).not.toMatch(/Review this row|other current columns/);
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    for (const scan of [51, 52, 53, 55]) await user.click(screen.getByLabelText(`Select Scan ${scan}`));
    for (const scan of [51, 52, 53, 55]) expect((screen.getByLabelText(`Select Scan ${scan}`) as HTMLInputElement).checked).toBe(true);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.excluded_rows).toEqual([2, 3, 4, 5]);
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

  it('reorders and restores channels but still blocks invalid readings when warnings are accepted', async () => {
    const user = userEvent.setup();
    render(<TemperatureRisePage onBack={() => undefined} />);
    await upload();
    fireEvent.contextMenu(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'TC1' }));
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    vi.mocked(api.prepareTemperatureData).mockResolvedValueOnce({ ready: false, measurements: [],
      issues: [{ code: 'invalid_reading', severity: 'error', source_row: 2, message: 'Row 2: missing reading.' }] });
    await user.click(screen.getByRole('button', { name: 'Confirm Data' }));
    expect(vi.mocked(api.prepareTemperatureData).mock.calls.at(-1)?.[0].selection.temperature_columns).toEqual([4, 3]);
    await screen.findByText('Scan 1: missing reading.');
    expect(screen.queryByLabelText('Keep Flagged Rows')).toBeNull();
    expect(api.prepareTemperatureData).toHaveBeenLastCalledWith(expect.objectContaining({ acknowledge_warnings: true }));
    expect(api.analyzeTemperatureData).not.toHaveBeenCalled();
    expect(api.generateTemperatureDerating).not.toHaveBeenCalled();
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
      fireEvent.change(screen.getByLabelText('Max work Temp (°C)'), { target: { value: '125' } });
      expect(screen.queryByRole('img', { name: 'Current vs Ambient Temperature' })).toBeNull();
      expect(screen.getByLabelText('Calculated Current').textContent).toContain('30');
      await user.click(screen.getByRole('button', { name: 'Derating' }));
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
      expect((screen.getByRole('button', { name: 'Derating' }) as HTMLButtonElement).disabled).toBe(true);
    } finally { click.mockRestore(); vi.unstubAllGlobals(); }
  });
});
