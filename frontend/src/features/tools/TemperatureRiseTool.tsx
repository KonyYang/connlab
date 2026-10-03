import { useEffect, useRef, useState, type ReactElement } from "react";
import { analyzeTemperatureRise, exportTemperatureRise, previewTemperatureRise, suggestTemperatureRise,
  type TemperatureAnalysis, type TemperatureBlock, type TemperatureCurve, type TemperatureMapping, type TemperatureOptions } from "../../api/client";

const INITIAL = { current_mode: "amperes" as const, current_gain: 1, zero_intercept: true, include_origin: true,
  target_rise: 30, max_temperature: 125, derating_factor: .8 };

export function TemperatureRiseTool(): ReactElement {
  const [file, setFile] = useState<File | null>(null);
  const [blocks, setBlocks] = useState<TemperatureBlock[]>([]);
  const [blockId, setBlockId] = useState("");
  const [mapping, setMapping] = useState<TemperatureMapping>({ ambient: 0, current: 1, channels: [] });
  const [selected, setSelected] = useState<number[]>([]);
  const [settings, setSettings] = useState<Omit<TemperatureOptions, "mapping" | "selected_rows" | "block_id" | "ambient_temperatures">>(INITIAL);
  const [ambientText, setAmbientText] = useState("20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125");
  const [showAll, setShowAll] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TemperatureAnalysis | null>(null);
  const [downloadName, setDownloadName] = useState<string | null>(null);
  const [suggestionsStale, setSuggestionsStale] = useState(false);
  const token = useRef(0);
  const running = useRef(false);
  useEffect(() => () => { token.current += 1; }, []);
  const block = blocks.find((item) => item.id === blockId);
  const traceColumns = block?.headers.flatMap((header, column) => /scan|time|扫描|掃描|时间|時間/i.test(header) ? [column] : []) ?? [];

  function invalidate(): void { setResult(null); setError(null); setDownloadName(null); }
  function chooseBlock(item: TemperatureBlock): void {
    setBlockId(item.id); setMapping(item.suggested_mapping); setSelected(item.candidate_rows);
    setSettings((value) => ({ ...value, current_mode: "amperes", current_gain: 1 }));
    setSuggestionsStale(false); setShowAll(false); invalidate();
  }
  function options(): TemperatureOptions {
    const text = ambientText.trim();
    const temperatures = text.split(/[,;\s]+/).filter(Boolean).map(Number);
    if (!text || temperatures.some((value) => !Number.isFinite(value))) throw new Error("Enter ambient temperatures separated by commas.");
    return { ...settings, block_id: blockId, mapping, selected_rows: selected, ambient_temperatures: temperatures };
  }
  async function run(action: "preview" | "suggest" | "analyze" | "export"): Promise<void> {
    if (running.current) return;
    if (!file) { setError("Select a measurement file first."); return; }
    const current = ++token.current;
    running.current = true; setBusy(true); setError(null); setDownloadName(null);
    try {
      if (action === "preview") {
        const response = await previewTemperatureRise(file);
        if (token.current !== current) return;
        setBlocks(response.blocks); chooseBlock(response.blocks[0]);
      } else if (action === "suggest") {
        const response = await suggestTemperatureRise(file, blockId, mapping.current);
        if (token.current !== current) return;
        setBlocks((value) => value.map((item) => item.id === blockId ? { ...item, candidate_rows: response.candidate_rows } : item));
        setSelected(response.candidate_rows); setSuggestionsStale(false); invalidate();
      } else if (action === "analyze") {
        setResult(null);
        const response = await analyzeTemperatureRise(file, options());
        if (token.current === current) setResult(response);
      } else {
        const response = await exportTemperatureRise(file, options());
        if (token.current !== current) return;
        const name = response.fileName ?? "TemperatureRise.xlsx";
        const url = URL.createObjectURL(response.blob);
        const anchor = document.createElement("a");
        try { anchor.href = url; anchor.download = name; document.body.append(anchor); anchor.click(); }
        finally { anchor.remove(); URL.revokeObjectURL(url); }
        setDownloadName(name);
      }
    } catch (caught) {
      if (token.current === current) setError(caught instanceof Error ? caught.message : "Check the measurement file and settings, then retry.");
    } finally {
      if (token.current === current) { running.current = false; setBusy(false); }
    }
  }
  function editSetting<K extends keyof typeof settings>(key: K, value: typeof settings[K]): void {
    setSettings({ ...settings, [key]: value }); invalidate();
  }

  return <article className="tools-card temperature-rise-tool">
    <div className="tools-card-heading"><h3>Temperature Rise &amp; Derating</h3></div>
    <label className="tools-file-picker"><span>Measurement file</span>
      <input type="file" accept=".csv,.xls,.xlsx,.xlsm" disabled={busy} onChange={(event) => {
        token.current += 1; setFile(event.target.files?.[0] ?? null); setBlocks([]); setBlockId("");
        setSettings((value) => ({ ...value, current_mode: "amperes", current_gain: 1 })); invalidate();
      }} /></label>
    <button type="button" className="secondary-action" disabled={busy || !file} onClick={() => void run("preview")}>{busy ? "Working..." : "Preview Measurement Data"}</button>
    {block && <fieldset className="temperature-controls" disabled={busy}>
      <legend>Confirm channels and stage points</legend>
      <label>Data block <select value={blockId} onChange={(event) => chooseBlock(blocks.find((item) => item.id === event.target.value)!)}>
        {blocks.map((item) => <option key={item.id} value={item.id}>{item.sheet} · header row {item.header_row} · {item.row_count} records</option>)}
      </select></label>
      <div className="temperature-fields">
        <ColumnSelect label="Ambient channel" value={mapping.ambient} block={block} onChange={(ambient) => { setMapping({ ...mapping, ambient, channels: mapping.channels.filter((channel) => channel.column !== ambient) }); invalidate(); }} />
        <ColumnSelect label="Current channel" value={mapping.current} block={block} onChange={(current) => { setMapping({ ...mapping, current, channels: mapping.channels.filter((channel) => channel.column !== current) }); setSuggestionsStale(true); invalidate(); }} />
        <label>Current values <select value={settings.current_mode} onChange={(event) => editSetting("current_mode", event.target.value as "amperes" | "voltage")}>
          <option value="amperes">Already converted to A</option><option value="voltage">Raw voltage × gain</option>
        </select></label>
        <label>Voltage-to-current gain <input type="number" step="any" disabled={settings.current_mode === "amperes"} value={settings.current_gain} onChange={(event) => editSetting("current_gain", Number(event.target.value))} /></label>
      </div>
      <p className="tools-card-hint">Current source: {block.headers[mapping.current]}. Confirm units: instrument-scaled values must not be multiplied again.</p>
      {block.current_metadata.length > 0 && <details><summary>Instrument current configuration</summary><p>{block.current_metadata.filter((value) => value !== null && value !== "").join(" · ")}</p></details>}
      <div className="temperature-table-scroll"><table className="temperature-table"><thead><tr><th>Source channel</th><th>Include</th><th>Sample</th><th>Point</th></tr></thead><tbody>
        {block.headers.map((header, column) => {
          if (column === mapping.ambient || column === mapping.current || traceColumns.includes(column)) return null;
          const channel = mapping.channels.find((item) => item.column === column);
          return <tr key={column}><td>{header}</td><td><input type="checkbox" aria-label={`Include ${header}`} checked={Boolean(channel)} onChange={(event) => {
            setMapping({ ...mapping, channels: event.target.checked ? [...mapping.channels, { column, sample: `Sample ${column + 1}`, point: header }] : mapping.channels.filter((item) => item.column !== column) }); invalidate();
          }} /></td><td>{channel && <input aria-label={`Sample for ${header}`} value={channel.sample} onChange={(event) => { setMapping({ ...mapping, channels: mapping.channels.map((item) => item.column === column ? { ...item, sample: event.target.value } : item) }); invalidate(); }} />}</td>
            <td>{channel && <input aria-label={`Point for ${header}`} value={channel.point} onChange={(event) => { setMapping({ ...mapping, channels: mapping.channels.map((item) => item.column === column ? { ...item, point: event.target.value } : item) }); invalidate(); }} />}</td></tr>;
        })}
      </tbody></table></div>
      <p className="tools-card-hint">Candidate stage ends use a current range ≤ 1%. This is a point suggestion, not a thermal stability assessment. Confirm or exclude each point.</p>
      <div className="temperature-actions"><button type="button" className="secondary-action" onClick={() => void run("suggest")}>Refresh Stage Suggestions</button>
        <label><input type="checkbox" checked={showAll} onChange={(event) => setShowAll(event.target.checked)} /> Show all records to add points</label></div>
      {suggestionsStale && <p className="tools-feedback">Current channel changed. Refresh suggestions or select records manually.</p>}
      <div className="temperature-table-scroll temperature-records"><table className="temperature-table"><thead><tr><th>Use</th><th>Source row</th><th>Scan / Time</th><th>Current input</th><th>Ambient</th></tr></thead><tbody>
        {block.records.filter((record) => showAll || block.candidate_rows.includes(record.row) || selected.includes(record.row)).map((record) => <tr key={record.row}>
          <td><input type="checkbox" aria-label={`Use row ${record.row}`} checked={selected.includes(record.row)} onChange={(event) => {
            setSelected(event.target.checked ? [...selected, record.row] : selected.filter((row) => row !== record.row)); invalidate();
          }} /></td><td>{record.row}</td><td>{traceColumns.map((column) => record.values[column]).join(" · ") || "—"}</td><td>{record.values[mapping.current]}</td><td>{record.values[mapping.ambient]}</td>
        </tr>)}
      </tbody></table></div>
      <p className="tools-card-hint">{selected.length} confirmed rows · {new Set(mapping.channels.map((channel) => channel.sample)).size} samples</p>
      <div className="temperature-fields">
        <label><input type="checkbox" checked={settings.zero_intercept} onChange={(event) => editSetting("zero_intercept", event.target.checked)} /> Force zero intercept</label>
        <label><input type="checkbox" checked={settings.include_origin} onChange={(event) => editSetting("include_origin", event.target.checked)} /> Display non-measured origin (0 A, 0 °C)</label>
        <label>Target rise (°C) <input type="number" step="any" value={settings.target_rise} onChange={(event) => editSetting("target_rise", Number(event.target.value))} /></label>
        <label>Maximum temperature (°C) <input type="number" step="any" value={settings.max_temperature} onChange={(event) => editSetting("max_temperature", Number(event.target.value))} /></label>
        <label>Derating factor <input type="number" min="0" max="1" step=".01" value={settings.derating_factor} onChange={(event) => editSetting("derating_factor", Number(event.target.value))} /></label>
        <label>Ambient temperatures (°C, comma separated) <input value={ambientText} onChange={(event) => { setAmbientText(event.target.value); invalidate(); }} /></label>
      </div>
      <p className="tools-card-hint">Origin is display data, separate from the intercept constraint. Centered R² uses measured points and the origin when displayed; fitting uses measured points at full precision.</p>
      <button type="button" className="primary-action" disabled={!selected.length || !mapping.channels.length} onClick={() => void run("analyze")}>Calculate Preview</button>
    </fieldset>}
    {error && <p className="tools-feedback tools-feedback-error" role="alert">{error}</p>}
    {result && <section className="temperature-results" aria-label="Calculation preview">
      <p>Max-curve current at {settings.target_rise} °C: <strong>{result.target_current.toFixed(1)} A</strong></p>
      <p className="tools-card-hint">Single Max = largest rise in each sample on the selected row. Avg of Max = mean of those sample maxima.</p>
      <div className="temperature-table-scroll"><table className="temperature-table"><thead><tr><th>Source row</th><th>Applied current (A)</th><th>Max (°C)</th><th>Avg of Max (°C)</th></tr></thead><tbody>
        {result.points.map((point) => <tr key={point.row}><td>{point.row}</td><td>{point.current.toFixed(1)}</td><td>{point.maximum.toFixed(1)}</td><td>{point.average_of_max.toFixed(1)}</td></tr>)}
      </tbody></table></div>
      <p>Max: {equation(result.max_curve)} · centered R² {result.max_curve.r_squared.toFixed(6)}</p>
      <p>Avg of Max: {equation(result.avg_curve)} · centered R² {result.avg_curve.r_squared.toFixed(6)}</p>
      {result.extrapolated && <p className="tools-feedback">Some calculated currents exceed the measured range. Review extrapolated values before use.</p>}
      <div className="temperature-table-scroll"><table className="temperature-table"><thead><tr><th>Ambient (°C)</th><th>Allowable rise (°C)</th><th>Basic current (A)</th><th>Derated current (A)</th></tr></thead><tbody>
        {result.derating.map((point) => <tr key={point.ambient}><td>{point.ambient}</td><td>{point.allowable_rise.toFixed(1)}</td><td>{point.basic_current.toFixed(1)}</td><td>{point.derated_current.toFixed(1)}</td></tr>)}
      </tbody></table></div>
      <button type="button" className="primary-action" disabled={busy} onClick={() => void run("export")}>Download Temperature Rise Workbook</button>
    </section>}
    {downloadName && <p className="tools-feedback tools-feedback-success" role="status" aria-label="Temperature workbook downloaded">{downloadName}</p>}
  </article>;
}

function ColumnSelect({ label, value, block, onChange }: { label: string; value: number; block: TemperatureBlock; onChange: (value: number) => void }): ReactElement {
  return <label>{label}<select value={value} onChange={(event) => onChange(Number(event.target.value))}>
    {block.headers.map((header, column) => <option key={column} value={column}>{column + 1}: {header}</option>)}
  </select></label>;
}

function equation(curve: TemperatureCurve): string {
  return `ΔT = ${curve.a.toFixed(6)} I² ${curve.b < 0 ? "−" : "+"} ${Math.abs(curve.b).toFixed(6)} I ${curve.c < 0 ? "−" : "+"} ${Math.abs(curve.c).toFixed(6)}`;
}
