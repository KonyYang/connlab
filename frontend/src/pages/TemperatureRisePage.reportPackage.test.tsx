import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as api from '../api/temperature';
import { TemperatureRisePage } from './TemperatureRisePage';
import * as profileApi from '../api/localIdentity';
import { refreshCurrentProfile } from '../currentUser';

vi.mock('../features/temperature/temperatureWorkspaceStorage', () => ({
  readTemperatureWorkspace: vi.fn(async () => null), writeTemperatureWorkspace: vi.fn(), clearTemperatureWorkspace: vi.fn(),
}));
vi.mock('../api/temperature', () => ({
  importTemperatureWorkbook: vi.fn(), prepareTemperatureData: vi.fn(), analyzeTemperatureData: vi.fn(),
  calculateTemperatureCurrent: vi.fn(), generateTemperatureDerating: vi.fn(), downloadTemperatureWorkbook: vi.fn(),
  exportTemperatureReportPackage: vi.fn(),
}));
vi.mock('../api/client', async original => ({ ...await original<typeof import('../api/client')>(),
  listProjectRegistryRows: vi.fn(async () => []), getProjectBasicInformation: vi.fn(),
}));
vi.mock('../api/localIdentity', async original => ({ ...await original<typeof import('../api/localIdentity')>(),
  getLocalProfile: vi.fn(), saveLocalProfile: vi.fn(),
}));

const source = new File(['original source bytes'], 'scanner.xlsx');
const table: api.WorkbookTable = { file_name: source.name, sheet_name: 'Data', sheet_names: ['Data'],
  rows: [['Scan', 'Time', 'TC1', 'TC2', 'Ambient', 'Current'], [1, '18:00', 24, 25, 20, 10], [2, '18:01', 29, 30, 20, 20]] };
const selection: api.DataSelection = { header_row: 1, start_row: 2, end_row: 3, ambient_column: 5,
  current_column: 6, temperature_columns: [3, 4], thermocouples_per_sample: 2, excluded_rows: [], current_multiplier: 1 };
const coefficients = { a: .01, b: .2, c: 0 };
const analysis: api.TemperatureAnalysis = {
  points: [{ source_row: 2, current: 10, maximum: 5, average: 5, rises: [4, 5], sample_maxima: [5] },
    { source_row: 3, current: 20, maximum: 10, average: 10, rises: [9, 10], sample_maxima: [10] }],
  maximum_fit: { coefficients, fitted_coefficients: coefficients, r_squared: .99 },
  average_fit: { coefficients, fitted_coefficients: coefficients, r_squared: .99 }, zero_intercept: true, thermocouples_per_sample: 2,
};
beforeEach(async () => {
  vi.clearAllMocks();
  vi.mocked(profileApi.getLocalProfile).mockResolvedValue({ profile: null });
  await refreshCurrentProfile();
  vi.mocked(api.importTemperatureWorkbook).mockResolvedValue({ table, selection, region_issue: null });
  vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [] });
  vi.mocked(api.analyzeTemperatureData).mockResolvedValue(analysis);
  vi.mocked(api.calculateTemperatureCurrent).mockResolvedValue({ current: 30 });
  vi.mocked(api.generateTemperatureDerating).mockResolvedValue({ points: [], annotation: { ambient: 75, basic: 60, derated: 48 },
    coefficients, max_temperature: 105, step: 2.5 });
  vi.mocked(api.exportTemperatureReportPackage).mockResolvedValue({ blob: new Blob(['zip']), fileName: 'scanner_ReportResults.zip' });
  vi.mocked(api.downloadTemperatureWorkbook).mockResolvedValue({ blob: new Blob(['xlsx']), fileName: 'scanner_Summary.xlsx' });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
  vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:report-package'), revokeObjectURL: vi.fn() });
});
async function prepare() {
  const view = render(<TemperatureRisePage onBack={() => undefined} />);
  await screen.findByRole('button', { name: 'Load Initial Data', exact: true });
  expect(screen.getByRole('button', { name: 'Export for Report' }).hasAttribute('disabled')).toBe(true);
  fireEvent.change(screen.getByLabelText('Load Initial Data'), { target: { files: [source] } });
  fireEvent.click(await screen.findByRole('button', { name: 'Confirm Data' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Export for Report' }).hasAttribute('disabled')).toBe(false));
  return view;
}
describe('Temperature report results package', () => {
  it('exports the source and the same reviewed download settings without changing Excel export', async () => {
    await prepare();
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    expect(await screen.findByText('scanner_ReportResults.zip')).toBeTruthy();
    expect(api.exportTemperatureReportPackage).toHaveBeenCalledWith(source, expect.objectContaining({
      table, selection: expect.objectContaining({ current_decimals: 0, temperature_columns: [3, 4] }),
      maximum_coefficients: coefficients, average_coefficients: coefficients, zero_intercept: true, target_rise: 30,
    }));
    expect(api.downloadTemperatureWorkbook).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Download Excel' }));
    expect(await screen.findByText('scanner_Summary.xlsx')).toBeTruthy();
    expect(api.downloadTemperatureWorkbook).toHaveBeenCalledWith(vi.mocked(api.exportTemperatureReportPackage).mock.calls[0][1]);
    expect(api.analyzeTemperatureData).toHaveBeenCalledOnce();
  });
  it('does not download a stale package after leaving the page', async () => {
    let finish!: (value: Awaited<ReturnType<typeof api.exportTemperatureReportPackage>>) => void;
    vi.mocked(api.exportTemperatureReportPackage).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
    const view = await prepare();
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    await screen.findByText('Preparing Report Package...');
    view.unmount();
    await act(async () => finish({ blob: new Blob(['zip']), fileName: 'stale.zip' }));
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  });
});
