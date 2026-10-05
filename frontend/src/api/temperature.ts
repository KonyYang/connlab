import { requestJson, requestBlobResponse } from './client';

export type WorkbookTable = { file_name: string; sheet_names: string[]; sheet_name: string; rows: (string | number | boolean | null)[][] };
export type DataSelection = {
  header_row: number; start_row: number; end_row: number; ambient_column: number; current_column: number;
  temperature_columns: number[]; thermocouples_per_sample: number; excluded_rows: number[]; current_multiplier: number;
};
export type DataRegion = Pick<DataSelection, 'header_row' | 'start_row' | 'end_row'>;
export type WorkbookImportResult = { table: WorkbookTable; selection: DataSelection | null; region_issue: string | null };
export type PreparationRequest = { table: WorkbookTable; selection: DataSelection; acknowledge_warnings: boolean; zero_intercept: boolean };
export type DataIssue = { code: string; severity: string; source_row: number; message: string };
export type PreparedData = { ready: boolean; issues: DataIssue[]; measurements: { source_row: number; current: number; ambient: number; temperatures: number[] }[] };
export type Coefficients = { a: number; b: number; c: number };
export type PolynomialFit = { coefficients: Coefficients; fitted_coefficients: Coefficients; r_squared: number };
export type RisePoint = { source_row: number | null; current: number; maximum: number; average: number; rises: number[]; sample_maxima: number[] };
export type TemperatureAnalysis = { points: RisePoint[]; maximum_fit: PolynomialFit; average_fit: PolynomialFit; zero_intercept: boolean; thermocouples_per_sample: number };
export type DeratingSettings = { max_temperature: number; step: number; ambient_point: number };
export type DeratingPoint = { ambient: number; basic: number; derated: number };
export type DeratingAnalysis = { points: DeratingPoint[]; annotation: DeratingPoint; coefficients: Coefficients; max_temperature: number; step: number };
export type TemperatureDownloadRequest = PreparationRequest & {
  maximum_coefficients: Coefficients | null; average_coefficients: Coefficients | null;
  target_rise: number | null; derating: DeratingSettings | null;
};
const base = '/api/tools/temperature-rise';
const post = (body: unknown): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

export function importTemperatureWorkbook(file: File, sheetName?: string, region?: DataRegion) {
  const body = new FormData();
  body.append('file', file);
  if (sheetName) body.append('sheet_name', sheetName);
  if (region) for (const [key, value] of Object.entries(region)) body.append(key, String(value));
  return requestJson<WorkbookImportResult>(`${base}/import`, { method: 'POST', body });
}
export const prepareTemperatureData = (request: PreparationRequest) => requestJson<PreparedData>(`${base}/prepare`, post(request));
export const analyzeTemperatureData = (request: PreparationRequest) => requestJson<TemperatureAnalysis>(`${base}/analyze`, post(request));
export const calculateTemperatureCurrent = (coefficients: Coefficients, targetRise: number) =>
  requestJson<{ current: number }>(`${base}/current`, post({ coefficients, target_rise: targetRise }));
export const generateTemperatureDerating = (coefficients: Coefficients, settings: DeratingSettings) =>
  requestJson<DeratingAnalysis>(`${base}/derating`, post({ coefficients, ...settings }));
export const downloadTemperatureWorkbook = (request: TemperatureDownloadRequest) => requestBlobResponse(`${base}/download`, post(request));
