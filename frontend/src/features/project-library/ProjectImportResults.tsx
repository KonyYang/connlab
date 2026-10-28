import { useState } from "react";
import type { LibraryBatch } from "../../api/projectLibrary";

type Props = {
  batch: LibraryBatch;
  titlesBySource: Record<string, string>;
  busy: boolean;
  onOpenMember: (id: string, batchId?: string) => void;
  onViewLibrary: (batchId: string) => void;
  onRefresh: () => void;
  onResume: () => void;
  onReceiveMore: () => void;
  heading?: string;
};

const pageSize = 20;
const needsAttention = (status: string) => status === "failed" || status === "review";

export function ProjectImportResults({ batch, titlesBySource, busy, onOpenMember, onViewLibrary, onRefresh, onResume, onReceiveMore, heading = "3. Receiving Result" }: Props) {
  const [location, setLocation] = useState({ batchId: batch.batch_id, page: 1 });
  const items = [...batch.items].sort((a, b) => Number(needsAttention(b.status)) - Number(needsAttention(a.status)));
  const pages = Math.max(1, Math.ceil(items.length / pageSize));
  const page = location.batchId === batch.batch_id ? Math.min(location.page, pages) : 1;
  const running = batch.status === "running";
  return <section className="library-panel" aria-label="Receiving result">
    <h2>{heading}</h2>
    <p role="status">{batch.counts.added} added; {batch.counts.already_added} already added; {batch.counts.review} need review; {batch.counts.failed} failed.</p>
    <div className="library-actions">
      {running && <button type="button" disabled={busy} onClick={onRefresh}>Refresh Batch Status</button>}
      {batch.status === "interrupted" && <button type="button" className="primary-action" disabled={busy} onClick={onResume}>Resume Batch</button>}
      <button type="button" disabled={busy || running || batch.counts.added === 0} onClick={() => onViewLibrary(batch.batch_id)}>View Added Projects</button>
      <button type="button" disabled={busy || running} onClick={onReceiveMore}>Receive More Projects</button>
    </div>
    {items.slice((page - 1) * pageSize, page * pageSize).map(item => {
      // A recovered batch has no preview titles. The basename is display-only; member IDs still own navigation.
      const title = titlesBySource[item.source_path] || item.source_path.replace(/[\\/]+$/, "").split(/[\\/]/).pop() || "Project";
      return <div key={item.source_path} className="library-result">
        <strong>{title}</strong>
        {item.status !== "added" && <p>{item.message}</p>}
        <details><summary>Source Location</summary><p>{item.source_path}</p></details>
        {item.member_id && <button type="button" disabled={busy || running} onClick={() => onOpenMember(item.member_id!, item.status === "added" ? batch.batch_id : undefined)}>Open {title}</button>}
      </div>;
    })}
    {pages > 1 && <nav className="library-actions" aria-label="Import result pages">
      <button type="button" disabled={busy || page <= 1} onClick={() => setLocation({ batchId: batch.batch_id, page: page - 1 })}>Previous</button>
      <span>Page {page} of {pages}</span>
      <button type="button" disabled={busy || page >= pages} onClick={() => setLocation({ batchId: batch.batch_id, page: page + 1 })}>Next</button>
    </nav>}
  </section>;
}
