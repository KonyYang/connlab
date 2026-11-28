import { useState } from 'react';
import { checkCustomerReviewCopy, type CustomerReportOutput, type ReportAuthoringOutput } from '../../api/reportAuthoring';
import { ReportIssueActions, type ReportIssueSection } from './ReportIssueActions';

const reviewable = new Set(['visual_review_required', 'unreviewed_embedding', 'unreviewed_package_part']);
const lines = (value: string) => value.split('\n').map(term => term.trim()).filter(Boolean);

type Props = {
  projectId: string; revision: number; internal: ReportAuthoringOutput; customer: CustomerReportOutput;
  disabled: boolean; check: (action: () => ReturnType<typeof checkCustomerReviewCopy>) => void;
  downloadPart: (part: string) => void;
  onOpenSection?: (section: ReportIssueSection) => void;
};

export function CustomerDisclosureReview({ projectId, revision, internal, customer, disabled, check, downloadPart, onOpenSection }: Props) {
  const audit = customer.audit;
  const changed = audit?.issues.some(issue => issue.code === 'review_context_changed');
  const [scope, setScope] = useState(!changed && !!audit?.disclosure_scope_confirmed);
  const [content, setContent] = useState(!changed && !!internal.artifact && audit?.content_review_sha256 === internal.artifact.sha256);
  const [parts, setParts] = useState<Record<string, string>>(changed ? {} : audit?.reviewed_parts || {});
  const [terms, setTerms] = useState((audit?.sensitive_terms || []).join('\n'));
  const [oldIds, setOldIds] = useState((audit?.forbidden_project_ids || []).join('\n'));

  function submit() {
    if (!customer.artifact || !internal.artifact) return;
    const request = {
      expected_revision: revision, output_id: customer.output_id, output_sha256: customer.artifact.sha256,
      reviewed_parts: parts, sensitive_terms: lines(terms), forbidden_project_ids: lines(oldIds),
      disclosure_scope_confirmed: scope, content_review_sha256: content ? internal.artifact.sha256 : null,
    };
    check(() => checkCustomerReviewCopy(projectId, request));
  }
  return <fieldset className="report-customer-copy-form" disabled={disabled}>
    <legend>Review before saving</legend>
    <details><summary>Additional disclosure checks</summary>
      <div className="report-customer-copy-fields">
        <label className="report-customer-copy-field">Restricted terms (one per line)
          <textarea value={terms} onChange={event => { setTerms(event.target.value); setScope(false); }} /></label>
        <label className="report-customer-copy-field">Previous project IDs to exclude (one per line)
          <textarea value={oldIds} onChange={event => { setOldIds(event.target.value); setScope(false); }} /></label>
      </div>
    </details>
    <div className="report-customer-copy-checks">
      <label className="report-customer-copy-check"><input type="checkbox" checked={scope} onChange={e => setScope(e.target.checked)} />
        <span>I checked the disclosure scope, including unclassified materials and the distinction between metals and resins.</span></label>
      <label className="report-customer-copy-check"><input type="checkbox" checked={content} onChange={e => setContent(e.target.checked)} />
        <span>I reviewed this Internal Report’s project facts, specification, conclusions, samples, photos and completeness.</span></label>
    </div>
    {Boolean(audit?.issues.length) && <ul className="report-customer-copy-issues" aria-label="Items to review">
      {audit!.issues.map((issue, index) => <li key={`${issue.code}-${issue.location}-${index}`}>
        <p>{issue.location !== 'review' && <strong>{issue.location} · </strong>}{issue.message}</p>
        {issue.sha256 && reviewable.has(issue.code) && <div className="report-customer-copy-issue-review">
          <button className="report-editor-link" type="button" onClick={() => downloadPart(issue.location)}>Download exact part for review</button>
          <label className="report-customer-copy-check"><input type="checkbox" checked={parts[issue.location] === issue.sha256}
            onChange={event => {
              const next = { ...parts };
              if (event.target.checked) next[issue.location] = issue.sha256!;
              else delete next[issue.location];
              setParts(next);
            }} /><span>I reviewed this exact image/object and approve its disclosure</span></label>
        </div>}
      </li>)}
    </ul>}
    <ReportIssueActions issues={audit?.issues || []} disabled={disabled} onOpenSection={onOpenSection} />
    <button className="primary-action" type="button" disabled={!customer.artifact || !internal.artifact} onClick={submit}>Check customer copy</button>
  </fieldset>;
}
