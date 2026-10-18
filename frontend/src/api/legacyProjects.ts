import { requestJson } from "./client";

export type LegacyProjectCandidate = {
  folder: string;
  number: string | null;
  name: string;
  status: "ready" | "review";
  notes: string[];
  duplicate_folders: string[];
  duplicate_count: number;
};

export type LegacyProjectPreviewResult = {
  read_only: boolean;
  projects: LegacyProjectCandidate[];
  scanned_folders: number;
  duplicate_roots: number;
  diagnostics: string[];
  truncated: boolean;
};

export async function pickLegacyProjectDirectory(): Promise<string | null> {
  const result = await requestJson<{ path: string | null }>("/api/tools/legacy-projects/pick-directory", { method: "POST" });
  return result.path;
}

export function previewLegacyProjects(roots: string[], signal: AbortSignal): Promise<LegacyProjectPreviewResult> {
  return requestJson("/api/tools/legacy-projects/preview", { method: "POST", body: JSON.stringify({ roots }), signal });
}

export type LegacyRegistrationCandidate = Omit<LegacyProjectCandidate, "status"> & {
  status: "ready" | "review" | "already_added" | "failed";
  fingerprint: string;
  can_keep_separate?: boolean;
};
export type LegacyRegistrationPlan = { projects: LegacyRegistrationCandidate[] };
export type LegacyRegistrationChoice = { folder: string; fingerprint: string; keep_separate: boolean };
export type LegacyRegistrationResult = {
  counts: { added: number; already_added: number; review: number; failed: number };
  items: { folder: string; status: string; message: string; record_id: string | null }[];
};
export type LegacyProjectRecord = {
  record_id: string; name: string; number: string | null; number_evidence: string[];
  folder_path: string; notes: string[]; revision: number; imported_at: string; updated_at: string;
};
export function planLegacyRegistration(folders: string[], signal: AbortSignal): Promise<LegacyRegistrationPlan> {
  return requestJson("/api/tools/legacy-projects/registration-plan", { method: "POST", body: JSON.stringify({ folders }), signal });
}
export function importLegacyProjects(folders: string[], selected: LegacyRegistrationChoice[]): Promise<LegacyRegistrationResult> {
  return requestJson("/api/tools/legacy-projects/import", { method: "POST", body: JSON.stringify({ folders, selected }) });
}
export function listLegacyProjects(query: string, signal: AbortSignal): Promise<LegacyProjectRecord[]> {
  return requestJson(`/api/legacy-projects?q=${encodeURIComponent(query)}`, { signal });
}
export function getLegacyProject(recordId: string, signal: AbortSignal): Promise<LegacyProjectRecord> {
  return requestJson(`/api/legacy-projects/${encodeURIComponent(recordId)}`, { signal });
}
export function openLegacyProjectFolder(recordId: string): Promise<{ status: string; message: string }> {
  return requestJson(`/api/legacy-projects/${encodeURIComponent(recordId)}/open-folder`, { method: "POST" });
}
export function changeLegacyProjectLocation(recordId: string, folder: string, revision: number): Promise<LegacyProjectRecord> {
  return requestJson(`/api/legacy-projects/${encodeURIComponent(recordId)}/location`, { method: "POST", body: JSON.stringify({ folder, expected_revision: revision }) });
}
