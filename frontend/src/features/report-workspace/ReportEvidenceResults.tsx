import { useEffect, useRef, useState } from 'react';
import { confirmReportResult, getReportSourceTable, getReportSourceRegion, previewReportResult, type ReportAuthoringState,
  type ReportResult, type ReportTable, type SemanticRecord, type SemanticResultImportRequest,
  type ResultAdoption, type RelatedResultImportRequest, type ReportSourceBlock } from '../../api/reportAuthoring';

type Kind = 'electrical' | 'resistance_stages';
const record = (kind: Kind): SemanticRecord => kind === 'electrical'
  ? { stage: '', measurement: 'ir', cells: {}, unit: 'MΩ', voltage_v: '', duration_s: '', condition_locator: '' }
  : { stage: '', quantity: 'absolute', cells: {}, unit: 'mΩ' };
const columnLabel = (index: number): string => index < 26 ? String.fromCharCode(65 + index)
  : columnLabel(Math.floor(index / 26) - 1) + String.fromCharCode(65 + index % 26);

export function ReportEvidenceResults({ projectId, state, disabled, beginOperation, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  beginOperation: () => (() => void) | null; onChanged: (next: ReportAuthoringState) => void;
}) {
  const [kind, setKind] = useState<Kind>('electrical');
  const [sourceId, setSourceId] = useState('');
  const [table, setTable] = useState<ReportTable | null>(null);
  const [sheet, setSheet] = useState('');
  const [stepIndex, setStepIndex] = useState(-1);
  const [records, setRecords] = useState<SemanticRecord[]>([record('electrical')]);
  const [selectionConfirmed, setSelectionConfirmed] = useState(false);
  const [outcome, setOutcome] = useState<SemanticResultImportRequest['outcome']>('pending');
  const [reason, setReason] = useState('');
  const [preview, setPreview] = useState<ReportResult | null>(null);
  const [checked, setChecked] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const epoch = useRef(0);
  const sources = state.sources.filter(source => ['evidence', 'cr'].includes(source.role) && /\.(csv|xls|xlsx)$/i.test(source.file_name));
  useEffect(() => { epoch.current += 1; setPreview(null); setChecked(false); },
    [projectId, state.revision, kind, sourceId, sheet, records, stepIndex, selectionConfirmed, outcome, reason]);
  useEffect(() => { setSourceId(''); setTable(null); setRecords([record('electrical')]); setKind('electrical'); setStepIndex(-1); }, [projectId]);
  useEffect(() => () => { epoch.current += 1; }, []);
  function edit(index: number, patch: Partial<SemanticRecord>) {
    setRecords(records.map((row, i) => i === index ? { ...row, ...patch } : row));
  }
  async function readSheet(nextSheet = '') {
    if (disabled || busy || !sourceId) return;
    const release = beginOperation(); if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try {
      const next = await getReportSourceTable(projectId, sourceId, nextSheet);
      if (token === epoch.current) { setTable(next); setSheet(next.sheet_name); setRecords([record(kind)]); setSelectionConfirmed(false); }
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to read source cells.'); }
    finally { release(); setBusy(false); }
  }
  async function evaluate(confirm = false) {
    const step = state.context.steps[stepIndex];
    if (!step || !table || disabled || busy) return;
    const release = beginOperation(); if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    const request: SemanticResultImportRequest = { expected_revision: state.revision, source_id: sourceId, kind, sheet_name: sheet,
      group_id: step.group_id, row_id: step.row_id, step_token: step.step_token, outcome, acceptance_reason: reason,
      semantic_selection: { type: kind, records, selection_confirmed: selectionConfirmed } };
    try {
      if (confirm && preview && checked) {
        const next = await confirmReportResult(projectId, { ...request, preview_sha256: preview.preview_sha256 });
        if (token === epoch.current) { onChanged(next); setPreview(null); }
      } else {
        const next = await previewReportResult(projectId, request);
        if (token === epoch.current) { setPreview(next); setChecked(false); }
      }
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to read the selected measurements.'); }
    finally { release(); setBusy(false); }
  }
  return <><RelatedReportEvidence projectId={projectId} state={state} disabled={disabled} beginOperation={beginOperation} onChanged={onChanged} />
  {sources.length > 0 && <section aria-label="Electrical and multistage evidence" className="report-evidence-results">
    <h3>Electrical and multi-stage measurements</h3>
    <p>Read retained source cells. Add all samples, pairs and stages for one report Step together. Blank cells stay blank; no automatic Pass is assigned.</p>
    <fieldset disabled={disabled || busy}>
      <label>Evidence workbook<select value={sourceId} onChange={event => { setSourceId(event.target.value); setTable(null); setSheet(''); }}>
        <option value="">Choose retained source</option>{sources.map(source => <option key={source.source_id} value={source.source_id}>{source.file_name}</option>)}
      </select></label>
      <label>Measurement family<select value={kind} onChange={event => { const next = event.target.value as Kind; setKind(next); setRecords([record(next)]); setSelectionConfirmed(false); }}>
        <option value="electrical">IR / DWV</option><option value="resistance_stages">LLCR / CR by stage</option>
      </select></label>
      <button type="button" disabled={!sourceId} onClick={() => void readSheet()}>Read evidence workbook</button>
      {table && <>
        <label>Evidence sheet<select value={sheet} onChange={event => void readSheet(event.target.value)}>
          {table.sheet_names.map(name => <option key={name}>{name}</option>)}
        </select></label>
        <details><summary>Source cell preview</summary><div className="report-evidence-source-table"><table><thead><tr><th>Row</th>{Array.from({ length: Math.max(0, ...table.rows.map(row => row.length)) }, (_, col) => <th key={col}>{columnLabel(col)}</th>)}</tr></thead><tbody>
          {table.rows.slice(0, 80).map((row, index) => <tr key={index}><th>{index + 1}</th>{row.map((value, col) => <td key={col} title={`${columnLabel(col)}${index + 1}`}>{String(value ?? '')}</td>)}</tr>)}
        </tbody></table></div><p>Preview shows the first 80 rows; selected addresses are checked against the complete retained sheet.</p></details>
        <label>Evidence Group / Step<select value={stepIndex} onChange={event => setStepIndex(Number(event.target.value))}>
          <option value={-1}>Choose confirmed Matrix step</option>{state.context.steps.map((step, index) => <option key={index} value={index}>Group {step.group_label} / {step.step_token} / {step.test_item}</option>)}
        </select></label>
        {records.map((row, index) => <fieldset key={index}><legend>Measurement {index + 1}</legend>
          <label>Stage<input value={row.stage} onChange={event => edit(index, { stage: event.target.value })} placeholder="Initial, Final, Post humidity…" /></label>
          {kind === 'electrical' ? <label>Electrical quantity<select value={row.measurement} onChange={event => edit(index, { measurement: event.target.value as 'ir' | 'dwv', unit: event.target.value === 'ir' ? 'MΩ' : 'µA' })}>
            <option value="ir">Insulation resistance</option><option value="dwv">DWV leakage / breakdown</option></select></label>
            : <label>Resistance quantity<select value={row.quantity} onChange={event => edit(index, { quantity: event.target.value as SemanticRecord['quantity'] })}>
              <option value="absolute">Absolute R from source</option><option value="delta">ΔR already recorded in source</option><option value="delta_from_absolute">Calculate ΔR from absolute R and selected baseline</option>
            </select></label>}
          <label>Source unit<select value={row.unit} onChange={event => edit(index, { unit: event.target.value })}>
            {(kind === 'resistance_stages' ? ['mΩ', 'Ω'] : row.measurement === 'ir' ? ['MΩ', 'GΩ', 'Ω'] : ['µA', 'mA', 'nA']).map(unit => <option key={unit}>{unit}</option>)}
          </select></label>
          {['sample', 'pair', 'value', ...(kind === 'electrical' && row.measurement === 'dwv' ? ['breakdown'] : []), ...(row.quantity === 'delta_from_absolute' ? ['baseline'] : [])].map(key =>
            <label key={key}>{key} source cell<input value={row.cells[key] || ''} placeholder="C22" onChange={event => {
              const cells = { ...row.cells }; if (event.target.value.trim()) cells[key] = event.target.value.trim(); else delete cells[key]; edit(index, { cells });
            }} /></label>)}
          {kind === 'electrical' && <><label>Confirmed test voltage / V<input value={row.voltage_v} onChange={event => edit(index, { voltage_v: event.target.value })} /></label>
            <label>Confirmed duration / seconds<input value={row.duration_s} onChange={event => edit(index, { duration_s: event.target.value })} /></label>
            <label>Condition source location<input value={row.condition_locator} onChange={event => edit(index, { condition_locator: event.target.value })} placeholder="Sheet / condition cell, e.g. B14" /></label></>}
          {records.length > 1 && <button type="button" onClick={() => setRecords(records.filter((_, i) => i !== index))}>Remove measurement {index + 1}</button>}
        </fieldset>)}
        <button type="button" onClick={() => setRecords([...records, { ...records[records.length - 1], cells: {} }])}>Add measurement / stage</button>
        <label><input type="checkbox" checked={selectionConfirmed} onChange={event => setSelectionConfirmed(event.target.checked)} />I checked source labels, stages, units and sample/pair identities against this Matrix Step</label>
        <label>Evidence report outcome<select value={outcome} onChange={event => setOutcome(event.target.value as typeof outcome)}><option value="pending">Pending decision</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="not_applicable">Not applicable</option></select></label>
        <label>Evidence acceptance reason<textarea value={reason} onChange={event => setReason(event.target.value)} /></label>
        <button type="button" disabled={stepIndex < 0} onClick={() => void evaluate()}>Preview selected measurements</button>
      </>}
    </fieldset>
    {error && <p role="alert">{error}</p>}
    {preview && <div><p>Report outcome: {preview.outcome}. {preview.data.missing && 'Some measurements or observations are missing; keep engineering acceptance pending.'}</p>
      <table><thead><tr><th>Sample</th><th>Pair</th><th>Stage</th><th>Quantity</th><th>Value</th><th>Breakdown observation</th></tr></thead><tbody>
        {preview.data.rows?.map((row, index) => <tr key={index}><td>{String(row.sample_id)}</td><td>{String(row.pair ?? '')}</td><td>{String(row.stage)}</td>
          <td>{String(row.measurement ?? row.quantity)}</td><td>{row.value == null ? 'Not recorded' : `${row.comparator || ''}${row.value} ${row.unit}`}</td><td>{String(row.breakdown ?? '—')}</td></tr>)}
      </tbody></table>
      <label><input type="checkbox" disabled={disabled || busy} checked={checked} onChange={event => setChecked(event.target.checked)} />I verified the selected source cells and this preview</label>
      <button type="button" disabled={disabled || busy || !checked} onClick={() => void evaluate(true)}>Retain measurements for report</button>
    </div>}
  </section>}</>;
}

function RelatedReportEvidence({ projectId, state, disabled, beginOperation, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  beginOperation: () => (() => void) | null; onChanged: (next: ReportAuthoringState) => void;
}) {
  const [kind, setKind] = useState<'external_reference' | 'linked_temperature'>('external_reference');
  const [sourceId, setSourceId] = useState('');
  const [step, setStep] = useState(-1);
  const [blocks, setBlocks] = useState<ReportSourceBlock[]>([]);
  const [start, setStart] = useState(-1); const [end, setEnd] = useState(-1);
  const [freeze, setFreeze] = useState(false);
  const emptyAdoption: ResultAdoption = { report_identity: '', source_version: '', source_locator: '', adopted_scope: '',
    applicability_reason: '', adverse_observations: '', source_observations: '', confirmed: false, customer_reference_allowed: false };
  const [adoption, setAdoption] = useState<ResultAdoption>(emptyAdoption);
  const [outcome, setOutcome] = useState<RelatedResultImportRequest['outcome']>('pending');
  const [reason, setReason] = useState('');
  const [preview, setPreview] = useState<ReportResult | null>(null);
  const [checked, setChecked] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const epoch = useRef(0);
  useEffect(() => { epoch.current += 1; setPreview(null); setChecked(false); }, [projectId, state.revision, sourceId, kind, step, adoption, start, end, freeze, outcome, reason]);
  useEffect(() => { setAdoption(previous => ({ ...previous, confirmed: false, customer_reference_allowed: false })); setOutcome('pending'); setReason(''); }, [sourceId, kind, step, start, end]);
  useEffect(() => { setSourceId(''); setBlocks([]); setAdoption(emptyAdoption); setStep(-1); }, [projectId]);
  useEffect(() => () => { epoch.current += 1; }, []);
  const sources = state.sources.filter(source => source.role === 'evidence' && (kind !== 'linked_temperature' || /\.docx$/i.test(source.file_name)));
  async function run(action: 'read' | 'preview' | 'confirm') {
    if (disabled || busy || !sourceId) return;
    const release = beginOperation(); if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try {
      if (action === 'read') {
        const next = await getReportSourceRegion(projectId, sourceId);
        if (token === epoch.current) { setBlocks(next); setStart(-1); setEnd(-1); }
      } else {
        const target = state.context.steps[step]; if (!target) return;
        const request: RelatedResultImportRequest = { expected_revision: state.revision, source_id: sourceId, kind,
          group_id: target.group_id, row_id: target.row_id, step_token: target.step_token,
          outcome, acceptance_reason: reason, adoption,
          ...(kind === 'linked_temperature' ? { linked_region: { start, end, freeze_external_charts: freeze } } : {}) };
        if (action === 'confirm' && checked && preview) {
          const next = await confirmReportResult(projectId, { ...request, preview_sha256: preview.preview_sha256 });
          if (token === epoch.current) { onChanged(next); setPreview(null); }
        } else {
          const next = await previewReportResult(projectId, request);
          if (token === epoch.current) { setPreview(next); setChecked(false); }
        }
      }
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to inspect related evidence.'); }
    finally { release(); setBusy(false); }
  }
  if (!state.sources.some(source => source.role === 'evidence')) return null;
  return <section aria-label="Related report adoption" className="report-evidence-results">
    <h3>Related report evidence</h3><p>Adopt only a defined source scope. Its observations are not this project's Pass decision. Acceptance starts pending and requires separate project evidence.</p>
    <fieldset disabled={disabled || busy}>
      <label>Adoption mode<select value={kind} onChange={event => { setKind(event.target.value as typeof kind); setSourceId(''); setBlocks([]); }}>
        <option value="external_reference">Scoped reference and observations</option><option value="linked_temperature">Native temperature table and curve from DOCX</option></select></label>
      <label>Related evidence source<select value={sourceId} onChange={event => { setSourceId(event.target.value); setBlocks([]); setStart(-1); setEnd(-1); }}>
        <option value="">Choose retained evidence</option>{sources.map(source => <option key={source.source_id} value={source.source_id}>{source.file_name}</option>)}</select></label>
      <label>Related evidence Group / Step<select value={step} onChange={event => setStep(Number(event.target.value))}>
        <option value={-1}>Choose confirmed Matrix step</option>{state.context.steps.map((target, index) => <option key={index} value={index}>Group {target.group_label} / {target.step_token} / {target.test_item}</option>)}</select></label>
      {([['report_identity', 'Source report number'], ['source_version', 'Source report version'], ['source_locator', 'Source page / table / section'],
        ['adopted_scope', 'Exact scope adopted for this project'], ['applicability_reason', 'Why this evidence applies to this project'],
        ['source_observations', 'Source observations'], ['adverse_observations', 'Adverse observations and applicability limitations']] as const).map(([key, label]) =>
        <label key={key}>{label}<textarea value={adoption[key]} onChange={event => { setAdoption({ ...adoption, [key]: event.target.value, confirmed: false, customer_reference_allowed: false }); setOutcome('pending'); }} /></label>)}
      {kind === 'linked_temperature' && <><button type="button" disabled={!sourceId} onClick={() => void run('read')}>Inspect source report region</button>
        {blocks.length > 0 && <><label>First source block<select value={start} onChange={event => setStart(Number(event.target.value))}><option value={-1}>Choose start</option>{blocks.map(block => <option key={block.index} value={block.index}>{block.index}: {block.kind} {block.text.slice(0, 100)}</option>)}</select></label>
          <label>Last source block<select value={end} onChange={event => setEnd(Number(event.target.value))}><option value={-1}>Choose end</option>{blocks.filter(block => block.index >= start).map(block => <option key={block.index} value={block.index}>{block.index}: {block.kind} {block.text.slice(0, 100)}</option>)}</select></label>
          <div>{blocks.filter(block => block.index >= start && block.index <= end).map(block => <p key={block.index}>{block.index} · {block.text || block.kind} ({block.tables} tables, {block.charts} native charts)</p>)}</div></>}
        <label><input type="checkbox" checked={freeze} onChange={event => setFreeze(event.target.checked)} />Freeze complete source curve caches; do not connect to or update the external workbook</label></>}
      <label><input type="checkbox" checked={adoption.confirmed} onChange={event => setAdoption({ ...adoption, confirmed: event.target.checked })} />I confirmed this exact evidence scope and its applicability, not an automatic Pass</label>
      <label><input type="checkbox" checked={adoption.customer_reference_allowed} onChange={event => setAdoption({ ...adoption, customer_reference_allowed: event.target.checked })} />This exact related-report reference and adopted region may appear in the customer copy</label>
      <label>Related evidence outcome<select value={outcome} onChange={event => setOutcome(event.target.value as typeof outcome)}><option value="pending">Pending decision</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="not_applicable">Not applicable</option></select></label>
      <label>Current-project acceptance evidence<textarea value={reason} onChange={event => setReason(event.target.value)} /></label>
      <button type="button" disabled={!sourceId || step < 0 || (kind === 'linked_temperature' && (start < 0 || end < start))} onClick={() => void run('preview')}>Preview scoped adoption</button>
    </fieldset>
    {error && <p role="alert">{error}</p>}
    {preview && <><p>Engineering outcome: {preview.outcome}. Frozen native charts: {preview.data.frozen_chart_count || 0}. No source workbook is fetched.</p>
      <p>{preview.data.excerpt || preview.data.adoption?.adopted_scope}</p>
      <label><input type="checkbox" disabled={disabled || busy} checked={checked} onChange={event => setChecked(event.target.checked)} />I checked the selected region and reference preview</label>
      <button type="button" disabled={disabled || busy || !checked} onClick={() => void run('confirm')}>Retain scoped evidence</button></>}
  </section>;
}
