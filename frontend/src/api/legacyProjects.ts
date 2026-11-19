import { requestJson } from "./client";

export async function pickLegacyProjectDirectory(): Promise<string | null> {
  const result = await requestJson<{ path: string | null }>("/api/tools/legacy-projects/pick-directory", { method: "POST" });
  return result.path;
}

export type LegacyProjectRecord = {
  record_id: string; name: string; number: string | null; number_evidence: string[];
  folder_path: string; notes: string[]; revision: number; imported_at: string; updated_at: string;
};
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
