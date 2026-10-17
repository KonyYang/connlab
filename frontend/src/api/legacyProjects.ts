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
