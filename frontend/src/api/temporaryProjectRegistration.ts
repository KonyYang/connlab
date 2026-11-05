import { requestJson, type SpecifiedLtrWorkbookAuthorityPreview } from './client';

export type TemporaryRegistrationValues = Record<string, string>;
export type TemporaryRegistrationPreview = {
  project_id: string; preview_token: string; ltr_number: string; action: string;
  workbook_path: string; values: TemporaryRegistrationValues;
  row: unknown[]; comparison: SpecifiedLtrWorkbookAuthorityPreview | null; recovery_required: boolean;
};
export type TemporaryRegistrationPreparation = {
  project_id: string; values: TemporaryRegistrationValues; required_fields: Record<string, string>;
  registered_ltr_number: string | null; recovery_preview: TemporaryRegistrationPreview | null;
};
const base = (projectId: string) => `/api/projects/${encodeURIComponent(projectId)}/ltr-registration`;
const post = (body: unknown): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
export const prepareTemporaryRegistration = (projectId: string) => requestJson<TemporaryRegistrationPreparation>(base(projectId));
export const previewTemporaryRegistration = (projectId: string, input: {
  values: TemporaryRegistrationValues; mode: string; specified_number: string | null;
}) => requestJson<TemporaryRegistrationPreview>(`${base(projectId)}/preview`, post(input));
export const commitTemporaryRegistration = (projectId: string, previewToken: string) =>
  requestJson<{ project_id: string; ltr_number: string }>(`${base(projectId)}/commit`, post({ preview_token: previewToken, operator_confirmed: true }));
