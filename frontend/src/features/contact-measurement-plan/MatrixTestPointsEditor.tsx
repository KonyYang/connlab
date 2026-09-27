import { useState, type ReactNode } from "react";
import type {
  MatrixTestPointOverride,
  MatrixTestPointProfile,
} from "../../api/client";
import {
  parsePointExpression,
  pointProfileValidation,
} from "./projectPointProfileSelectors";
import "../../contact-measurement-plan.css";

export type MatrixTestPointStepOption = {
  draftGroupId: string;
  draftRowId: string;
  stepSequence: number;
  stepSuffixNote: string;
  recordType: "LLCR" | "CR";
  label: string;
};

const EMPTY_PROFILE: MatrixTestPointProfile = {
  categories: [{ prefix: "", point_expression: "", cr_selected: true }],
  delta_r_enabled: true,
};

function stepKey(option: Pick<MatrixTestPointStepOption, "draftGroupId" | "draftRowId" | "stepSequence" | "stepSuffixNote">): string {
  return JSON.stringify([option.draftGroupId, option.draftRowId, option.stepSequence, option.stepSuffixNote]);
}

function overrideKey(override: MatrixTestPointOverride): string {
  return JSON.stringify([override.draft_group_id, override.draft_row_id, override.step_sequence, override.step_suffix_note]);
}

export function matrixTestPointsValidation(
  profile: MatrixTestPointProfile | null,
  overrides: MatrixTestPointOverride[],
  stepOptions: MatrixTestPointStepOption[],
): string | null {
  if (!profile) return overrides.length ? "Set project Test point IDs before adding step exceptions." : null;
  const profileError = pointProfileValidation(profile.categories.map((category) => ({
    category_id: null, ...category,
  })));
  if (profileError) return profileError;
  if (stepOptions.some((option) => option.recordType === "CR") &&
      !profile.categories.some((category) => category.cr_selected)) {
    return "CR Matrix steps require at least one category selected for CR.";
  }
  const byPrefix = new Map(profile.categories.map((category) => [
    category.prefix.trim().toLowerCase(), category,
  ]));
  const availableSteps = new Map(stepOptions.map((option) => [stepKey(option), option]));
  const seenSteps = new Set<string>();
  for (const override of overrides) {
    const key = overrideKey(override);
    const option = availableSteps.get(key);
    if (!option) return "A Test point exception refers to a removed or non-LLCR/CR Matrix step.";
    if (seenSteps.has(key)) return "A Matrix step has more than one Test point exception.";
    seenSteps.add(key);
    if (!override.categories.length) return "Select at least one point category for each exception.";
    const seenCategories = new Set<string>();
    for (const category of override.categories) {
      const prefix = category.prefix.trim().toLowerCase();
      const shared = byPrefix.get(prefix);
      if (!shared || seenCategories.has(prefix)) return "Exception categories must be unique project Test point categories.";
      seenCategories.add(prefix);
      if (option.recordType === "CR" && !shared.cr_selected) return "CR exceptions may only use CR-enabled categories.";
      const points = parsePointExpression(category.point_expression);
      const sharedPoints = parsePointExpression(shared.point_expression);
      if (!points || !sharedPoints || points.some((point) => !sharedPoints.includes(point))) {
        return "Exception Test point IDs must be a subset of the project category.";
      }
    }
  }
  return null;
}

type Props = {
  profile: MatrixTestPointProfile | null;
  warning?: string | null;
  overrides: MatrixTestPointOverride[];
  stepOptions: MatrixTestPointStepOption[];
  readOnly: boolean;
  onProfileChange: (profile: MatrixTestPointProfile) => void;
  onOverridesChange: (overrides: MatrixTestPointOverride[]) => void;
  recordActions?: { llcr: ReactNode; cr: ReactNode };
};

export function MatrixTestPointsEditor({
  profile, warning, overrides, stepOptions, readOnly, onProfileChange, onOverridesChange, recordActions,
}: Props) {
  const current = profile ?? EMPTY_PROFILE;
  const [selectedStepKey, setSelectedStepKey] = useState("");
  const remainingSteps = stepOptions.filter((option) => !overrides.some((override) => overrideKey(override) === stepKey(option)));
  const validation = matrixTestPointsValidation(profile, overrides, stepOptions);
  const llcrCount = profile?.categories.reduce((total, category) => total + (parsePointExpression(category.point_expression)?.length ?? 0), 0) ?? 0;
  const crCount = profile?.categories.reduce((total, category) => total + (category.cr_selected ? parsePointExpression(category.point_expression)?.length ?? 0 : 0), 0) ?? 0;
  const setCategory = (index: number, patch: Partial<MatrixTestPointProfile["categories"][number]>) => {
    onProfileChange({ ...current, categories: current.categories.map((item, rowIndex) => rowIndex === index ? { ...item, ...patch } : item) });
  };
  const setOverride = (index: number, next: MatrixTestPointOverride) => {
    onOverridesChange(overrides.map((item, rowIndex) => rowIndex === index ? next : item));
  };

  return <section className="contact-measurement-summary matrix-test-points-editor" aria-label="Test points">
    <header className="contact-measurement-summary-header"><h3>Test points</h3></header>
    <p>Project point IDs are shared. Any changes here remain a Matrix draft until Confirm Matrix.</p>
    {warning && !profile ? <p className="contact-measurement-summary-warning" role="status">{warning}</p> : null}
    <div className="project-point-profile-card">
      <header className="project-point-profile-header">
        <h4>LLCR / CR project points</h4>
        <label className="project-point-profile-delta-r">
          <input type="checkbox" aria-label="Delta R for LLCR" checked={current.delta_r_enabled} disabled={readOnly}
            onChange={(event) => onProfileChange({ ...current, delta_r_enabled: event.target.checked })} />
          <span>ΔR</span>
        </label>
      </header>
      <table className="project-point-profile-table"><thead><tr>
        <th scope="col">Point category</th><th scope="col">Test point IDs</th><th scope="col" className="project-point-profile-cr-cell">CR</th><th scope="col" className="project-point-profile-action">
          <button type="button" className="contact-measurement-button is-compact" disabled={readOnly || current.categories.length >= 256}
            onClick={() => onProfileChange({ ...current, categories: [...current.categories, { prefix: "", point_expression: "", cr_selected: true }] })}>Add row</button>
        </th>
      </tr></thead><tbody>{current.categories.map((category, index) => <tr key={index}>
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
    {validation ? <p className="contact-measurement-setup-alert is-error" role="alert">{validation}</p> : null}
    <div className="matrix-test-points-exceptions">
      <h4>Group / step exceptions</h4>
      <p>Only enter points actually tested at a step; other steps keep the project points.</p>
      {overrides.map((override, index) => {
        const option = stepOptions.find((item) => stepKey(item) === overrideKey(override));
        const eligible = current.categories.filter((item) => option?.recordType !== "CR" || item.cr_selected);
        return <div className="matrix-test-points-exception" key={overrideKey(override)}>
          <div className="contact-measurement-summary-header"><strong>{option?.label ?? "Removed Matrix step"}</strong>
            <button type="button" disabled={readOnly} onClick={() => onOverridesChange(overrides.filter((_, itemIndex) => itemIndex !== index))}>Remove exception</button></div>
          {override.categories.map((category, categoryIndex) => <div className="matrix-test-points-exception-row" key={categoryIndex}>
            <select aria-label={`${option?.label ?? "Step"} category ${categoryIndex + 1}`} value={category.prefix} disabled={readOnly}
              onChange={(event) => setOverride(index, { ...override, categories: override.categories.map((item, rowIndex) => rowIndex === categoryIndex ? { prefix: event.target.value, point_expression: "" } : item) })}>
              {eligible.map((item) => <option key={item.prefix} value={item.prefix}>{item.prefix}</option>)}
            </select>
            <input aria-label={`${option?.label ?? "Step"} Test point IDs ${categoryIndex + 1}`} value={category.point_expression} disabled={readOnly}
              placeholder="Only tested IDs" onChange={(event) => setOverride(index, { ...override, categories: override.categories.map((item, rowIndex) => rowIndex === categoryIndex ? { ...item, point_expression: event.target.value } : item) })} />
            <button type="button" disabled={readOnly} onClick={() => setOverride(index, { ...override, categories: override.categories.filter((_, rowIndex) => rowIndex !== categoryIndex) })}>Remove category</button>
          </div>)}
          <button type="button" disabled={readOnly || eligible.length === override.categories.length} onClick={() => {
            const next = eligible.find((item) => !override.categories.some((category) => category.prefix === item.prefix));
            if (next) setOverride(index, { ...override, categories: [...override.categories, { prefix: next.prefix, point_expression: "" }] });
          }}>Add category</button>
        </div>;
      })}
      <div className="matrix-test-points-exception-add">
        <select aria-label="Group and step for Test point exception" value={selectedStepKey} disabled={readOnly || !profile || remainingSteps.length === 0}
          onChange={(event) => setSelectedStepKey(event.target.value)}>
          <option value="">Choose Group / step</option>
          {remainingSteps.map((option) => <option key={stepKey(option)} value={stepKey(option)}>{option.label}</option>)}
        </select>
        <button type="button" disabled={readOnly || !profile || !selectedStepKey} onClick={() => {
          const option = remainingSteps.find((item) => stepKey(item) === selectedStepKey);
          const first = current.categories.find((item) => option?.recordType !== "CR" || item.cr_selected);
          if (!option || !first) return;
          onOverridesChange([...overrides, {
            draft_group_id: option.draftGroupId, draft_row_id: option.draftRowId,
            step_sequence: option.stepSequence, step_suffix_note: option.stepSuffixNote,
            categories: [{ prefix: first.prefix, point_expression: "" }],
          }]);
          setSelectedStepKey("");
        }}>Add step exception</button>
      </div>
    </div>
    <dl className="contact-measurement-summary-points">
      <div><dt>LLCR</dt><dd>{profile ? `${llcrCount} points / sample · ΔR ${profile.delta_r_enabled ? "on" : "off"}` : "Not set"}</dd>{recordActions?.llcr}</div>
      <div><dt>CR</dt><dd>{profile ? `${crCount} points / sample` : "Not set"}</dd>{recordActions?.cr}</div>
      <div><dt>IR</dt><dd>Not set</dd></div><div><dt>DWV</dt><dd>Not set</dd></div>
    </dl>
  </section>;
}
