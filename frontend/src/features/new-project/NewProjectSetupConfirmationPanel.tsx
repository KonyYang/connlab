import type { ReactElement } from "react";

export type NewProjectSetupConfirmationValues = {
  ltrMode: "auto" | "specified";
  specifiedLtrNumber: string;
  testItem: string;
  sampleDescription: string;
  testTypeInSheet: string;
  projectLeader: string;
  labPerformingTests: string;
};

type NewProjectSetupConfirmationPanelProps = {
  disabled: boolean;
  missingKeys: Set<string>;
  testTypeInSheetOptions: string[];
  values: NewProjectSetupConfirmationValues;
  onChange: (values: NewProjectSetupConfirmationValues) => void;
};

const LAB_PERFORMING_TESTS_OPTIONS = ["Dongguan", "Valley Green"] as const;

export function NewProjectSetupConfirmationPanel({
  disabled,
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

      <label className="new-project-setup-field">
        <span>Lab Performing the Tests*</span>
        <select
          className={missingKeys.has("lab_performing_tests") ? "setup-field-missing" : ""}
          disabled={disabled}
          value={values.labPerformingTests}
          onChange={(event) => update({ labPerformingTests: event.target.value })}
        >
          {LAB_PERFORMING_TESTS_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}
