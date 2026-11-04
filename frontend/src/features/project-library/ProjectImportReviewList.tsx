import { useState } from "react";
import type { LibraryIntakeItem, LibraryIntakePlan, PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { ProjectImportSnapshotDetails } from "./ProjectImportSnapshots";
import { ProjectImportDecision } from "./ProjectImportDecision";
import { intakeReviewKey } from "./projectImportReview";

type Props = {
  plan: LibraryIntakePlan | null;
  snapshots: PortableRestorePlan[];
  selected: string[];
  separate: string[];
  disabled: boolean;
  onToggle: (path: string, checked: boolean) => void;
  onKeepSeparate: (path: string, keep: boolean) => void;
  onResolveSnapshot: (path: string, resolution?: PortableResolution) => void;
  onOpenMember: (id: string) => void;
  onSelectReady: () => void;
  onClear: () => void;
  onFilesOnly?: (path: string) => void;
};
const labels = { ready: "Ready", conflict: "Choose an action", already_added: "Already exists", unavailable: "Cannot import" };
const pageSize = 20;
function importPurpose(item: LibraryIntakeItem | PortableRestorePlan) {
  if (item.status === "already_added") return "Already exists. Open the project to continue.";
  if ("resolution" in item) return "Restore existing project data and continue working.";
  if (item.source_state === "files_only") return "Import files only. Existing ConnLab test data will not be restored.";
  if (item.source_state === "local_project") return "Keep the existing project data and use the imported working folder.";
  if (item.target_member_id) return "Add these files to the existing project. Existing test data stays unchanged.";
  return "Import existing files. Project information can be completed later.";
}
export function ProjectImportReviewList({ plan, snapshots, selected, separate, disabled, onToggle, onKeepSeparate, onResolveSnapshot, onOpenMember, onSelectReady, onClear, onFilesOnly }: Props) {
  const [filter, setFilter] = useState("all"), [page, setPage] = useState(1);
  const [skipped, setSkipped] = useState<string[]>([]);
  const rows = [
    ...(plan?.items ?? []).map(item => ({ item, snapshot: null, status: item.status === "conflict" && item.can_keep_separate && separate.includes(item.source_path) ? "ready" as const : item.status })),
    ...snapshots.map(item => ({ item, snapshot: item, status: item.blockers.length ? "unavailable" as const : item.status })),
  ];
  const single = rows.length === 1;
  const visible = rows.filter(row => filter === "all" || row.status === filter);
  const pages = Math.max(1, Math.ceil(visible.length / pageSize)), currentPage = Math.min(page, pages);
  function skip(item: LibraryIntakeItem | PortableRestorePlan) { setSkipped(values => [...new Set([...values, intakeReviewKey(item)])]); onToggle(item.source_path, false); }
  function content({ item, snapshot, status }: typeof rows[number]) {
    const decisionKey = intakeReviewKey(item), isSkipped = skipped.includes(decisionKey);
    const already = status === "already_added";
    const project = <>
      <strong>{item.ltr_number || "No LTR yet"}</strong><h3>{item.title}</h3>
      {(item.status === "ready" && !("resolution" in item && item.resolution) || already) && <p className="library-import-purpose">{importPurpose(item)}</p>}
    </>;
    const decision = <>
      {snapshot ? isSkipped ? <p>Import cancelled. <button type="button" disabled={disabled} onClick={() => setSkipped(values => values.filter(key => key !== decisionKey))}>Review Again</button></p>
        : <ProjectImportSnapshotDetails plan={snapshot} disabled={disabled} onResolve={onResolveSnapshot} onSkip={() => skip(item)} />
        : <>
          <ProjectImportDecision item={item} disabled={disabled} keep={separate.includes(item.source_path)} skipped={isSkipped}
            onKeep={keep => { if (keep) setSkipped(values => values.filter(key => key !== decisionKey)); else skip(item); onKeepSeparate(item.source_path, keep); }}
            onChange={() => { setSkipped(values => values.filter(key => key !== decisionKey)); onKeepSeparate(item.source_path, false); }}
            onFilesOnly={onFilesOnly ? () => onFilesOnly(item.source_path) : undefined} />
          <details><summary>{item.status === "conflict" && item.can_keep_separate ? "View Differences" : "Details"}</summary>
            {item.differences?.map(note => <p key={note}>{note}</p>)}
            {item.warnings.map((note, index) => <p key={index}>{note}</p>)}
            <dl><dt>Source</dt><dd>{item.source_path}</dd><dt>Save location</dt><dd>{item.target_path}</dd></dl>
          </details>
        </>}
      {already && item.existing_member_id && <button type="button" className="primary-action" disabled={disabled} aria-label={`Open Existing ${item.title}`} onClick={() => onOpenMember(item.existing_member_id!)}>Open Project</button>}
    </>;
    return single ? <article key={item.source_path} className="library-import-project" aria-label="Project to import">{project}{decision}</article>
      : <tr key={item.source_path}><td><input type="checkbox" aria-label={`Select ${item.title}`} disabled={disabled || status !== "ready"} checked={selected.includes(item.source_path)} onChange={event => { if (event.target.checked) setSkipped(values => values.filter(key => key !== decisionKey)); onToggle(item.source_path, event.target.checked); }} /></td><td>{project}</td><td>{decision}</td></tr>;
  }
  return <>
    <h2>{single ? "Review project" : "Review projects"}</h2>
    {!single && <>
      <p>{rows.length} found; {selected.length} selected.</p>
      {rows.every(row => row.status === "already_added") && <p role="status">Nothing needs to be imported. Open an existing project to continue.</p>}
      <div className="library-actions"><label>Show<select value={filter} disabled={disabled} onChange={event => { setFilter(event.target.value); setPage(1); }}>
        <option value="all">All ({rows.length})</option>{Object.entries(labels).map(([key, label]) => <option key={key} value={key}>{label} ({rows.filter(row => row.status === key).length})</option>)}
      </select></label><button type="button" disabled={disabled} onClick={() => { setSkipped([]); onSelectReady(); }}>Select Ready Projects</button><button type="button" disabled={disabled} onClick={onClear}>Clear Selection</button></div>
    </>}
    {plan?.warnings.length ? <details><summary>Details</summary>{plan.warnings.map((note, index) => <p key={index}>{note}</p>)}</details> : null}
    {single ? rows.map(content) : <div className="library-table library-import-table"><table aria-label="Projects to receive"><thead><tr><th>Select</th><th>Project</th><th>Action</th></tr></thead><tbody>{visible.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(content)}</tbody></table></div>}
    {!visible.length && <p>No projects match this filter. Choose All to see the complete selection.</p>}
    {pages > 1 && <nav className="library-actions" aria-label="Project review pages"><button type="button" disabled={disabled || currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage} of {pages}</span><button type="button" disabled={disabled || currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button></nav>}
  </>;
}
