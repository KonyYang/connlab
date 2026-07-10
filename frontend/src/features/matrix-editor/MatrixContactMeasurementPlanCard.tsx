import type { MatrixStepQuantityItem } from "../../api/client";
import type {
  ContactMeasurementKind,
  ContactPlanProfiles,
} from "./matrixContactMeasurementPlanSelectors";
import {
  buildContactPlanTargets,
  deriveReadingsPerSample,
  validateContactPlanProfiles,
} from "./matrixContactMeasurementPlanSelectors";

type MatrixContactMeasurementPlanCardProps = {
  items: MatrixStepQuantityItem[];
  profiles: ContactPlanProfiles;
  groupLabels: Record<string, string>;
  disabled: boolean;
  workbookDisabled?: boolean;
  saving: boolean;
  message: string | null;
  error: string | null;
  onFamilyCountChange: (kind: ContactMeasurementKind, familyId: string, value: string) => void;
  onFamilyIncludedChange: (
    kind: ContactMeasurementKind,
    familyId: string,
    included: boolean
  ) => void;
  onFamilyLabelChange: (kind: ContactMeasurementKind, familyId: string, value: string) => void;
  onFamilyPrefixChange: (kind: ContactMeasurementKind, familyId: string, value: string) => void;
  onAddCustomFamily: (kind: ContactMeasurementKind) => void;
  onRemoveCustomFamily: (kind: ContactMeasurementKind, familyId: string) => void;
  onTargetIncludedChange: (
    item: MatrixStepQuantityItem,
    included: boolean,
    exclusionReason: string
  ) => void;
  onTargetExclusionReasonChange: (item: MatrixStepQuantityItem, value: string) => void;
  onApply: () => void;
  onSave: () => void;
  workbook?: {
    busy: "preview" | "generate" | "download" | null;
    preview: {
      status: "ready" | "blocked" | "review_required" | "empty";
      row_count: number;
      sections: Array<{ group_label: string; source_step: string; record_type: string }>;
      diagnostics?: Array<{
        code: string;
        first_family_id?: string | null;
        first_family_label?: string | null;
        second_family_id?: string | null;
        second_family_label?: string | null;
      }>;
    } | null;
    generated: { file_name: string } | null;
    error: string | null;
    canGenerate: boolean;
    onPreview: () => void;
    onGenerate: () => void;
    onDownload: () => void;
  };
};

const PROFILE_LABELS: Record<ContactMeasurementKind, string> = {
  llcr: "LLCR",
  cr_specified_current: "CR specified current",
};

export function MatrixContactMeasurementPlanCard({
  items,
  profiles,
  groupLabels,
  disabled,
  workbookDisabled = disabled,
  saving,
  message,
  error,
  onFamilyCountChange,
  onFamilyIncludedChange,
  onFamilyLabelChange,
  onFamilyPrefixChange,
  onAddCustomFamily,
  onRemoveCustomFamily,
  onTargetIncludedChange,
  onTargetExclusionReasonChange,
  onApply,
  onSave,
  workbook,
}: MatrixContactMeasurementPlanCardProps) {
  const targets = buildContactPlanTargets(items);
  const profileError = validateContactPlanProfiles(
    profiles,
    targets.filter((target) => target.plan.included).map((target) => target.plan.contact_kind)
  );
  const hasTargets = targets.length > 0;
  return (
    <section className="matrix-contact-plan-card" aria-label="Contact Measurement Plan">
      <div className="matrix-contact-plan-header">
        <div>
          <h3>Contact Measurement Plan</h3>
          <p>Shared LLCR/CR contact counts for eligible included Matrix steps.</p>
        </div>
        <strong>{targets.length} targets</strong>
      </div>
      <div className="matrix-contact-plan-profiles">
        {(["llcr", "cr_specified_current"] as ContactMeasurementKind[]).map((kind) => (
          <section key={kind} className="matrix-contact-plan-profile">
            <div className="matrix-contact-plan-profile-header">
              <h4>{PROFILE_LABELS[kind]}</h4>
              <span>Readings / sample: {deriveReadingsPerSample(profiles[kind]) ?? "Review"}</span>
            </div>
            <div className="matrix-contact-plan-family-grid">
              {profiles[kind].map((family) => (
                <div key={family.familyId} className="matrix-contact-plan-family">
                  <label>
                    <input
                      type="checkbox"
                      checked={family.included}
                      disabled={disabled}
                      onChange={(event) =>
                        onFamilyIncludedChange(kind, family.familyId, event.target.checked)
                      }
                    />
                    Contact family
                  </label>
                  {family.isCustom ? (
                    <input
                      aria-label={`${PROFILE_LABELS[kind]} custom contact label`}
                      value={family.familyLabel}
                      disabled={disabled}
                      onChange={(event) =>
                        onFamilyLabelChange(kind, family.familyId, event.target.value)
                      }
                    />
                  ) : (
                    <strong>{family.familyLabel}</strong>
                  )}
                  <input
                    aria-label={`${PROFILE_LABELS[kind]} ${family.familyLabel} count per sample`}
                    value={family.countPerSample}
                    disabled={disabled || !family.included}
                    onChange={(event) =>
                      onFamilyCountChange(kind, family.familyId, event.target.value)
                    }
                  />
                  {family.isCustom ? (
                    <input
                      aria-label={`${PROFILE_LABELS[kind]} ${family.familyLabel} record prefix`}
                      value={family.recordPrefix}
                      disabled={disabled}
                      onChange={(event) =>
                        onFamilyPrefixChange(kind, family.familyId, event.target.value)
                      }
                    />
                  ) : (
                    <em>{family.recordPrefix}</em>
                  )}
                  {family.isCustom ? (
                    <button
                      type="button"
                      disabled={disabled}
                      onClick={() => onRemoveCustomFamily(kind, family.familyId)}
                    >
                      Remove
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onAddCustomFamily(kind)}
            >
              Add custom {PROFILE_LABELS[kind]} contact
            </button>
          </section>
        ))}
      </div>
      <div className="matrix-contact-plan-coverage" aria-label="Contact target coverage">
        <h4>Target coverage</h4>
        {targets.map(({ item, plan, status }, index) => {
          const targetLabel = `${groupLabels[item.draft_group_id] ?? `Group ${index + 1}`} ${item.test_item} Step ${item.raw_token ?? item.step_sequence}`;
          const manual = status === "Manual override";
          return (
            <div key={`${item.draft_group_id}-${item.draft_row_id}-${item.step_sequence}`} className="matrix-contact-plan-target">
              <label>
                <input
                  aria-label={`Include ${item.test_item} Step ${item.raw_token ?? item.step_sequence}`}
                  type="checkbox"
                  checked={plan.included}
                  disabled={disabled || manual}
                  onChange={(event) =>
                    onTargetIncludedChange(item, event.target.checked, plan.exclusion_reason ?? "")
                  }
                />
                {targetLabel}
              </label>
              <span>{status}</span>
              {!plan.included ? (
                <input
                  aria-label={`Exclusion reason for ${item.test_item} Step ${item.raw_token ?? item.step_sequence}`}
                  value={plan.exclusion_reason ?? ""}
                  disabled={disabled || manual}
                  placeholder="Reason required"
                  onChange={(event) => onTargetExclusionReasonChange(item, event.target.value)}
                />
              ) : null}
            </div>
          );
        })}
      </div>
      <div className="matrix-contact-plan-actions">
        <button type="button" disabled={disabled || !hasTargets || !!profileError} onClick={onApply}>
          Apply to blank contact targets
        </button>
        <button type="button" disabled={disabled || saving} onClick={onSave}>
          {saving ? "Saving" : "Save contact plan"}
        </button>
      </div>
      {workbook ? (
        <div className="matrix-contact-plan-workbook" aria-label="Specialized record workbook">
          <div>
            <strong>Specialized LLCR/CR record</strong>
            {workbook.preview ? (
              <p>
                {workbookPreviewMessage(workbook.preview)}
              </p>
            ) : (
              <p>Preview confirmed contact-plan records before generation.</p>
            )}
          </div>
          <div className="matrix-contact-plan-workbook-actions">
            <button
              type="button"
              disabled={workbookDisabled || workbook.busy !== null}
              onClick={workbook.onPreview}
            >
              {workbook.busy === "preview" ? "Previewing" : "Preview specialized record"}
            </button>
            <button
              type="button"
              disabled={workbookDisabled || workbook.busy !== null || !workbook.canGenerate}
              onClick={workbook.onGenerate}
            >
              {workbook.busy === "generate" ? "Generating" : "Generate workbook"}
            </button>
            {workbook.generated ? (
              <button
                type="button"
                disabled={workbookDisabled || workbook.busy !== null}
                onClick={workbook.onDownload}
              >
                {workbook.busy === "download" ? "Downloading" : "Download workbook"}
              </button>
            ) : null}
          </div>
          {workbook.error ? <p className="matrix-contact-plan-error">{workbook.error}</p> : null}
        </div>
      ) : null}
      {profileError ? <p className="matrix-contact-plan-error">{profileError}</p> : null}
      {message ? <p className="matrix-contact-plan-message">{message}</p> : null}
      {error ? <p className="matrix-contact-plan-error">{error}</p> : null}
    </section>
  );
}

function workbookPreviewMessage(
  preview: NonNullable<MatrixContactMeasurementPlanCardProps["workbook"]>["preview"]
): string {
  if (!preview) return "Preview confirmed contact-plan records before generation.";
  if (preview.status === "ready") return `${preview.row_count} record rows ready`;
  if (preview.status === "empty") return "No included LLCR/CR targets";
  const collision = preview.diagnostics?.find(
    (diagnostic) => diagnostic.code === "normalized_prefix_collision"
  );
  if (
    collision?.first_family_id &&
    collision.first_family_label &&
    collision.second_family_id &&
    collision.second_family_label
  ) {
    return `${collision.first_family_label} (${collision.first_family_id}) conflicts with ${collision.second_family_label} (${collision.second_family_id}).`;
  }
  return "Review contact plan blockers";
}
