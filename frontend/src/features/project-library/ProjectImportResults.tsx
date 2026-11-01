import { useState } from "react";
import type { LibraryBatch } from "../../api/projectLibrary";

export type ImportOutcomeKind = "files" | "restored" | "history" | "existing_files";
export type ImportResultDetails = { ltrNumber: string | null; kind?: ImportOutcomeKind; warnings: string[] };
const guidance: Record<ImportOutcomeKind, { summary: string; next: string }> = {
  files: { summary: "Project files imported.", next: "Open the project to review files and complete missing project information and Matrix setup before testing." },
  restored: { summary: "Project and saved test data restored.", next: "Open the project to review its data and continue testing." },
  history: { summary: "Historical copy saved for browsing.", next: "Open the project to browse this copy. The current working project is unchanged." },
  existing_files: { summary: "Files added to the existing project.", next: "Open the project to review the added files. Existing test data stays unchanged." },
};

type Props = {
  batch: LibraryBatch;
  titlesBySource: Record<string, string>;
  detailsBySource?: Record<string, ImportResultDetails>;
  busy: boolean;
  onOpenMember: (id: string, batchId?: string) => void;
  onViewLibrary: () => void;
  onRefresh: () => void;
  onResume: () => void;
  onReceiveMore: () => void;
  heading?: string;
};

const pageSize = 20;
const needsAttention = (status: string) => status === "failed" || status === "review";

export function ProjectImportResults({ batch, titlesBySource, detailsBySource = {}, busy, onOpenMember, onViewLibrary, onRefresh, onResume, onReceiveMore, heading = "Import Results" }: Props) {
  const [location, setLocation] = useState({ batchId: batch.batch_id, page: 1 });
  const items = [...batch.items].sort((a, b) => Number(needsAttention(b.status)) - Number(needsAttention(a.status)));
  const pages = Math.max(1, Math.ceil(items.length / pageSize));
  const page = location.batchId === batch.batch_id ? Math.min(location.page, pages) : 1;
  const running = batch.status === "running";
  const singleSuccess = items.length === 1 && batch.status === "completed" && items[0].status === "added" && Boolean(items[0].member_id);
  return <section className="library-panel" aria-label="Import results">
    <h2>{heading}</h2>
    <p role="status">{singleSuccess ? "Import complete." : `${batch.counts.added} added; ${batch.counts.already_added} already added; ${batch.counts.review} need review; ${batch.counts.failed} failed.`}</p>
    {(running || batch.status === "interrupted") && <div className="library-actions">
      {running && <button type="button" disabled={busy} onClick={onRefresh}>Refresh Batch Status</button>}
      <button type="button" className="primary-action" disabled={busy} onClick={onResume}>Resume Batch</button>
    </div>}
    {items.slice((page - 1) * pageSize, page * pageSize).map(item => {
      // A recovered batch has no preview titles. The basename is display-only; member IDs still own navigation.
      const title = titlesBySource[item.source_path] || item.source_path.replace(/[\\/]+$/, "").split(/[\\/]/).pop() || "Project";
      const details = detailsBySource[item.source_path];
      const outcome = item.status === "added" && details?.kind ? guidance[details.kind] : undefined;
      return <div key={item.source_path} className="library-result">
        <h3>{details?.ltrNumber && <><span className="library-result-ltr">{details.ltrNumber}</span>{" "}</>}<span>{title}</span></h3>
        {outcome && <><p>{outcome.summary}</p><p>{outcome.next}</p></>}
        {item.status !== "added" && <p>{item.message}</p>}
        {details && details.warnings.length > 0 && <details className="library-result-issues" open>
          <summary>{details.warnings.length} {details.warnings.length === 1 ? "item needs" : "items need"} review</summary>
          <ul>{details.warnings.map(note => <li key={note}>{note}</li>)}</ul>
        </details>}
        {item.member_id && <button type="button" className={singleSuccess ? "primary-action" : undefined} aria-label={`Open ${title}`} disabled={busy || running} onClick={() => onOpenMember(item.member_id!)}>Open Project</button>}
        <details><summary>Source Location</summary><p>{item.source_path}</p></details>
      </div>;
    })}
    {pages > 1 && <nav className="library-actions" aria-label="Import result pages">
      <button type="button" disabled={busy || page <= 1} onClick={() => setLocation({ batchId: batch.batch_id, page: page - 1 })}>Previous</button>
      <span>Page {page} of {pages}</span>
      <button type="button" disabled={busy || page >= pages} onClick={() => setLocation({ batchId: batch.batch_id, page: page + 1 })}>Next</button>
    </nav>}
    <div className="library-actions library-result-footer">
      <button type="button" disabled={busy || running} onClick={() => onViewLibrary()}>View Projects</button>
      <button type="button" className="library-text-action" disabled={busy || running} onClick={onReceiveMore}>Import More</button>
    </div>
  </section>;
}
