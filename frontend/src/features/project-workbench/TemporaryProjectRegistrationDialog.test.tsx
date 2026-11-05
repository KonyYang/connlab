import { act, render, renderHook, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, it, vi } from 'vitest';
import { TemporaryProjectRegistrationDialog } from './TemporaryProjectRegistrationDialog';
import { prepareTemporaryRegistration, previewTemporaryRegistration, commitTemporaryRegistration } from '../../api/temporaryProjectRegistration';
import { useProjectWorkbenchModel } from './useProjectWorkbenchModel';

vi.mock('../../api/temporaryProjectRegistration', () => ({
  prepareTemporaryRegistration: vi.fn(), previewTemporaryRegistration: vi.fn(), commitTemporaryRegistration: vi.fn(),
}));
const values = { sample_description: 'Connector', test_item: 'Qualification', requested_by: 'Alice',
  location: 'Nantong', project_type: 'New Product Development', test_type_in_sheet: 'Partial Qualification',
  project_leader: 'White', lab_performing_tests: 'Dongguan' };
const required = { sample_description: 'Sample Description', test_item: 'Test Item', requested_by: 'Requested By',
  location: 'Mfg. Site', project_type: 'Project Type', test_type_in_sheet: 'Test Type in sheet',
  project_leader: 'Project Leader', lab_performing_tests: 'Lab Performing the Tests' };
const preview = { project_id: 'P1', preview_token: 'preview-1', ltr_number: 'DL-2026-11-001',
  action: 'append_auto', workbook_path: 'LTR.xlsx', values, row: [], comparison: null, recovery_required: false };
beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(prepareTemporaryRegistration).mockResolvedValue({ project_id: 'P1', values,
    required_fields: required, registered_ltr_number: null, recovery_preview: null });
  vi.mocked(previewTemporaryRegistration).mockResolvedValue(preview);
  vi.mocked(commitTemporaryRegistration).mockResolvedValue({ project_id: 'P1', ltr_number: preview.ltr_number });
});

it('prefills the current project, invalidates preview on edit, and cancels without registration', async () => {
  const user = userEvent.setup(), close = vi.fn();
  render(<TemporaryProjectRegistrationDialog projectId="P1" onClose={close} onRegistered={vi.fn()} />);
  expect(await screen.findByDisplayValue('Connector')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Preview registration' }));
  expect(await screen.findByText('DL-2026-11-001')).toBeTruthy();
  await user.type(screen.getByLabelText('Test Item'), ' revised');
  expect(screen.queryByRole('button', { name: 'Confirm registration' })).toBeNull();
  await user.click(screen.getByRole('button', { name: 'Cancel' }));
  expect(close).toHaveBeenCalledOnce();
  expect(commitTemporaryRegistration).not.toHaveBeenCalled();
});

it('requires preview and prevents duplicate submission while registering on the same project', async () => {
  const user = userEvent.setup(), registered = vi.fn();
  let finish!: (value: { project_id: string; ltr_number: string }) => void;
  vi.mocked(commitTemporaryRegistration).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  render(<TemporaryProjectRegistrationDialog projectId="P1" onClose={vi.fn()} onRegistered={registered} />);
  await screen.findByDisplayValue('Connector');
  expect(screen.queryByRole('button', { name: 'Confirm registration' })).toBeNull();
  await user.click(screen.getByRole('button', { name: 'Preview registration' }));
  const confirm = await screen.findByRole('button', { name: 'Confirm registration' });
  await user.dblClick(confirm);
  expect(commitTemporaryRegistration).toHaveBeenCalledTimes(1);
  expect(commitTemporaryRegistration).toHaveBeenCalledWith('P1', 'preview-1');
  finish({ project_id: 'P1', ltr_number: preview.ltr_number });
  await waitFor(() => expect(registered).toHaveBeenCalledOnce());
});

it('shows pending recovery on reopen without accepting changed registration information', async () => {
  vi.mocked(prepareTemporaryRegistration).mockResolvedValue({ project_id: 'P1', values,
    required_fields: required, registered_ltr_number: null, recovery_preview: { ...preview, recovery_required: true } });
  render(<TemporaryProjectRegistrationDialog projectId="P1" onClose={vi.fn()} onRegistered={vi.fn()} />);
  expect(await screen.findByRole('button', { name: 'Continue registration' })).toBeTruthy();
  expect(screen.getByLabelText('Test Item')).toHaveProperty('disabled', true);
});

it('recognizes a successful registration after its response is lost and refreshes the same project', async () => {
  const user = userEvent.setup(), registered = vi.fn();
  vi.mocked(prepareTemporaryRegistration).mockResolvedValueOnce({ project_id: 'P1', values,
    required_fields: required, registered_ltr_number: null, recovery_preview: null })
    .mockResolvedValue({ project_id: 'P1', values, required_fields: required,
      registered_ltr_number: preview.ltr_number, recovery_preview: null });
  vi.mocked(commitTemporaryRegistration).mockRejectedValue(new Error('Response lost'));
  render(<TemporaryProjectRegistrationDialog projectId="P1" onClose={vi.fn()} onRegistered={registered} />);
  await screen.findByDisplayValue('Connector');
  await user.click(screen.getByRole('button', { name: 'Preview registration' }));
  await user.click(await screen.findByRole('button', { name: 'Confirm registration' }));
  await waitFor(() => expect(registered).toHaveBeenCalledOnce());
  expect(commitTemporaryRegistration).toHaveBeenCalledTimes(1);
});

it('keeps initial identity loading single and refreshes the identity only after explicit registration', async () => {
  let registered = false;
  const fetcher = vi.fn(async (input: RequestInfo | URL) => {
    const path = new URL(String(input), 'http://localhost').pathname;
    let body: unknown;
    if (path === '/api/projects/P1') body = { project_id: 'P1', product_name: registered ? 'Registered connector' : 'Temporary connector', requestor: 'Alice', status: registered ? 'ltr_registered' : 'draft' };
    else if (path === '/api/projects/P1/ltr') body = registered ? [{ ltr_id: 'L1', project_id: 'P1', ltr_number: 'DL-2026-11-001', status: 'registered' }] : [];
    else if (path === '/api/projects/P1/lifecycle') body = { project_id: 'P1', lifecycle_state: 'active', readonly: false, allowed_actions: ['close'], status: registered ? 'ltr_registered' : 'draft', warnings: [] };
    else if (path === '/api/external-resources') body = [];
    else return new Response(JSON.stringify({ detail: 'No retained resource in this isolated API fixture' }), { status: 404, headers: { 'Content-Type': 'application/json' } });
    return new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } });
  });
  vi.stubGlobal('fetch', fetcher);
  const reads = () => fetcher.mock.calls.filter(([input]) => new URL(String(input), 'http://localhost').pathname === '/api/projects/P1').length;
  const view = renderHook(() => useProjectWorkbenchModel('P1'));
  try {
    await waitFor(() => expect(view.result.current.project?.product_name).toBe('Temporary connector'));
    await waitFor(() => expect(view.result.current.lifecycleLoading).toBe(false));
    expect(reads()).toBe(1);
    await act(async () => { await view.result.current.onRefreshLifecycle(); });
    expect(reads()).toBe(1);
    registered = true;
    await act(async () => { await view.result.current.onRefreshLifecycle(true); });
    expect(reads()).toBe(2);
    expect(view.result.current.project?.project_id).toBe('P1');
    expect(view.result.current.project?.product_name).toBe('Registered connector');
    expect(view.result.current.latestLtr).toBe('DL-2026-11-001');
  } finally {
    view.unmount();
    vi.unstubAllGlobals();
  }
});
