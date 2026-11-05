import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, it, vi } from 'vitest';
import { TemporaryProjectRegistrationDialog } from './TemporaryProjectRegistrationDialog';
import { prepareTemporaryRegistration, previewTemporaryRegistration, commitTemporaryRegistration } from '../../api/temporaryProjectRegistration';

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
