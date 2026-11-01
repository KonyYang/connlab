import type { PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { PortableCoverage, RestoreProtection } from "./PortableRestore";

type Props = { plan: PortableRestorePlan; disabled: boolean; onResolve: (path: string, resolution?: PortableResolution) => void; onSkip?: () => void };
const choices: Record<PortableResolution, string> = { replace_working_copy: "Use Imported Version", keep_as_history: "Keep Another Copy" };
export function ProjectImportSnapshotDetails({ plan, disabled, onResolve, onSkip }: Props) {
  const options = !plan.blockers.length ? (plan.resolution_options ?? []).filter(option => option in choices) : [];
  const conflict = plan.status === "conflict" || Boolean(plan.resolution);
  return <div className="library-snapshot-details">
    {plan.blockers.length > 0 && <p role="alert">{plan.blockers.some(note => note.startsWith("Update ConnLab")) ? "Update ConnLab before importing this project." : "Saved project data could not be verified. Export this project again from the original computer."}</p>}
    {plan.status === "conflict" && !plan.blockers.length && <>
      <p>This project has different data. View the differences, then choose which copy to keep.</p>
      <div className="library-actions">{options.map(option => <button key={option} type="button" disabled={disabled} onClick={() => onResolve(plan.source_path, option)}>{choices[option]}</button>)}
        {onSkip && <button type="button" disabled={disabled} onClick={onSkip}>Skip</button>}
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
