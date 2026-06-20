import type { ReactElement } from "react";
import {
  BASIC_INFORMATION_FIELD_GROUPS,
  BASIC_INFORMATION_META_FIELDS,
  type BasicInformationFieldConfig,
} from "./basicInformationFieldConfig";
import {
  selectBasicInformationMissingLabels,
  selectBasicInformationStatusLabel,
  selectChangedSourceFieldLabels,
  sourceReviewMessage,
} from "./basicInformationSelectors";
import {
  type BackToWorkbenchOptions,
  useProjectBasicInformationModel,
} from "./useProjectBasicInformationModel";

type ProjectBasicInformationWorkspaceProps = {
  projectId: string;
  onBackToWorkbench: (options: BackToWorkbenchOptions) => void;
};

export function ProjectBasicInformationWorkspace({
  projectId,
  onBackToWorkbench,
}: ProjectBasicInformationWorkspaceProps): ReactElement {
  const model = useProjectBasicInformationModel({ projectId, onBackToWorkbench });
  const statusLabel = selectBasicInformationStatusLabel(model.response);
  const missingLabels = selectBasicInformationMissingLabels(model.response);
  const changedSourceLabels = selectChangedSourceFieldLabels(model.response);
  const confirmBlocked = model.loading || model.confirming || model.saving;

  return (
    <section className="basic-information-page" aria-label="Project Basic Information">
      <header className="basic-information-header">
        <div>
          <h2>Basic Information</h2>
          <p>{statusLabel}</p>
        </div>
      </header>

      {model.loading ? (
        <section className="basic-information-surface" aria-busy="true">
          Loading Basic Information...
        </section>
      ) : (
        <section className="basic-information-surface">
          {model.error ? (
            <div className="basic-information-alert is-danger" role="alert">
              {model.error}
            </div>
          ) : null}
          {model.savedMessage ? (
            <div className="basic-information-alert" role="status">
              {model.savedMessage}
            </div>
          ) : null}
          {missingLabels.length > 0 ? (
            <div className="basic-information-alert is-warning">
              <strong>Missing required fields</strong>
              <span>{missingLabels.join(", ")}</span>
            </div>
          ) : null}
          {changedSourceLabels.length > 0 ? (
            <div className="basic-information-alert is-warning">
              <strong>Source review</strong>
              <ul>
                {changedSourceLabels.map((label) => (
                  <li key={label}>{sourceReviewMessage(label)}</li>
                ))}
              </ul>
            </div>
          ) : null}

          <section className="basic-information-meta-grid">
            {BASIC_INFORMATION_META_FIELDS.map((field) => (
              <BasicInformationField
                key={field.key}
                field={field}
                value={model.values[field.key] ?? ""}
                onChange={model.updateValue}
              />
            ))}
          </section>

          {BASIC_INFORMATION_FIELD_GROUPS.map((group) => (
            <section key={group.title} className="basic-information-field-group">
              <h3>{group.title}</h3>
              <div className="basic-information-field-grid">
                {group.fields.map((field) => (
                  <BasicInformationField
                    key={field.key}
                    field={field}
                    value={model.values[field.key] ?? ""}
                    onChange={model.updateValue}
                  />
                ))}
              </div>
            </section>
          ))}
        </section>
      )}

      <footer className="basic-information-completion-dock">
        <span>
          {model.saving
            ? "Saving draft automatically..."
            : "Draft saves automatically. Confirm creates a new authoritative Basic Information version."}
        </span>
        <div className="basic-information-completion-actions">
          <button type="button" onClick={model.cancel}>
            Cancel
          </button>
          <button
            type="button"
            className="basic-information-primary-action"
            disabled={confirmBlocked}
            onClick={() => void model.confirm()}
          >
            {model.confirming ? "Confirming..." : "Confirm"}
          </button>
        </div>
      </footer>
    </section>
  );
}

function BasicInformationField({
  field,
  value,
  onChange,
}: {
  field: BasicInformationFieldConfig;
  value: string;
  onChange: (key: string, value: string) => void;
}): ReactElement {
  const label = field.required ? `${field.label} *` : field.label;
  if (field.kind === "textarea") {
    return (
      <label className="basic-information-field is-textarea">
        <span>{label}</span>
        <textarea
          aria-label={field.label}
          value={value}
          onChange={(event) => onChange(field.key, event.target.value)}
        />
      </label>
    );
  }
  return (
    <label className="basic-information-field">
      <span>{label}</span>
      <input
        aria-label={field.label}
        type={field.kind === "date" ? "date" : "text"}
        value={value}
        readOnly={field.kind === "readonly"}
        onChange={(event) => onChange(field.key, event.target.value)}
      />
    </label>
  );
}
