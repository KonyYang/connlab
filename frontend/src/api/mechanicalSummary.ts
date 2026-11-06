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

export type FolderRow = MechanicalRow & { colour: string; part: string; end_section?: number; end_section1?: number };
export type ReportTable = { title: string; row_heading: string; column_heading: string; columns: string[];
  samples: string[]; results: string[][]; diagonal: boolean; curves: string[] };
export type FolderSection = { id: string; sha256: string; source: string; name: string; kind: string; sheet: number | null;
  rows: FolderRow[]; raw_curves?: string[]; source_text: string; information: Record<string, string>;
  force_fields: string[]; force_field: string; withdraw_magnitude: boolean; tables: ReportTable[];
  issues: string[]; type_required?: boolean; qualitative_confirmed?: boolean };
export type FolderAnalysis = { project: string; ready: boolean; sections: FolderSection[];
  ignored: { file: string; reason: string }[]; errors: { file: string; message: string }[] };
export type SectionReview = { kind?: string; rows?: Pick<FolderRow, 'curve' | 'sample' | 'colour' | 'part'>[];
  information?: Record<string, string>; force_field?: string; withdraw_magnitude?: boolean;
  tables?: ReportTable[]; qualitative_confirmed?: boolean };
export type FolderReview = { project: string; sections: Record<string, SectionReview> };
function folderBody(files: File[], review?: FolderReview) {
  const body = new FormData();
  files.forEach(file => body.append('files', file, file.webkitRelativePath || file.name));
  if (review) body.append('review', JSON.stringify(review));
  return body;
}
export function previewMechanicalFolder(files: File[], review?: FolderReview): Promise<FolderAnalysis> {
  return requestJson('/api/tools/mechanical-summary/folder/preview', { method: 'POST', body: folderBody(files, review) });
}
export function generateMechanicalFolder(files: File[], review?: FolderReview) {
  return requestBlobResponse('/api/tools/mechanical-summary/folder/generate', { method: 'POST', body: folderBody(files, review) });
}
