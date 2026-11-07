import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoringDelivery';
import type { ReportAuthoringState } from '../../api/reportAuthoring';
import { ReportDelivery } from './ReportDelivery';

vi.mock('../../api/reportAuthoringDelivery', () => ({ getReportDelivery: vi.fn(), confirmReportRetainedContent: vi.fn(),
  saveReviewedReports: vi.fn(), resumeReviewedReportSave: vi.fn() }));
const state = { project_id: 'P1', revision: 7, sources: [], mappings: [], context: { steps: [] },
  outputs: [{ output_id: 'internal', file_name: 'Internal.docx', artifact: { sha256: 'a'.repeat(64) } }],
  customer_outputs: [{ output_id: 'customer', parent_output_id: 'internal', file_name: 'Customer.docx', artifact: { sha256: 'b'.repeat(64) } }],
} as unknown as ReportAuthoringState;

it('does not save on inspection, cancellation or download; exact pair requires explicit save', async () => {
  vi.mocked(api.getReportDelivery).mockResolvedValue({ can_save: true, issues: [], preview_sha256: 'c'.repeat(64),
    output_id: 'internal', output_sha256: 'a'.repeat(64), customer_output_id: 'customer', operation: null,
    workspace: { notice: 'History', files: [{ role: 'internal', file_name: 'Current.docx', replaces_existing: true, archive_required: true }] } });
  vi.mocked(api.saveReviewedReports).mockResolvedValue(state);
  render(<ReportDelivery projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  expect(api.getReportDelivery).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Inspect delivery checks' }));
  await screen.findByText('Delivery checks passed for the selected pair.');
  expect(api.saveReviewedReports).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Save reviewed reports to project folder' }));
  expect(screen.getByRole('dialog', { name: 'Confirm saving reviewed reports' })).toBeTruthy();
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Cancel' }));
  fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' });
  expect(screen.queryByRole('dialog')).toBeNull();
  expect(api.saveReviewedReports).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Save reviewed reports to project folder' }));
  fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
  expect(api.saveReviewedReports).not.toHaveBeenCalled();
  expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Save reviewed reports to project folder' }));
  fireEvent.click(screen.getByRole('button', { name: 'Save reviewed reports to project folder' }));
  fireEvent.click(screen.getByRole('button', { name: 'Confirm save' }));
  await waitFor(() => expect(api.saveReviewedReports).toHaveBeenCalledWith('P1', {
    expected_revision: 7, output_id: 'internal', output_sha256: 'a'.repeat(64), customer_output_id: 'customer',
    preview_sha256: 'c'.repeat(64), confirmed_by: 'Lab User' }));
});

it('shows precise blockers instead of enabling save for a generated but unchecked copy', async () => {
  vi.mocked(api.getReportDelivery).mockResolvedValue({ can_save: false, issues: [{ code: 'coverage_incomplete', message: 'Group A evidence missing' }],
    preview_sha256: null, operation: null });
  render(<ReportDelivery projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect delivery checks' }));
  await screen.findByText('Group A evidence missing');
  expect(screen.getByRole('button', { name: 'Save reviewed reports to project folder' })).toHaveProperty('disabled', true);
});

it('does not present an earlier completed pair as the currently selected version', async () => {
  vi.mocked(api.getReportDelivery).mockResolvedValue({ can_save: false, issues: [{ code: 'customer_copy_required', message: 'Regenerate matching customer copy' }],
    preview_sha256: 'd'.repeat(64), operation_matches_current: false,
    operation: { operation_id: 'old', status: 'completed', output_id: 'previous', output_sha256: 'e'.repeat(64),
      customer_output_id: 'old-customer', customer_sha256: 'f'.repeat(64), items: [] } });
  render(<ReportDelivery projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Inspect delivery checks' }));
  await screen.findByText('An earlier report version was saved; current delivery checks are separate.');
  expect(screen.queryByText('Selected report pair saved — not formally issued.')).toBeNull();
});
