import { useState } from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as batchApi from '../../api/reportAuthoringBatch';
import * as reportApi from '../../api/reportAuthoring';
import { ReportBatchPreparation } from './ReportBatchPreparation';

vi.mock('../../api/reportAuthoringBatch', () => ({
  getReportInventory: vi.fn(), retainReportInventory: vi.fn(), getReportCoverage: vi.fn(),
  previewReportAssembly: vi.fn(), applyReportAssembly: vi.fn(),
}));
vi.mock('../../api/reportAuthoring', async () => ({
  ...await vi.importActual<typeof import('../../api/reportAuthoring')>('../../api/reportAuthoring'),
  getReportResultTargets: vi.fn(), getReportPhotoSlots: vi.fn(),
}));

const step = { group_id: 'g1', row_id: 'r1', group_label: 'Ab', step_token: '2', test_item: 'Retention force' };
const state: batchApi.ReportBatchState = {
  project_id: 'P1', revision: 7, base_source_id: 's1', sources: [], mappings: [],
  context: { dl_number: 'DL-032', matrix_id: 'M1', steps: [step] },
  outputs: [{ output_id: 'out1', file_name: 'Working.docx', status: 'needs_review', operation: 'select_base',
    issues: [], download_url: '/working', base_source_id: 's1', artifact: { sha256: 'a'.repeat(64) } }],
  results: [{ result_id: 'force1', kind: 'mechanical', source_id: 'source1', source_sha256: 's'.repeat(64), matrix_id: 'M1',
    target: step, profile: {} as reportApi.ResultImportRequest, outcome: 'pending', acceptance_reason: '', preview_sha256: 'v',
    data: { sheet_name: 'Retention', unit: 'N', quantity: 'hold' } }],
};
const inventory: batchApi.ReportInventory = { root_token: 'root-token', available: true, reason: '', warnings: [], items: [
  { relative_path: 'Test results/force.zip', name: 'force.zip', size_bytes: 100, modified_ns: '1', file_token: 'file-token',
    suggested_role: 'tools_result_package', status: 'candidate', reason: '' },
] };
const coverage: batchApi.ReportCoverage = { matrix_id: 'M1', has_confirmed_matrix: true, complete: false,
  counts: { ready: 0, missing: 0, needs_review: 1, not_applicable: 0 }, pending_mappings: [],
  rows: [{ ...step, status: 'needs_review', reasons: ['Report outcome remains pending.'], result_ids: ['force1'], usable_result_ids: ['force1'], applied_result_ids: [] }] };

function Host({ initial = state }: { initial?: batchApi.ReportBatchState }) {
  const [current, setCurrent] = useState(initial);
  return <ReportBatchPreparation projectId={current.project_id} state={current} disabled={false} onChanged={setCurrent} />;
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(batchApi.getReportInventory).mockResolvedValue(inventory);
  vi.mocked(batchApi.getReportCoverage).mockResolvedValue(coverage);
  vi.mocked(reportApi.getReportPhotoSlots).mockResolvedValue({ output_sha256: 'a'.repeat(64), slots: [] });
  vi.mocked(reportApi.getReportResultTargets).mockResolvedValue({ output_sha256: 'a'.repeat(64), result_id: 'force1',
    result_rows: [{ table_index: 2, row_index: 3, step: '2', test_item: 'Retention force' }], appendix_tables: [] });
  vi.mocked(batchApi.retainReportInventory).mockResolvedValue({ ...state, revision: 8 });
});

it('scans only on request, exposes unresolved coverage, and retains selected files with their exact scan tokens', async () => {
  render(<Host />);
  expect(batchApi.getReportInventory).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  expect(await screen.findByText('Report outcome remains pending.')).toBeTruthy();
  expect(screen.getByText(/Ready means evidence is available, not a Pass decision/)).toBeTruthy();
  expect(screen.getByLabelText('Retain Test results/force.zip')).toHaveProperty('checked', false);
  fireEvent.click(screen.getByLabelText('Retain Test results/force.zip'));
  fireEvent.click(screen.getByRole('button', { name: 'Retain selected source copies' }));
  await waitFor(() => expect(batchApi.retainReportInventory).toHaveBeenCalledWith('P1', {
    expected_revision: 7, root_token: 'root-token',
    items: [{ relative_path: 'Test results/force.zip', file_token: 'file-token', role: 'tools_result_package' }],
  }));
  expect(batchApi.applyReportAssembly).not.toHaveBeenCalled();
});

it('previews selected updates and consumes the durable plan once without changing an outcome or the official report', async () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'plan1', preview_sha256: 'p'.repeat(64), base_output_id: 'out1', output_sha256: 'a'.repeat(64), status: 'prepared',
    can_apply: true, changes: [{ kind: 'result', label: 'Update retention result and Appendix C.' }], issues: [], omitted: ['Other results remain unchanged.'],
    request: { expected_revision: 7, output_id: 'out1', output_sha256: 'a'.repeat(64), mapping_ids: [],
      results: [{ result_id: 'force1', result_table: 2, result_row: 3, appendix_table: null, appendix_title: 'Appendix C' }], assignments: [] } };
  vi.mocked(batchApi.previewReportAssembly).mockResolvedValue({ ...state, revision: 8, assembly_plan: plan });
  vi.mocked(batchApi.applyReportAssembly).mockResolvedValue({ ...state, revision: 9, assembly_plan: null,
    outputs: [...state.outputs, { ...state.outputs[0], output_id: 'out2', file_name: 'Batch.docx' }] });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  fireEvent.click(await screen.findByLabelText('Include Group Ab / 2 / mechanical'));
  const result = screen.getByRole('group', { name: 'Group Ab / 2 / mechanical' });
  fireEvent.change(within(result).getByLabelText('Evidence destination'), { target: { value: 'appendix' } });
  fireEvent.change(within(result).getByLabelText('Appendix destination'), { target: { value: 'new' } });
  fireEvent.change(within(result).getByLabelText('Appendix identifier'), { target: { value: 'Appendix C' } });
  fireEvent.click(screen.getByRole('button', { name: 'Preview selected updates' }));
  await waitFor(() => expect(batchApi.previewReportAssembly).toHaveBeenCalledWith('P1', plan.request));
  expect(await screen.findByText('Update retention result and Appendix C.')).toBeTruthy();
  expect(screen.getByText('Other results remain unchanged.')).toBeTruthy();
  fireEvent.click(screen.getByLabelText('I checked this batch preview; unresolved items remain pending'));
  fireEvent.click(screen.getByRole('button', { name: 'Generate one working copy' }));
  await waitFor(() => expect(batchApi.applyReportAssembly).toHaveBeenCalledWith('P1', {
    expected_revision: 8, plan_id: 'plan1', preview_sha256: 'p'.repeat(64),
  }));
  expect(batchApi.applyReportAssembly).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole('button', { name: 'Generate one working copy' })).toBeNull();
});

it('restores a persisted preview after reopening and refuses a plan for a different working copy', () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'saved-plan', preview_sha256: 'p', base_output_id: 'previous-output',
    output_sha256: 'old', status: 'prepared', can_apply: true, changes: [{ kind: 'result', label: 'Saved update' }], issues: [], omitted: [],
    request: { expected_revision: 6, output_id: 'previous-output', output_sha256: 'old', mapping_ids: [], results: [], assignments: [] } };
  render(<Host initial={{ ...state, assembly_plan: plan }} />);
  expect(screen.getByText(/Preview no longer matches the selected working copy/)).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Generate one working copy' }).matches(':disabled')).toBe(true);
});

it('does not apply a late inspection to a switched project', async () => {
  let resolve!: (value: batchApi.ReportInventory) => void;
  vi.mocked(batchApi.getReportInventory).mockReturnValue(new Promise(done => { resolve = done; }));
  const { rerender } = render(<ReportBatchPreparation projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  rerender(<ReportBatchPreparation projectId="P2" state={{ ...state, project_id: 'P2' }} disabled={false} onChanged={vi.fn()} />);
  resolve(inventory);
  await waitFor(() => expect(screen.queryByLabelText('Retain Test results/force.zip')).toBeNull());
  expect(batchApi.retainReportInventory).not.toHaveBeenCalled();
});

it('keeps coverage and retained-source updates usable when project materials are unavailable', async () => {
  vi.mocked(batchApi.getReportInventory).mockResolvedValue({ available: false, reason: 'No linked project folder. Manual upload is available.', root_token: null, warnings: [], items: [] });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  expect(await screen.findByText('No linked project folder. Manual upload is available.')).toBeTruthy();
  expect(screen.getByText('Report outcome remains pending.')).toBeTruthy();
  expect(screen.getByLabelText('Include Group Ab / 2 / mechanical').matches(':disabled')).toBe(false);
  expect(screen.queryByRole('button', { name: 'Retain selected source copies' })).toBeNull();
});

it('does not hide the material scan when one report target inspection fails', async () => {
  vi.mocked(reportApi.getReportResultTargets).mockRejectedValue(new Error('This result has no supported Word target.'));
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  expect(await screen.findByLabelText('Retain Test results/force.zip')).toBeTruthy();
  expect(screen.getByText('This result has no supported Word target.')).toBeTruthy();
  expect(screen.getByLabelText('Include Group Ab / 2 / mechanical').matches(':disabled')).toBe(true);
});

it('requires an explicit result row when the report contains multiple matching candidates', async () => {
  vi.mocked(reportApi.getReportResultTargets).mockResolvedValue({ output_sha256: 'a'.repeat(64), result_id: 'force1',
    result_rows: [{ table_index: 2, row_index: 3, step: '2', test_item: 'Retention force' },
      { table_index: 3, row_index: 1, step: '2', test_item: 'Retention force' }], appendix_tables: [] });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  fireEvent.click(await screen.findByLabelText('Include Group Ab / 2 / mechanical'));
  expect(screen.getByLabelText('Report result row')).toHaveProperty('value', '');
  fireEvent.change(screen.getByLabelText('Appendix destination'), { target: { value: 'new' } });
  fireEvent.change(screen.getByLabelText('Appendix identifier'), { target: { value: 'Appendix C' } });
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(true);
  fireEvent.change(screen.getByLabelText('Report result row'), { target: { value: '1' } });
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(false);
  expect(batchApi.previewReportAssembly).not.toHaveBeenCalled();
});

it('restores a completed batch as evidence, without offering a duplicate generation', () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'done', preview_sha256: 'p', status: 'completed', can_apply: false,
    base_output_id: 'old', output_sha256: 'old-sha', applied_output_id: 'out1', changes: [], issues: [], omitted: [],
    request: { output_id: 'old', output_sha256: 'old-sha', mapping_ids: [], results: [], assignments: [] } };
  render(<Host initial={{ ...state, assembly_plan: plan }} />);
  expect(screen.getByText(/This batch already produced a working copy/)).toBeTruthy();
  expect(screen.queryByRole('button', { name: 'Generate one working copy' })).toBeNull();
  expect(batchApi.applyReportAssembly).not.toHaveBeenCalled();
});

it('uses automatic placement for a unique match and shows the resolved locations and exact changes before generation', async () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'auto', preview_sha256: 'p', status: 'prepared', can_apply: true,
    base_output_id: 'out1', output_sha256: 'a'.repeat(64), prepared_revision: 8,
    changes: [{ kind: 'result', label: 'Group Ab / Step 2 retention', result_id: 'force1' }],
    issues: ['Engineering acceptance is pending.'], omitted: [],
    request: { output_id: 'out1', output_sha256: 'a'.repeat(64), mapping_ids: [], results: [{ result_id: 'force1' }], assignments: [] },
    document_plan: { facts: [{ old: 'Old product', new: 'New product', occurrences: 2, parts: ['word/document.xml'] }],
      results: [{ result_id: 'force1', target: { result_table: 2, result_row: 3, appendix_title: 'Appendix B', appendix_table: null },
        current_result: 'Previous retention: 250 N', current_comment: 'Historical Pass',
        new_result: 'Minimum retention: 245 N; maintained 6 s', new_comment: '' }] },
  };
  vi.mocked(batchApi.previewReportAssembly).mockResolvedValue({ ...state, revision: 8, assembly_plan: plan });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  fireEvent.click(await screen.findByLabelText('Include Group Ab / 2 / mechanical'));
  expect(screen.getByLabelText('Evidence destination')).toHaveProperty('value', 'automatic');
  expect(screen.queryByLabelText('Appendix identifier')).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Preview selected updates' }));
  await waitFor(() => expect(batchApi.previewReportAssembly).toHaveBeenCalledWith('P1', { ...plan.request, expected_revision: 7 }));
  expect(await screen.findByRole('table', { name: 'Resolved batch result locations' })).toBeTruthy();
  expect(screen.getByRole('cell', { name: 'Appendix B' })).toBeTruthy();
  expect(screen.getByRole('cell', { name: 'Table 2, row 3' })).toBeTruthy();
  expect(screen.getByRole('cell', { name: 'Old product' })).toBeTruthy();
  expect(screen.getByRole('cell', { name: 'New product' })).toBeTruthy();
  const resultPreview = screen.getByRole('table', { name: 'Resolved batch result locations' });
  expect(within(resultPreview).getByText('Previous retention: 250 N')).toBeTruthy();
  expect(within(resultPreview).getByText('Comment: Historical Pass')).toBeTruthy();
  expect(within(resultPreview).getByText('Minimum retention: 245 N; maintained 6 s')).toBeTruthy();
  expect(within(resultPreview).getByText('Comment: —')).toBeTruthy();
  expect(screen.getByText('Engineering acceptance is pending.')).toBeTruthy();
  expect(batchApi.applyReportAssembly).not.toHaveBeenCalled();
});

it('trusts a valid dependency-checked plan after unrelated source retention, rather than invalidating it by revision alone', () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'saved', preview_sha256: 'p', status: 'prepared', can_apply: true,
    prepared_revision: 3, base_output_id: 'out1', output_sha256: 'a'.repeat(64), changes: [], issues: [], omitted: [],
    request: { output_id: 'out1', output_sha256: 'a'.repeat(64), mapping_ids: [], results: [{ result_id: 'force1' }], assignments: [] } };
  render(<Host initial={{ ...state, assembly_plan: plan }} />);
  fireEvent.click(screen.getByLabelText('I checked this batch preview; unresolved items remain pending'));
  expect(screen.getByRole('button', { name: 'Generate one working copy' }).matches(':disabled')).toBe(false);
});

const llcrDataset = { dataset_id: 'llcr-1', revision: 4, source_file_name: 'LLCR measurements.xlsx', source_sha256: 'l'.repeat(64), entries: [
  { entry_id: 'llcr-entry-1', group_id: 'g1', row_id: 'r1', group_label: 'Ab', step_token: '2', stage: 'initial', stage_label: 'Initial R',
    outcome: 'not_determined', summary: { min: '0.4', max: '0.8', average: '0.6', unit: 'mΩ' } },
] };

it('includes the existing LLCR dataset only after explicit whole-dataset selection, without recalculating or approving it', async () => {
  vi.mocked(batchApi.getReportCoverage).mockResolvedValue({ ...coverage, llcr_dataset: llcrDataset, llcr_unavailable_reason: '' });
  vi.mocked(batchApi.previewReportAssembly).mockResolvedValue({ ...state, revision: 8 });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  const include = await screen.findByLabelText('Include current LLCR dataset');
  expect(include).toHaveProperty('checked', false);
  expect(screen.getByText('LLCR measurements.xlsx')).toBeTruthy();
  expect(screen.getByText(/One dataset updates its result rows and shared Appendix A/)).toBeTruthy();
  expect(screen.getByRole('cell', { name: 'pending' })).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(true);
  fireEvent.click(include);
  fireEvent.click(screen.getByRole('button', { name: 'Preview selected updates' }));
  await waitFor(() => expect(batchApi.previewReportAssembly).toHaveBeenCalledWith('P1', {
    expected_revision: 7, output_id: 'out1', output_sha256: 'a'.repeat(64), mapping_ids: [], results: [], assignments: [], llcr_dataset_id: 'llcr-1',
  }));
  expect(batchApi.applyReportAssembly).not.toHaveBeenCalled();
});

it('shows saved LLCR old-to-new values and shared Appendix A action, and obeys backend stale-plan protection', () => {
  const plan: batchApi.ReportAssemblyPlan = { plan_id: 'llcr-plan', preview_sha256: 'p', status: 'prepared', can_apply: false,
    base_output_id: 'out1', output_sha256: 'a'.repeat(64), changes: [{ kind: 'llcr', label: 'Update LLCR dataset and Appendix A' }],
    issues: ['The selected LLCR dataset changed. Prepare a new preview.'], omitted: [],
    request: { output_id: 'out1', output_sha256: 'a'.repeat(64), mapping_ids: [], results: [], assignments: [], llcr_dataset_id: 'llcr-1' },
    document_plan: { facts: [], results: [], llcr: { dataset_id: 'llcr-1', revision: 4, source_sha256: 'l'.repeat(64), dataset_sha256: 'd', changed: true,
      rows: [{ result_id: 'entry1', group_label: 'Ab', step_token: '2', table_index: 3, row_index: 1, requirement: 'Initial R ≤ 1 mΩ',
        current_result: 'Old value: 0.9 mΩ', current_comment: 'Old acceptance', new_result: 'New value: 0.6 mΩ', new_comment: '', changed: true }],
      appendix: { identifier: 'A', action: 'update', heading_block_index: 8, table_index: 4, summary_rows: 1, sha256: 'a' } } },
  };
  render(<Host initial={{ ...state, assembly_plan: plan }} />);
  const preview = screen.getByRole('table', { name: 'LLCR exact result changes' });
  expect(within(preview).getByText('Old value: 0.9 mΩ')).toBeTruthy();
  expect(within(preview).getByText('New value: 0.6 mΩ')).toBeTruthy();
  expect(within(preview).getByText('Comment: —')).toBeTruthy();
  expect(screen.getByText('Appendix A: update — 1 summary rows. No measurement recalculation.')).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Generate one working copy' }).matches(':disabled')).toBe(true);
  expect(batchApi.applyReportAssembly).not.toHaveBeenCalled();
});

it('does not silently substitute a newly discovered LLCR dataset for an earlier selection', async () => {
  vi.mocked(batchApi.getReportCoverage)
    .mockResolvedValueOnce({ ...coverage, llcr_dataset: llcrDataset, llcr_unavailable_reason: '' })
    .mockResolvedValueOnce({ ...coverage, llcr_dataset: { ...llcrDataset, dataset_id: 'llcr-2', revision: 5 }, llcr_unavailable_reason: '' });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  fireEvent.click(await screen.findByLabelText('Include current LLCR dataset'));
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(false);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  expect(await screen.findByText('Include current LLCR dataset — revision 5')).toBeTruthy();
  expect(screen.getByLabelText('Include current LLCR dataset')).toHaveProperty('checked', false);
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(true);
});

it('explains why LLCR is unavailable without blocking an independent selected result', async () => {
  vi.mocked(batchApi.getReportCoverage).mockResolvedValue({ ...coverage, llcr_dataset: null, llcr_unavailable_reason: 'LLCR dataset belongs to a previous Matrix version.' });
  render(<Host />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect materials and coverage' }));
  expect(await screen.findByText('LLCR dataset belongs to a previous Matrix version.')).toBeTruthy();
  expect(screen.queryByLabelText('Include current LLCR dataset')).toBeNull();
  fireEvent.click(screen.getByLabelText('Include Group Ab / 2 / mechanical'));
  expect(screen.getByRole('button', { name: 'Preview selected updates' }).matches(':disabled')).toBe(false);
});
