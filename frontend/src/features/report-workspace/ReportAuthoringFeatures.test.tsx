import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import { ReportResultsImport } from './ReportResultsImport';
import { ReportResultUpdate } from './ReportResultUpdate';
import { ReportPhotoSlots } from './ReportPhotoSlots';
import { ReportCustomerCopy } from './ReportCustomerCopy';

vi.mock('../../api/reportAuthoring', () => ({ getReportSourceTable: vi.fn(), previewReportResult: vi.fn(), confirmReportResult: vi.fn(),
  getReportResultTargets: vi.fn(), applyReportResult: vi.fn(), getReportPhotoSlots: vi.fn(), getReportPhotoImage: vi.fn(),
  downloadReportArtifact: vi.fn(), applyReportPhotos: vi.fn(), checkCustomerReviewCopy: vi.fn(), generateCustomerReviewCopy: vi.fn(), downloadCustomerPart: vi.fn() }));

const step = { group_id: 'g1', row_id: 'r1', group_label: '1', step_token: '2', test_item: 'Contact resistance' };
const output = { output_id: 'copy1', file_name: 'Copy.docx', operation: 'prepare_base', status: 'needs_review', issues: [],
  base_source_id: 'original', download_url: '/copy', artifact: { sha256: 'b'.repeat(64) } };
const initial: api.ReportAuthoringState = { project_id: 'P1', revision: 2, base_source_id: 'original',
  context: { dl_number: 'DL-2026-01-001', matrix_id: 'matrix1', steps: [step] }, mappings: [], outputs: [output],
  sources: [{ source_id: 'data1', role: 'cr', file_name: 'CR.csv', sha256: 'a'.repeat(64), size_bytes: 1,
    created_at: '', report_dl: '', download_url: '/data' }] };
const result: api.ReportResult = { result_id: 'result1', kind: 'cr', source_id: 'data1', source_sha256: 'a'.repeat(64),
  matrix_id: 'matrix1', target: step, profile: {} as api.ResultImportRequest, outcome: 'pending', acceptance_reason: '', preview_sha256: 'c'.repeat(64),
  data: { unit: 'mΩ', quantity: 'absolute', sheet_name: 'Sheet1', rows: [{ sample_id: 'SN1', record_id: 'r9', color: 'Black', current_a: '450', resistance_mohm: '0.085511' }] } };

beforeEach(() => { vi.resetAllMocks(); });

it('requires explicit CR columns and Matrix mapping, preserving pending outcomes', async () => {
  vi.mocked(api.getReportSourceTable).mockResolvedValue({ file_name: 'CR.csv', sheet_name: 'Sheet1', sheet_names: ['Sheet1'], rows: [['SN', 'V', 'I'], ['SN1', 38.48, 450]] });
  vi.mocked(api.previewReportResult).mockResolvedValue(result);
  vi.mocked(api.confirmReportResult).mockResolvedValue({ ...initial, revision: 3, results: [result] });
  const onChanged = vi.fn();
  render(<ReportResultsImport projectId="P1" state={initial} disabled={false} onChanged={onChanged} />);
  fireEvent.change(screen.getByLabelText('Measurement source'), { target: { value: 'data1' } });
  fireEvent.click(screen.getByText('Inspect measurement workbook'));
  await screen.findByText('Source preview (first 20 rows)');
  fireEvent.change(screen.getByLabelText('Sample SN column'), { target: { value: '1' } });
  fireEvent.change(screen.getByLabelText('Voltage drop column'), { target: { value: '2' } });
  fireEvent.change(screen.getByLabelText('Measured current column (A)'), { target: { value: '3' } });
  fireEvent.change(screen.getByLabelText('Result Group / Step'), { target: { value: '0' } });
  fireEvent.click(screen.getByText('Preview mapped results'));
  await screen.findByText('0.085511 mΩ');
  expect(api.previewReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({ columns: { sample: 1, voltage: 2, current: 3 }, unit: 'mV', outcome: 'pending' }));
  expect((screen.getByText('Confirm result mapping') as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByLabelText('I verified the source columns, samples, units and Matrix target'));
  fireEvent.click(screen.getByText('Confirm result mapping'));
  await waitFor(() => expect(api.confirmReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({ preview_sha256: 'c'.repeat(64) })));
});

it('updates only explicitly chosen report destinations with the inspected exact hash', async () => {
  vi.mocked(api.getReportResultTargets).mockResolvedValue({ output_sha256: 'b'.repeat(64), result_id: 'result1',
    result_rows: [{ table_index: 3, row_index: 4, step: '2', test_item: 'Contact resistance' }],
    appendix_tables: [{ table_index: 7, title: 'Appendix C: Contact Resistance', headers: ['SN', 'R'] }] });
  vi.mocked(api.applyReportResult).mockResolvedValue({ ...initial, revision: 3 });
  render(<ReportResultUpdate projectId="P1" state={{ ...initial, results: [result] }} disabled={false} onChanged={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Confirmed measurements'), { target: { value: 'result1' } });
  fireEvent.click(screen.getByText('Inspect report destinations'));
  await screen.findByLabelText('Appendix destination');
  fireEvent.change(screen.getByLabelText('Appendix destination'), { target: { value: '7' } });
  expect((screen.getByText('Update report copy') as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByLabelText('I checked the result row, appendix, title and measurement meaning'));
  fireEvent.click(screen.getByText('Update report copy'));
  await waitFor(() => expect(api.applyReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({
    expected_revision: 2, output_sha256: 'b'.repeat(64), result_table: 3, result_row: 4, appendix_table: 7 })));
});

it('requires photo comparison and carries explicit crop and transform choices', async () => {
  vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:photo'), revokeObjectURL: vi.fn() }));
  vi.mocked(api.getReportPhotoSlots).mockResolvedValue({ output_sha256: 'b'.repeat(64), slots: [{ slot_id: 'photo-1', caption: 'Figure 1',
    width_emu: 100, height_emu: 100, media_sha256: 'd'.repeat(64), supported: true, reason: null, rotation: 5400000, flip_horizontal: false, flip_vertical: false }] });
  vi.mocked(api.getReportPhotoImage).mockResolvedValue({ blob: new Blob(), fileName: null });
  vi.mocked(api.downloadReportArtifact).mockResolvedValue({ blob: new Blob(), fileName: null });
  vi.mocked(api.applyReportPhotos).mockResolvedValue({ ...initial, revision: 3 });
  const state = { ...initial, sources: initial.sources.map(item => ({ ...item, role: 'photo' as const, file_name: 'Photo.png' })) };
  render(<ReportPhotoSlots projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByText('Inspect photo slots'));
  await screen.findByLabelText('Approved photo slot');
  fireEvent.change(screen.getByLabelText('Approved photo slot'), { target: { value: 'photo-1' } });
  fireEvent.change(screen.getByLabelText('Replacement photo'), { target: { value: 'data1' } });
  fireEvent.change(screen.getByLabelText('Photo fit'), { target: { value: 'centre_crop' } });
  fireEvent.click(screen.getByLabelText("I checked and accept this slot's existing rotation/flips for the new photo"));
  fireEvent.click(screen.getByText('Compare source photos'));
  await screen.findByAltText('Replacement source photo');
  fireEvent.click(screen.getByLabelText('I verified the sample, slot, crop and orientation'));
  fireEvent.click(screen.getByText('Replace photo in a new copy'));
  await waitFor(() => expect(api.applyReportPhotos).toHaveBeenCalledWith('P1', expect.objectContaining({ assignments: [
    { slot_id: 'photo-1', source_id: 'data1', crop_mode: 'centre_crop', accept_slot_transform: true }] })));
});

it('does not silently approve unknown customer images or disclosure scope', async () => {
  const customer = { ...output, output_id: 'customer1', audit: { passed: false, sensitive_terms: [], forbidden_project_ids: [], reviewed_parts: {}, disclosure_scope_confirmed: false,
    issues: [{ code: 'visual_review_required', location: 'word/media/image1.png', message: 'Review image pixels', sha256: 'd'.repeat(64) }] } };
  vi.mocked(api.checkCustomerReviewCopy).mockResolvedValue({ ...initial, revision: 3, customer_outputs: [customer] });
  render(<ReportCustomerCopy projectId="P1" state={{ ...initial, customer_outputs: [customer] }} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByText('Check saved customer package'));
  await waitFor(() => expect(api.checkCustomerReviewCopy).toHaveBeenCalledWith('P1', expect.objectContaining({
    reviewed_parts: {}, disclosure_scope_confirmed: false })));
  expect(screen.queryByText('Package disclosure checks passed; not release approval')).toBeNull();
});

it('shows every selected old temperature block and sends an explicitly confirmed bounded region', async () => {
  vi.mocked(api.getReportResultTargets).mockResolvedValue({ output_sha256: 'b'.repeat(64), result_id: 'result1',
    result_rows: [{ table_index: 8, row_index: 2, step: '2', test_item: 'Temperature rise' }], appendix_tables: [],
    unreconciled_temperature_evidence: true, evidence_blocks: [
      { block_index: 62, kind: 'p', text: 'Figure 14: Setup', drawing_count: 0, temperature_evidence: false, protected_other_step: false, owned_current_result: false },
      { block_index: 64, kind: 'p', text: 'Table-1: Temperature Rise Measurements', drawing_count: 0, temperature_evidence: true, protected_other_step: false, owned_current_result: false },
      { block_index: 65, kind: 'tbl', text: 'Old measured table', drawing_count: 0, temperature_evidence: true, protected_other_step: false, owned_current_result: false },
      { block_index: 66, kind: 'p', text: '', drawing_count: 1, temperature_evidence: false, protected_other_step: false, owned_current_result: false },
      { block_index: 67, kind: 'p', text: 'Old 496.9A conclusion', drawing_count: 0, temperature_evidence: true, protected_other_step: false, owned_current_result: false },
    ] });
  vi.mocked(api.applyReportResult).mockResolvedValue({ ...initial, revision: 3 });
  render(<ReportResultUpdate projectId="P1" state={{ ...initial, results: [{ ...result, kind: 'temperature' }] }} disabled={false} onChanged={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Confirmed measurements'), { target: { value: 'result1' } });
  fireEvent.click(screen.getByText('Inspect report destinations'));
  await screen.findByLabelText('First evidence block');
  fireEvent.change(screen.getByLabelText('First evidence block'), { target: { value: '64' } });
  fireEvent.change(screen.getByLabelText('Last evidence block'), { target: { value: '67' } });
  expect(screen.getByLabelText('Selected evidence blocks').textContent).toContain('1 image/object(s)');
  expect(screen.getByLabelText('Selected evidence blocks').textContent).not.toContain('Figure 14');
  expect((screen.getByText('Update report copy') as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByLabelText('I checked the result row and complete old temperature evidence region, including table, curve and conclusion'));
  fireEvent.click(screen.getByText('Update report copy'));
  await waitFor(() => expect(api.applyReportResult).toHaveBeenCalledWith('P1', expect.objectContaining({
    output_sha256: 'b'.repeat(64), evidence_start: 64, evidence_end: 67, evidence_selection_confirmed: true, appendix_table: null })));
});
