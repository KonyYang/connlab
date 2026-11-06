import { afterEach, expect, it, vi } from 'vitest';
import { exportMechanicalReportPackage, type FolderReview } from './mechanicalSummary';

afterEach(() => vi.unstubAllGlobals());

it('exports mechanical sources with their relative names and reviewed identities, without binding a project', async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(new Blob(['zip']), {
    headers: { 'Content-Disposition': "attachment; filename*=UTF-8''Mechanical_ReportResults.zip" },
  }));
  vi.stubGlobal('fetch', fetch);
  const source = new File(['original source'], 'force.pdf');
  Object.defineProperty(source, 'webkitRelativePath', { value: 'Test results/force.pdf' });
  const review: FolderReview = { project: 'DL-2026-09-032', sections: { source: { rows: [{ curve: '72', sample: '#1', colour: 'Orange', part: 'Plug' }] } } };
  const result = await exportMechanicalReportPackage([source], review);
  expect(fetch.mock.calls[0][0]).toBe('/api/tools/mechanical-summary/folder/export-package');
  const options = fetch.mock.calls[0][1];
  expect(options.body.getAll('files').map((file: File) => file.name)).toEqual(['Test results/force.pdf']);
  expect(JSON.parse(options.body.get('review'))).toEqual(review);
  expect(options.body.get('project_id')).toBeNull();
  expect(new Headers(options.headers).get('Content-Type')).toBeNull();
  expect(result.fileName).toBe('Mechanical_ReportResults.zip');
});
