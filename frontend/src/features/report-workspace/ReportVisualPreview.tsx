import { useEffect, useRef, useState } from 'react';
import { confirmReportVisualPages, createReportVisualPreview, downloadReportArtifact, reportVisualPreviewUrl, type ReportAuthoringState } from '../../api/reportAuthoring';

export function ReportVisualPreview({ projectId, state, disabled, beginOperation, onChanged, outputId }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  beginOperation?: () => (() => void) | null; onChanged: (state: ReportAuthoringState) => void;
  outputId?: string;
}) {
  const output = outputId ? [...state.outputs, ...(state.customer_outputs || [])].find(item => item.output_id === outputId) : state.outputs.at(-1);
  const isCustomer = state.customer_outputs?.some(item => item.output_id === output?.output_id);
  const preview = output?.visual_preview?.output_sha256 === output?.artifact?.sha256 ? output?.visual_preview : undefined;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [url, setUrl] = useState('');
  const [pages, setPages] = useState<number[]>([]);
  const [page, setPage] = useState(1);
  const [notes, setNotes] = useState('');
  const epoch = useRef(0);
  useEffect(() => { epoch.current++; setBusy(false); setError(''); setUrl(''); setPages([]); setPage(1); setNotes(''); }, [projectId, output?.output_id]);
  useEffect(() => () => { epoch.current++; }, []);
  useEffect(() => () => { if (url) URL.revokeObjectURL(url); }, [url]);
  async function run(work: () => Promise<ReportAuthoringState | { blob: Blob }>) {
    if (disabled || busy || state.project_id !== projectId) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try {
      const value = await work();
      if (token !== epoch.current) return;
      if ('project_id' in value) { if (value.project_id === projectId) onChanged(value); }
      else setUrl(URL.createObjectURL(value.blob));
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Word preview failed. Original documents remain unchanged.'); }
    finally { release(); if (token === epoch.current) setBusy(false); }
  }
  if (!output?.artifact) return null;
  const identity = { expected_revision: state.revision, output_id: output.output_id, output_sha256: output.artifact.sha256 };
  return <section className="report-visual-preview" aria-label={isCustomer ? 'Customer Word visual preview' : 'Word visual preview'}><h5>{isCustomer ? 'Customer Word visual layout' : 'Word visual layout'}</h5>
    <p>Microsoft Word renders an isolated read-only working copy on the server. Macros and automatic external-link updates are disabled. Original files remain unchanged.</p>
    {!preview ? <button type="button" disabled={disabled || busy} onClick={() => void run(() => createReportVisualPreview(projectId, identity))}>Render this working copy with Word</button>
      : <><p>{preview.page_count} pages · {preview.status} · exact file {preview.output_sha256.slice(0, 12)}</p>
        <button type="button" disabled={disabled || busy} onClick={() => void run(() => downloadReportArtifact(reportVisualPreviewUrl(projectId, output.output_id)))}>Open retained PDF — no re-render</button>
        <p>{preview.affected_pages_reason}</p>
        <p>Inspect first: {preview.affected_pages.map(number => <button type="button" key={number} disabled={!url} onClick={() => setPage(number)}>Page {number}</button>)}</p>
        {url && <><a href={url} target="_blank" rel="noreferrer">Open complete PDF in a new tab</a>
          <iframe title={`Word preview page ${page}`} src={`${url}#page=${page}`} />
          <fieldset disabled={disabled || busy}><legend>Full-document visual check (all pages, no fixed page count)</legend>
            <div className="report-page-checks">{preview.pages.map(item => <label className="report-batch-check" key={item.page}><input type="checkbox" checked={pages.includes(item.page)}
              onChange={event => setPages(previous => event.target.checked ? [...previous, item.page] : previous.filter(value => value !== item.page))} />Page {item.page}</label>)}</div>
            <label className="report-batch-check"><input type="checkbox" checked={pages.length === preview.page_count}
              onChange={event => setPages(event.target.checked ? preview.pages.map(item => item.page) : [])} />I have visually checked every page of this exact PDF</label>
            <label>Layout review notes<textarea value={notes} onChange={event => setNotes(event.target.value)} placeholder="Check clipping, captions, pagination, tables, photos and fixed wording" /></label>
            <button type="button" disabled={pages.length !== preview.page_count} onClick={() => void run(() => confirmReportVisualPages(projectId,
              { ...identity, preview_sha256: preview.artifact.sha256, pages, notes, confirmed_by: 'Lab User' }))}>Record full visual review — not formal release</button>
          </fieldset></>}
      </>}
    {busy && <p role="status">Preparing Word preview (maximum 120 seconds)…</p>}{error && <p role="alert">{error}</p>}
  </section>;
}
