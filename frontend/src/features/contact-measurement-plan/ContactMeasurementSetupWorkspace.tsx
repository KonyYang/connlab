import { useEffect, useRef, useState, type ChangeEvent } from "react";
import type { ContactMeasurementPlanTarget } from "../../api/client";
import { DraftMeasurementPlanWorkbookPanel } from "./DraftMeasurementPlanWorkbookPanel";
import { useContactMeasurementPlanModel } from "./useContactMeasurementPlanModel";

type ContactMeasurementSetupWorkspaceProps = {
  projectId: string;
  onBackToMatrix: () => void;
};

export function ContactMeasurementSetupWorkspace({
  projectId,
  onBackToMatrix,
}: ContactMeasurementSetupWorkspaceProps) {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const model = useContactMeasurementPlanModel({ projectId });
  const [draftWorkbookBusy, setDraftWorkbookBusy] = useState(false);
  const controlsBusy = Boolean(model.busy) || draftWorkbookBusy;

  useEffect(() => {
    if (!model.loading) headingRef.current?.focus();
  }, [model.loading]);

  if (model.loading) {
    return <section className="contact-measurement-setup-page" aria-busy="true">Loading contact measurement setup...</section>;
  }

  return (
    <section className="contact-measurement-setup-page" aria-label="Contact measurement setup">
      <header className="contact-measurement-setup-header">
        <button type="button" onClick={onBackToMatrix}>Back to Matrix</button>
        <div>
          <h2 ref={headingRef} tabIndex={-1}>Contact measurement setup</h2>
          <p>{workspaceLabel(model.workspace?.status, model.workspace?.revision?.revision_sequence)}</p>
        </div>
      </header>
      {model.error ? <p className="contact-measurement-setup-alert is-error" role="alert">{model.error}</p> : null}
      {model.message ? <p className="contact-measurement-setup-alert" role="status">{model.message}</p> : null}
      {model.staleLocalTarget ? (
        <section className="contact-measurement-stale-recovery" aria-label="Stale contact measurement plan recovery">
          <strong>Contact measurement plan changed.</strong>
          <div>
            <button type="button" disabled={Boolean(model.busy)} onClick={() => void model.reloadLatest()}>Reload latest</button>
            <button type="button" disabled={Boolean(model.busy)} onClick={model.discardStaleLocalEdits}>Discard local edits</button>
            <button type="button" disabled={Boolean(model.busy)} onClick={() => void model.reapplySavedEdits()}>Re-apply saved edits</button>
          </div>
        </section>
      ) : null}
      {!model.workspace?.editable_revision_id ? (
        <section className="contact-measurement-setup-empty">
          <p>Open an editable measurement plan to review contact targets.</p>
          <button type="button" disabled={Boolean(model.busy)} onClick={() => void model.openDraft()}>
            Open measurement plan
          </button>
        </section>
      ) : (
        <>
          <section className="contact-measurement-review-band" aria-label="Measurement plan review">
            <span>{`${model.workspace.summary.needs_review_count} changes need review`}</span>
            <button type="button" disabled={controlsBusy} onClick={() => void model.refreshImpacts()}>
              Review changes
            </button>
            <button type="button" disabled={controlsBusy} onClick={() => void model.acceptCompatible()}>
              Accept suggested changes
            </button>
          </section>
          <div className="contact-measurement-setup-grid">
            <section className="contact-measurement-target-list" aria-label="Contact measurement targets">
              <h3>Targets</h3>
              {model.workspace.targets.map((target) => (
                <button
                  key={target.stable_target_key}
                  type="button"
                  className={target.stable_target_key === model.selectedTarget?.stable_target_key ? "is-selected" : ""}
                  disabled={controlsBusy || (model.dirty && target.stable_target_key !== model.selectedTarget?.stable_target_key)}
                  onClick={() => model.selectTarget(target.stable_target_key)}
                >
                  <strong>{target.group_label}</strong>
                  <span>{`${target.test_item} Step ${target.step_sequence}${target.step_suffix_note}`}</span>
                  <span>{target.included ? "Included" : "Excluded"}</span>
                </button>
              ))}
            </section>
            <TargetEditor
              target={model.selectedTarget}
              disabled={controlsBusy}
              onChange={model.updateSelectedTarget}
              onAddCustomFamily={model.addCustomFamily}
              onRemoveCustomFamily={model.removeCustomFamily}
            />
          </div>
          {model.workspace.impacts.length > 0 ? (
            <section className="contact-measurement-impact-list" aria-label="Contact measurement impacts">
              <h3>Review changes</h3>
              {model.workspace.impacts.map((impact) => (
                <div key={impact.impact_subject_key}>
                  <strong>{impact.candidate ? `${impact.candidate.group_label}: ${impact.candidate.test_item}` : "Matrix change"}</strong>
                  <span>{impact.reason ?? impact.category}</span>
                  {impact.candidate && model.selectedTarget ? (
                    <button type="button" disabled={controlsBusy} onClick={() => void model.rebindSelectedTarget(impact.impact_subject_key)}>
                      Rebind selected target
                    </button>
                  ) : null}
                </div>
              ))}
            </section>
          ) : null}
          <DraftMeasurementPlanWorkbookPanel projectId={projectId} revisionId={model.workspace.editable_revision_id} disabled={Boolean(model.busy)} onBusyChange={setDraftWorkbookBusy} />
          <footer className="contact-measurement-setup-actions">
            <button type="button" disabled={!model.dirty || controlsBusy} onClick={model.cancelSelectedTarget}>Cancel local edits</button>
            <button type="button" disabled={!model.dirty || controlsBusy} onClick={() => void model.saveSelectedTarget()}>Save target</button>
            <button type="button" disabled={controlsBusy} onClick={() => void model.saveDraft()}>Save draft</button>
            <button type="button" disabled={controlsBusy || model.workspace.summary.needs_review_count > 0} onClick={() => void model.confirmPlan()}>Confirm measurement plan</button>
          </footer>
        </>
      )}
    </section>
  );
}

function TargetEditor({
  target,
  disabled,
  onChange,
  onAddCustomFamily,
  onRemoveCustomFamily,
}: {
  target: ContactMeasurementPlanTarget | null;
  disabled: boolean;
  onChange: (update: (target: ContactMeasurementPlanTarget) => ContactMeasurementPlanTarget) => void;
  onAddCustomFamily: () => void;
  onRemoveCustomFamily: (familyId: string) => void;
}) {
  if (!target) return <section className="contact-measurement-target-editor"><p>Select a target.</p></section>;
  return (
    <section className="contact-measurement-target-editor" aria-label="Selected contact target">
      <h3>{`${target.group_label}: ${target.test_item}`}</h3>
      <label>
        <input type="checkbox" checked={target.included} disabled={disabled} onChange={(event) => onChange((current) => ({ ...current, included: event.target.checked, exclusion_reason: event.target.checked ? null : current.exclusion_reason }))} />
        Include target
      </label>
      {!target.included ? <label>Exclusion reason<input value={target.exclusion_reason ?? ""} disabled={disabled} onChange={(event) => onChange((current) => ({ ...current, exclusion_reason: event.target.value }))} /></label> : null}
      <p>{target.is_override ? "Manual override" : target.target_review_state.replaceAll("_", " ")}</p>
      <div className="contact-measurement-family-list">
        {target.families.map((family, index) => (
          <div key={family.family_id}>
            <label>
              <input aria-label={`Include ${family.label} contact family`} type="checkbox" checked={family.included} disabled={disabled} onChange={(event) => updateFamily(onChange, index, { included: event.target.checked })} />
              Include family
            </label>
            <label>Label<input aria-label={`${family.label} label`} value={family.label} disabled={disabled} onChange={(event) => updateFamily(onChange, index, { label: event.target.value })} /></label>
            <label>Record label<input aria-label={`${family.label} record label`} value={family.record_label} disabled={disabled} onChange={(event) => updateFamily(onChange, index, { record_label: event.target.value })} /></label>
            <label>Count per sample<input aria-label={`${family.label} count per sample`} type="number" min="0" value={family.count_per_sample} disabled={disabled || !family.included} onChange={(event) => updateFamily(onChange, index, { count_per_sample: numberValue(event) })} /></label>
            <label>Prefix<input aria-label={`${family.label} prefix`} value={family.record_prefix} disabled={disabled} onChange={(event) => updateFamily(onChange, index, { record_prefix: event.target.value })} /></label>
            {family.is_custom ? <button type="button" disabled={disabled} onClick={() => onRemoveCustomFamily(family.family_id)}>Remove custom contact</button> : null}
          </div>
        ))}
      </div>
      <button type="button" disabled={disabled} onClick={onAddCustomFamily}>Add custom contact</button>
      <p>{`Readings per sample: ${target.families.filter((family) => family.included).reduce((sum, family) => sum + family.count_per_sample, 0)}`}</p>
    </section>
  );
}

function updateFamily(
  onChange: (update: (target: ContactMeasurementPlanTarget) => ContactMeasurementPlanTarget) => void,
  index: number,
  patch: Partial<ContactMeasurementPlanTarget["families"][number]>
): void {
  onChange((target) => ({
    ...target,
    families: target.families.map((family, familyIndex) => familyIndex === index ? { ...family, ...patch } : family),
  }));
}

function numberValue(event: ChangeEvent<HTMLInputElement>): number {
  return Math.max(0, Number.parseInt(event.target.value, 10) || 0);
}

function workspaceLabel(status: string | undefined, sequence: number | undefined): string {
  return `Plan ${sequence ?? "-"} ${status?.replaceAll("_", " ") ?? "not started"}`;
}
