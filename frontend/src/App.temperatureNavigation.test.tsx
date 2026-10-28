import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import * as api from './api/temperature';
import * as storage from './features/temperature/temperatureWorkspaceStorage';
import type { TemperatureWorkspaceDraft } from './features/temperature/temperatureWorkspace';

vi.mock('./api/temperature', () => ({
  importTemperatureWorkbook: vi.fn(), prepareTemperatureData: vi.fn(), analyzeTemperatureData: vi.fn(),
  calculateTemperatureCurrent: vi.fn(), generateTemperatureDerating: vi.fn(), downloadTemperatureWorkbook: vi.fn(),
}));
vi.mock('./api/client', async original => ({ ...await original<typeof import('./api/client')>(),
  listExternalResources: vi.fn(async () => []), listProjectRegistryRows: vi.fn(async () => []),
}));
vi.mock('./api/localIdentity', async original => ({ ...await original<typeof import('./api/localIdentity')>(),
  getLocalProfile: vi.fn(async () => ({ profile: null })),
}));
vi.mock('./features/temperature/temperatureWorkspaceStorage', () => ({
  readTemperatureWorkspace: vi.fn(), writeTemperatureWorkspace: vi.fn(), clearTemperatureWorkspace: vi.fn(),
  hasTemperatureWorkspace: vi.fn(),
}));
let saved: TemperatureWorkspaceDraft | null;
const imported: api.WorkbookImportResult = {
  region_issue: null,
  table: { file_name: 'navigation.csv', sheet_name: 'Initial Data', sheet_names: ['Initial Data'], rows: [
    ['Scan', 'Time', '1_HS (C)', 'Ambient (C)', 'Current (A)'],
    [1, '10:00', 24, 23, 0], [2, '10:01', 27, 23, 10],
    [3, '10:02', 32, 23, 20], [4, '10:03', 39, 23, 30],
  ] },
  selection: { header_row: 1, start_row: 2, end_row: 5, ambient_column: 4, current_column: 5,
    temperature_columns: [3], thermocouples_per_sample: 1, sample_count: 1, excluded_rows: [], current_multiplier: 1 },
};
const coefficients = { a: .01, b: .2, c: 0 };
const analysis: api.TemperatureAnalysis = {
  points: [0, 10, 20, 30].map((current, index) => ({ source_row: index ? index + 2 : null,
    current, maximum: index * 5, average: index * 5, rises: [index * 5], sample_maxima: [index * 5] })),
  maximum_fit: { coefficients, fitted_coefficients: coefficients, r_squared: 1 },
  average_fit: { coefficients, fitted_coefficients: coefficients, r_squared: 1 },
  zero_intercept: true, thermocouples_per_sample: 1,
};
const sidebar = () => within(screen.getByRole('complementary', { name: 'Primary navigation' }));
async function openImportedWorkspace() {
  await userEvent.setup().click(await screen.findByRole('button', { name: 'Drawing Curves', exact: true }));
  const input = await screen.findByLabelText('Load Initial Data');
  fireEvent.change(input, { target: { files: [new File(['source bytes'], 'navigation.csv')] } });
  await screen.findByRole('button', { name: 'Confirm Data', exact: true });
}

describe('Tools sidebar resumes the temperature workspace', () => {
  beforeAll(async () => {
    // Keep cold Vite transforms out of navigation timing under full-suite concurrency.
    await Promise.all([
      import('./pages/ToolsPage'),
      import('./pages/TemperatureRisePage'),
      import('./pages/SettingsPage'),
    ]);
  }, 30000);

  beforeEach(() => {
    vi.clearAllMocks();
    saved = null;
    window.history.replaceState({}, '', '/tools');
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    vi.mocked(storage.readTemperatureWorkspace).mockImplementation(async () => saved);
    vi.mocked(storage.writeTemperatureWorkspace).mockImplementation(async value => { saved = value; });
    vi.mocked(storage.clearTemperatureWorkspace).mockImplementation(async () => { saved = null; });
    vi.mocked(storage.hasTemperatureWorkspace).mockImplementation(async () => saved !== null);
    vi.mocked(api.importTemperatureWorkbook).mockResolvedValue(structuredClone(imported));
    vi.mocked(api.prepareTemperatureData).mockResolvedValue({ ready: true, issues: [], measurements: [] });
    vi.mocked(api.analyzeTemperatureData).mockResolvedValue(analysis);
    vi.mocked(api.calculateTemperatureCurrent).mockResolvedValue({ current: 30 });
    vi.mocked(api.generateTemperatureDerating).mockResolvedValue({
      points: [{ ambient: 0, basic: 100, derated: 80 }, { ambient: 105, basic: 0, derated: 0 }],
      annotation: { ambient: 75, basic: 60, derated: 48 }, coefficients, max_temperature: 105, step: 2.5,
    });
  });

  it('retains analysis, parameters and Undo through Settings → sidebar Tools and only clears on confirmed exit', async () => {
    const user = userEvent.setup();
    render(<App />);
    await openImportedWorkspace();
    fireEvent.change(screen.getByLabelText('Current Decimals'), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText('LTR'), { target: { value: 'QA-NAVIGATION' } });
    fireEvent.contextMenu(screen.getByRole('checkbox', { name: 'Select Scan 1', exact: true }));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected Rows (1)' }));
    await user.click(screen.getByRole('button', { name: 'Confirm Data', exact: true }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    await user.click(sidebar().getByRole('button', { name: 'Settings', exact: true }));
    await screen.findByRole('heading', { name: 'Settings', exact: true });
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    expect(window.location.pathname).toBe('/tools/temperature-rise');
    expect(screen.getByLabelText('Current Decimals')).toHaveProperty('value', '1');
    expect(screen.getByLabelText('LTR')).toHaveProperty('value', 'QA-NAVIGATION');
    expect(screen.getByText('3 Included / 1 Excluded Rows')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Undo', exact: true }));
    expect(screen.getByText('4 Included / 0 Excluded Rows')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Back To Tools' }));
    await user.click(within(screen.getByRole('dialog', { name: 'Clear workspace?' })).getByRole('button', { name: 'Cancel' }));
    await user.click(sidebar().getByRole('button', { name: 'Settings', exact: true }));
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByText('4 Included / 0 Excluded Rows');
    expect(storage.clearTemperatureWorkspace).not.toHaveBeenCalled();
    await user.click(screen.getByRole('button', { name: 'Back To Tools' }));
    await user.click(screen.getByRole('button', { name: 'Clear and Return' }));
    await screen.findByRole('button', { name: 'Drawing Curves', exact: true });
    expect(window.location.pathname).toBe('/tools');
    await user.click(sidebar().getByRole('button', { name: 'Settings', exact: true }));
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByRole('button', { name: 'Drawing Curves', exact: true });
    expect(window.location.pathname).toBe('/tools');
    expect(api.importTemperatureWorkbook).toHaveBeenCalledOnce();
    expect(storage.clearTemperatureWorkspace).toHaveBeenCalledOnce();
  }, 15000);

  it('resumes the persisted workspace from the sidebar in a freshly mounted app', async () => {
    const user = userEvent.setup();
    const view = render(<App />);
    await openImportedWorkspace();
    fireEvent.change(screen.getByLabelText('LTR'), { target: { value: 'FRESH-APP' } });
    view.unmount();
    window.history.replaceState({}, '', '/settings');
    render(<App />);
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByText('4 Included / 0 Excluded Rows');
    expect(window.location.pathname).toBe('/tools/temperature-rise');
    expect(screen.getByLabelText('LTR')).toHaveProperty('value', 'FRESH-APP');
    expect(api.importTemperatureWorkbook).toHaveBeenCalledOnce();
    expect(storage.hasTemperatureWorkspace).toHaveBeenCalledOnce();
  });

  it('keeps the tool directory when there is no recent workspace', async () => {
    window.history.replaceState({}, '', '/settings');
    render(<App />);
    await userEvent.setup().click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByRole('button', { name: 'Drawing Curves', exact: true });
    expect(window.location.pathname).toBe('/tools');
    expect(storage.clearTemperatureWorkspace).not.toHaveBeenCalled();
  });

  it('does not remount or clear the active chart when clicking its selected sidebar item', async () => {
    const user = userEvent.setup();
    render(<App />);
    await openImportedWorkspace();
    await user.click(screen.getByRole('button', { name: 'Confirm Data', exact: true }));
    const chart = await screen.findByRole('img', { name: 'Current vs Ambient Temperature' });
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    expect(screen.getByRole('img', { name: 'Current vs Ambient Temperature' })).toBe(chart);
    expect(storage.clearTemperatureWorkspace).not.toHaveBeenCalled();
    expect(screen.queryByRole('dialog', { name: 'Clear workspace?' })).toBeNull();
  });

  it('keeps sidebar resumption active when the confirmed deletion fails', async () => {
    const user = userEvent.setup();
    render(<App />);
    await openImportedWorkspace();
    vi.mocked(storage.clearTemperatureWorkspace).mockRejectedValueOnce(new Error('storage busy'));
    await user.click(screen.getByRole('button', { name: 'Back To Tools' }));
    await user.click(screen.getByRole('button', { name: 'Clear and Return' }));
    await screen.findByText(/Could not clear the workspace/);
    expect(window.location.pathname).toBe('/tools/temperature-rise');
    await user.click(sidebar().getByRole('button', { name: 'Settings', exact: true }));
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByText('4 Included / 0 Excluded Rows');
    expect(window.location.pathname).toBe('/tools/temperature-rise');
  });

  it.each(['later navigation', 'app unmount'] as const)('ignores a late saved-workspace lookup after %s', async action => {
    let resolve!: (exists: boolean) => void;
    vi.mocked(storage.hasTemperatureWorkspace).mockReturnValueOnce(new Promise(done => { resolve = done; }));
    window.history.replaceState({}, '', '/settings');
    const user = userEvent.setup();
    const view = render(<App />);
    await user.click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await waitFor(() => expect(storage.hasTemperatureWorkspace).toHaveBeenCalledOnce());
    if (action === 'app unmount') view.unmount();
    else await user.click(sidebar().getByRole('button', { name: 'Settings', exact: true }));
    await act(async () => resolve(true));
    expect(window.location.pathname).toBe('/settings');
    expect(screen.queryByRole('heading', { name: 'Temperature Rise', exact: true })).toBeNull();
  });

  it('opens the workspace recovery error instead of silently treating storage failure as an empty directory', async () => {
    vi.mocked(storage.hasTemperatureWorkspace).mockRejectedValueOnce(new Error('storage unavailable'));
    vi.mocked(storage.readTemperatureWorkspace).mockRejectedValueOnce(new Error('storage unavailable'));
    window.history.replaceState({}, '', '/settings');
    render(<App />);
    await userEvent.setup().click(sidebar().getByRole('button', { name: 'Tools', exact: true }));
    await screen.findByText(/Could not restore the workspace/);
    expect(window.location.pathname).toBe('/tools/temperature-rise');
    expect(storage.clearTemperatureWorkspace).not.toHaveBeenCalled();
    expect(storage.writeTemperatureWorkspace).not.toHaveBeenCalled();
  });
});
