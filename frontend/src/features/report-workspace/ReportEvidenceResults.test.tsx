import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import { ReportEvidenceResults } from './ReportEvidenceResults';

vi.mock('../../api/reportAuthoring', async () => ({ ...await vi.importActual<typeof import('../../api/reportAuthoring')>('../../api/reportAuthoring'),
  getReportSourceTable: vi.fn(), getReportSourceRegion: vi.fn(), previewReportResult: vi.fn(), confirmReportResult: vi.fn() }));
const state: api.ReportAuthoringState = { project_id: 'P1', revision: 1, mappings: [], outputs: [], base_source_id: null,
  context: { dl_number: 'DL-001', matrix_id: 'M1', steps: [{ group_id: 'G1', row_id: 'R1', group_label: 'B', step_token: '2', test_item: 'DWV' }] },
  sources: ['raw.xlsx', 'source.docx', 'other.docx'].map((name, index) => ({ source_id: String(index), file_name: name, role: 'evidence', sha256: 'a'.repeat(64), size_bytes: 100, created_at: '', report_dl: '', download_url: '' })) };
beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.getReportSourceTable).mockResolvedValue({ file_name: 'raw.xlsx', sheet_name: 'Group B', sheet_names: ['Group B', 'Group Ga'], rows: [['', 'SN1'], ['P1/P2', 69.95]] });
  vi.mocked(api.previewReportResult).mockResolvedValue({ kind: 'electrical', source_id: '0', source_sha256: 'a'.repeat(64), matrix_id: 'M1',
    target: state.context.steps[0], profile: {} as api.ResultImportRequest, outcome: 'pending', acceptance_reason: '', preview_sha256: 'b'.repeat(64),
    data: { sheet_name: 'Group B', unit: 'µA', quantity: 'electrical', missing: true,
      rows: [{ sample_id: 'SN1', pair: 'P1/P2', stage: 'Final', measurement: 'dwv', value: '69.95', unit: 'µA', breakdown: 'not_recorded' }] } });
});
const show = () => render(<ReportEvidenceResults projectId="P1" state={state} disabled={false} beginOperation={() => () => {}} onChanged={vi.fn()} />);

it('reads horizontal source cells with Excel headers and invalidates stale measurement preview', async () => {
  show();
  fireEvent.change(screen.getByLabelText('Evidence workbook'), { target: { value: '0' } });
  fireEvent.click(screen.getByRole('button', { name: 'Read evidence workbook' }));
  await screen.findByLabelText('Evidence sheet');
  expect(screen.getByRole('columnheader', { name: 'B', hidden: true })).toBeTruthy();
  fireEvent.change(screen.getByLabelText('Evidence Group / Step'), { target: { value: '0' } });
  fireEvent.change(screen.getByLabelText('Stage'), { target: { value: 'Final' } });
  fireEvent.change(screen.getByLabelText('Electrical quantity'), { target: { value: 'dwv' } });
  fireEvent.change(screen.getByLabelText('sample source cell'), { target: { value: 'B1' } });
  fireEvent.change(screen.getByLabelText('pair source cell'), { target: { value: 'A2' } });
  fireEvent.change(screen.getByLabelText('value source cell'), { target: { value: 'B2' } });
  fireEvent.click(screen.getByRole('button', { name: 'Preview selected measurements' }));
  expect(await screen.findByText('69.95 µA')).toBeTruthy();
  expect(api.previewReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({ outcome: 'pending', semantic_selection: expect.objectContaining({ records: [expect.objectContaining({ cells: { sample: 'B1', pair: 'A2', value: 'B2' } })] }) }));
  fireEvent.change(screen.getByLabelText('Measurement family'), { target: { value: 'resistance_stages' } });
  await waitFor(() => expect(screen.queryByRole('button', { name: 'Retain measurements for report' })).toBeNull());
});

it('clears applicability and disclosure approvals when the related source changes', () => {
  show();
  fireEvent.change(screen.getByLabelText('Related evidence source'), { target: { value: '1' } });
  const applicability = screen.getByLabelText('I confirmed this exact evidence scope and its applicability, not an automatic Pass');
  const disclosure = screen.getByLabelText('This exact related-report reference and adopted region may appear in the customer copy');
  fireEvent.click(applicability); fireEvent.click(disclosure);
  expect(applicability).toHaveProperty('checked', true);
  fireEvent.change(screen.getByLabelText('Related evidence source'), { target: { value: '2' } });
  expect(applicability).toHaveProperty('checked', false); expect(disclosure).toHaveProperty('checked', false);
  expect(screen.getByLabelText('Related evidence outcome')).toHaveProperty('value', 'pending');
});
