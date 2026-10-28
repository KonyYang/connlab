import { useState, type ReactElement } from 'react';
import { generateMechanicalSummary, previewMechanicalSource, type MechanicalPreview, type MechanicalRow } from '../../api/mechanicalSummary';

type Entry = { file: File; kind: string; group: string; sheet: number; preview?: MechanicalPreview;
  rows: MechanicalRow[]; information: Record<string, string>; confirmed: boolean };
const fields = ['LTR', 'Test Date', 'Tested By', 'Amb Temp. and Rel. Hum.', 'Test Equipment ID', 'Test Condition', 'Item/Process', 'Remark'];
const initial = (file: File): Entry => ({ file, kind: '', group: '', sheet: 1, rows: [], information: {}, confirmed: false });
const ready = (entry: Entry) => Boolean(entry.preview && entry.kind && entry.rows.length && entry.rows.every(row =>
  row.curve.trim() && row.sample.trim() && (entry.kind !== 'qualitative' || ['Pass', 'Fail', 'N/A'].includes(row.result || ''))));

export function MechanicalSummaryTool(): ReactElement {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [downloaded, setDownloaded] = useState('');
  function update(index: number, patch: Partial<Entry>) {
    setEntries(old => old.map((entry, i) => i === index ? { ...entry, ...patch, confirmed: false } : entry));
    setDownloaded('');
  }
  function updateRow(index: number, rowIndex: number, patch: Partial<MechanicalRow>) {
    setEntries(old => old.map((entry, i) => i === index ? { ...entry, confirmed: false,
      rows: entry.rows.map((row, j) => j === rowIndex ? { ...row, ...patch } : row) } : entry));
    setDownloaded('');
  }
  async function preview(index: number) {
    const entry = entries[index];
    setBusy(true); setError('');
    try {
      const result = await previewMechanicalSource(entry.file, entry.kind);
      setEntries(old => old.map((item, i) => i === index && item.file === entry.file && item.kind === entry.kind
        ? { ...item, preview: result, rows: result.rows ?? [], confirmed: false } : item));
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not read this file.'); }
    finally { setBusy(false); }
  }
  async function generate() {
    setBusy(true); setError('');
    try {
      const response = await generateMechanicalSummary(entries.map(entry => entry.file), entries.map(entry => ({
        kind: entry.kind, group: entry.group, sheet: entry.sheet, rows: entry.rows,
        information: entry.information, confirmed: entry.confirmed, sha256: entry.preview?.sha256,
      })));
      const url = URL.createObjectURL(response.blob);
      const anchor = document.createElement('a');
      anchor.href = url; anchor.download = response.fileName || 'Mechanical_Summary.xlsx';
      document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
      setDownloaded(anchor.download);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not generate the summary.'); }
    finally { setBusy(false); }
  }
  return <article className="tools-card mechanical-summary-tool" aria-label="Mechanical Summary">
    <div className="tools-card-heading"><h3>Mechanical Summary</h3></div>
    <p>Select instrument files, review the data and download an editable workbook. Original files stay unchanged.</p>
    <label className="tools-file-picker">Select mechanical test files
      <input type="file" multiple accept=".pdf,.xls,.xlsx" disabled={busy}
        onChange={event => { setEntries(Array.from(event.target.files || []).map(initial)); setError(''); setDownloaded(''); }} />
    </label>
    {entries.map((entry, index) => <fieldset className="mechanical-source" key={`${index}-${entry.file.name}`} disabled={busy}>
      <legend>{entry.file.name}</legend>
      <label>Test type for {entry.file.name}
        <select aria-label={`Test type for ${entry.file.name}`} value={entry.kind}
          onChange={event => update(index, { kind: event.target.value, preview: undefined, rows: [] })}>
          <option value="">Select test type</option>
          {/\.pdf$/i.test(entry.file.name) ? <>
            <option value="mating">Mating / withdraw</option><option value="retention">Peak retention</option>
            <option value="hold">Hold force — FEnd section</option><option value="hold_end1">Hold force — FEnd section 1</option></> : <option value="qualitative">Qualitative test</option>}
        </select>
      </label>
      <button type="button" disabled={!entry.kind} onClick={() => void preview(index)}>Preview {entry.file.name}</button>
      {entry.preview && <>
        <label>Group <input value={entry.group} onChange={event => update(index, { group: event.target.value })} /></label>
        {entry.preview.source_text && <details><summary>View original PDF text</summary>
          <pre className="mechanical-source-values">{entry.preview.source_text}</pre></details>}
        {entry.preview.sheets && <><label>Source sheet <select value={entry.sheet}
          onChange={event => update(index, { sheet: Number(event.target.value) })}>
          {entry.preview.sheets.map((sheet, i) => <option key={i} value={i + 1}>{sheet.name}</option>)}
        </select></label><details><summary>View original values</summary><div className="mechanical-source-values"><table><tbody>
          {entry.preview.sheets[entry.sheet - 1]?.rows.map((row, i) => <tr key={i}><th>{i + 1}</th>{row.map((value, j) => <td key={j}>{String(value ?? '')}</td>)}</tr>)}
        </tbody></table></div></details></>}
        {entry.kind === 'qualitative' && <button type="button" onClick={() => update(index, { rows: [...entry.rows, { curve: '', sample: '', result: '' }] })}>Add reviewed result</button>}
        {entry.rows.map((row, rowIndex) => <div className="mechanical-result-row" key={rowIndex}>
          <label>Curve <input aria-label={`Curve ${rowIndex + 1} for ${entry.file.name}`} value={row.curve} readOnly={entry.kind !== 'qualitative'}
            onChange={event => updateRow(index, rowIndex, { curve: event.target.value })} /></label>
          <label>Sample <input aria-label={`Sample for curve ${row.curve}`} value={row.sample}
            onChange={event => updateRow(index, rowIndex, { sample: event.target.value })} /></label>
          {entry.kind === 'qualitative' ? <label>Result <select aria-label={`Result for curve ${row.curve}`} value={row.result || ''}
            onChange={event => updateRow(index, rowIndex, { result: event.target.value })}>
            <option value="">Select result</option><option>Pass</option><option>Fail</option><option>N/A</option>
          </select></label> : <span>{entry.kind === 'mating' ? `Mating ${row.mating} N; Withdraw ${row.withdraw} N` : `${row.value} N`}</span>}
          {entry.kind === 'qualitative' && <button type="button" onClick={() => update(index, { rows: entry.rows.filter((_, i) => i !== rowIndex) })}>Remove result</button>}
        </div>)}
        <details><summary>Test information</summary>{fields.map(field => <label key={field}>{field}
          <input value={entry.information[field] || ''} onChange={event => update(index, { information: { ...entry.information, [field]: event.target.value } })} />
        </label>)}</details>
        <label><input type="checkbox" aria-label={`Confirm ${entry.file.name}`} checked={entry.confirmed} disabled={!ready(entry)}
          onChange={event => setEntries(old => old.map((item, i) => i === index ? { ...item, confirmed: event.target.checked } : item))} />
          I have reviewed the source, test type, group and sample mapping.</label>
      </>}
    </fieldset>)}
    {error && <p className="tools-feedback tools-feedback-error" role="alert">{error}</p>}
    <button type="button" className="primary-action tools-picker-action" disabled={busy || !entries.length || entries.some(entry => !entry.confirmed || !ready(entry))}
      onClick={() => void generate()}>Generate Summary</button>
    {downloaded && <p role="status">Downloaded: {downloaded}</p>}
  </article>;
}
