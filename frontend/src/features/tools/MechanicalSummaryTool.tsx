import { useEffect, useRef, useState, type ReactElement } from 'react';
import { generateMechanicalFolder, previewMechanicalFolder, type FolderAnalysis, type FolderSection, type ReportTable } from '../../api/mechanicalSummary';
import { informationFields, qualitative, reviewFor, resizeTable, savedReview, saveReview, sectionReady, tableReady } from './mechanicalSummaryReview';
import { ToolsFeedback } from './ToolsFeedback';

const labels = (value: string) => value.split(/[,，;；\n]+/).map(v => v.trim()).filter(Boolean);
function ReportTableEditor({ table, change, remove }: { table: ReportTable; change: (t: ReportTable) => void; remove: () => void }) {
  return <fieldset className="mechanical-source">
    <legend>{table.title || 'Report table'}</legend>
    <label>Table title <input value={table.title} onChange={e => change({ ...table, title: e.target.value })} /></label>
    <label>Row part / colour <input value={table.row_heading} onChange={e => change({ ...table, row_heading: e.target.value })} /></label>
    <label>Column part / colour <input value={table.column_heading} onChange={e => change({ ...table, column_heading: e.target.value })} /></label>
    <label>Sample rows (comma-separated) <input defaultValue={table.samples.join(', ')}
      onBlur={e => change(resizeTable(table, labels(e.target.value), table.columns))} /></label>
    <label>Report columns (comma-separated) <input defaultValue={table.columns.join(', ')}
      placeholder="Receptacle, Header — or Board / Orange, Board / Black"
      onBlur={e => change(resizeTable(table, table.samples, labels(e.target.value)))} /></label>
    <label>Curve per row (optional, comma-separated) <input defaultValue={table.curves.join(', ')}
      onBlur={e => change({ ...table, curves: labels(e.target.value) })} /></label>
    <label><input type="checkbox" checked={table.diagonal}
      onChange={e => change(resizeTable(table, table.samples, table.columns, e.target.checked))} />Polarisation diagonal; other combinations are not applicable</label>
    {table.samples.length > 0 && table.columns.length > 0 && <>
      <div className="mechanical-source-values"><table><thead><tr><th>Sample</th>{table.columns.map((c, j) => <th key={j}>{c}</th>)}</tr></thead>
        <tbody>{table.samples.map((sample, i) => <tr key={i}><th>{sample}</th>{table.columns.map((column, j) => <td key={j}>
          {table.diagonal && i !== j ? '—' : <select aria-label={`${sample} / ${column} result`} value={table.results[i]?.[j] || ''}
            onChange={e => change({ ...table, results: table.results.map((row, r) => row.map((v, c) => r === i && c === j ? e.target.value : v)) })}>
            <option value="">Select</option><option>Pass</option><option>Fail</option><option>N/A</option>
          </select>}</td>)}</tr>)}</tbody></table></div>
      <button type="button" onClick={() => change({ ...table, results: table.samples.map((_, i) => table.columns.map((_, j) => table.diagonal && i !== j ? '' : 'Pass')) })}>
        Set applicable results to Pass</button>
    </>}
    <button type="button" onClick={remove}>Remove table</button>
  </fieldset>;
}

function SectionEditor({ section, change }: { section: FolderSection; change: (s: FolderSection) => void }) {
  function setTables(tables: ReportTable[]) { change({ ...section, tables, qualitative_confirmed: false }); }
  return <>
    <p>{section.source}</p>
    {section.type_required && <label>Test type <select value={section.kind} onChange={e => {
      const name = e.target.value === 'polarisation' ? 'Polarisation & Mis-mating' : 'Protection electric shock';
      change({ ...section, kind: e.target.value, name, qualitative_confirmed: false,
        information: { ...section.information, 'Item/Process': name } });
    }}><option value="qualitative">Select test type</option>
      <option value="polarisation">Polarisation & Mis-mating</option><option value="protection">Protection electric shock</option>
    </select></label>}
    {section.source_text && <details><summary>View original record</summary><pre className="mechanical-source-values">{section.source_text}</pre></details>}
    {qualitative(section) ? <>
      <p>{section.raw_curves?.length} original curves retained: {section.raw_curves?.join(', ')}. Confirm the report sample/part layout independently.</p>
      {section.tables.map((table, i) => <ReportTableEditor key={i} table={table}
        change={t => setTables(section.tables.map((old, j) => i === j ? t : old))}
        remove={() => setTables(section.tables.filter((_, j) => j !== i))} />)}
      <button type="button" onClick={() => setTables([...section.tables, { title: section.kind === 'protection' ? 'contact not touched by test finger' : 'Polarisation',
        row_heading: '', column_heading: '', columns: [], samples: [], results: [], diagonal: section.kind === 'polarisation', curves: [] }])}>Add report table</button>
      <label><input type="checkbox" checked={section.qualitative_confirmed || false}
        disabled={!section.tables.length || !section.tables.every(tableReady)}
        onChange={e => change({ ...section, qualitative_confirmed: e.target.checked })} />I confirm this project's report layout and results.</label>
    </> : <>
      <div className="mechanical-source-values"><table><thead><tr><th>Curve</th><th>Sample</th><th>Colour</th><th>Part</th><th>{section.force_fields.length ? 'FEnd section / FEnd section 1 (N)' : 'Recorded force (N)'}</th></tr></thead>
        <tbody>{section.rows.map((row, i) => <tr key={row.curve}><td>{row.curve}</td>
          {(['sample', 'colour', 'part'] as const).map(field => <td key={field}><input
            aria-label={`${field === 'sample' ? 'Sample' : field === 'colour' ? 'Colour' : 'Part'} for curve ${row.curve}`}
            value={row[field]} placeholder={field === 'sample' ? 'Required' : 'If recorded'}
            onChange={e => change({ ...section, rows: section.rows.map((old, j) => j === i ? { ...old, [field]: e.target.value } : old) })} /></td>)}
          <td>{section.kind === 'mating' ? `${row.mating} / ${row.withdraw}` : section.force_fields.length ? `${row.end_section} / ${row.end_section1}` : row.value}</td></tr>)}</tbody></table></div>
      {section.force_fields.length > 0 && <label>Recorded hold-force field <select value={section.force_field}
        onChange={e => change({ ...section, force_field: e.target.value })}>
        <option value="">Select field</option>{section.force_fields.map(field => <option key={field}>{field}</option>)}</select></label>}
      {section.kind === 'mating' && <label><input type="checkbox" checked={section.withdraw_magnitude}
        onChange={e => change({ ...section, withdraw_magnitude: e.target.checked })} />Display withdraw force as magnitude; retain the original signed record</label>}
    </>}
    <details><summary>Eight test information fields</summary><p>Missing information remains Not recorded. Enter only confirmed information; dates use YYYY-MM-DD.</p>
      {informationFields.map(field => <label key={field}>{field}<input value={section.information[field] || ''}
        onChange={e => change({ ...section, information: { ...section.information, [field]: e.target.value } })} /></label>)}
    </details>
  </>;
}

export function MechanicalSummaryTool(): ReactElement {
  const picker = useRef<HTMLInputElement>(null);
  const request = useRef(0);
  const running = useRef(false);
  const [files, setFiles] = useState<File[]>([]);
  const [analysis, setAnalysis] = useState<FolderAnalysis>();
  const [stage, setStage] = useState('');
  const [error, setError] = useState('');
  const [downloaded, setDownloaded] = useState('');
  const [notice, setNotice] = useState('');
  useEffect(() => { picker.current?.setAttribute('webkitdirectory', ''); return () => { request.current += 1; }; }, []);
  const busy = Boolean(stage);
  async function download(selected: File[], result: FolderAnalysis, token: number) {
    setStage('Generating workbook…');
    const response = await generateMechanicalFolder(selected, reviewFor(result));
    if (request.current !== token) return;
    const url = URL.createObjectURL(response.blob);
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = response.fileName || 'Mechanical Force Summary.xlsx';
    document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
    setDownloaded(anchor.download);
    setNotice(saveReview(result) ? 'Confirmed details are saved for this project and unchanged source records on this computer.' :
      'Workbook downloaded. Confirmations could not be saved on this computer.');
  }
  async function choose(selected: File[]) {
    if (!selected.length || running.current) return;
    const supported = selected.filter(file => /\.(pdf|xlsx?)$/i.test(file.name));
    setFiles(supported); setAnalysis(undefined); setDownloaded(''); setNotice(''); setError('');
    if (!supported.length) { setError('No PDF or Excel records in this folder. Select the test-results folder.'); return; }
    running.current = true;
    const token = ++request.current;
    setStage('Reading test records…');
    try {
      let result = await previewMechanicalFolder(supported);
      if (token !== request.current) return;
      const saved = savedReview(result);
      if (saved) {
        try { result = await previewMechanicalFolder(supported, saved); }
        catch { setNotice('Saved confirmations could not be applied. Please review the unresolved details.'); }
      }
      if (token !== request.current) return;
      result = { ...result, sections: result.sections.map(section => ({ ...section,
        qualitative_confirmed: qualitative(section) && section.tables.length > 0 && section.issues.length === 0 })) };
      setAnalysis(result);
      if (result.ready) await download(supported, result, token);
    } catch (cause) { if (token === request.current) setError(cause instanceof Error ? cause.message : 'Could not read the test folder.'); }
    finally { if (token === request.current) { setStage(''); running.current = false; } }
  }
  async function generate() {
    if (!analysis || running.current) return;
    const token = ++request.current;
    running.current = true; setError(''); setDownloaded('');
    try { await download(files, analysis, token); }
    catch (cause) { if (token === request.current) setError(cause instanceof Error ? cause.message : 'Could not generate the workbook. Check that Microsoft Excel is available and retry.'); }
    finally { if (token === request.current) { setStage(''); running.current = false; } }
  }
  function change(index: number, section: FolderSection) {
    setAnalysis(old => old && ({ ...old, sections: old.sections.map((s, i) => i === index ? section : s) }));
    setDownloaded(''); setError('');
  }
  const ready = analysis && !analysis.errors.length && analysis.sections.length > 0 && analysis.sections.every(sectionReady);
  return <article className="tools-action-group" aria-label="Mechanical Summary">
    <input ref={picker} type="file" hidden multiple disabled={busy} aria-label="Select mechanical test folder"
      onChange={e => { const selected = Array.from(e.target.files || []); e.target.value = ''; void choose(selected); }} />
    <button type="button" className="primary-action tools-picker-action" disabled={busy}
      title="Choose a test-results folder to generate a new summary. Only unresolved details need your input."
      onClick={() => picker.current?.click()}>Mechanical Summary</button>
    {(analysis || busy || error) && <ToolsFeedback><section className="tools-action-feedback mechanical-summary-review" aria-label="Mechanical Summary Review">
      {stage && <p role="status">{stage}</p>}
      {error && <p className="tools-feedback-error" role="alert">{error}</p>}
      {downloaded && <p role="status" aria-label="Downloaded File">{downloaded}</p>}
      {notice && <p>{notice}</p>}
      {analysis && <>
        <p>{analysis.project || 'Selected folder'} · {analysis.sections.length} test records</p>
        {analysis.errors.map(item => <div key={item.file} className="tools-feedback-error"><p>{item.file}: {item.message}</p>
          <button type="button" disabled={busy} onClick={() => void choose(files.filter(f => (f.webkitRelativePath || f.name) !== item.file))}>Exclude this file and rescan</button></div>)}
        {!ready && <p>Complete the unresolved details below. Unknown test information may remain Not recorded.</p>}
        {analysis.sections.map((section, index) => <details className="mechanical-source" key={section.id} open={section.issues.length > 0 || undefined}>
          <summary>{section.name} — {sectionReady(section) ? 'Ready' : 'Details needed'}</summary>
          <fieldset disabled={busy}><SectionEditor section={section} change={s => change(index, s)} /></fieldset>
        </details>)}
        {analysis.ignored.length > 0 && <details><summary>{analysis.ignored.length} files excluded from generation</summary>
          {analysis.ignored.map((item, i) => <p key={i}>{item.file}: {item.reason}</p>)}</details>}
        {!downloaded && <button type="button" className="primary-action tools-picker-action" disabled={busy || !ready} onClick={() => void generate()}>Generate Summary</button>}
      </>}
    </section></ToolsFeedback>}
  </article>;
}
