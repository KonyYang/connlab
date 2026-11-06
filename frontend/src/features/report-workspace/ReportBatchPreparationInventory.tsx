import type { ReportSourceRole } from '../../api/reportAuthoring';
import type { ReportCoverage, ReportInventory } from '../../api/reportAuthoringBatch';

const roles: [ReportSourceRole, string][] = [
  ['original', "This project's Internal Report"], ['layout_reference', 'Layout reference'],
  ['tools_result_package', 'Tools results package'], ['temperature', 'Temperature data'],
  ['cr', 'Contact resistance'], ['mechanical', 'Mechanical Summary'], ['photo', 'Photo'],
  ['specification', 'Specification'], ['evidence', 'Supporting evidence'],
];

export function ReportBatchPreparationInventory({ inventory, coverage, selected, onSelect, onRetain, disabled }: {
  inventory: ReportInventory | null; coverage: ReportCoverage | null;
  selected: Record<string, ReportSourceRole>; onSelect: (path: string, role: ReportSourceRole | null) => void;
  onRetain: () => void; disabled: boolean;
}) {
  return <>
    {inventory && <details open className="report-batch-section">
      <summary>Project materials — {inventory.items.length} files inspected</summary>
      <p>Only the linked project folder is inspected. Retaining a copy does not confirm its meaning or approve a result.</p>
      {!inventory.available && <p role="status">{inventory.reason || 'No project folder is available. Use Retain a source above instead.'}</p>}
      {inventory.warnings.length > 0 && <ul>{inventory.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
      {inventory.items.length > 0 && <div className="report-batch-table-wrap"><table>
        <thead><tr><th>Material / relative path</th><th>Role to retain</th><th>Inspection</th></tr></thead>
        <tbody>{inventory.items.map(item => {
          const selectable = item.status === 'candidate' && !!item.file_token && !!item.suggested_role;
          return <tr key={item.relative_path}>
            <td><label className="report-batch-check"><input type="checkbox" disabled={disabled || !selectable}
              aria-label={`Retain ${item.relative_path}`} checked={!!selected[item.relative_path]}
              onChange={event => onSelect(item.relative_path, event.target.checked ? item.suggested_role : null)} />
              <span>{item.relative_path}{item.duplicate_name && <small>Same filename elsewhere — check the full relative path.</small>}</span></label></td>
            <td>{item.status === 'candidate' ? <label><span className="report-batch-sr-only">Role for {item.relative_path}</span>
              <select disabled={disabled || !selected[item.relative_path]} value={selected[item.relative_path] || item.suggested_role || ''}
                onChange={event => onSelect(item.relative_path, event.target.value as ReportSourceRole)}>
                {!item.suggested_role && <option value="">Choose role</option>}
                {roles.map(([role, label]) => <option key={role} value={role}>{label}</option>)}
              </select></label> : '—'}</td>
            <td>{item.status}{item.reason && <small>{item.reason}</small>}</td>
          </tr>;
        })}</tbody>
      </table></div>}
      {inventory.available && <button type="button" disabled={disabled || !Object.keys(selected).length || !inventory.root_token}
        onClick={onRetain}>Retain selected source copies</button>}
    </details>}
    {coverage && <section className="report-batch-section" aria-label="Matrix evidence coverage">
      <h5>Matrix evidence coverage</h5>
      <p>Ready means evidence is available, not a Pass decision. Missing or unconfirmed items stay visible; a new working copy is not a complete or released report.</p>
      {!coverage.has_confirmed_matrix && <p role="alert">A confirmed Matrix is required before step coverage can be established.</p>}
      <p>{coverage.counts.ready || 0} ready · {coverage.counts.missing || 0} missing · {coverage.counts.needs_review || 0} need review · {coverage.counts.not_applicable || 0} not applicable</p>
      <div className="report-batch-table-wrap"><table>
        <thead><tr><th>Group / Step</th><th>Test</th><th>Coverage</th><th>Review / next action</th></tr></thead>
        <tbody>{coverage.rows.map(row => <tr key={`${row.group_id}/${row.row_id}/${row.step_token}`}>
          <td>{row.group_label} / {row.step_token}</td><td>{row.test_item}</td>
          <td>{row.status.replaceAll('_', ' ')}</td><td>{row.reasons.length ? row.reasons.join(' ') : 'No unresolved evidence issue.'}</td>
        </tr>)}</tbody>
      </table></div>
      {coverage.pending_mappings.length > 0 && <div><h5>Decisions awaiting confirmation</h5>
        <ul>{coverage.pending_mappings.map(mapping => <li key={mapping.mapping_id}>{mapping.label}: {mapping.reason || 'Confirm the source and its project applicability in mappings above.'}</li>)}</ul>
      </div>}
    </section>}
  </>;
}
