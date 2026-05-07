import type { ReactElement } from "react";

export type NewProjectSetupConfirmationValues = {
  ltrMode: "auto" | "specified";
  specifiedLtrNumber: string;
  workbookWriteAcknowledged: boolean;
  testItem: string;
  sampleDescription: string;
  location: string;
  testTypeInSheet: string;
  projectLeader: string;
};

type NewProjectSetupConfirmationPanelProps = {
  disabled: boolean;
  locationOptions: string[];
  missingKeys: Set<string>;
  testTypeInSheetOptions: string[];
  values: NewProjectSetupConfirmationValues;
  onChange: (values: NewProjectSetupConfirmationValues) => void;
};

export function NewProjectSetupConfirmationPanel({
  disabled,
  locationOptions,
  missingKeys,
  testTypeInSheetOptions,
  values,
  onChange
}: NewProjectSetupConfirmationPanelProps): ReactElement {
  const update = (patch: Partial<NewProjectSetupConfirmationValues>) =>
    onChange({ ...values, ...patch });

  return (
    <section className="intake-panel new-project-setup-panel">
      <div className="new-project-setup-heading">
        <strong>Project setup confirmation</strong>
      </div>

      <div className="new-project-ltr-mode-row" role="radiogroup" aria-label="LTR number mode">
        <label>
          <input
            checked={values.ltrMode === "auto"}
            disabled={disabled}
            name="new-project-ltr-mode"
            type="radio"
            onChange={() => update({ ltrMode: "auto" })}
          />
          Auto assign next LTR number
        </label>
        <label>
          <input
            checked={values.ltrMode === "specified"}
            disabled={disabled}
            name="new-project-ltr-mode"
            type="radio"
            onChange={() => update({ ltrMode: "specified" })}
          />
          Use specified LTR number
        </label>
      </div>

      <label className="new-project-setup-field">
        <span>Specified LTR number</span>
        <input
          className={missingKeys.has("specified_ltr_number") ? "setup-field-missing" : ""}
          disabled={disabled || values.ltrMode !== "specified"}
          placeholder="DL-YYYY-MM-NNN"
          type="text"
          value={values.specifiedLtrNumber}
          onChange={(event) => update({ specifiedLtrNumber: event.target.value })}
        />
      </label>

      <label
        className={`new-project-workbook-ack ${
          missingKeys.has("workbook_write_acknowledged") ? "setup-field-missing" : ""
        }`}
      >
        <input
          checked={values.workbookWriteAcknowledged}
          disabled={disabled}
          type="checkbox"
          onChange={(event) => update({ workbookWriteAcknowledged: event.target.checked })}
        />
        <span>
          I confirm ConnLab may write this LTR registration to the controlled workbook.
        </span>
      </label>

      <label className="new-project-setup-field">
        <span>Test Item*</span>
        <input
          className={missingKeys.has("test_item") ? "setup-field-missing" : ""}
          disabled={disabled}
          type="text"
          value={values.testItem}
          onChange={(event) => update({ testItem: event.target.value })}
        />
      </label>

      <label className="new-project-setup-field">
        <span>Sample Description*</span>
        <input
          className={missingKeys.has("sample_description") ? "setup-field-missing" : ""}
          disabled={disabled}
          type="text"
          value={values.sampleDescription}
          onChange={(event) => update({ sampleDescription: event.target.value })}
        />
      </label>

      <label className="new-project-setup-field">
        <span>Location*</span>
        <select
          className={missingKeys.has("location") ? "setup-field-missing" : ""}
          disabled={disabled}
          value={values.location}
          onChange={(event) => update({ location: event.target.value })}
        >
          <option value="">Select location</option>
          {locationOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="new-project-setup-field">
        <span>Test Type in sheet*</span>
        <select
          className={missingKeys.has("test_type_in_sheet") ? "setup-field-missing" : ""}
          disabled={disabled}
          value={values.testTypeInSheet}
          onChange={(event) => update({ testTypeInSheet: event.target.value })}
        >
          <option value="">Select test type</option>
          {testTypeInSheetOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="new-project-setup-field">
        <span>Project Leader*</span>
        <input
          className={missingKeys.has("project_leader") ? "setup-field-missing" : ""}
          disabled={disabled}
          type="text"
          value={values.projectLeader}
          onChange={(event) => update({ projectLeader: event.target.value })}
        />
      </label>
    </section>
  );
}
