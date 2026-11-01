import type { LibraryIntakeItem } from "../../api/projectLibrary";

type Props = {
  item: LibraryIntakeItem;
  disabled: boolean;
  keep: boolean;
  skipped: boolean;
  onKeep: (keep: boolean) => void;
  onChange: () => void;
  onFilesOnly?: () => void;
};

export function ProjectImportDecision({ item, disabled, keep, skipped, onKeep, onChange, onFilesOnly }: Props) {
  if (item.source_state === "upgrade_required") return <p role="alert">Update ConnLab before importing this project.</p>;
  if (item.source_state === "incomplete" && item.status !== "already_added") return <div>
    <p>This ConnLab project has no data snapshot. Export it from the original computer to restore its data.</p>
    {onFilesOnly && <button type="button" disabled={disabled} onClick={onFilesOnly}>Import Files Only</button>}
  </div>;
  if (skipped || keep) return <p>{skipped ? "Skipped." : "Keep another copy. The existing project stays unchanged."}{" "}<button type="button" className="library-text-action" disabled={disabled} onClick={onChange}>Change Decision</button></p>;
  if (item.status === "conflict") return <div>
    <p>{item.can_keep_separate ? "A different copy of this project already exists." : "Check this project before importing. See Details for the required action."}</p>
    {item.can_keep_separate && <div className="library-actions">
      <button type="button" disabled={disabled} onClick={() => onKeep(true)}>Keep Another Copy</button>
      <button type="button" disabled={disabled} onClick={() => onKeep(false)}>Skip</button>
    </div>}
  </div>;
  if (item.status === "unavailable") return <p role="alert">This project could not be checked. See Details, then choose it again.</p>;
  return null;
}
