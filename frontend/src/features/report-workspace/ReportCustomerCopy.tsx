import { useEffect, useRef, useState } from 'react';
import { downloadCustomerPart, downloadReportArtifact,
  type CustomerReportOutput, type ReportAuthoringState } from '../../api/reportAuthoring';
import { CustomerDisclosureReview } from './CustomerDisclosureReview';
import { ReportDelivery } from './ReportDelivery';
import type { ReportIssueSection } from './ReportIssueActions';
import './reportCustomerCopy.css';

type Props = {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
  onOpenSection?: (section: ReportIssueSection) => void;
};

export function ReportCustomerCopy(props: Props) {
  const { projectId, state, disabled, onChanged, beginOperation } = props;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [editingReview, setEditingReview] = useState(false);
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  const previous = state.customer_outputs?.at(-1);
  const customer = state.customer_outputs?.slice().reverse().find(item => item.parent_output_id === output?.output_id);
  const interrupted = !!state.delivery && state.delivery.status !== 'completed';
  useEffect(() => {
    setBusy(false); setError(''); setEditingReview(false);
    return () => { epoch.current++; };
  }, [projectId, state.revision]);

  async function run(action: () => Promise<void>) {
    if (disabled || busy || state.project_id !== projectId) return;
    const release = beginOperation ? beginOperation() : () => undefined;
    if (!release) return;
    const token = epoch.current;
    setBusy(true); setError('');
    try { await action(); }
    catch (cause) {
      if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to complete the customer copy action.');
    } finally { release(); if (token === epoch.current) setBusy(false); }
  }
  function update(action: () => Promise<ReportAuthoringState>) {
    const token = epoch.current;
    void run(async () => {
      const next = await action();
      if (token === epoch.current && next.project_id === projectId) onChanged(next);
    });
  }
  function download(copy: CustomerReportOutput, part?: string) {
    const token = epoch.current;
    void run(async () => {
      const file = part ? await downloadCustomerPart(projectId, copy.output_id, part) : await downloadReportArtifact(copy.download_url);
      if (token !== epoch.current) return;
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.fileName || part?.split('/').at(-1) || copy.file_name;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }
  if (interrupted) return <ReportDelivery {...props} />;
  if (!output) return null;
  const checked = customer?.status === 'package_checked' && customer.audit?.passed;
  const reviewContextChanged = customer?.audit?.issues.some(issue => issue.code === 'review_context_changed') ?? false;
  if (!customer) return <div>
    <p>Generate a customer report from the current working copy before saving it to the project.</p>
    {previous && <button className="report-editor-link" type="button" disabled={disabled || busy}
      onClick={() => download(previous)}>Download previous customer copy</button>}
    {error && <p role="alert">{error}</p>}
  </div>;
  return <section className="report-customer-copy" aria-label="Customer report review copy">
      <header className="report-customer-copy-header">
        <strong>{customer.file_name}</strong>
        <button className="report-editor-link" type="button" disabled={disabled || busy} onClick={() => download(customer)}>Download customer review copy</button>
      </header>
      {checked && !editingReview ?
        <ReportDelivery {...props} disabled={disabled || busy}>
          <button className="report-editor-link" type="button" disabled={disabled || busy} onClick={() => setEditingReview(true)}>Review disclosure checks again</button>
        </ReportDelivery> :
        <>
          <CustomerDisclosureReview key={`${projectId}/${customer.output_id}/${state.revision}/${reviewContextChanged}`}
            projectId={projectId} revision={state.revision} internal={output} customer={customer}
            disabled={disabled || busy} check={update} downloadPart={part => download(customer, part)} onOpenSection={props.onOpenSection} />
          {editingReview && <button type="button" className="report-editor-link" disabled={disabled || busy} onClick={() => setEditingReview(false)}>Discard review edits</button>}
        </>}
    {busy && <p role="status">Preparing customer copy…</p>}
    {error && <p className="report-customer-copy-error" role="alert">{error}</p>}
  </section>;
}
