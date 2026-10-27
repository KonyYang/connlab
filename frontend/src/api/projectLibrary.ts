import { requestJson } from "./client";

const BASE = "/api/project-library";
const memberPath = (id: string) => `${BASE}/members/${encodeURIComponent(id)}`;
const post = <T,>(path: string, body: unknown, signal?: AbortSignal) => requestJson<T>(path, { method: "POST", body: JSON.stringify(body), signal });

export type LibraryRuntime = { library_root: string; projects_root: string; data_root: string; database_path: string; configured: boolean; format_version: number };
export type LibraryMember = { member_id: string; project_id: string | null; ltr_number: string | null; title: string; folder_path: string; revision: number; batch_id: string | null; snapshot_status: "missing" | "current" | "stale" | "unavailable"; snapshot_created_at: string | null; warnings: string[]; can_continue: boolean };
export type LibraryCandidate = { source_path: string; title: string; ltr_number: string | null; kind: "project" | "file"; warnings: string[]; child_folders: string[] };
export type LibraryScan = { items: LibraryCandidate[]; warnings: string[]; truncated: boolean };
export type LibraryFileAssignment = { source_path: string; target_member_id?: string; new_project_title?: string };
export type LibraryIntakeItem = { source_path: string; target_path: string; title: string; ltr_number: string | null; status: "ready" | "conflict" | "already_added" | "unavailable"; warnings: string[]; can_keep_separate: boolean; target_member_id?: string | null; new_project_title?: string | null };
export type LibraryIntakePlan = { plan_id: string; fingerprint: string; items: LibraryIntakeItem[]; warnings: string[] };
export type LibraryBatch = { batch_id: string; status: "completed" | "interrupted" | "running"; counts: { added: number; already_added: number; review: number; failed: number }; items: { source_path: string; status: string; message: string; member_id: string | null }[] };
export type LibraryPlanToken = { plan_id: string; fingerprint: string };
export type LibraryLocationPlan = LibraryPlanToken & { source_path: string; target_path: string; warnings: string[] };
export type LibraryFiles = { items: { name: string; relative_path: string; is_directory: boolean; size_bytes: number | null }[]; warnings: string[] };
export type PortableInfo = { status: "missing" | "current" | "stale" | "unavailable"; fingerprint: string; created_at: string | null; format_version: number; record_counts: Record<string, number>; file_count: number; warnings: string[]; blockers: string[] };
export type PortableRestorePlan = LibraryPlanToken & { project_id: string; ltr_number: string | null; title: string; source_path: string; target_path: string; status: "ready" | "already_added" | "conflict" | "unavailable"; created_at: string | null; record_counts: Record<string, number>; file_count: number; warnings: string[]; blockers: string[] };
export type LibraryTakeoverPlan = LibraryPlanToken & { project_id: string | null; ltr_number: string | null; title: string; status: "ready" | "needs_information" | "already_managed" | "conflict"; missing: string[]; warnings: string[]; blockers: string[] };

export const getLibraryRuntime = (signal?: AbortSignal) => requestJson<LibraryRuntime>(`${BASE}/runtime`, { signal });
export const listLibraryMembers = (query = "", batchId = "", signal?: AbortSignal) => requestJson<{ items: LibraryMember[] }>(`${BASE}/members?${new URLSearchParams({ q: query, batch_id: batchId })}`, { signal });
export const getLibraryMember = (id: string, signal?: AbortSignal) => requestJson<LibraryMember>(memberPath(id), { signal });
export const scanLibrarySources = (roots: string[], signal?: AbortSignal) => post<LibraryScan>(`${BASE}/scan`, { roots }, signal);
export const planLibraryIntake = (sources: string[], signal?: AbortSignal, assignments?: LibraryFileAssignment[]) => post<LibraryIntakePlan>(`${BASE}/intake-plan`, { sources, ...(assignments ? { assignments } : {}) }, signal);
export const startLibraryBatch = (selection: LibraryPlanToken & { selected: string[]; keep_separate: string[] }) => post<LibraryBatch>(`${BASE}/batches`, selection);
export const getLibraryBatch = (id: string, signal?: AbortSignal) => requestJson<LibraryBatch>(`${BASE}/batches/${encodeURIComponent(id)}`, { signal });
export const resumeLibraryBatch = (id: string) => post<LibraryBatch>(`${BASE}/batches/${encodeURIComponent(id)}/resume`, {});
export const getLibraryFiles = (id: string, relativePath = "", signal?: AbortSignal) => requestJson<LibraryFiles>(`${memberPath(id)}/files?${new URLSearchParams({ relative_path: relativePath })}`, { signal });
export const openLibraryFolder = (id: string) => post<{ status: string; message: string }>(`${memberPath(id)}/open-folder`, {});
export const planLibraryTitle = (id: string, title: string) => post<LibraryLocationPlan>(`${memberPath(id)}/title-plan`, { title });
export const updateLibraryTitle = (id: string, plan: LibraryPlanToken) => post<LibraryMember>(`${memberPath(id)}/title`, plan);
export const planLibraryLocation = (id: string, folder: string) => post<LibraryLocationPlan>(`${memberPath(id)}/location-plan`, { folder });
export const updateLibraryLocation = (id: string, plan: LibraryPlanToken) => post<LibraryMember>(`${memberPath(id)}/location`, plan);
export const getPortableInfo = (id: string, signal?: AbortSignal) => requestJson<PortableInfo>(`${memberPath(id)}/portable`, { signal });
export const preparePortableProject = (id: string, fingerprint: string) => post<PortableInfo>(`${memberPath(id)}/prepare`, { fingerprint });
export const inspectPortableProject = (folder: string, signal?: AbortSignal) => post<PortableRestorePlan>(`${BASE}/inspect-portable`, { folder }, signal);
export const planPortableRestore = (folder: string, signal?: AbortSignal) => post<PortableRestorePlan>(`${BASE}/restore-plan`, { folder }, signal);
export const restorePortableProject = (plan: LibraryPlanToken) => post<{ status: "restored" | "already_added"; member: LibraryMember; warnings: string[] }>(`${BASE}/restore`, plan);
export const planLibraryTakeover = (id: string, signal?: AbortSignal) => requestJson<LibraryTakeoverPlan>(`${memberPath(id)}/takeover-plan`, { signal });
export const takeoverLibraryProject = (id: string, plan: LibraryPlanToken) => post<{ member: LibraryMember; project_id: string; warnings: string[] }>(`${memberPath(id)}/takeover`, plan);
export async function pickLibraryFolder(): Promise<string | null> {
  return (await requestJson<{ path: string | null }>("/api/tools/legacy-projects/pick-directory", { method: "POST" })).path;
}
