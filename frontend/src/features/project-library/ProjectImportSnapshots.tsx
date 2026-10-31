import type { PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { PortableCoverage, RestoreProtection, resolutionLabels } from "./PortableRestore";

type Props = {
  plan: PortableRestorePlan;
  disabled: boolean;
  onResolve: (path: string, resolution: PortableResolution) => void;
};

export function ProjectImportSnapshotDetails({ plan, disabled, onResolve }: Props) {
  const options = !plan.blockers.length ? (plan.resolution_options ?? []).filter(option => option in resolutionLabels) : [];
  return <div className="library-snapshot-details">
      {plan.warnings.length > 0 && <div><p role="status">{plan.warnings.length} warnings need review. Importing does not fill missing source files.</p><details><summary>Review {plan.warnings.length} {plan.warnings.length === 1 ? "warning" : "warnings"}</summary>{plan.warnings.map((note, index) => <p key={index}>{note}</p>)}</details></div>}
      {plan.blockers.map((note, index) => <p key={index} role="alert">{note}</p>)}
      {plan.resolution === "replace_working_copy" && <div role="alert"><p>The current working copy will be replaced. A complete recovery copy will be saved first.</p><p>Recovery copy: {plan.backup_path}</p></div>}
      {plan.resolution === "keep_as_history" && <p>This copy will be kept for browsing. The current LTR owner stays unchanged.</p>}
      {options.length > 0 && <fieldset className="library-resolution" disabled={disabled}><legend>Choose how to keep this project</legend>{options.map(option => <label key={option}>
        <input type="radio" name={`resolve-${plan.source_path}`} checked={plan.resolution === option} onChange={() => onResolve(plan.source_path, option)} />{resolutionLabels[option]}
      </label>)}<p>Both copies stay complete. Individual fields are not merged.</p></fieldset>}
      {plan.status === "conflict" && !plan.resolution && <p role="alert">Review this conflict before importing. No existing project will be overwritten automatically.</p>}
      <PortableCoverage counts={plan.record_counts} fileCount={plan.file_count} label="Saved test data" expanded={false} showFileCount={false} />
      <details><summary>Import Details</summary><RestoreProtection plan={plan} /></details>
  </div>;
}
