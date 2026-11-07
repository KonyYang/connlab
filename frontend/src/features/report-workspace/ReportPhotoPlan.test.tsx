import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { ReportPhotoPlan } from './ReportPhotoPlan';
import type { ReportAuthoringState, ReportDocumentReviewData } from '../../api/reportAuthoring';

it('does not treat filename hints as confirmed photos and permits a non-step overview scope', () => {
  const state = { project_id: 'P1', revision: 1, sources: [], mappings: [], context: { steps: [] },
    outputs: [{ output_id: 'out', artifact: { sha256: 'a' } }] } as unknown as ReportAuthoringState;
  const review = { output_sha256: 'a', slots: [{ slot_id: 'photo-1', caption: 'Sample overview', supported: true, coverage: 'needs_review', rotation: 0 }],
    photo_candidates: [{ source_id: 's1', file_name: 'Group Ab SN1.png', suggestions: [{ slot_id: 'photo-1', score: 1, hints: ['sn1'] }] }] } as ReportDocumentReviewData;
  render(<ReportPhotoPlan projectId="P1" state={state} review={review} disabled={false} onConfirm={vi.fn()} />);
  const save = screen.getByRole('button', { name: 'Save confirmed photo mapping' });
  expect(save).toHaveProperty('disabled', true);
  fireEvent.change(screen.getByLabelText('Replacement for photo-1'), { target: { value: 's1' } });
  fireEvent.change(screen.getByLabelText('Scope for photo-1'), { target: { value: 'sample_overview' } });
  expect(screen.queryByLabelText('Group / Step for photo-1')).toBeNull();
  expect(save).toHaveProperty('disabled', true);
});
