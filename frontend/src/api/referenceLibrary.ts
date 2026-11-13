import { requestJson } from "./client";
export type ReferenceProject = { key: string; project_id: string | null; member_id: string | null; number: string | null; title: string; test_item: string; source: string; available: boolean; folder_path: string };
export type ReferenceFile = { key: string; title: string; number: string | null; name: string; relative_path: string; directory: string; kind: string };
export type ReferenceResults = { projects: ReferenceProject[]; files: ReferenceFile[]; total: number; warnings: string[] };
export const searchReferenceLibrary = (query: string, source: string, kind: string, project: string, offset: number, signal?: AbortSignal) =>
  requestJson<ReferenceResults>(`/api/project-library/search?${new URLSearchParams({ q: query, source, kind, project, offset: String(offset) })}`, { signal });
export const openReferenceFile = (key: string, relative_path = "", containing = false) =>
  requestJson<{ status: string; message: string }>("/api/project-library/open-file", { method: "POST", body: JSON.stringify({ key, relative_path, containing }) });
