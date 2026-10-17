import { useEffect, useRef, useState } from 'react';
import * as api from '../../api/temperature';
import { reportMetadata, type ReportInfoFields } from './reportInfo';
import { useTemperatureReportInfo } from './useTemperatureReportInfo';
import { equalSampleSize, regroupSamples } from './sampleGroups';

export type CoefficientFields = Record<keyof api.Coefficients, string>;
type State = {
  file: File | null; table: api.WorkbookTable | null; selection: api.DataSelection | null;
  region_issue: string | null;
  channel_layout: api.ChannelLayout | null; manualZeroIntercept: boolean;
  review: api.PreparedData | null; confirmed: boolean; zeroIntercept: boolean;
  analysis: api.TemperatureAnalysis | null; maximum: CoefficientFields | null; average: CoefficientFields | null;
  targetRise: string; current: number | null; maxTemperature: string; step: string; ambientPoint: string;
  derating: api.DeratingAnalysis | null; busy: string | null; error: string | null; downloaded: string | null;
};
const initial: State = {
  file: null, table: null, selection: null, region_issue: null, channel_layout: null, manualZeroIntercept: false, review: null, confirmed: false, zeroIntercept: true,
  analysis: null, maximum: null, average: null, targetRise: '30', current: null,
  maxTemperature: '105', step: '2.5', ambientPoint: '75', derating: null, busy: null, error: null, downloaded: null,
};
const clearResults = { analysis: null, maximum: null, average: null, current: null, derating: null, downloaded: null };

export function numeric(fields: CoefficientFields): api.Coefficients {
  if (Object.values(fields).some(value => !value.trim() || !Number.isFinite(Number(value)))) throw new Error('Enter all three finite coefficients.');
  return { a: Number(fields.a), b: Number(fields.b), c: Number(fields.c) };
}
function fields(values: api.Coefficients): CoefficientFields {
  return { a: values.a.toFixed(6), b: values.b.toFixed(6), c: values.c.toFixed(6) };
}
function parameter(value: string, label: string) {
  if (!value.trim() || !Number.isFinite(Number(value))) throw new Error(`Enter a valid ${label}.`);
  return Number(value);
}

export function useTemperatureTool() {
  const [state, setState] = useState<State>(initial);
  const reportInfo = useTemperatureReportInfo(state.table, state.selection);
  const generation = useRef(0);
  useEffect(() => () => { generation.current += 1; }, []);

  async function run<T>(label: string, operation: () => Promise<T>, success: (result: T) => Partial<State>) {
    const token = ++generation.current;
    setState(old => ({ ...old, busy: label, error: null, downloaded: null }));
    try {
      const result = await operation();
      if (token !== generation.current) return;
      setState(old => ({ ...old, ...success(result), busy: null }));
      return result;
    } catch (error) {
      if (token !== generation.current) return;
      setState(old => ({ ...old, busy: null, error: error instanceof Error ? error.message : 'The operation could not complete. Retry.' }));
    }
  }

  function load(file: File | null, sheetName?: string) {
    generation.current += 1;
    setState({ ...initial, file });
    if (!file) return;
    void run('Reading Workbook...', () => api.importTemperatureWorkbook(file, sheetName), result => ({
      ...result, channel_layout: result.channel_layout ?? null, file,
      zeroIntercept: result.channel_layout?.zero_intercept_default ?? true,
    }));
  }

  function changeData(patch: Partial<api.DataSelection>) {
    generation.current += 1;
    setState(old => {
      if (!old.selection) return old;
      const selection = { ...old.selection, ...patch };
      selection.temperature_columns = selection.temperature_columns.filter(column =>
        column !== selection.current_column && column !== selection.ambient_column);
      if (patch.sample_count !== undefined && !('sample_groups' in patch)) {
        selection.sample_groups = regroupSamples(selection.temperature_columns, selection);
        selection.thermocouples_per_sample = equalSampleSize(selection.sample_groups) ?? selection.thermocouples_per_sample;
      } else if (patch.thermocouples_per_sample !== undefined && !('sample_groups' in patch)) {
        // A manual count edit explicitly establishes new consecutive blocks.
        delete selection.sample_groups;
        selection.sample_count = null;
      } else if (selection.sample_groups) {
        selection.sample_groups = selection.sample_groups.map(group => group.filter(column => selection.temperature_columns.includes(column)));
      }
      selection.excluded_rows = selection.excluded_rows.filter(row => row >= selection.start_row && row <= selection.end_row);
      const zeroIntercept = !old.manualZeroIntercept && (patch.current_column !== undefined || patch.ambient_column !== undefined)
        ? !old.channel_layout?.stable_current_columns.some(column => column !== selection.current_column && column !== selection.ambient_column)
        : old.zeroIntercept;
      return { ...old, ...clearResults, selection, zeroIntercept, review: null, confirmed: false, busy: null, error: null };
    });
  }

  function correctRegion(region: api.DataRegion) {
    const { file, table } = state;
    if (!file || !table) return;
    return run('Checking Data Rows...', () => api.importTemperatureWorkbook(file, table.sheet_name, region),
      result => ({ ...result, channel_layout: result.channel_layout ?? null, ...clearResults,
        zeroIntercept: state.manualZeroIntercept ? state.zeroIntercept : result.channel_layout?.zero_intercept_default ?? true,
        review: null, confirmed: false }));
  }

  function request(zeroIntercept = state.zeroIntercept): api.PreparationRequest {
    if (!state.table || !state.selection) throw new Error('Import a workbook first.');
    // The backend quantizes the selected current once; source readings remain untouched.
    return { table: state.table, selection: { ...state.selection, current_multiplier: 1,
      current_decimals: state.selection.current_decimals ?? 0 },
      // Confirm Data retains warning-only rows; backend validation still blocks invalid readings.
      acknowledge_warnings: true, zero_intercept: zeroIntercept };
  }
  async function confirm() {
    const review = await run('Checking Data...', () => api.prepareTemperatureData(request()),
      review => ({ review, confirmed: review.ready }));
    if (!review?.ready) return;
    const zeroIntercept = !state.manualZeroIntercept && review.stable_auxiliary_current_columns !== undefined
      ? review.stable_auxiliary_current_columns.length === 0 : state.zeroIntercept;
    const analysis = await analyze(zeroIntercept);
    // Use this analysis, not state from the render before confirmation. A stale/failed run returns nothing.
    if (analysis && zeroIntercept) await generateDerating(fields(analysis.average_fit.coefficients));
  }
  async function analyze(zeroIntercept = state.zeroIntercept) {
    const analysis = await run('Generating T-riseChart...', () => api.analyzeTemperatureData(request(zeroIntercept)), analysis => ({
      ...clearResults, analysis, zeroIntercept, maximum: fields(analysis.maximum_fit.coefficients),
      average: fields(analysis.average_fit.coefficients),
    }));
    if (!analysis) return;
    // The render still has the old fit. Calculate from this response, and stop the chain on failure/staleness.
    const calculated = await calculateCurrent(fields(analysis.maximum_fit.coefficients));
    return calculated ? analysis : undefined;
  }
  function zeroIntercept(zeroIntercept: boolean) {
    generation.current += 1;
    setState(old => ({ ...old, ...clearResults, zeroIntercept, manualZeroIntercept: true, busy: null, error: null }));
  }
  function editParameter(key: 'targetRise' | 'maxTemperature' | 'step' | 'ambientPoint', value: string) {
    generation.current += 1;
    setState(old => ({ ...old, [key]: value, ...(key === 'targetRise' ? { current: null } : { derating: null }),
      downloaded: null, error: null, busy: null }));
  }
  function deratingSettings(): api.DeratingSettings {
    return { max_temperature: parameter(state.maxTemperature, 'maximum working temperature'),
      step: parameter(state.step, 'step'), ambient_point: parameter(state.ambientPoint, 'ambient point') };
  }
  const calculateCurrent = (maximum: CoefficientFields | null) => run('Calculating Current...', () => {
    if (!maximum) throw new Error('Generate T-riseChart first.');
    return api.calculateTemperatureCurrent(numeric(maximum), parameter(state.targetRise, 'target rise'));
  }, result => ({ current: result.current }));
  const current = () => calculateCurrent(state.maximum);
  const generateDerating = (average: CoefficientFields | null) => run('Generating Derating...', () => {
    if (!average) throw new Error('Generate T-riseChart first.');
    return api.generateTemperatureDerating(numeric(average), deratingSettings());
  }, result => ({ derating: result }));
  const derating = () => generateDerating(state.average);
  async function download() {
    const token = generation.current + 1;
    await run('Preparing Excel...', () => api.downloadTemperatureWorkbook({ ...request(),
      maximum_coefficients: state.maximum ? numeric(state.maximum) : null,
      average_coefficients: state.average ? numeric(state.average) : null,
      target_rise: state.current !== null ? parameter(state.targetRise, 'target rise') : null,
      derating: state.derating ? deratingSettings() : null,
      report_metadata: reportMetadata(reportInfo.values),
    }).then(result => {
      if (generation.current !== token) return null;
      const fileName = result.fileName ?? 'T-rise_Derating.xlsx';
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement('a');
      anchor.href = url; anchor.download = fileName;
      document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
      return fileName;
    }), downloaded => ({ downloaded }));
  }
  return { state, load, changeData, correctRegion, confirm, analyze, zeroIntercept,
    editParameter, current, derating, download, reportInfo,
    editReportInfo: (key: keyof ReportInfoFields, value: string) => {
      reportInfo.edit(key, value);
      setState(old => ({ ...old, downloaded: null }));
    },
  };
}
