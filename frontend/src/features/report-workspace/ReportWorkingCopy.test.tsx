import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as api from '../../api/client';
import * as authoring from '../../api/reportAuthoring';
import { ReportWorkspace } from './ReportWorkspace';

vi.mock('../../api/client', async () => ({
  ...await vi.importActual<typeof import('../../api/client')>('../../api/client'),
  fetchReportWorkspace: vi.fn(), fetchCurrentReport: vi.fn(), fetchCurrentCustomerReport: vi.fn(),
  fetchLatestProjectCustomerReportJob: vi.fn(), fetchReportUpdateSource: vi.fn(),
  updateCurrentReportLlcr: vi.fn(), updateEquipmentListOneClick: vi.fn(),
  generateInternalReport: vi.fn(), startProjectCustomerReportJob: vi.fn(),
}));
vi.mock('../../api/reportAuthoring', async () => ({
  ...await vi.importActual<typeof import('../../api/reportAuthoring')>('../../api/reportAuthoring'),
  getReportAuthoring: vi.fn(), updateWorkingCopyLlcr: vi.fn(), updateWorkingCopyEquipment: vi.fn(),
  adoptCurrentReportWorkingCopy: vi.fn(), generateCustomerReviewCopy: vi.fn(),
}));

const retained: authoring.ReportAuthoringState = {
  project_id: 'P1', revision: 4, sources: [], mappings: [], base_source_id: 'base',
  context: { dl_number: 'DL-001', matrix_id: 'M1', steps: [] },
  outputs: [{ output_id: 'W1', file_name: 'Reviewed Working.docx', operation: 'select_base', status: 'needs_review',
    issues: [], base_source_id: 'base', download_url: '/working', artifact: { sha256: 'w'.repeat(64) } }],
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(null);
  vi.mocked(api.fetchReportWorkspace).mockResolvedValue({ project_id: 'P1', basic_information_status: 'confirmed',
    confirmed_basic_information_version: 1, active_confirmed_matrix_id: 'M1', active_confirmed_matrix_revision: 1,
    latest_report_revision: null, report_revisions: [], datasets: [{ dataset_id: 'D1', dataset_type: 'llcr', revision: 1,
      project_id: 'P1', confirmed_matrix_id: 'M1', confirmed_matrix_revision: 1, source_file_name: 'LLCR.xlsx',
      source_sha256: 's', parser_profile_version: '1', validation_status: 'confirmed', confirmed_at: '', confirmed_by: '', entries: [] }] });
  vi.mocked(api.fetchCurrentReport).mockResolvedValue({ status: 'ready', mode: 'official', file_name: 'Official.docx',
    file_path: 'isolated/Official.docx', file_sha256: 'o'.repeat(64), report_revision_id: null,
    folder_path: 'isolated', official_folder_path: 'isolated', can_publish_to_official: false, download_url: '/official' });
  vi.mocked(api.fetchReportUpdateSource).mockImplementation(() => api.fetchCurrentReport('P1'));
  vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({ project_id: 'P1', status: 'missing', mode: 'official',
    file_name: null, file_sha256: null, internal_report_sha256: 'o'.repeat(64), generated_from_internal_sha256: null,
    can_generate: true, blockers: [], warnings: [], download_url: null });
  vi.mocked(authoring.getReportAuthoring).mockResolvedValue(retained);
  vi.mocked(authoring.updateWorkingCopyLlcr).mockResolvedValue({ ...retained, revision: 5,
    outputs: [...retained.outputs, { ...retained.outputs[0], output_id: 'W2', file_name: 'Working LLCR.docx', artifact: { sha256: 'l'.repeat(64) } }] });
  vi.mocked(authoring.updateWorkingCopyEquipment).mockResolvedValue({ ...retained, revision: 6,
    outputs: [...retained.outputs, { ...retained.outputs[0], output_id: 'W3', file_name: 'Working Equipment.docx', artifact: { sha256: 'e'.repeat(64) } }] });
  vi.mocked(authoring.generateCustomerReviewCopy).mockResolvedValue({ ...retained, revision: 5 });
});

it('restores the selected working copy and keeps section updates away from the official report', async () => {
  render(<ReportWorkspace projectId="P1" onBack={vi.fn()} />);
  expect(await screen.findByText('Reviewed Working.docx')).toBeTruthy();
  expect(screen.getByText('Official.docx')).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Generate Internal Report' }).matches(':disabled')).toBe(true);
  fireEvent.click(screen.getByRole('button', { name: 'Update LLCR Results' }));
  await waitFor(() => expect(authoring.updateWorkingCopyLlcr).toHaveBeenCalledWith('P1', {
    expected_revision: 4, expected_sha256: 'w'.repeat(64), dataset_revision_id: 'D1',
  }));
  expect(await screen.findByText('Working LLCR.docx')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Update Equipment List' }));
  await waitFor(() => expect(authoring.updateWorkingCopyEquipment).toHaveBeenCalledWith('P1', {
    expected_revision: 5, expected_sha256: 'l'.repeat(64),
  }));
  expect(await screen.findByText('Working Equipment.docx')).toBeTruthy();
  expect(api.updateCurrentReportLlcr).not.toHaveBeenCalled();
  expect(api.updateEquipmentListOneClick).not.toHaveBeenCalled();
  expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
});

it('does not fall back to official writes when the saved working-copy state cannot be read', async () => {
  vi.mocked(authoring.getReportAuthoring).mockRejectedValue(new Error('Source unavailable'));
  render(<ReportWorkspace projectId="P1" onBack={vi.fn()} />);
  await screen.findByText(/Unable to check the selected working copy/);
  expect(screen.getByRole('button', { name: 'Generate Internal Report' }).matches(':disabled')).toBe(true);
  fireEvent.click(screen.getByRole('button', { name: 'Update Equipment List' }));
  expect(api.updateEquipmentListOneClick).not.toHaveBeenCalled();
});

it('creates a customer review copy from the selected working version instead of the official report', async () => {
  render(<ReportWorkspace projectId="P1" onBack={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Review customer copy from this version' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Generate customer review copy' }));
  await waitFor(() => expect(authoring.generateCustomerReviewCopy).toHaveBeenCalledWith('P1', {
    expected_revision: 4, output_id: 'W1', output_sha256: 'w'.repeat(64), temperature_result_ids: [],
  }));
  expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
});

it('adopts the exact retained section-update draft instead of a different official report', async () => {
  vi.mocked(authoring.getReportAuthoring).mockResolvedValue({ ...retained, outputs: [] });
  vi.mocked(api.fetchReportUpdateSource).mockResolvedValue({ status: 'ready', mode: 'download_draft',
    file_name: 'Later manual draft.docx', file_sha256: 'd'.repeat(64), report_revision_id: null,
    draft_revision_id: 'draft-7', folder_path: null, official_folder_path: null, can_publish_to_official: false, download_url: '/draft' });
  vi.mocked(authoring.adoptCurrentReportWorkingCopy).mockResolvedValue(retained);
  render(<ReportWorkspace projectId="P1" onBack={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Use report source as working copy' }));
  await waitFor(() => expect(authoring.adoptCurrentReportWorkingCopy).toHaveBeenCalledWith('P1', {
    expected_revision: 4, source_sha256: 'd'.repeat(64), source_mode: 'download_draft',
  }));
  expect(await screen.findByText('Reviewed Working.docx')).toBeTruthy();
  expect(api.generateInternalReport).not.toHaveBeenCalled();
});

it('keeps missing equipment-source selection on the working-copy path', async () => {
  vi.mocked(authoring.updateWorkingCopyEquipment).mockResolvedValueOnce({ status: 'source_required', project_id: 'P1' });
  render(<ReportWorkspace projectId="P1" onBack={vi.fn()} />);
  await screen.findByText('Reviewed Working.docx');
  fireEvent.click(screen.getByRole('button', { name: 'Update Equipment List' }));
  const input = await screen.findByLabelText('Equipment IDs');
  fireEvent.change(input, { target: { value: 'DG-Q-0033' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save And Update' }));
  await waitFor(() => expect(authoring.updateWorkingCopyEquipment).toHaveBeenLastCalledWith('P1', {
    expected_revision: 4, expected_sha256: 'w'.repeat(64),
  }, { referencesText: 'DG-Q-0033' }));
  expect(api.updateEquipmentListOneClick).not.toHaveBeenCalled();
});
