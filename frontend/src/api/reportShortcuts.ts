import { requestJson } from "./client";
export type ReportRole = "internal" | "customer";
export type ReportShortcut = {role: ReportRole; relative_path: string; available: boolean; modified_at: string | null};
export type ReportShortcuts = {key: string; items: ReportShortcut[]};
const base = "/api/project-library/report-shortcuts";
export const getReportShortcuts = (key: string, signal?: AbortSignal) => requestJson<ReportShortcuts>(`${base}?${new URLSearchParams({key})}`, {signal});
export const setReportShortcut = (key: string, role: ReportRole, relative_path: string, expected_path: string | null, replacement_confirmed=false) => requestJson<ReportShortcuts>(`${base}/set`, {method:"POST", body:JSON.stringify({key,role,relative_path,expected_path,replacement_confirmed})});
export const clearReportShortcut = (key: string, role: ReportRole, expected_path: string) => requestJson<ReportShortcuts>(`${base}/clear`, {method:"POST", body:JSON.stringify({key,role,expected_path})});
