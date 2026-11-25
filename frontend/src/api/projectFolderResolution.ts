import { requestJson, type BasicProjectWorkspaceResult } from "./client";

export type FolderResolutionChoice = {strategy: "relink" | "recreate"; path: string | null};
export type FolderResolutionPreview = {
  project_id: string;
  strategy: FolderResolutionChoice["strategy"];
  old_path: string;
  target_path: string;
  expected_context: string;
};

function postResolution<T>(projectId: string, action: string, input: object): Promise<T> {
  return requestJson(`/api/projects/${encodeURIComponent(projectId)}/official-workspace/resolution/${action}`, {
    method: "POST", body: JSON.stringify(input),
  });
}

export function previewFolderResolution(projectId: string, choice: FolderResolutionChoice) {
  return postResolution<FolderResolutionPreview>(projectId, "preview", choice);
}

export function applyFolderResolution(projectId: string, choice: FolderResolutionChoice, expectedContext: string, requestId: string) {
  return postResolution<BasicProjectWorkspaceResult>(projectId, "apply", {...choice, expected_context: expectedContext, request_id: requestId});
}

export function resumeFolderResolution(projectId: string, operationId: string) {
  return postResolution<BasicProjectWorkspaceResult>(projectId, "resume", {operation_id: operationId});
}

export function abandonFolderResolution(projectId: string, operationId: string) {
  return postResolution<{status: "abandoned"; directory_available: boolean}>(projectId, "abandon", {operation_id: operationId});
}
