import { requestBlobResponse, requestJson } from './client';

export type MechanicalRow = { curve: string; sample: string; value?: number; mating?: number; withdraw?: number; result?: string };
export type MechanicalPreview = { sha256: string; requires_review: boolean; rows?: MechanicalRow[]; source_text?: string;
  sheets?: { name: string; rows: unknown[][] }[] };

export function previewMechanicalSource(file: File, kind: string): Promise<MechanicalPreview> {
  const body = new FormData();
  body.append('file', file);
  body.append('kind', kind);
  return requestJson('/api/tools/mechanical-summary/preview', { method: 'POST', body });
}

export function generateMechanicalSummary(files: File[], manifest: unknown[]) {
  const body = new FormData();
  files.forEach(file => body.append('files', file));
  body.append('manifest', JSON.stringify(manifest));
  return requestBlobResponse('/api/tools/mechanical-summary/generate', { method: 'POST', body });
}
