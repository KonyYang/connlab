import {requestJson, requestNoContent, type StandaloneCustomerReportJob} from './client';

type DecisionOption = {value: string; label: string};
export type CustomerDecisionField = {
  id: string; kind: 'sample' | 'material' | 'temperature'; label: string; part_number?: string;
  value?: string; options?: DecisionOption[]; depends_on?: string;
};
export type CustomerDecisions = Record<string, string>;
export type CustomerInspection = {
  source_sha256: string; input_id?: string; fields: CustomerDecisionField[]; decisions: CustomerDecisions;
  samples: {description: string; part_number: string; decision_id?: string; base_material: string;
    housing_material: string; base_decision_id?: string; housing_decision_id?: string}[];
  temperatures: {label: string; headers: string[]; rows: string[][]; decision_id?: string;
    options?: (DecisionOption & {cells: string[]; rows?: string[][]})[]}[];
};
export type WorkingCustomerSource = {
  expected_revision: number; output_id: string; output_sha256: string; temperature_result_ids: string[];
};
export function inspectUploadedCustomerSource(file: File) {
  const body = new FormData(); body.set('file', file);
  return requestJson<CustomerInspection>('/api/tools/customer-report/inspect', {method: 'POST', body});
}
export function inspectProjectCustomerSource(project: string, source: WorkingCustomerSource | {source_sha256: string}) {
  const action = 'output_id' in source ? 'authoring/customer/inspect' : 'customer-download/inspect';
  return requestJson<CustomerInspection>(`/api/projects/${encodeURIComponent(project)}/report-workspace/${action}`,
    {method: 'POST', body: JSON.stringify(source)});
}
export function discardCustomerInput(input: string) {
  return requestNoContent(`/api/tools/customer-report/inputs/${encodeURIComponent(input)}`, {method:'DELETE'});
}
export function startInspectedCustomerReport(input: string, decisions: CustomerDecisions) {
  return requestJson<StandaloneCustomerReportJob>(`/api/tools/customer-report/inputs/${encodeURIComponent(input)}/generate`,
    {method: 'POST', body: JSON.stringify({decisions})});
}
