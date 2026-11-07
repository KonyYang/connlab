import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import { ReportAuthoringPanel } from './ReportAuthoringPanel';

vi.mock('../../api/reportAuthoring', async () => ({
  ...await vi.importActual<typeof import('../../api/reportAuthoring')>('../../api/reportAuthoring'),
  getReportAuthoring: vi.fn(), getReportToolsPackage: vi.fn(), uploadReportSource: vi.fn(),
  previewReportResult: vi.fn(), confirmReportResult: vi.fn(),
}));

const state: api.ReportAuthoringState = { project_id: 'P1', revision: 2, base_source_id: null, outputs: [], mappings: [],
  context: { dl_number: 'DL-032', matrix_id: 'M1', steps: [{ group_id: 'G1', group_label: 'Ab', row_id: 'R1', step_token: '2', test_item: 'Retention force' }] },
  sources: [{ source_id: 'package-1', role: 'tools_result_package', file_name: 'Mechanical.results.zip', sha256: 'p'.repeat(64),
    size_bytes: 100, created_at: '', report_dl: '', download_url: '/package' }] };

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.getReportAuthoring).mockResolvedValue(state);
  vi.mocked(api.getReportToolsPackage).mockResolvedValue({ entries: [
    { entry_id: 'force-1', label: 'Retention force — Orange', kind: 'mechanical', supported_for_report: true, reason: '', source_names: ['original.pdf'] },
    { entry_id: 'qual-1', label: 'Mis-mating', kind: 'mechanical_qualitative', supported_for_report: false,
      reason: 'Retained for review; qualitative report placement is not supported in this batch.', source_names: ['raw.xls'] },
  ] });
  vi.mocked(api.previewReportResult).mockResolvedValue({ result_id: 'preview', kind: 'mechanical', source_id: 'package-1',
    source_sha256: 'p'.repeat(64), matrix_id: 'M1', target: state.context.steps[0], outcome: 'pending', acceptance_reason: '',
    profile: { package_entry_id: 'force-1' } as api.ResultImportRequest, preview_sha256: 'v'.repeat(64),
    data: { sheet_name: 'Retention', unit: 'N', quantity: 'peak', force_field: 'withdraw', withdraw_magnitude: true,
      rows: [{ sample_id: 'SN1', record_id: '3', color: 'Orange', part: 'Cable end', value: 250.1, raw_value: -250.1 }] } });
  vi.mocked(api.confirmReportResult).mockResolvedValue({ ...state, revision: 3 });
});

it('shows a qualitative matrix as observations without inheriting its Pass as the report outcome', async () => {
  vi.mocked(api.getReportToolsPackage).mockResolvedValue({ entries: [{ entry_id: 'qual-1', label: 'Mis-mating',
    kind: 'mechanical_qualitative', supported_for_report: true, reason: '', source_names: ['raw.xls'] }] });
  vi.mocked(api.previewReportResult).mockResolvedValue({ kind: 'mechanical_qualitative', source_id: 'package-1',
    source_sha256: 'p'.repeat(64), matrix_id: 'M1', target: state.context.steps[0], outcome: 'pending', acceptance_reason: '',
    profile: {} as api.ResultImportRequest, preview_sha256: 'v'.repeat(64),
    data: { sheet_name: '', unit: '', quantity: 'qualitative', raw_curves: ['72'], tables: [{ title: 'Mis-mating observations',
      row_heading: 'Receptacle', column_heading: 'Header', samples: ['SN1'], columns: ['Orange', 'Black'], results: [['Pass', 'Fail']] }] } });
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByRole('button', { name: 'Update report content' }));
  fireEvent.change(await screen.findByLabelText('Reviewed Tools result'), { target: { value: 'qual-1' } });
  fireEvent.change(screen.getByLabelText('Package result Group / Step'), { target: { value: '0' } });
  fireEvent.click(screen.getByRole('button', { name: 'Preview Tools result' }));
  expect(await screen.findByRole('cell', { name: 'Fail' })).toBeTruthy();
  expect(screen.getByRole('columnheader', { name: 'Header Black' })).toBeTruthy();
  expect(screen.getByText(/not one curve per observation/)).toBeTruthy();
  expect(screen.getByLabelText('Package report outcome')).toHaveProperty('value', 'pending');
});

it('reuses reviewed Tools results without remapping columns or inheriting report Pass', async () => {
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByRole('button', { name: 'Update report content' }));
  const entries = await screen.findByLabelText('Reviewed Tools result');
  expect(screen.getByText(/qualitative report placement is not supported/)).toBeTruthy();
  expect(screen.queryByLabelText('Force column (N)')).toBeNull();
  fireEvent.change(entries, { target: { value: 'force-1' } });
  fireEvent.change(screen.getByLabelText('Package result Group / Step'), { target: { value: '0' } });
  expect(screen.getByLabelText('Package report outcome')).toHaveProperty('value', 'pending');
  fireEvent.click(screen.getByRole('button', { name: 'Preview Tools result' }));
  await waitFor(() => expect(api.previewReportResult).toHaveBeenCalledWith('P1', {
    expected_revision: 2, source_id: 'package-1', package_entry_id: 'force-1', kind: 'mechanical',
    group_id: 'G1', row_id: 'R1', step_token: '2', outcome: 'pending', acceptance_reason: '',
  }));
  expect(await screen.findByText('250.1 N')).toBeTruthy();
  expect(screen.getByText('Cable end')).toBeTruthy();
  expect(screen.getByText('-250.1 N')).toBeTruthy();
  expect(screen.getByText(/Source force field: withdraw/)).toBeTruthy();
  expect(screen.getByText(/Magnitude selected in Tools; original signed values are retained/)).toBeTruthy();
  fireEvent.click(screen.getByLabelText('I verified this Tools result and its report Group / Step'));
  fireEvent.click(screen.getByRole('button', { name: 'Confirm Tools result for report' }));
  await waitFor(() => expect(api.confirmReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({
    package_entry_id: 'force-1', outcome: 'pending', preview_sha256: 'v'.repeat(64),
  })));
});

it('shows the retained hold duration and specimen part before report confirmation', async () => {
  const base = await api.previewReportResult('P1', {} as api.ResultImportRequest);
  vi.mocked(api.previewReportResult).mockResolvedValue({ ...base, data: {
    sheet_name: 'Hold', unit: 'N', quantity: 'hold', force_field: 'end1', withdraw_magnitude: false,
    rows: [{ sample_id: 'SN1', record_id: '3', color: 'Orange', part: 'Board end', value: 240, raw_value: 240, hold_seconds: 6 }],
  } });
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByRole('button', { name: 'Update report content' }));
  fireEvent.change(await screen.findByLabelText('Reviewed Tools result'), { target: { value: 'force-1' } });
  fireEvent.change(screen.getByLabelText('Package result Group / Step'), { target: { value: '0' } });
  fireEvent.click(screen.getByRole('button', { name: 'Preview Tools result' }));
  expect(await screen.findByText('Board end')).toBeTruthy();
  expect(screen.getByRole('columnheader', { name: 'Hold / s' })).toBeTruthy();
  expect(screen.getByRole('cell', { name: '6' })).toBeTruthy();
  expect(screen.getByText(/Source force field: end1/)).toBeTruthy();
});

it('recognizes a Tools ZIP on upload without requiring a measurement source role', async () => {
  vi.mocked(api.getReportAuthoring).mockResolvedValue({ ...state, sources: [] });
  vi.mocked(api.uploadReportSource).mockResolvedValue(state);
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByRole('button', { name: 'Choose report base' }));
  const file = new File(['package'], 'Mechanical.results.zip', { type: 'application/zip' });
  fireEvent.change(await screen.findByLabelText('Source file'), { target: { files: [file] } });
  fireEvent.click(screen.getByRole('button', { name: 'Retain source copy' }));
  await waitFor(() => expect(api.uploadReportSource).toHaveBeenCalledWith('P1', file, 'tools_result_package', 2));
  expect(await screen.findByLabelText('Reviewed Tools result')).toBeTruthy();
});

it('requires explicit cross-project applicability and keeps temperature sample identities separate from channel numbers', async () => {
  vi.mocked(api.getReportToolsPackage).mockResolvedValue({ project_hint: 'DL-032B', entries: [{
    entry_id: 'temp-1', label: 'Temperature', kind: 'temperature', supported_for_report: true, reason: '',
    source_names: ['temperature.xlsx'], sample_count: 2, sample_ids: [],
  }] });
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByRole('button', { name: 'Update report content' }));
  fireEvent.change(await screen.findByLabelText('Reviewed Tools result'), { target: { value: 'temp-1' } });
  fireEvent.change(screen.getByLabelText('Package result Group / Step'), { target: { value: '0' } });
  const button = screen.getByRole('button', { name: 'Preview Tools result' });
  expect(button.matches(':disabled')).toBe(true);
  expect(screen.getByLabelText(/Temperature sample identities/)).toHaveProperty('value', '');
  fireEvent.change(screen.getByLabelText(/Temperature sample identities/), { target: { value: 'SN1, SN2' } });
  fireEvent.click(screen.getByLabelText(/I confirm results identified as DL-032B/));
  fireEvent.click(button);
  await waitFor(() => expect(api.previewReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({
    package_entry_id: 'temp-1', source_project_confirmed: true, sample_ids: ['SN1', 'SN2'], outcome: 'pending',
  })));
});
