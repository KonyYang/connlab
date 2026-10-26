import { useEffect, useRef, useState } from "react";
import { getReportSourceTable, previewReportResult, confirmReportResult,
  type ReportAuthoringState, type ReportTable, type ReportResult, type ResultImportRequest } from "../../api/reportAuthoring";

export function ReportResultsImport({ projectId, state, disabled, onChanged, beginOperation }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
}) {
  const [sourceId, setSourceId] = useState("");
  const [table, setTable] = useState<ReportTable | null>(null);
  const [preview, setPreview] = useState<ReportResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [checked, setChecked] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [start, setStart] = useState(2); const [end, setEnd] = useState(2);
  const [headerRow, setHeaderRow] = useState(1);
  const [columns, setColumns] = useState<Record<string, number>>({});
  const [unit, setUnit] = useState<"mV" | "V">("mV");
  const [quantity, setQuantity] = useState<"absolute" | "delta">("absolute");
  const [forceType, setForceType] = useState<"mating" | "unmating" | "retention">("retention");
  const [forceKind, setForceKind] = useState<"peak" | "hold">("peak");
  const [temperatureColumns, setTemperatureColumns] = useState<number[]>([]);
  const [channelsPerSample, setChannelsPerSample] = useState(1);
  const [sampleCount, setSampleCount] = useState(1);
  const [sampleNames, setSampleNames] = useState('');
  const [zero, setZero] = useState(true);
  const [warnings, setWarnings] = useState(false);
  const [outcome, setOutcome] = useState<ResultImportRequest["outcome"]>("pending");
  const [reason, setReason] = useState("");
  const sequence = useRef(0);
  const sources = state.sources.filter(source => ["temperature", "cr", "mechanical"].includes(source.role));
  const source = sources.find(item => item.source_id === sourceId);
  const step = state.context.steps[stepIndex];
  const locked = busy || disabled;
  useEffect(() => { sequence.current += 1; setPreview(null); setChecked(false); setBusy(false); setError("");
    return () => { sequence.current += 1; }; }, [projectId, state.revision]);
  useEffect(() => { setPreview(null); setChecked(false); }, [sourceId, stepIndex, start, end, headerRow, columns, unit, quantity,
    forceType, forceKind, temperatureColumns, channelsPerSample, sampleCount, sampleNames, zero, warnings, outcome, reason]);

  async function inspect(sheet = "") {
    if (!source || disabled || busy) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++sequence.current; setBusy(true); setError(""); setPreview(null); setTable(null);
    try {
      const result = await getReportSourceTable(projectId, source.source_id, sheet);
      if (token === sequence.current) { setTable(result); setHeaderRow(1); setStart(2); setEnd(result.rows.length); setColumns({}); setTemperatureColumns([]); }
    } catch (cause) { if (token === sequence.current) setError(cause instanceof Error ? cause.message : "The workbook could not be read."); }
    finally { release(); if (token === sequence.current) setBusy(false); }
  }

  function request(): ResultImportRequest {
    if (!source || !table || !step) throw new Error("Select a source table and current Matrix Group / Step.");
    const kind = source.role as ResultImportRequest["kind"];
    return { expected_revision: state.revision, source_id: source.source_id, kind, sheet_name: table.sheet_name,
      start_row: start, end_row: end, columns: kind === 'temperature' ? {} : Object.fromEntries(Object.entries(columns).filter(([, value]) => value > 0)),
      unit: kind === "mechanical" ? "N" : unit, quantity, test_type: forceType, measurement_kind: forceKind,
      group_id: step.group_id, row_id: step.row_id, step_token: step.step_token,
      outcome, acceptance_reason: reason, zero_intercept: zero, acknowledge_warnings: warnings,
      sample_ids: kind === 'temperature' ? sampleNames.split(',').map(value => value.trim()).filter(Boolean) : [],
      ...(kind === "temperature" ? { temperature_selection: { header_row: headerRow, start_row: start, end_row: end,
        ambient_column: columns.ambient || 0, current_column: columns.current || 0, temperature_columns: temperatureColumns,
        thermocouples_per_sample: channelsPerSample, sample_count: sampleCount } } : {}) };
  }

  async function evaluate(confirm = false) {
    if (disabled || busy) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++sequence.current; setBusy(true); setError("");
    try {
      if (confirm && preview) {
        const result = await confirmReportResult(projectId, { ...request(), preview_sha256: preview.preview_sha256 });
        if (token === sequence.current) { onChanged(result); setPreview(null); }
      } else {
        const result = await previewReportResult(projectId, request());
        if (token === sequence.current) { setPreview(result); setChecked(false); }
      }
    } catch (cause) { if (token === sequence.current) setError(cause instanceof Error ? cause.message : "Result import failed."); }
    finally { release(); if (token === sequence.current) setBusy(false); }
  }

  const columnHeaders = table ? Array.from({ length: Math.max(0, ...table.rows.map(row => row.length)) }, (_, index) =>
    String(table.rows[headerRow - 1]?.[index] ?? `Column ${index + 1}`)) : [];
  function column(name: string, label: string) {
    return <label key={name}>{label}<select value={columns[name] || 0} onChange={event => setColumns({ ...columns, [name]: Number(event.target.value) })}>
      <option value={0}>Choose column</option>{columnHeaders.map((header, index) => <option key={index} value={index + 1}>{index + 1}: {header}</option>)}
    </select></label>;
  }
  return <section aria-label="Import report measurements">
    <h3>Temperature, CR and mechanical results</h3>
    {!sources.length ? <p>Retain a measurement workbook above to map and review its results.</p> : <fieldset disabled={locked}>
      <legend>Read retained measurements</legend>
      <label>Measurement source <select value={sourceId} onChange={event => { sequence.current += 1; setSourceId(event.target.value); setTable(null); setPreview(null); }}>
        <option value="">Choose source</option>{sources.map(item => <option key={item.source_id} value={item.source_id}>{item.file_name}</option>)}
      </select></label>
      <button type="button" disabled={!source} onClick={() => void inspect()}>Inspect measurement workbook</button>
      {table && <>
        <label>Sheet <select value={table.sheet_name} onChange={event => void inspect(event.target.value)}>{table.sheet_names.map(name => <option key={name}>{name}</option>)}</select></label>
        <div style={{ overflowX: "auto", maxHeight: "16rem" }}><table><caption>Source preview (first 20 rows)</caption><tbody>
          {table.rows.slice(0, 20).map((row, index) => <tr key={index}><th>{index + 1}</th>{row.map((value, col) => <td key={col}>{String(value ?? "")}</td>)}</tr>)}
        </tbody></table></div>
        <label>First measurement row <input type="number" min={2} max={table.rows.length} value={start} onChange={event => setStart(Number(event.target.value))} /></label>
        <label>Column header row <input type="number" min={1} max={table.rows.length} value={headerRow} onChange={event => setHeaderRow(Number(event.target.value))} /></label>
        <label>Last measurement row <input type="number" min={start} max={table.rows.length} value={end} onChange={event => setEnd(Number(event.target.value))} /></label>
        <label>Result Group / Step <select value={stepIndex} onChange={event => setStepIndex(Number(event.target.value))}>
          <option value={-1}>Choose confirmed Matrix step</option>{state.context.steps.map((item, index) => <option key={index} value={index}>Group {item.group_label} / {item.step_token} / {item.test_item}</option>)}
        </select></label>
        {source?.role === "temperature" ? <>
          {column("ambient", "Ambient temperature column (°C)")}{column("current", "Measured current column (A)")}
          <label>Temperature columns (°C)<select multiple value={temperatureColumns.map(String)} onChange={event => setTemperatureColumns(Array.from(event.target.selectedOptions, item => Number(item.value)))}>
            {columnHeaders.map((header, index) => <option key={index} value={index + 1}>{index + 1}: {header}</option>)}
          </select></label>
          <label>Thermocouples per sample <input type="number" min={1} value={channelsPerSample} onChange={event => setChannelsPerSample(Number(event.target.value))} /></label>
          <label>Sample count <input type="number" min={1} value={sampleCount} onChange={event => setSampleCount(Number(event.target.value))} /></label>
          <label>Sample identities in channel-group order (comma separated)<input value={sampleNames} onChange={event => setSampleNames(event.target.value)} /></label>
          <p>If identities are unconfirmed, the preview uses Sample group numbers, not invented sample SNs.</p>
          <label><input type="checkbox" checked={zero} onChange={event => setZero(event.target.checked)} />Zero-intercept fit (origin is not measured data)</label>
          <label><input type="checkbox" checked={warnings} onChange={event => setWarnings(event.target.checked)} />I reviewed flagged measurement warnings</label>
        </> : <>
          {column("sample", "Sample SN column")}{column("record_id", "Instrument record ID column (optional)")}{column("color", "Color column (optional)")}
          {source?.role === "cr" ? <>
            {column("voltage", "Voltage drop column")}{column("current", "Measured current column (A)")}
            <label>Voltage unit <select value={unit} onChange={event => setUnit(event.target.value as "mV" | "V")}><option>mV</option><option>V</option></select></label>
            <label>Resistance meaning <select value={quantity} onChange={event => setQuantity(event.target.value as "absolute" | "delta")}><option value="absolute">Absolute resistance</option><option value="delta">Change from initial resistance</option></select></label>
            {quantity === "delta" && column("initial_mohm", "Initial resistance column (mΩ)")}
          </> : <>
            {column("value", "Force column (N)")}
            <label>Force test <select value={forceType} onChange={event => setForceType(event.target.value as typeof forceType)}><option value="mating">Mating</option><option value="unmating">Unmating</option><option value="retention">Retention force</option></select></label>
            <label>Measured force <select value={forceKind} onChange={event => setForceKind(event.target.value as typeof forceKind)}><option value="peak">Peak force</option><option value="hold">Held force</option></select></label>
            {forceKind === "hold" && column("hold_seconds", "Hold duration column (seconds)")}
          </>}
        </>}
        <label>Project outcome <select value={outcome} onChange={event => setOutcome(event.target.value as ResultImportRequest["outcome"])}>
          <option value="pending">Pending decision</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="not_applicable">Not applicable</option>
        </select></label>
        <label>Acceptance evidence / reason <textarea value={reason} onChange={event => setReason(event.target.value)} /></label>
        <button type="button" disabled={!step} onClick={() => void evaluate()}>Preview mapped results</button>
      </>}
    </fieldset>}
    {error && <p role="alert">{error}</p>}
    {preview && <div>
      <p>Group {preview.target.group_label} / Step {preview.target.step_token} — {preview.data.quantity}; outcome: {preview.outcome}</p>
      {preview.data.analysis ? <table><thead><tr><th>Source row</th><th>Current / A</th><th>Max rise / °C</th><th>Avg of Max / °C</th></tr></thead><tbody>
        {preview.data.analysis.points.map((point, index) => <tr key={index}><td>{point.source_row ?? "Fit origin — not measured"}</td><td>{point.current}</td><td>{point.maximum}</td><td>{point.average}</td></tr>)}
      </tbody></table> : <table><thead><tr><th>SN</th><th>Instrument ID</th><th>Color</th><th>Measured value</th><th>Current / hold duration</th></tr></thead><tbody>
        {preview.data.rows?.map((row, index) => <tr key={index}><td>{String(row.sample_id)}</td><td>{String(row.record_id)}</td><td>{String(row.color)}</td>
          <td>{String(row.delta_mohm ?? row.resistance_mohm ?? row.value)} {preview.data.unit}</td><td>{String(row.current_a ?? row.hold_seconds ?? "—")}</td></tr>)}
      </tbody></table>}
      <label><input type="checkbox" disabled={locked} checked={checked} onChange={event => setChecked(event.target.checked)} />I verified the source columns, samples, units and Matrix target</label>
      <button type="button" disabled={locked || !checked} onClick={() => void evaluate(true)}>Confirm result mapping</button>
    </div>}
    {(state.results || []).map(item => <p key={item.result_id}>Confirmed {item.kind} data: Group {item.target.group_label} / {item.target.step_token} — {item.data.quantity}; outcome {item.outcome}</p>)}
  </section>;
}
