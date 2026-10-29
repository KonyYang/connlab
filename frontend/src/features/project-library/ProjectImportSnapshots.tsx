import type { PortableResolution, PortableRestorePlan } from "../../api/projectLibrary";
import { PortableCoverage, RestoreProtection, resolutionLabels } from "./PortableRestore";

type Props = {
  plans: PortableRestorePlan[];
  selected: string[];
  disabled: boolean;
  confirmation?: boolean;
  onToggle?: (path: string, checked: boolean) => void;
  onResolve?: (path: string, resolution: PortableResolution) => void;
};

export function ProjectImportSnapshots({ plans, selected, disabled, confirmation = false, onToggle, onResolve }: Props) {
  const sources = plans.map(plan => plan.source_path).join("\n");
  const [location, setLocation] = useState({ sources, page: 1 });
  const pages = Math.max(1, Math.ceil(plans.length / 20));
  const page = location.sources === sources ? Math.min(location.page, pages) : 1;
  const visible = confirmation ? plans : plans.slice((page - 1) * 20, page * 20);
  return <div className="library-snapshot-list">{visible.map(plan => {
    const options = !plan.blockers.length ? (plan.resolution_options ?? []).filter(option => option in resolutionLabels) : [];
    return <article key={plan.source_path} className="library-review" aria-label={`Saved project ${plan.title}`}>
      <div className="library-snapshot-heading">
        {!confirmation && <input type="checkbox" aria-label={`Select ${plan.title}`} disabled={disabled || plan.status !== "ready" || Boolean(plan.blockers.length)} checked={selected.includes(plan.source_path)} onChange={event => onToggle?.(plan.source_path, event.target.checked)} />}
        <div><h3>{plan.ltr_number ? `${plan.ltr_number} · ` : ""}{plan.title}</h3><p>{plan.status === "already_added" ? "Already Added" : plan.status === "ready" ? "Ready to Import" : "Needs Review"} · Includes saved test data</p></div>
      </div>
      {plan.warnings.length > 0 && <div><p role="status">{plan.warnings.length} warnings need review. Importing does not fill missing source files.</p><details><summary>Review {plan.warnings.length} {plan.warnings.length === 1 ? "warning" : "warnings"}</summary>{plan.warnings.map((note, index) => <p key={index}>{note}</p>)}</details></div>}
      {plan.blockers.map((note, index) => <p key={index} role="alert">{note}</p>)}
      {plan.resolution === "replace_working_copy" && <div role="alert"><p>The current working copy will be replaced. A complete recovery copy will be saved first.</p><p>Recovery copy: {plan.backup_path}</p></div>}
      {plan.resolution === "keep_as_history" && <p>This copy will be kept for browsing. The current LTR owner stays unchanged.</p>}
      {!confirmation && options.length > 0 && <fieldset className="library-resolution" disabled={disabled}><legend>Choose how to keep this project</legend>{options.map(option => <label key={option}>
        <input type="radio" name={`resolve-${plan.source_path}`} checked={plan.resolution === option} onChange={() => onResolve?.(plan.source_path, option)} />{resolutionLabels[option]}
      </label>)}<p>Both copies stay complete. Individual fields are not merged.</p></fieldset>}
      {plan.status === "conflict" && !plan.resolution && <p role="alert">Review this conflict before importing. No existing project will be overwritten automatically.</p>}
      <PortableCoverage counts={plan.record_counts} fileCount={plan.file_count} label="Saved test data" expanded={false} showFileCount={false} />
      <details><summary>Import Details</summary><RestoreProtection plan={plan} /></details>
    </article>;
  })}{!confirmation && pages > 1 && <nav className="library-actions" aria-label="Saved test data projects">
    <button type="button" aria-label="Previous projects with saved data" disabled={disabled || page <= 1} onClick={() => setLocation({ sources, page: page - 1 })}>Previous</button>
    <span>Page {page} of {pages}</span>
    <button type="button" aria-label="Next projects with saved data" disabled={disabled || page >= pages} onClick={() => setLocation({ sources, page: page + 1 })}>Next</button>
  </nav>}</div>;
}
import { useState } from "react";
