import type { ReactElement } from "react";

export const NEW_PROJECT_SETUP_LABELS = {
  sample_description: "Sample Description",
  test_item: "Test Item",
  test_type_in_sheet: "Test Type in sheet",
  project_leader: "Project Leader",
  lab_performing_tests: "Lab Performing the Tests"
} as const;

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
        <span>{NEW_PROJECT_SETUP_LABELS.sample_description}*</span>
        <input
          className={missingKeys.has("sample_description") ? "setup-field-missing" : ""}
          disabled={disabled}
          id="intake-setup-sample_description"
          type="text"
          value={values.sampleDescription}
          onChange={(event) => update({ sampleDescription: event.target.value })}
        />
      </label>

      <label className="new-project-setup-field">
        <span>{NEW_PROJECT_SETUP_LABELS.test_item}*</span>
        <input
          className={missingKeys.has("test_item") ? "setup-field-missing" : ""}
          disabled={disabled}
          id="intake-setup-test_item"
          type="text"
          value={values.testItem}
          onChange={(event) => update({ testItem: event.target.value })}
        />
      </label>

      <label className="new-project-setup-field">
        <span>{NEW_PROJECT_SETUP_LABELS.test_type_in_sheet}*</span>
        <select
          className={missingKeys.has("test_type_in_sheet") ? "setup-field-missing" : ""}
          disabled={disabled}
          id="intake-setup-test_type_in_sheet"
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
        <span>{NEW_PROJECT_SETUP_LABELS.project_leader}*</span>
        <input
          className={missingKeys.has("project_leader") ? "setup-field-missing" : ""}
          disabled={disabled}
          id="intake-setup-project_leader"
          type="text"
          value={values.projectLeader}
          onChange={(event) => update({ projectLeader: event.target.value })}
        />
      </label>

      <label className="new-project-setup-field">
        <span>{NEW_PROJECT_SETUP_LABELS.lab_performing_tests}*</span>
        <select
          className={missingKeys.has("lab_performing_tests") ? "setup-field-missing" : ""}
          disabled={disabled}
          id="intake-setup-lab_performing_tests"
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
