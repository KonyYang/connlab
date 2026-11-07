import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import * as api from '../../api/reportAuthoring';
import { ReportDocumentReview } from './ReportDocumentReview';

vi.mock('../../api/reportAuthoring', async () => ({ ...await vi.importActual('../../api/reportAuthoring'), getReportDocumentReview: vi.fn() }));

it('inspects explicit scoped regions and never marks unknown content complete', async () => {
  const state = { project_id: 'P1', revision: 2, sources: [], mappings: [], base_source_id: 'source',
    context: { dl_number: 'DL-001', matrix_id: 'M1', steps: [] }, outputs: [{ output_id: 'out', file_name: 'Working.docx',
      artifact: { sha256: 'a'.repeat(64) }, status: 'needs_review', operation: 'prepare_base', issues: [], download_url: '/copy', base_source_id: 'source' }] } as api.ReportAuthoringState;
  vi.mocked(api.getReportDocumentReview).mockResolvedValue({ output_id: 'out', output_sha256: 'a'.repeat(64), review_sha256: 'b'.repeat(64),
    base_role: 'layout_reference', complete: false, notice: '', regions: [], region_groups: [{ region_id: 'group:1', kind: 'Purpose',
      text: 'Historical project purpose', sha256: 'c'.repeat(64), status: 'needs_review', reasons: ['Source decision needed'], paragraph_count: 12, region_ids: [] }],
    slots: [], figures: [], findings: [], numbering: { ready: true, issues: [], replacements: [] }, photo_candidates: [] });
  render(<ReportDocumentReview projectId="P1" state={state} disabled={false} onChanged={vi.fn()} />);
  expect(api.getReportDocumentReview).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Inspect original coverage and photo candidates' }));
  expect(await screen.findByText(/Content still needs verification/)).toBeTruthy();
  expect(screen.getByText('Regional content checklist (1 sections; 0 paragraphs inventoried)')).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Save this regional decision' })).toHaveProperty('disabled', true);
});
