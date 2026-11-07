import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import { ReportVisualPreview } from './ReportVisualPreview';

vi.mock('../../api/reportAuthoring', async () => ({ ...await vi.importActual('../../api/reportAuthoring'),
  createReportVisualPreview: vi.fn(), downloadReportArtifact: vi.fn(), confirmReportVisualPages: vi.fn() }));

it('reopens a retained PDF without re-rendering and records an explicit full-page check', async () => {
  vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:preview'), revokeObjectURL: vi.fn() }));
  const state = { project_id: 'P1', revision: 2, sources: [], mappings: [], context: { steps: [] }, outputs: [{ output_id: 'out',
    file_name: 'Working.docx', artifact: { sha256: 'a'.repeat(64) }, visual_preview: { output_sha256: 'a'.repeat(64),
      artifact: { sha256: 'b'.repeat(64), file_name: 'preview.pdf' }, status: 'rendered_not_reviewed', page_count: 2,
      pages: [{ page: 1 }, { page: 2 }], affected_pages: [2], affected_pages_reason: 'Caption located on page 2' } }] } as api.ReportAuthoringState;
  vi.mocked(api.downloadReportArtifact).mockResolvedValue({ blob: new Blob(['pdf']), fileName: 'preview.pdf' });
  vi.mocked(api.confirmReportVisualPages).mockResolvedValue(state);
  render(<ReportVisualPreview projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Open retained PDF — no re-render' }));
  await screen.findByTitle('Word preview page 1');
  expect(api.createReportVisualPreview).not.toHaveBeenCalled();
  const save = screen.getByRole('button', { name: 'Record full visual review — not formal release' });
  expect(save).toHaveProperty('disabled', true);
  fireEvent.click(screen.getByLabelText('I have visually checked every page of this exact PDF'));
  fireEvent.click(save);
  await waitFor(() => expect(api.confirmReportVisualPages).toHaveBeenCalledWith('P1', expect.objectContaining({
    output_id: 'out', output_sha256: 'a'.repeat(64), preview_sha256: 'b'.repeat(64), pages: [1, 2] })));
});
