import { useEffect, useRef, useState } from 'react';
import * as api from '../../api/temperature';

export type CoefficientFields = Record<keyof api.Coefficients, string>;
type State = {
  file: File | null; table: api.WorkbookTable | null; selection: api.DataSelection | null;
  review: api.PreparedData | null; acknowledged: boolean; confirmed: boolean; zeroIntercept: boolean;
  analysis: api.TemperatureAnalysis | null; maximum: CoefficientFields | null; average: CoefficientFields | null;
  targetRise: string; current: number | null; maxTemperature: string; step: string; ambientPoint: string;
  derating: api.DeratingAnalysis | null; busy: string | null; error: string | null; downloaded: string | null;
};
const initial: State = {
  file: null, table: null, selection: null, review: null, acknowledged: false, confirmed: false, zeroIntercept: true,
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
  const generation = useRef(0);
  useEffect(() => () => { generation.current += 1; }, []);

  async function run<T>(label: string, operation: () => Promise<T>, success: (result: T) => Partial<State>) {
    const token = ++generation.current;
    setState(old => ({ ...old, busy: label, error: null, downloaded: null }));
    try {
      const result = await operation();
      if (token !== generation.current) return;
      setState(old => ({ ...old, ...success(result), busy: null }));
    } catch (error) {
      if (token !== generation.current) return;
      setState(old => ({ ...old, busy: null, error: error instanceof Error ? error.message : 'The operation could not complete. Retry.' }));
    }
  }

  function load(file: File | null, sheetName?: string) {
    generation.current += 1;
    setState(old => ({ ...initial, file, zeroIntercept: old.zeroIntercept }));
    if (!file) return;
    void run('Reading Workbook...', () => api.importTemperatureWorkbook(file, sheetName), result => ({ ...result, file }));
  }

  function changeData(patch: Partial<api.DataSelection>) {
    generation.current += 1;
    setState(old => {
      if (!old.selection) return old;
      const selection = { ...old.selection, ...patch };
      selection.excluded_rows = selection.excluded_rows.filter(row => row >= selection.start_row && row <= selection.end_row);
      return { ...old, ...clearResults, selection, review: null, acknowledged: false, confirmed: false, busy: null, error: null };
    });
  }

  function request(): api.PreparationRequest {
    if (!state.table || !state.selection) throw new Error('Import a workbook first.');
    return { table: state.table, selection: state.selection, acknowledge_warnings: state.acknowledged, zero_intercept: state.zeroIntercept };
  }
  const confirm = () => run('Checking Data...', () => api.prepareTemperatureData(request()), review => ({ review, confirmed: review.ready }));
  const analyze = () => run('Generating T-riseChart...', () => api.analyzeTemperatureData(request()), analysis => ({ ...clearResults, analysis }));
  function acknowledge(acknowledged: boolean) {
    generation.current += 1;
    setState(old => ({ ...old, ...clearResults, confirmed: false, acknowledged, busy: null }));
  }
  function zeroIntercept(zeroIntercept: boolean) {
    generation.current += 1;
    setState(old => ({ ...old, ...clearResults, zeroIntercept, busy: null, error: null }));
  }
  function getCoefficients() {
    setState(old => old.analysis ? { ...old, maximum: fields(old.analysis.maximum_fit.coefficients),
      average: fields(old.analysis.average_fit.coefficients), current: null, derating: null, downloaded: null, error: null } : old);
  }
  function editCoefficient(curve: 'maximum' | 'average', key: keyof api.Coefficients, value: string) {
    generation.current += 1;
    setState(old => ({ ...old, [curve]: { ...old[curve], [key]: value },
      ...(curve === 'maximum' ? { current: null } : { derating: null }), downloaded: null, error: null, busy: null }));
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
  const current = () => run('Calculating Current...', () => {
    if (!state.maximum) throw new Error('Get Coefficients first.');
    return api.calculateTemperatureCurrent(numeric(state.maximum), parameter(state.targetRise, 'target rise'));
  }, result => ({ current: result.current }));
  const derating = () => run('Generating Derating...', () => {
    if (!state.average) throw new Error('Get Coefficients first.');
    return api.generateTemperatureDerating(numeric(state.average), deratingSettings());
  }, result => ({ derating: result }));
  async function download() {
    const token = generation.current + 1;
    await run('Preparing Excel...', () => api.downloadTemperatureWorkbook({ ...request(),
      maximum_coefficients: state.maximum ? numeric(state.maximum) : null,
      average_coefficients: state.average ? numeric(state.average) : null,
      target_rise: state.current !== null ? parameter(state.targetRise, 'target rise') : null,
      derating: state.derating ? deratingSettings() : null,
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
  return { state, load, changeData, confirm, analyze, acknowledge, zeroIntercept,
    getCoefficients, editCoefficient, editParameter, current, derating, download };
}
