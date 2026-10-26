import { useEffect, useRef, useState } from 'react';
import './reportCustomerCopy.css';
import { checkCustomerReviewCopy, generateCustomerReviewCopy, downloadCustomerPart, downloadReportArtifact,
  type ReportAuthoringState } from '../../api/reportAuthoring';

const reviewable = new Set(['visual_review_required', 'unreviewed_embedding', 'unreviewed_package_part']);
export function ReportCustomerCopy({ projectId, state, disabled, onChanged, beginOperation }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
}) {
  const [selected, setSelected] = useState<string[]>([]);
  const [terms, setTerms] = useState('');
  const [oldIds, setOldIds] = useState('');
  const [scope, setScope] = useState(false);
  const [contentReviewed, setContentReviewed] = useState(false);
  const [parts, setParts] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  const customer = state.customer_outputs?.at(-1);
  useEffect(() => { epoch.current++; setBusy(false); setParts(customer?.audit?.reviewed_parts || {});
    setTerms((customer?.audit?.sensitive_terms || []).join('\n')); setOldIds((customer?.audit?.forbidden_project_ids || []).join('\n'));
    setScope(customer?.audit?.disclosure_scope_confirmed || false);
    setContentReviewed(!!output?.artifact && customer?.audit?.content_review_sha256 === output.artifact.sha256);
  }, [projectId, customer?.output_id, state.revision]);
  useEffect(() => () => { epoch.current++; }, []);
  async function run(action: () => Promise<ReportAuthoringState>) {
    if (disabled || busy) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try { const next = await action(); if (token === epoch.current) onChanged(next); }
    catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Customer copy operation failed.'); }
    finally { release(); if (token === epoch.current) setBusy(false); }
  }
  async function download(part?: string) {
    if (!customer || disabled || busy) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try { const file = part ? await downloadCustomerPart(projectId, customer.output_id, part) : await downloadReportArtifact(customer.download_url);
      if (token !== epoch.current) return;
      const url = URL.createObjectURL(file.blob); const anchor = document.createElement('a'); anchor.href = url;
      anchor.download = file.fileName || part?.split('/').at(-1) || customer.file_name; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Download failed.'); }
    finally { release(); if (token === epoch.current) setBusy(false); }
  }
  if (!output) return null;
  const temperatures = (state.results || []).filter(item => item.kind === 'temperature' && state.applied_result_ids?.includes(item.result_id!));
  return <section className="report-customer-copy" aria-label="Customer report review copy"><h4>Customer report copy and disclosure checks</h4>
    <p className="report-customer-copy-note">Uses the registered E-4515 template and current Internal Report copy. Nothing is formally released or written to project folders.</p>
    <fieldset className="report-customer-copy-form" disabled={disabled || busy}>
      {temperatures.length > 0 && <div className="report-customer-copy-checks"><p>Include the complete temperature measurement tables and editable curves already applied to this report:</p>
        {temperatures.map(result => <label className="report-customer-copy-check" key={result.result_id}><input type="checkbox" checked={selected.includes(result.result_id!)} onChange={event => setSelected(previous => event.target.checked ? [...previous, result.result_id!] : previous.filter(id => id !== result.result_id))} />
          <span>Group {result.target.group_label} / Step {result.target.step_token}</span></label>)}
      </div>}
      <div className="report-customer-copy-actions"><button className="secondary-action" type="button" disabled={!output.artifact} onClick={() => void run(() => generateCustomerReviewCopy(projectId, {
        expected_revision: state.revision, output_id: output.output_id, output_sha256: output.artifact!.sha256, temperature_result_ids: selected }))}>Generate customer review copy</button></div>
      {customer && <>
        <div className="report-customer-copy-status"><p>{customer.file_name} — {customer.status === 'package_checked' ? 'Package disclosure checks passed; not release approval' : 'Needs review'}</p>
          <div className="report-customer-copy-actions"><button className="secondary-action" type="button" onClick={() => void download()}>Download customer review copy</button></div>
        </div>
        <div className="report-customer-copy-fields">
          <label className="report-customer-copy-field"><span>Restricted material/disclosure terms (one per line)</span><textarea value={terms} onChange={event => { setTerms(event.target.value); setScope(false); }} /></label>
          <label className="report-customer-copy-field"><span>Previous project identifiers to exclude (one per line)</span><textarea value={oldIds} onChange={event => { setOldIds(event.target.value); setScope(false); }} /></label>
        </div>
        <div className="report-customer-copy-checks">
          <label className="report-customer-copy-check"><input type="checkbox" checked={scope} onChange={event => setScope(event.target.checked)} /><span>I checked the disclosure scope and unclassified materials; metals are not treated as resin</span></label>
          <label className="report-customer-copy-check"><input type="checkbox" checked={contentReviewed} onChange={event => setContentReviewed(event.target.checked)} /><span>I reviewed this Internal Report copy's project facts, specification, conclusions, samples, photos and completeness</span></label>
        </div>
        <ul className="report-customer-copy-issues">{customer.audit?.issues.map((issue, index) => <li key={index}><p><strong>{issue.location}</strong>: {issue.message}</p>
          {issue.sha256 && reviewable.has(issue.code) && <div className="report-customer-copy-issue-review">
            <div className="report-customer-copy-actions"><button className="secondary-action" type="button" onClick={() => void download(issue.location)}>Download exact part for review</button></div>
            <label className="report-customer-copy-check"><input type="checkbox" checked={parts[issue.location] === issue.sha256} onChange={event => setParts(previous => {
              const next = { ...previous }; if (event.target.checked) next[issue.location] = issue.sha256!; else delete next[issue.location]; return next;
            })} /><span>I reviewed this exact image/object and approve its disclosure</span></label>
          </div>}
        </li>)}</ul>
        <div className="report-customer-copy-actions"><button className="secondary-action" type="button" disabled={!customer.artifact} onClick={() => void run(() => checkCustomerReviewCopy(projectId, {
          expected_revision: state.revision, output_id: customer.output_id, output_sha256: customer.artifact!.sha256,
          sensitive_terms: terms.split('\n').map(term => term.trim()).filter(Boolean), forbidden_project_ids: oldIds.split('\n').map(term => term.trim()).filter(Boolean),
          reviewed_parts: parts, disclosure_scope_confirmed: scope, content_review_sha256: contentReviewed ? output.artifact?.sha256 : null }))}>Check saved customer package</button></div>
      </>}
    </fieldset>{error && <p className="report-customer-copy-error" role="alert">{error}</p>}
  </section>;
}
