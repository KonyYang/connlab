const destinations = [
  { section: 'llcr', label: 'Review LLCR results', codes: ['stale_llcr_result', 'pending_llcr_decision'] },
  { section: 'results', label: 'Review test results', codes: ['coverage_incomplete', 'pending_result_decision', 'stale_result', 'old_temperature_evidence'] },
  { section: 'sources', label: 'Review sources and decisions', codes: ['source_unavailable', 'pending_decisions'] },
  { section: 'review', label: 'Open document review', codes: ['content_conflict', 'content_incomplete', 'inherited_content'] },
] as const;
export type ReportIssueSection = typeof destinations[number]['section'];

export function ReportIssueActions({ issues, onOpenSection, disabled }: {
  issues: { code: string }[]; onOpenSection?: (section: ReportIssueSection) => void; disabled: boolean;
}) {
  if (!onOpenSection) return null;
  const related = destinations.filter(target => target.codes.some(code => issues.some(issue => issue.code === code)));
  if (!related.length) return null;
  return <div className="report-customer-copy-actions">{related.map(({ section, label }) =>
    <button key={section} className="report-editor-link" type="button" disabled={disabled} onClick={() => onOpenSection(section)}>{label}</button>)}</div>;
}
