import type { PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { PortableCoverage, RestoreProtection } from "./PortableRestore";

type Props = { plan: PortableRestorePlan; disabled: boolean; onResolve: (path: string, resolution?: PortableResolution) => void; onSkip?: () => void };
export function ProjectImportSnapshotDetails({ plan, disabled, onResolve, onSkip }: Props) {
  const canReplace = !plan.blockers.length && (plan.resolution_options ?? []).includes("replace_working_copy");
  const conflict = plan.status === "conflict" || Boolean(plan.resolution);
  return <div className="library-snapshot-details">
    {plan.blockers.length > 0 && <p role="alert">{plan.blockers.some(note => note.startsWith("Update ConnLab")) ? "Update ConnLab before importing this project." : "Saved project data could not be verified. Export this project again from the original computer."}</p>}
    {plan.status === "conflict" && !plan.blockers.length && <>
      <p>{canReplace
        ? "This is the same project with different saved data. Replacing it will save a complete recovery copy of the current project first."
        : "This folder is not verified as the same project, so it cannot replace the existing project."}</p>
      <div className="library-actions">
        {canReplace && <button type="button" disabled={disabled} onClick={() => onResolve(plan.source_path, "replace_working_copy")}>Replace Existing Project</button>}
        {onSkip && <button type="button" disabled={disabled} onClick={onSkip}>Cancel Import</button>}
      </div>
    </>}
    {plan.resolution === "replace_working_copy" && <p role="alert">The current working copy will be replaced. A complete recovery copy will be saved first: {plan.backup_path}</p>}
    {plan.resolution === "keep_as_history" && <p>Keep this copy for browsing. The current working project stays unchanged.</p>}
    {plan.resolution && <button type="button" className="library-text-action" disabled={disabled} onClick={() => onResolve(plan.source_path)}>Change Decision</button>}
    <details><summary>{conflict ? "View Differences" : "Details"}</summary>
      {plan.differences?.map(note => <p key={note}>{note}</p>)}
      {plan.warnings.map((note, index) => <p key={index}>{note}</p>)}
      {plan.blockers.map((note, index) => <p key={index}>{note}</p>)}
      <PortableCoverage counts={plan.record_counts} fileCount={plan.file_count} label="Saved test data" expanded={false} showFileCount={false} />
      <RestoreProtection plan={plan} />
    </details>
  </div>;
}
