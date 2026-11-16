import { requestJson, pickExternalResourcePath } from "./client";
import type { ReferenceProject } from "./referenceLibrary";
const base = "/api/material-receipts";
const post = <T,>(path: string, body: unknown) => requestJson<T>(`${base}${path}`, { method: "POST", body: JSON.stringify(body) });
export type ReceiptRuntime = { root_path: string; revision: number; configured: boolean; available: boolean };
export type ReceiptInput = { source: string; number: string; product_name: string; test_keywords: string; target_key: string; separate_description: string; material_state: string | null };
export type ReceiptCandidate = ReferenceProject & { can_supplement: boolean; reason: string };
export type ReceiptItem = { relative_path: string; target_relative: string; directory: boolean; action: string; reason: string; status?: string; message?: string };
export type ReceiptPlan = { status: "choose_target" | "choose_state" | "ready"; batch_id?: string; plan_id?: string; fingerprint?: string; target_path?: string; source_path?: string; product_name?: string; number?: string; material_state?: string; supplement?: boolean; candidates: ReceiptCandidate[]; items?: ReceiptItem[]; message?: string };
export type ReceiptBatch = { operation?: string; copy_context?: {session_id: string; intent: number}; batch_id: string; status: string; target_path: string; source_path: string; target_key: string; receipt_id: string | null; message?: string; items: ReceiptItem[]; counts: Record<string, number>; directory_counts: Record<string, number> };
export type ReceiptHistory = { batch_id: string; status: string; source_path: string; created_at: string; counts: Record<string, number>; directory_counts: Record<string, number> };
export type ReceiptDetail = { history?: ReceiptHistory[]; receipt_id: string; number: string | null; product_name: string; test_keywords: string; description: string; material_state: string; folder_path: string; source_path: string; revision: number; batch_id: string; created_at: string; available: boolean; batch: ReceiptBatch };
export type ReceiptLocationPlan = { plan_id: string; fingerprint: string; folder_path: string };
export const getReceiptRuntime = () => requestJson<ReceiptRuntime>(`${base}/runtime`);
export const setReceiptDestination = (folder: string) => post<ReceiptRuntime>("/destination", { folder });
export const previewReceipt = (input: ReceiptInput) => post<ReceiptPlan>("/preview", input);
export const confirmReceipt = (plan: ReceiptPlan) => post<ReceiptBatch>("/confirm", { plan_id: plan.plan_id, fingerprint: plan.fingerprint });
export const getReceiptBatch = (id: string) => requestJson<ReceiptBatch>(`${base}/batches/${encodeURIComponent(id)}`);
export const retryReceipt = (id: string, context?: CopyContextProof) => post<ReceiptBatch>(`/batches/${encodeURIComponent(id)}/retry`, { context });
export const getReceiptDetail = (id: string) => requestJson<ReceiptDetail>(`${base}/entries/${encodeURIComponent(id)}`);
export const editReceiptMetadata = (id: string, values: { revision: number; product_name: string; test_keywords: string; material_state: string }) => post<ReceiptDetail>(`/entries/${encodeURIComponent(id)}/metadata`, values);
export const previewReceiptLocation = (id: string, folder: string) => post<ReceiptLocationPlan>(`/entries/${encodeURIComponent(id)}/location-preview`, { folder });
export const confirmReceiptLocation = (id: string, plan: ReceiptLocationPlan) => post<ReceiptDetail>(`/entries/${encodeURIComponent(id)}/location`, { plan_id: plan.plan_id, fingerprint: plan.fingerprint });
export const pickReceiptFolder = async () => (await pickExternalResourcePath("project_output_root")).path;

export const previewCatalogLocation = (key: string, folder: string) => post<ReceiptLocationPlan>("/catalog-location-preview", { key, folder });
export const confirmCatalogLocation = (key: string, plan: ReceiptLocationPlan) => post<{ key: string; folder_path: string; source_path: string; revision: number }>("/catalog-location", { key, plan_id: plan.plan_id, fingerprint: plan.fingerprint });

export const previewMaterialCopy = (input: { source_key: string; relative_path: string; context: CopyContextProof; target_relative_directory: string }) => post<ReceiptPlan>("/copy-preview", input);
export const confirmMaterialCopy = (plan: ReceiptPlan, context: CopyContextProof) => post<ReceiptBatch>("/copy-confirm", { plan_id: plan.plan_id, fingerprint: plan.fingerprint, context });

export const getCatalogReceiptHistory = (key: string) => requestJson<{ items: ReceiptHistory[] }>(`${base}/catalog-history?${new URLSearchParams({ key })}`);


export type CopyContextProof = { session_id: string; token: string };
export type WorkbenchCopyContext = CopyContextProof & { intent: number; target: ReferenceProject };
export type CopyContextState = {session_id: string; intent: number; token: string | null; target: ReferenceProject | null};
export const createCopyContextSession = () => post<{session_id: string}>("/copy-context/session", {});
export const updateCopyContext = (session_id: string, intent: number, project_id: string | null) => post<CopyContextState>("/copy-context", {session_id, intent, project_id});
export const copyContextProof = (context: WorkbenchCopyContext): CopyContextProof => ({session_id: context.session_id, token: context.token});


export type ArchivePlan = {status:"ready"|"conflict"|"existing"|"pending";source_path:string;target_path:string;target_key?:string;plan_id?:string;fingerprint?:string;batch_id?:string;file_count?:number;operation?:ReceiptBatch};
export type ArchiveJob = {status:"working"|"cancellation_requested"|"done"|"cancelled"|"failed";result?:unknown;error?:string};
export const startArchivePreview=(source:string,independent=false)=>post<{job_id:string}>("/archive/preview",{source,independent});
export const confirmArchive=(plan:ArchivePlan)=>post<{job_id:string}>("/archive/confirm",{plan_id:plan.plan_id,fingerprint:plan.fingerprint});
export const refreshArchive=()=>post<{job_id:string}>("/archive/refresh",{});
export const getArchiveJob=(id:string)=>requestJson<ArchiveJob>(`${base}/archive/jobs/${encodeURIComponent(id)}`);
export const cancelArchiveJob=(id:string)=>post<ArchiveJob>(`/archive/jobs/${encodeURIComponent(id)}/cancel`,{});
export const getArchiveOperation=(id:string)=>requestJson<ReceiptBatch>(`${base}/archive/operations/${encodeURIComponent(id)}`);
export const retryArchive=(id:string)=>post<{job_id:string}>(`/archive/operations/${encodeURIComponent(id)}/retry`,{});
