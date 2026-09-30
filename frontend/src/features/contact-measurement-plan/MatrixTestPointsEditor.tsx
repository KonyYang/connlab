import type { ReactNode } from "react";
import type {
  MatrixTestPointOverride,
  MatrixTestPointProfile,
} from "../../api/client";
import { pointProfileValidation } from "./projectPointProfileSelectors";
import "../../contact-measurement-plan.css";

const EMPTY_PROFILE: MatrixTestPointProfile = {
  categories: [],
  delta_r_enabled: true,
};

export function matrixTestPointsValidation(
  profile: MatrixTestPointProfile | null,
  overrides: MatrixTestPointOverride[],
  hasCrMatrixStep: boolean,
): string | null {
  if (overrides.length) return "Use project-wide points before confirming this Matrix.";
  if (!profile) return null;
  for (const kind of ["ir", "dwv"] as const) {
    const value = (profile[`${kind}_points_per_sample`] ?? "").trim();
    if (value && (!/^[0-9]{1,5}$/.test(value) || Number(value) < 1 || Number(value) > 8192)) {
      return `${kind.toUpperCase()} test points per sample must be a whole number from 1 to 8192.`;
    }
  }
  const profileError = profile.categories.length ? pointProfileValidation(profile.categories.map((category) => ({
    category_id: null, ...category,
  }))) : null;
  if (profileError) return profileError;
  if (hasCrMatrixStep && profile.categories.length > 0 && !profile.categories.some((category) => category.cr_selected)) {
    return "CR Matrix steps require at least one category selected for CR.";
  }
  return null;
}

type Props = {
  profile: MatrixTestPointProfile | null;
  warning?: string | null;
  overrides: MatrixTestPointOverride[];
  hasCrMatrixStep: boolean;
  readOnly: boolean;
  onProfileChange: (profile: MatrixTestPointProfile) => void;
  onOverridesChange: (overrides: MatrixTestPointOverride[]) => void;
  recordActions?: { llcr: ReactNode; cr: ReactNode };
  electricalCoverage?: { ir: string[]; dwv: string[] };
};

export function MatrixTestPointsEditor({
  profile, warning, overrides, hasCrMatrixStep, readOnly, onProfileChange, onOverridesChange, recordActions, electricalCoverage,
}: Props) {
  const current = profile ?? EMPTY_PROFILE;
  const editableCategories = current.categories.length ? current.categories : [{ prefix: "", point_expression: "", cr_selected: true }];
  const validation = matrixTestPointsValidation(profile, overrides, hasCrMatrixStep);
  const setCategory = (index: number, patch: Partial<MatrixTestPointProfile["categories"][number]>) => {
    onProfileChange({ ...current, categories: editableCategories.map((item, rowIndex) => rowIndex === index ? { ...item, ...patch } : item) });
  };

  return <section className="contact-measurement-summary matrix-test-points-editor" aria-label="Test points">
    <header className="contact-measurement-summary-header"><h3 title="Project point IDs are shared. Any changes here remain a Matrix draft until Confirm Matrix.">Test points</h3></header>
    {warning && !profile ? <p className="contact-measurement-summary-warning" role="status">{warning}</p> : null}
    <div className="project-point-profile-card">
      <header className="project-point-profile-header">
        <h4>LLCR / CR project points</h4>
        <div className="matrix-test-points-header-controls">
          <label className="project-point-profile-delta-r">
            <input type="checkbox" aria-label="Delta R for LLCR" checked={current.delta_r_enabled} disabled={readOnly}
              onChange={(event) => onProfileChange({ ...current, delta_r_enabled: event.target.checked })} />
            <span>ΔR</span>
          </label>
          <div className="matrix-test-points-form-actions">{recordActions?.llcr}{recordActions?.cr}</div>
        </div>
      </header>
      <table className="project-point-profile-table"><thead><tr>
        <th scope="col">Point category</th><th scope="col">Test point IDs</th><th scope="col" className="project-point-profile-cr-cell">CR</th><th scope="col" className="project-point-profile-action">
          <button type="button" className="contact-measurement-button is-compact" disabled={readOnly || current.categories.length >= 256}
            onClick={() => onProfileChange({ ...current, categories: [...current.categories, { prefix: "", point_expression: "", cr_selected: true }] })}>Add row</button>
        </th>
      </tr></thead><tbody>{editableCategories.map((category, index) => <tr key={index}>
        <td><textarea aria-label={`Point category ${index + 1}`} className="project-point-profile-input" rows={1} value={category.prefix} disabled={readOnly}
          onChange={(event) => setCategory(index, { prefix: event.target.value })} /></td>
        <td><textarea aria-label={`Test point IDs ${index + 1}`} className="project-point-profile-input" rows={1} value={category.point_expression} disabled={readOnly}
          placeholder="Example: 1-5, HP7" onChange={(event) => setCategory(index, { point_expression: event.target.value })} /></td>
        <td className="project-point-profile-cr-cell"><input type="checkbox" aria-label={`Include ${category.prefix || `row ${index + 1}`} in CR`} checked={category.cr_selected} disabled={readOnly}
          onChange={(event) => setCategory(index, { cr_selected: event.target.checked })} /></td>
        <td className="project-point-profile-action"><button type="button" aria-label={`Delete point profile row ${category.prefix || index + 1}`} disabled={readOnly}
          onClick={() => onProfileChange({ ...current, categories: current.categories.filter((_, rowIndex) => rowIndex !== index) })}>Remove</button></td>
      </tr>)}</tbody></table>
    </div>
    <div className="project-point-profile-card">
      <header className="project-point-profile-header"><h4>IR / DWV test points</h4></header>
      <p className="contact-measurement-summary-warning">One reading per point per sample. Applies to all selected Matrix steps of the corresponding test. Confirm Matrix to update Fee quantities.</p>
      <div className="contact-measurement-summary-facts">
        {(["ir", "dwv"] as const).map((kind) => <div key={kind}>
          <label>
            <span>{kind.toUpperCase()} test points per sample</span>
            <input type="text" inputMode="numeric" className="project-point-profile-input"
              aria-label={`${kind.toUpperCase()} test points per sample`} disabled={readOnly}
              placeholder="Not set (example: 1)" value={current[`${kind}_points_per_sample`] ?? ""}
              title="Count the actual measurement points, not the connector pins or sample numbers."
              onChange={(event) => onProfileChange({ ...current, [`${kind}_points_per_sample`]: event.target.value })} />
          </label>
          <p>{electricalCoverage?.[kind].length ? electricalCoverage[kind].join("; ") : "No selected Matrix steps."}</p>
          {!current[`${kind}_points_per_sample`]?.trim() && electricalCoverage?.[kind].length ?
            <p className="contact-measurement-summary-warning">Not set — Fee quantities require review.</p> : null}
        </div>)}
      </div>
    </div>
    {overrides.length ? <div className="matrix-test-points-migration" role="alert">
      <p>This Matrix contains previously confirmed or saved Group/step point exceptions. Existing authority stays unchanged until you choose project-wide points and Confirm Matrix.</p>
      <button type="button" className="contact-measurement-button" disabled={readOnly}
        onClick={() => onOverridesChange([])}>Use project-wide points</button>
    </div> : validation ? <p className="contact-measurement-setup-alert is-error" role="alert">{validation}</p> : null}
  </section>;
}
