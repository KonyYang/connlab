import { useEffect, useRef, useState } from 'react';
import { confirmReportResult, getReportToolsPackage, previewReportResult,
  type ReportAuthoringState, type ReportResult, type ReportToolsPackage, type ToolsPackageImportRequest } from '../../api/reportAuthoring';

export function ReportToolsPackageImport({ projectId, state, disabled, beginOperation, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  beginOperation?: () => (() => void) | null; onChanged: (next: ReportAuthoringState) => void;
}) {
  const sources = state.sources.filter(source => source.role === 'tools_result_package');
  const [sourceId, setSourceId] = useState('');
  const [packet, setPacket] = useState<ReportToolsPackage | null>(null);
  const [entryId, setEntryId] = useState('');
  const [stepIndex, setStepIndex] = useState(-1);
  const [outcome, setOutcome] = useState<ToolsPackageImportRequest['outcome']>('pending');
  const [reason, setReason] = useState('');
  const [sampleIds, setSampleIds] = useState('');
  const [sourceConfirmed, setSourceConfirmed] = useState(false);
  const [checked, setChecked] = useState(false);
  const [preview, setPreview] = useState<ReportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);
  const epoch = useRef(0);
  const entry = packet?.entries.find(item => item.entry_id === entryId);
  const step = state.context.steps[stepIndex];
  const sourceMismatch = Boolean(packet?.project_hint && packet.project_hint.toUpperCase() !== state.context.dl_number.toUpperCase());

  useEffect(() => {
    setSourceId(previous => state.sources.some(item => item.source_id === previous && item.role === 'tools_result_package')
      ? previous : state.sources.filter(item => item.role === 'tools_result_package').at(-1)?.source_id || '');
  }, [projectId, state.sources]);
  useEffect(() => {
    let active = true;
    setPacket(null); setEntryId(''); setSourceConfirmed(false); setSampleIds(''); setError('');
    if (!sourceId) return;
    setLoading(true);
    // Retained source bytes are immutable; reading candidates does not reserve a write operation.
    void getReportToolsPackage(projectId, sourceId).then(next => { if (active) setPacket(next); })
      .catch(cause => { if (active) setError(cause instanceof Error ? cause.message : 'Unable to read this Tools package.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [projectId, sourceId, reload]);
  useEffect(() => {
    epoch.current += 1; setPreview(null); setChecked(false); setBusy(false);
    return () => { epoch.current += 1; };
  }, [projectId, state.revision]);
  useEffect(() => { setPreview(null); setChecked(false); }, [sourceId, entryId, stepIndex, outcome, reason, sampleIds, sourceConfirmed]);

  function request(): ToolsPackageImportRequest {
    if (!entry?.supported_for_report || !step || (entry.kind !== 'temperature' && entry.kind !== 'mechanical' && entry.kind !== 'mechanical_qualitative'))
      throw new Error('Choose a supported Tools result and this project’s confirmed Matrix step.');
    return { expected_revision: state.revision, source_id: sourceId, package_entry_id: entry.entry_id, kind: entry.kind,
      group_id: step.group_id, row_id: step.row_id, step_token: step.step_token, outcome, acceptance_reason: reason,
      ...(entry.kind === 'temperature' ? { sample_ids: sampleIds.split(/[,，;；\n]+/).map(value => value.trim()).filter(Boolean) } : {}),
      ...(sourceMismatch ? { source_project_confirmed: sourceConfirmed } : {}) };
  }
  async function evaluate(confirm = false) {
    if (disabled || busy || loading) return;
    const release = beginOperation ? beginOperation() : () => undefined;
    if (!release) return;
    const token = ++epoch.current;
    setBusy(true); setError('');
    try {
      if (confirm && preview && checked) {
        const next = await confirmReportResult(projectId, { ...request(), preview_sha256: preview.preview_sha256 });
        if (token === epoch.current) { onChanged(next); setPreview(null); }
      } else {
        const next = await previewReportResult(projectId, request());
        if (token === epoch.current) { setPreview(next); setChecked(false); }
      }
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to use this Tools result.'); }
    finally { release(); if (token === epoch.current) setBusy(false); }
  }
  if (!sources.length) return null;
  const locked = disabled || busy || loading;
  const mechanicalRows = preview?.data.rows || [];
  const hasPart = mechanicalRows.some(row => row.part !== undefined && row.part !== '');
  const hasHold = mechanicalRows.some(row => row.hold_seconds !== undefined);
  const hasSignedValue = mechanicalRows.some(row => row.raw_value !== undefined && String(row.raw_value) !== String(row.value));
  return <section className="report-tools-package" aria-label="Tools results for report">
    <h3>Use reviewed Tools results</h3>
    <p>Reuse the retained data, calculations and source evidence. Choose the report target and project decision; no column remapping is needed.</p>
    <fieldset disabled={locked}>
      <label>Tools results package<select value={sourceId} onChange={event => setSourceId(event.target.value)}>
        {sources.map(source => <option key={source.source_id} value={source.source_id}>{source.file_name}</option>)}
      </select></label>
      {packet && <>
        <label>Reviewed Tools result<select value={entryId} onChange={event => {
          setEntryId(event.target.value); setOutcome('pending'); setReason('');
          setSampleIds(packet.entries.find(item => item.entry_id === event.target.value)?.sample_ids?.join(', ') || '');
        }}><option value="">Choose result</option>{packet.entries.map(item =>
          <option key={item.entry_id} value={item.entry_id} disabled={!item.supported_for_report}>{item.label}</option>)}
        </select></label>
        {packet.entries.filter(item => !item.supported_for_report).map(item => <p key={item.entry_id}>{item.label}: {item.reason}</p>)}
        {entry && <p>Original sources: {entry.source_names.join(', ')}</p>}
        {sourceMismatch && <label className="report-tools-package-check"><input type="checkbox" checked={sourceConfirmed} onChange={event => setSourceConfirmed(event.target.checked)} />
          I confirm results identified as {packet.project_hint} are applicable to this project ({state.context.dl_number || 'no LTR'}).</label>}
        <label>Package result Group / Step<select value={stepIndex} onChange={event => setStepIndex(Number(event.target.value))}>
          <option value={-1}>Choose confirmed Matrix step</option>{state.context.steps.map((item, index) =>
            <option key={index} value={index}>Group {item.group_label} / {item.step_token} / {item.test_item}</option>)}
        </select></label>
        {entry?.kind === 'temperature' && <label>Temperature sample identities in channel-group order
          <input value={sampleIds} onChange={event => setSampleIds(event.target.value)} placeholder="Confirmed sample IDs, comma separated" />
          <small>{entry.sample_count ? `${entry.sample_count} sample groups. ` : ''}Leave unknown identities empty; group numbers are not specimen SNs.</small>
        </label>}
        <label>Package report outcome<select value={outcome} onChange={event => setOutcome(event.target.value as typeof outcome)}>
          <option value="pending">Pending decision</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="not_applicable">Not applicable</option>
        </select></label>
        <label className="report-tools-package-wide">Package acceptance evidence / reason<textarea value={reason} onChange={event => setReason(event.target.value)} /></label>
        <button type="button" disabled={!entry?.supported_for_report || !step || (sourceMismatch && !sourceConfirmed)} onClick={() => void evaluate()}>Preview Tools result</button>
      </>}
    </fieldset>
    {loading && <p role="status">Reading reviewed Tools results…</p>}
    {error && <div role="alert"><p>{error}</p>{!packet && <button type="button" disabled={disabled || loading} onClick={() => setReload(value => value + 1)}>Retry package inspection</button>}</div>}
    {preview && <div className="report-tools-package-preview">
      <p>Group {preview.target.group_label} / Step {preview.target.step_token} — {preview.data.quantity}; outcome: {preview.outcome}</p>
      {preview.data.force_field && <p>Source force field: {preview.data.force_field}.</p>}
      {preview.data.withdraw_magnitude && <p>Magnitude selected in Tools; original signed values are retained.</p>}
      {preview.kind === 'mechanical_qualitative' ? <>
        <p>{preview.data.raw_curves?.length || 0} source curves retained. These are not one curve per observation; source Pass labels do not approve this project's report outcome.</p>
        {preview.data.tables?.map((table, index) => <table key={index}>
          <caption>{table.title}</caption><thead><tr><th>{table.row_heading || 'Sample'}</th>
            {table.columns.map((column, i) => <th key={i}>{table.column_heading} {column}</th>)}</tr></thead>
          <tbody>{table.results.map((row, i) => <tr key={i}><th>{table.samples[i]}</th>{row.map((value, j) => <td key={j}>{value || '—'}</td>)}</tr>)}</tbody>
        </table>)}
      </> : preview.data.analysis ? <table><thead><tr><th>Source row</th><th>Current / A</th><th>Max rise / °C</th><th>Avg of Max / °C</th></tr></thead><tbody>
        {preview.data.analysis.points.map((point, index) => <tr key={index}><td>{point.source_row ?? 'Fit origin — not measured'}</td><td>{point.current}</td><td>{point.maximum}</td><td>{point.average}</td></tr>)}
      </tbody></table> : <table><thead><tr><th>SN</th><th>Instrument ID</th><th>Color</th>{hasPart && <th>Part</th>}<th>Measured value</th>{hasSignedValue && <th>Original signed value</th>}{hasHold && <th>Hold / s</th>}</tr></thead><tbody>
        {mechanicalRows.map((row, index) => <tr key={index}><td>{String(row.sample_id)}</td><td>{String(row.record_id ?? '')}</td><td>{String(row.color ?? '')}</td>{hasPart && <td>{String(row.part ?? '')}</td>}<td>{String(row.value)} {preview.data.unit}</td>{hasSignedValue && <td>{String(row.raw_value ?? '')} {preview.data.unit}</td>}{hasHold && <td>{String(row.hold_seconds ?? '')}</td>}</tr>)}
      </tbody></table>}
      <label className="report-tools-package-check"><input type="checkbox" disabled={locked} checked={checked} onChange={event => setChecked(event.target.checked)} />I verified this Tools result and its report Group / Step</label>
      <button type="button" disabled={locked || !checked} onClick={() => void evaluate(true)}>Confirm Tools result for report</button>
    </div>}
  </section>;
}
