import { useEffect, useState } from 'react';
import { getReportCoverage, type ReportCoverage } from '../../api/reportAuthoringBatch';
import type { ReportAuthoringState } from '../../api/reportAuthoring';

export type StepLink = { projectId: string; matrix: string; group: string; row: string; token: string };

export function readStepLink(projectId: string, search: string): StepLink | null {
  const params = new URLSearchParams(search);
  const matrix = params.get('matrix'), group = params.get('group'), row = params.get('row'), token = params.get('step');
  return matrix && group && row && token ? { projectId, matrix, group, row, token } : null;
}

const labels = { missing: 'No confirmed evidence linked', ready: 'Evidence ready for reporting',
  needs_review: 'Evidence needs review', not_applicable: 'Not applicable' };

export function StepReportEvidence({ projectId, step, report }: {
  projectId: string; step: StepLink; report?: ReportAuthoringState;
}) {
  const [attempt, setAttempt] = useState(0);
  // Coverage describes the entire confirmed Matrix. Selecting another cell must not reread all sources.
  const owner = JSON.stringify([projectId, step.matrix, report?.revision, attempt]);
  const [read, setRead] = useState<{ owner: string; data?: ReportCoverage; error?: string }>();
  useEffect(() => {
    let active = true;
    if (projectId === step.projectId) void getReportCoverage(projectId).then(
      data => { if (active) setRead({ owner, data }); },
      cause => { if (active) setRead({ owner, error: cause instanceof Error ? cause.message : 'Check storage access.' }); }
    );
    return () => { active = false; };
  }, [owner, projectId, step.projectId]);
  if (step.projectId !== projectId || (report && report.project_id !== projectId)) return null;
  if (read?.owner !== owner) return <p role="status">Checking report evidence…</p>;
  if (!read.data) return <p role="alert">Unable to read report evidence: {read.error} <button type="button" onClick={() => setAttempt(value => value + 1)}>Retry</button></p>;
  if (read.data.matrix_id !== step.matrix || (report && report.context.matrix_id !== step.matrix))
    return <p role="alert">The confirmed Matrix has changed. Reopen the step in Workbench.</p>;
  const matches = read.data.rows.filter(r => r.group_id === step.group && r.row_id === step.row && r.step_token === step.token);
  if (matches.length !== 1) return <p role="alert">Cannot uniquely locate this step. Check the confirmed Matrix.</p>;
  const entry = matches[0], dataset = read.data.llcr_dataset;
  const params = new URLSearchParams({matrix: step.matrix, group: step.group, row: step.row, step: step.token});
  const href = '/projects/' + encodeURIComponent(projectId) + '/report-workspace?' + params;
  const pending = read.data.pending_mappings.filter(m => m.matrix_id === step.matrix && m.group_id === step.group && m.row_id === step.row && m.step_token === step.token);
  return <section aria-label="Selected step report evidence">
    <strong>{report ? entry.group_label + ' / ' + step.token + ': ' + entry.test_item : 'Report evidence'}</strong>
    <p>{labels[entry.status]}</p>
    {entry.status !== 'missing' && entry.reasons.map(reason => <p key={reason}>{reason}</p>)}
    {pending.map(m => <p key={m.mapping_id}>Pending mapping: {m.label}{m.reason && ' — ' + m.reason}</p>)}
    {entry.result_ids.length > 0 && <p>{entry.applied_result_ids.length
      ? 'Used in the current working copy: ' + entry.applied_result_ids.length + ' of ' + entry.result_ids.length
      : entry.usable_result_ids.length ? 'Not used in the current working copy' : 'No verified evidence in the current working copy'}</p>}
    {report && entry.result_ids.length > 0 && <ul>{entry.result_ids.map(id => {
      const result = report.results?.find(r => r.result_id === id);
      const source = report.sources.find(s => s.source_id === result?.source_id);
      const llcr = dataset?.entries.find(e => e.entry_id === id);
      return <li key={id}>{source?.file_name || (llcr && dataset?.source_file_name) || 'Source unavailable'}
        {result?.data.sheet_name && ' / ' + result.data.sheet_name}{llcr && ' / ' + llcr.stage_label}
        {entry.applied_result_ids.includes(id) && ' — used in working copy'}</li>;
    })}</ul>}
    {!report && <a href={href}>View this step in Report Workspace</a>}
  </section>;
}
