import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import type { ReportAuthoringState } from '../../api/reportAuthoring';
import { afterEach, expect, it, vi } from 'vitest';
import { getReportCoverage, type ReportCoverage } from '../../api/reportAuthoringBatch';
import { StepReportEvidence, readStepLink } from './StepReportEvidence';

vi.mock('../../api/reportAuthoringBatch', () => ({ getReportCoverage: vi.fn() }));
afterEach(() => { cleanup(); vi.resetAllMocks(); });
const step = {projectId:'P1', matrix:'M1', group:'g', row:'r', token:'2(a)'};
const row = {group_id:'g', row_id:'r', step_token:'2(a)', group_label:'Ab', test_item:'Retention',
  status:'needs_review' as const, reasons:['Confirm hold duration.'], result_ids:['held'], usable_result_ids:['held'], applied_result_ids:[]};
const coverage: ReportCoverage = {matrix_id:'M1', has_confirmed_matrix:true, complete:false, pending_mappings:[], counts:{},
  rows:[{...row, row_id:'other', step_token:'2', reasons:['Other step only.']}, row]};

it('opens exactly the selected evidence, keeping suffix and distinguishing evidence from use in the report', async () => {
  vi.mocked(getReportCoverage).mockResolvedValue(coverage);
  render(<StepReportEvidence projectId="P1" step={step} />);
  expect(await screen.findByText('Confirm hold duration.')).toBeTruthy();
  expect(screen.queryByText('Other step only.')).toBeNull();
  expect(screen.getByText('Not used in the current working copy')).toBeTruthy();
  const target = new URL((screen.getByRole('link') as HTMLAnchorElement).href);
  expect(target.pathname).toBe('/projects/P1/report-workspace');
  expect(readStepLink('P1', target.search)).toEqual(step);
});

it('does not call a read failure missing evidence; retry checks the Matrix version', async () => {
  vi.mocked(getReportCoverage).mockRejectedValueOnce(new Error('Storage offline')).mockResolvedValue({...coverage, matrix_id:'old'});
  render(<StepReportEvidence projectId="P1" step={step} />);
  expect((await screen.findByRole('alert')).textContent).toContain('Storage offline');
  fireEvent.click(screen.getByRole('button', {name:'Retry'}));
  expect(await screen.findByText(/Matrix has changed/)).toBeTruthy();
  expect(screen.queryByRole('link')).toBeNull();
});

it('ignores a late read from a previous project and displays the exact source at the report destination', async () => {
  let finish: (data: ReportCoverage) => void = () => {};
  vi.mocked(getReportCoverage).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }))
    .mockResolvedValue({...coverage, rows:[{...row, applied_result_ids:['held']}]});
  const view = render(<StepReportEvidence projectId="P0" step={{...step,projectId:'P0'}} />);
  const report = {project_id:'P1', revision:1, context:{matrix_id:'M1'}, sources:[{source_id:'s',file_name:'Retention.csv'}],
    results:[{result_id:'held',source_id:'s',data:{sheet_name:'Readings'}}]} as ReportAuthoringState;
  view.rerender(<StepReportEvidence projectId="P1" step={step} report={report} />);
  expect(await screen.findByText('Retention.csv / Readings — used in working copy')).toBeTruthy();
  await act(async () => finish({...coverage,matrix_id:'old'}));
  expect(screen.getByText('Ab / 2(a): Retention')).toBeTruthy();
  expect(screen.queryByRole('link')).toBeNull();
});
