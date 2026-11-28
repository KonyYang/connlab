import {useEffect, useRef, useState, type ReactNode, type RefObject} from 'react';
import {downloadStandaloneCustomerReport, readStandaloneCustomerReportJob, type BlobDownloadResponse, type StandaloneCustomerReportJob} from '../../api/client';
import {discardCustomerInput, inspectProjectCustomerSource, inspectUploadedCustomerSource, startInspectedCustomerReport,
  type CustomerDecisions, type CustomerInspection, type WorkingCustomerSource} from '../../api/customerContent';
import {downloadReportArtifact, generateCustomerReviewCopy, type ReportAuthoringState} from '../../api/reportAuthoring';
import {CustomerReportProgress} from '../../components/common/CustomerReportProgress';
import {ToolsFeedback} from '../tools/ToolsFeedback';
import {CustomerContentDialog, confirmedChoices} from './CustomerContentDialog';

type Source = {kind: 'upload'; file: File} | {kind: 'project'; project: string; name: string; identity: {source_sha256: string}}
  | {kind: 'working'; project: string; name: string; identity: WorkingCustomerSource};
type InspectedSource = {source: Source; inspection: CustomerInspection};
type Download = {read: () => Promise<BlobDownloadResponse>; name: string};
type Props = {
  entryPicker?: RefObject<HTMLInputElement | null>;
  source?: Exclude<Source, {kind:'upload'}>; disabled?: boolean; tools?: boolean;
  begin?: () => (() => void) | null; changed?: (state: ReportAuthoringState) => void;
  extraActions?: (chooseFinishedWord: () => void) => ReactNode;
};

function hasExpired(error: unknown) {
  return typeof error === 'object' && error !== null && 'status' in error && [404,410].includes(Number(error.status));
}

export function CustomerReportDownload({source, disabled, tools, begin, changed, extraActions, entryPicker}: Props) {
  const ownPicker = useRef<HTMLInputElement>(null);
  const picker = entryPicker ?? ownPicker;
  const chooseFinishedFile = Boolean(entryPicker && !source);
  const alive = useRef(true);
  const running = useRef(false);
  const inspectedInput = useRef<string | undefined>(undefined);
  const submitting = useRef(false);
  const release = useRef<(() => void) | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState<InspectedSource | null>(null);
  const [progress, setProgress] = useState<StandaloneCustomerReportJob | null>(null);
  const [last, setLast] = useState<Download | null>(null);
  const [notices, setNotices] = useState<string[]>([]);
  const [fileName, setFileName] = useState('');
  const [reviewedSource, setReviewedSource] = useState<Source | null>(null);
  const [retryStart, setRetryStart] = useState<{input: InspectedSource; decisions: CustomerDecisions} | null>(null);
  const [retryOperation, setRetryOperation] = useState<StandaloneCustomerReportJob | null>(null);
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; if (inspectedInput.current) void discardCustomerInput(inspectedInput.current).catch(() => undefined); release.current?.(); release.current = undefined; };
  }, []);
  const nameOf = (item: Source) => item.kind === 'upload' ? item.file.name : item.name;

  function beginAction() {
    if (running.current || disabled) return false;
    const done = begin?.();
    if (begin && !done) return false;
    release.current = done ?? undefined;
    running.current = true; setBusy(true); setError('');
    return true;
  }
  function finish() {
    running.current = false; submitting.current = false;
    release.current?.(); release.current = undefined;
    if (alive.current) setBusy(false);
  }
  function failed(reason: unknown) {
    if (alive.current) setError(reason instanceof Error ? reason.message : 'Unable to generate the customer report. Try again.');
  }
  async function download(item: Download) {
    setLast(item);
    let response: BlobDownloadResponse;
    try { response = await item.read(); }
    catch (reason) {
      if (hasExpired(reason)) {
        if (alive.current) setLast(null);
        throw new Error('This download expired. Generate the customer report again.');
      }
      throw reason;
    }
    if (!alive.current) return;
    const name = response.fileName || item.name;
    const url = URL.createObjectURL(response.blob);
    const link = document.createElement('a'); link.href = url; link.download = name;
    document.body.appendChild(link);
    try { link.click(); } finally { link.remove(); window.setTimeout(() => URL.revokeObjectURL(url), 0); }
    setFileName(name);
  }
  async function completeJob(started: StandaloneCustomerReportJob) {
    let job = started;
    while (alive.current && (job.status === 'queued' || job.status === 'running')) {
      setProgress(job);
      try { job = await readStandaloneCustomerReportJob(started.operation_id); }
      catch (reason) { if (alive.current) {
        const gone = hasExpired(reason);
        setRetryOperation(gone ? null : started); setProgress(null);
        if (gone) throw new Error('This generation task expired. Generate the customer report again.');
      } throw reason; }
      if (job.status === 'queued' || job.status === 'running') {
        if (alive.current) setProgress(job);
        await new Promise(resolve => window.setTimeout(resolve, 750));
      }
    }
    if (!alive.current) return;
    setProgress(null); setRetryOperation(null);
    if (job.status !== 'completed') throw new Error(job.message || 'Customer report generation failed.');
    setNotices(job.notices || []);
    await download({name:job.file_name || 'Customer Report.docx', read:() => downloadStandaloneCustomerReport(job.operation_id)});
  }
  async function generate(input: InspectedSource, decisions: CustomerDecisions) {
    if (submitting.current) return;
    submitting.current = true;
    setDialog(null);
    const item = input.source;
    try {
      if (item.kind === 'working') {
        const state = await generateCustomerReviewCopy(item.project, {...item.identity, customer_decisions:decisions});
        if (!alive.current || state.project_id !== item.project) return;
        const result = state.customer_outputs?.at(-1);
        if (!result || result.parent_output_id !== item.identity.output_id) throw new Error('Generated file does not match this internal report. Refresh and try again.');
        setNotices(result.review_notices || []);
        changed?.(state);
        await download({name:result.file_name, read:() => downloadReportArtifact(result.download_url)});
      } else {
        if (!input.inspection.input_id) throw new Error('The checked internal report is unavailable. Select it again.');
        let job: StandaloneCustomerReportJob;
        try {
          job = await startInspectedCustomerReport(input.inspection.input_id, decisions);
        } catch (reason) {
          const status = reason && typeof reason === 'object' && 'status' in reason ? Number(reason.status) : 0;
          if ((!status || status >= 500) && alive.current) {
            setRetryStart({input,decisions});
            failed(reason);
            return;
          }
          throw reason;
        }
        setRetryStart(null);
        inspectedInput.current = undefined;
        if (alive.current) await completeJob(job);
      }
    } catch (reason) {
      if (alive.current) setRetryStart(null);
      const id = inspectedInput.current; inspectedInput.current = undefined;
      if (id) void discardCustomerInput(id).catch(() => undefined);
      failed(reason);
    } finally { finish(); }
  }
  async function inspect(item: Source, review = false) {
    if (!beginAction()) return;
    setLast(null); setFileName(''); setNotices([]); setProgress(null); setRetryOperation(null); setReviewedSource(null);
    try {
      if (item.kind === 'upload' && !/\.docx$/i.test(item.file.name)) throw new Error('Select an internal Word report in .docx format.');
      const inspection = item.kind === 'upload' ? await inspectUploadedCustomerSource(item.file) : await inspectProjectCustomerSource(item.project,item.identity);
      if (!alive.current) {
        if (inspection.input_id) await discardCustomerInput(inspection.input_id);
        return;
      }
      inspectedInput.current = inspection.input_id;
      const choices = confirmedChoices(inspection,inspection.decisions);
      if (inspection.fields.length) setReviewedSource(item);
      if (choices && (!review || !inspection.fields.length)) await generate({source:item,inspection},choices);
      else setDialog({source:item,inspection});
    } catch (reason) { failed(reason); finish(); }
  }
  async function retry(action: () => Promise<void>) {
    if (!beginAction()) return;
    try { await action(); } catch (reason) { failed(reason); } finally { finish(); }
  }
  function pick() { if (!disabled && !running.current) picker.current?.click(); }
  const feedback = <div className="customer-download-feedback">
    {busy && !dialog && (progress ? <CustomerReportProgress stage={progress.stage} elapsedSeconds={progress.elapsed_seconds} /> :
      <span role="status">Preparing customer report…</span>)}
    {error && <p role="alert">{error}</p>}
    {notices.length > 0 && <details className="customer-review-notices"><summary>{notices.length} item{notices.length === 1 ? '' : 's'} to review in Word</summary><ul>{notices.map((note,i) => <li key={i}>{note}</li>)}</ul></details>}
    {fileName && <p role="status" aria-label="Downloaded File">{fileName}</p>}
    {!busy && last && <button type="button" className="report-editor-link" onClick={() => void retry(() => download(last))}>{fileName ? 'Download again' : 'Retry download'}</button>}
    {!busy && retryStart && <button type="button" className="report-editor-link"
      onClick={() => { if (beginAction()) void generate(retryStart.input,retryStart.decisions); }}>Retry generation request</button>}
    {!busy && retryOperation && <button type="button" className="report-editor-link" onClick={() => void retry(() => completeJob(retryOperation))}>Retry status check</button>}
    {!busy && !retryStart && !retryOperation && reviewedSource && <button type="button" className="report-editor-link" onClick={() => void inspect(reviewedSource.kind === 'working' && source?.kind === 'working' ? source : reviewedSource,true)}>Review customer content…</button>}
  </div>;
  return <>
    <input ref={picker} type="file" accept=".docx" disabled={disabled || busy || !!retryStart || !!retryOperation} hidden aria-label="Select Internal Report" onChange={e => {
      const file = e.target.files?.[0]; e.target.value = ''; if (file) void inspect({kind:'upload',file});
    }}/>
    <button type="button" className={tools ? 'primary-action tools-picker-action' : chooseFinishedFile ? 'report-editor-link' : 'ui-secondary-action'}
      disabled={Boolean(disabled || busy || retryStart || retryOperation)} onClick={() => source ? void inspect(source) : pick()}>
      {tools ? 'Generate Customer Report' : chooseFinishedFile ? 'Create customer copy from a finished Word…' : 'Generate customer report'}</button>
    {extraActions?.(pick)}
    {tools ? <ToolsFeedback>{feedback}</ToolsFeedback> : feedback}
    {dialog && <CustomerContentDialog name={nameOf(dialog.source)} inspection={dialog.inspection}
      onGenerate={values => void generate(dialog,values)} onCancel={() => {
        const id = inspectedInput.current; inspectedInput.current = undefined;
        if (id) void discardCustomerInput(id).catch(failed);
        setDialog(null); finish(); }}/>}
  </>;
}
