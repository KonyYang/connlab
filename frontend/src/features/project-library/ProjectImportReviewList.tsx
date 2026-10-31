import { useState } from "react";
import type { LibraryIntakeItem, LibraryIntakePlan, PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { ProjectImportSnapshotDetails } from "./ProjectImportSnapshots";

type Props = {
  plan: LibraryIntakePlan | null;
  snapshots: PortableRestorePlan[];
  selected: string[];
  separate: string[];
  disabled: boolean;
  onToggle: (path: string, checked: boolean) => void;
  onKeepSeparate: (path: string, keep: boolean) => void;
  onResolveSnapshot: (path: string, resolution: PortableResolution) => void;
  onOpenMember: (id: string) => void;
  onSelectReady: () => void;
  onClear: () => void;
};

const labels = { ready: "Ready to Import", conflict: "Needs Review", already_added: "Already Added", unavailable: "Unavailable" };
const pageSize = 20;

function importPurpose(item: LibraryIntakeItem | PortableRestorePlan) {
  if (item.status === "already_added") return "Already in Projects. No files or data will be imported again.";
  if ("resolution" in item) return item.resolution === "keep_as_history"
    ? "Keep a complete historical copy for browsing. The working project stays unchanged."
    : "Restore the project and its saved test data. Review the restored project before continuing testing.";
  if (item.target_member_id) return "Add these files to the existing project for browsing. Existing test data stays unchanged.";
  return "Copy project files for browsing. Complete project information and Matrix setup before continuing testing.";
}

export function ProjectImportReviewList({ plan, snapshots, selected, separate, disabled, onToggle, onKeepSeparate, onResolveSnapshot, onOpenMember, onSelectReady, onClear }: Props) {
  const [filter, setFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [resolving, setResolving] = useState<string | null>(null);
  // Display eligibility only. Original plans/tokens still authorize every import and restore.
  const rows = [
    ...(plan?.items ?? []).map(item => ({ item, snapshot: null, status: item.status === "conflict" && item.can_keep_separate && separate.includes(item.source_path) ? "ready" as const : item.status })),
    ...snapshots.map(item => ({ item, snapshot: item, status: item.blockers.length ? "unavailable" as const : item.status })),
  ];
  const visible = rows.filter(row => filter === "all" || row.status === filter);
  const pages = Math.max(1, Math.ceil(visible.length / pageSize));
  const currentPage = Math.min(page, pages);
  const alreadyAddedCount = rows.filter(row => row.status === "already_added").length;
  return <>
    <h2>{rows.length === 1 ? "Review project" : "Review projects"}</h2>
    <p>{rows.length} found; {selected.length} selected.</p>
    {alreadyAddedCount > 0 && <p role="status">{alreadyAddedCount === rows.length ? "All projects in this preview are already in Projects. Nothing needs to be imported." : "Already added projects will be kept. Import only the projects you select."}</p>}
    {plan?.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}
    {rows.length > 1 && <div className="library-actions">
      <label>Show<select value={filter} disabled={disabled} onChange={event => { setFilter(event.target.value); setPage(1); }}>
        <option value="all">All ({rows.length})</option>
        {Object.entries(labels).map(([key, label]) => <option key={key} value={key}>{label} ({rows.filter(row => row.status === key).length})</option>)}
      </select></label>
      <button type="button" disabled={disabled} onClick={onSelectReady}>Select Ready Projects</button>
      <button type="button" disabled={disabled} onClick={onClear}>Clear Selection</button>
    </div>}
    <div className={`library-table library-import-table${rows.length === 1 ? " library-import-single" : ""}`}>
      <table aria-label="Projects to receive"><thead><tr><th>Select</th><th>Project</th><th>Result</th></tr></thead><tbody>
        {visible.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(({ item, snapshot, status }) => <tr key={item.source_path}>
          <td><input type="checkbox" aria-label={`Select ${item.title}`} disabled={disabled || status !== "ready"} checked={selected.includes(item.source_path)} onChange={event => onToggle(item.source_path, event.target.checked)} /></td>
          <td><strong>{item.ltr_number || "No LTR yet"}</strong><span>{item.title}</span>
            <p className="library-import-purpose">{importPurpose(item)}</p>
            <details><summary>Locations</summary><dl><dt>From</dt><dd>{item.source_path}</dd><dt>To</dt><dd>{item.target_path}</dd></dl></details>
          </td>
          <td><strong>{labels[status]}</strong>
            {snapshot ? <ProjectImportSnapshotDetails plan={snapshot} disabled={disabled} onResolve={onResolveSnapshot} /> : <>
              {item.warnings.map((note, i) => <p key={i}>{note}</p>)}
              {"existing_member_id" in item && item.status === "already_added" && item.existing_member_id && <button type="button" disabled={disabled} aria-label={`Open Existing ${item.title}`} onClick={() => onOpenMember(item.existing_member_id!)}>Open Existing Project</button>}
              {"can_keep_separate" in item && item.can_keep_separate && <div className="library-conflict-actions">
                <button type="button" disabled={disabled} aria-expanded={resolving === item.source_path} aria-label={`Resolve conflict for ${item.title}`} onClick={() => setResolving(resolving === item.source_path ? null : item.source_path)}>{separate.includes(item.source_path) ? "Change Decision" : "Resolve Conflict"}</button>
                {separate.includes(item.source_path) && <p>Keep as a separate project. Existing records stay unchanged.</p>}
                {resolving === item.source_path && <div role="group" aria-label={`Conflict decision for ${item.title}`}>
                  <p>This will keep another complete copy, without merging or replacing the existing project.</p>
                  <div className="library-actions"><button type="button" disabled={disabled} onClick={() => { onKeepSeparate(item.source_path, true); setResolving(null); }}>Keep as a Separate Project</button>
                    <button type="button" disabled={disabled} onClick={() => { onKeepSeparate(item.source_path, false); setResolving(null); }}>Skip This Project</button></div>
                </div>}
              </div>}
            </>}
          </td>
        </tr>)}
      </tbody></table>
    </div>
    {!visible.length && <p>No projects match this filter. Choose All to see the complete selection.</p>}
    {pages > 1 && <nav className="library-actions" aria-label="Project review pages">
      <button type="button" disabled={disabled || currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button>
      <span>Page {currentPage} of {pages}</span>
      <button type="button" disabled={disabled || currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button>
    </nav>}
  </>;
}
