import { requestJson, type ProjectLifecycleState } from "./client";

export type ProjectRegistryLocation = "active" | "trash" | "history";
export type ProjectRegistryEntry = {
  project_id: string;
  display_project_id: string;
  sample_description: string | null;
  test_item: string | null;
  requestor: string;
  created_on: string | null;
  lifecycle_state: ProjectLifecycleState;
  close_reason_label: string | null;
  registry_state: ProjectRegistryLocation;
  registry_revision: number;
  changed_at: string | null;
  reason: string | null;
};
export type ProjectRegistryAction = "trash" | "restore";
export type ProjectRegistryPreview = {
  project: ProjectRegistryEntry;
  action: ProjectRegistryAction;
  token: string;
  conflicts: ProjectRegistryEntry[];
  blockers: string[];
  retained_data: string[];
  warnings: string[];
};
export type ProjectRegistryRestoreRequest = {
  token: string;
  destination: "active" | "history";
  replace_conflicts: boolean;
  actor?: string | null;
};

export function listManagedProjects(location: "trash" | "history"): Promise<ProjectRegistryEntry[]> {
  return requestJson(`/api/project-registry/entries?location=${location}`);
}
export function previewProjectRegistryAction(projectId: string, action: ProjectRegistryAction): Promise<ProjectRegistryPreview> {
  return requestJson(`/api/project-registry/${encodeURIComponent(projectId)}/preview?action=${action}`);
}
export function moveProjectToTrash(projectId: string, request: {token: string; reason: string; actor?: string | null}): Promise<ProjectRegistryEntry> {
  return requestJson(`/api/project-registry/${encodeURIComponent(projectId)}/trash`, {method: "POST", body: JSON.stringify(request)});
}
export function restoreManagedProject(projectId: string, request: ProjectRegistryRestoreRequest): Promise<ProjectRegistryEntry> {
  return requestJson(`/api/project-registry/${encodeURIComponent(projectId)}/restore`, {method: "POST", body: JSON.stringify(request)});
}
