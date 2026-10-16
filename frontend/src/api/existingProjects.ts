import { requestJson } from "./client";

export type WorkspaceInfo = {runtime_mode: string; database_path: string | null; data_directory: string;
  config_path: string; application_version: string; release: Record<string, string>; release_status: string;
  sqlite_user_version: number | null; schema_status: string; notice: string};
export type ExistingSource = {path: string; name: string; source_kind: "manual" | "connlab";
  source_project_id: string | null; source_number: string | null; source_number_origin: string;
  source_fingerprint: string; root_identity: string; manifest_error: string | null};
export type ExistingLocation = {location_id: string; project_id: string; path: string; management_number: string;
  source_number: string | null; source_project_id: string | null; source_kind: string;
  registry_state: "active" | "trash" | "history"; revision: number; product_name: string; registered_at: string};
export type ExistingTarget = {project_id: string; display_project_id: string; number: string | null; name: string; state: string; revision: number};
export type ExistingPreview = ExistingSource & {token: string; conflicts: ExistingTarget[]; targets: ExistingTarget[];
  existing: ExistingLocation | null; suggested_number: string; notice: string};
export type ExistingDecision = {path: string; token: string; action: "register" | "independent" | "link" | "skip";
  management_number: string; target_project_id: string | null; ignore_manifest: boolean};
export type ExistingFiles = {relative_path: string; entries: {name: string; relative_path: string; is_directory: boolean}[]; diagnostics: string[]};
export type RelocationPreview = {location: ExistingLocation; source: ExistingSource; blockers: string[]; token: string};

const post = <T,>(url: string, body: unknown): Promise<T> => requestJson(url, {method:"POST",body:JSON.stringify(body)});
export async function getWorkspaceInfo(): Promise<WorkspaceInfo> {
  const value=await requestJson<WorkspaceInfo>("/api/workspace/info");
  if(!value||typeof value.runtime_mode!=="string"||!value.release||typeof value.release!=="object") {
    throw new Error("Workspace information is incompatible. Refresh or use a matching program version.");
  }
  return value;
}
export async function scanExistingProjects(roots: string[], depth: number): Promise<{candidates: ExistingSource[]; diagnostics: string[]}> {
  return post("/api/existing-projects/scan", {roots, depth});
}
export async function previewExistingProject(path: string): Promise<ExistingPreview> { return post("/api/existing-projects/preview", {path}); }
export async function registerExistingProject(input: ExistingDecision): Promise<ExistingLocation> { return post("/api/existing-projects/register", input); }
export async function listExistingLocations(projectId?: string): Promise<ExistingLocation[]> {
  return requestJson(`/api/existing-projects/locations${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`);
}
export async function listExistingFiles(locationId: string, relative = ""): Promise<ExistingFiles> {
  return requestJson(`/api/existing-projects/locations/${encodeURIComponent(locationId)}/files?relative=${encodeURIComponent(relative)}`);
}
export function existingFileDownloadUrl(locationId: string, relative: string): string {
  const base=(import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
  return `${base}/api/existing-projects/locations/${encodeURIComponent(locationId)}/download?relative=${encodeURIComponent(relative)}`;
}
export async function previewExistingRelocation(locationId: string, path: string): Promise<RelocationPreview> {
  return post(`/api/existing-projects/locations/${encodeURIComponent(locationId)}/relocation-preview`, {path});
}
export async function relocateExistingLocation(locationId: string, path: string, token: string): Promise<ExistingLocation> {
  return post(`/api/existing-projects/locations/${encodeURIComponent(locationId)}/relocate`, {path,token});
}
