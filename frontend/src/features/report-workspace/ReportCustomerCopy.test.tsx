import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import * as delivery from '../../api/reportAuthoringDelivery';
import { ReportCustomerCopy } from './ReportCustomerCopy';

vi.mock('../../api/reportAuthoring', () => ({ generateCustomerReviewCopy: vi.fn(), checkCustomerReviewCopy: vi.fn(),
  downloadReportArtifact: vi.fn(), downloadCustomerPart: vi.fn() }));
vi.mock('../../api/reportAuthoringDelivery', () => ({ getReportDelivery: vi.fn(), resumeReviewedReportSave: vi.fn(), saveReviewedReports: vi.fn() }));
const internal = { output_id: 'internal', file_name: 'Current.docx', operation: 'llcr', status: 'needs_review',
  issues: [], base_source_id: 'base', download_url: '/internal', artifact: { sha256: 'a'.repeat(64) } };
const customer = { ...internal, output_id: 'customer', file_name: 'Customer.docx', parent_output_id: 'internal',
  download_url: '/customer', artifact: { sha256: 'b'.repeat(64) } };
const state: api.ReportAuthoringState = { project_id: 'P1', revision: 3, sources: [], mappings: [], outputs: [internal],
  base_source_id: 'base', context: { dl_number: 'DL-2026-10-001', matrix_id: 'm', steps: [] } };
const props = { projectId: 'P1', disabled: false, onChanged: vi.fn() };
beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.generateCustomerReviewCopy).mockResolvedValue(state);
  vi.mocked(api.checkCustomerReviewCopy).mockResolvedValue(state);
});

it('keeps an older copy downloadable without offering to save it as the current version', async () => {
  render(<ReportCustomerCopy {...props} state={{ ...state, customer_outputs: [{ ...customer, parent_output_id: 'older' }] }} />);
  expect(screen.getByRole('button', { name: 'Download previous customer copy' })).toBeTruthy();
  expect(screen.queryByRole('checkbox')).toBeNull();
  expect(screen.queryByRole('button', { name: 'Save reviewed reports to project folder' })).toBeNull();
  expect(screen.getByText(/Generate a customer report from the current working copy/)).toBeTruthy();
  expect(api.generateCustomerReviewCopy).not.toHaveBeenCalled();
});

it('requires review of this version with optional search terms tucked away, and sends exact review choices', async () => {
  render(<ReportCustomerCopy {...props} state={{ ...state, customer_outputs: [customer] }} />);
  expect(screen.queryByRole('button', { name: 'Generate customer review copy' })).toBeNull();
  expect(screen.getByText('Additional disclosure checks').closest('details')).toHaveProperty('open', false);
  expect(delivery.getReportDelivery).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText('Additional disclosure checks'));
  fireEvent.change(screen.getByLabelText(/Restricted terms/), { target: { value: '  proprietary\n' } });
  fireEvent.click(screen.getByLabelText(/disclosure scope/i));
  fireEvent.click(screen.getByLabelText(/I reviewed this Internal Report/i));
  fireEvent.click(screen.getByRole('button', { name: 'Check customer copy' }));
  await waitFor(() => expect(api.checkCustomerReviewCopy).toHaveBeenCalledWith('P1', {
    expected_revision: 3, output_id: 'customer', output_sha256: customer.artifact.sha256,
    sensitive_terms: ['proprietary'], forbidden_project_ids: [], reviewed_parts: {},
    disclosure_scope_confirmed: true, content_review_sha256: internal.artifact.sha256 }));
});

it('requests fresh human confirmations when the Matrix or evidence invalidates a completed check', () => {
  const audit = { passed: false, reviewed_parts: {}, sensitive_terms: [], forbidden_project_ids: [], disclosure_scope_confirmed: true,
    content_review_sha256: internal.artifact.sha256,
    issues: [{ code: 'review_context_changed', location: 'review', message: 'Review changed Matrix evidence', sha256: null }] };
  const {rerender} = render(<ReportCustomerCopy {...props} state={{ ...state, customer_outputs: [{ ...customer,
    audit: { ...audit, issues: [] } }] }} />);
  expect(screen.getByLabelText(/disclosure scope/i)).toHaveProperty('checked', true);
  rerender(<ReportCustomerCopy {...props} state={{ ...state, customer_outputs: [{ ...customer, audit }] }} />);
  expect(screen.getByText('Review changed Matrix evidence')).toBeTruthy();
  expect(screen.getByLabelText(/disclosure scope/i)).toHaveProperty('checked', false);
  expect(screen.getByLabelText(/I reviewed this Internal Report/i)).toHaveProperty('checked', false);
});

it('takes a blocked customer check to the affected LLCR section without rerunning generation', () => {
  const audit = { passed: false, reviewed_parts: {}, sensitive_terms: [], forbidden_project_ids: [], disclosure_scope_confirmed: false,
    issues: [{ code: 'stale_llcr_result', location: 'llcr', message: 'Review the updated dataset.', sha256: null }] };
  const onOpenSection = vi.fn();
  render(<ReportCustomerCopy {...props} onOpenSection={onOpenSection} state={{ ...state, customer_outputs: [{ ...customer, audit }] }} />);
  fireEvent.click(screen.getByRole('button', { name: 'Review LLCR results' }));
  expect(onOpenSection).toHaveBeenCalledWith('llcr');
  expect(api.generateCustomerReviewCopy).not.toHaveBeenCalled();
});

it('stops offering regeneration after an interrupted save on the same page', async () => {
  const audit = { passed: true, reviewed_parts: {}, sensitive_terms: [], forbidden_project_ids: [], disclosure_scope_confirmed: true,
    content_review_sha256: internal.artifact.sha256, issues: [] };
  vi.mocked(delivery.getReportDelivery).mockResolvedValueOnce({ can_save: true, issues: [], operation: null,
    preview_sha256: 'preview', customer_output_id: customer.output_id }).mockResolvedValueOnce({ can_save: false, issues: [],
    preview_sha256: null, customer_output_id: customer.output_id, operation: { operation_id: 'partial', status: 'saving', items: [] } });
  vi.mocked(delivery.saveReviewedReports).mockRejectedValue(new Error('Customer document is open in Word.'));
  render(<ReportCustomerCopy {...props} state={{ ...state, customer_outputs: [{ ...customer, status: 'package_checked', audit }] }} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Save reviewed reports to project folder' }));
  fireEvent.click(screen.getByRole('button', { name: 'Confirm save' }));
  await screen.findByRole('button', { name: 'Resume this report save' });
  expect(screen.getByRole('alert').textContent).toContain('open in Word');
  expect(screen.queryByText('Generate another copy')).toBeNull();
  expect(screen.queryByRole('button', { name: 'Review disclosure checks again' })).toBeNull();
});

it('offers recovery before conversion or fresh checks even when the saved customer belongs to an older version', async () => {
  const operation = { operation_id: 'partial', status: 'saving', items: [{ role: 'internal', file_name: 'Old.docx', status: 'saved' }] };
  vi.mocked(delivery.getReportDelivery).mockRejectedValue(new Error('Project folder offline'));
  vi.mocked(delivery.resumeReviewedReportSave).mockResolvedValue(state);
  render(<ReportCustomerCopy {...props} state={{ ...state, delivery: operation, customer_outputs: [{ ...customer, parent_output_id: 'older' }] }} />);
  expect(screen.queryByRole('button', { name: /Generate.*customer copy/i })).toBeNull();
  fireEvent.click(await screen.findByRole('button', { name: 'Resume this report save' }));
  await waitFor(() => expect(delivery.resumeReviewedReportSave).toHaveBeenCalledWith('P1', 'partial'));
});
