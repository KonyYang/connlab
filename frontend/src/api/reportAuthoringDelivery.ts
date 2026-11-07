import { requestJson } from './client';
import type { ReportAuthoringState, DocumentReviewIdentity } from './reportAuthoring';

export type ReportDeliveryOperation = { operation_id: string; status: string;
  output_id?: string; output_sha256?: string; customer_output_id?: string; customer_sha256?: string; basis_sha256?: string;
  items: { role: string; file_name: string; status: string }[]; formal_release?: boolean };
export type ReportDeliveryPreview = { can_save: boolean; issues: { code: string; message: string }[];
  output_id?: string; output_sha256?: string; customer_output_id?: string | null;
  preview_sha256: string | null; review_sha256?: string; expected_revision?: number;
  workspace?: { files: { role: string; file_name: string; replaces_existing: boolean; archive_required: boolean }[]; notice: string } | null;
  operation: ReportDeliveryOperation | null; operation_matches_current?: boolean };
const base = (id: string) => `/api/projects/${encodeURIComponent(id)}/report-workspace/authoring/delivery`;
export const getReportDelivery = (id: string) => requestJson<ReportDeliveryPreview>(base(id));
export const confirmReportRetainedContent = (id: string, request: DocumentReviewIdentity & {
  review_sha256: string; confirmed_by: string; notes: string;
}) => requestJson<ReportAuthoringState>(base(id) + '/content-review', { method: 'POST', body: JSON.stringify(request) });
export const saveReviewedReports = (id: string, request: DocumentReviewIdentity & {
  customer_output_id: string; preview_sha256: string; confirmed_by: string;
}) => requestJson<ReportAuthoringState>(base(id) + '/save', { method: 'POST', body: JSON.stringify(request) });
export const resumeReviewedReportSave = (id: string, operationId: string) =>
  requestJson<ReportAuthoringState>(base(id) + '/resume', { method: 'POST', body: JSON.stringify({ operation_id: operationId }) });
