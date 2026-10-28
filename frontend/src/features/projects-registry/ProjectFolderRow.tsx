import type { ProjectCatalogRow } from "./projectCatalog";
import { catalogIdentifier, catalogTitle } from "./projectCatalog";

export function ProjectFolderRow({ row, onOpenMember, onOpenLinked }: {
  row: Exclude<ProjectCatalogRow, { kind: "registered" }>;
  onOpenMember?: (id: string) => void; onOpenLinked?: (id: string) => void;
}) {
  const title = catalogTitle(row);
  const record = row.kind === "managed" ? row.member : row.record;
  const open = row.kind === "managed" ? onOpenMember : onOpenLinked;
  return <tr className="project-registry-row">
    <td className="project-no registry-project-id-cell" data-label="Project ID">{catalogIdentifier(row)}<span className="registry-temp-badge">{row.kind === "managed" && row.member.is_history ? "Historical Copy" : "Files Only"}</span></td>
    <td className="registry-sample-cell" data-label="Sample Description">{title}<details><summary>Project Location</summary><p>{record.folder_path}</p></details></td>
    <td className="registry-test-item-column registry-test-item-cell" data-label="Test Item">Not recorded</td>
    <td className="registry-status-text registry-status-cell" data-label="Group completion">—</td>
    <td className="registry-next-step registry-next-step-cell" data-label="Estimated completion">Not scheduled</td>
    <td className="registry-action-cell" data-label="Action"><button className="row-action" type="button" disabled={!open} aria-label={`Open ${title}`} onClick={() => row.kind === "managed" ? onOpenMember?.(row.member.member_id) : onOpenLinked?.(row.record.record_id)}>Open</button></td>
  </tr>;
}
