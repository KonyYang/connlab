import type { ReactElement } from "react";

import type { IntakeCaseReviewField } from "../../api/client";
import type { PrecheckFieldSpec } from "./precheckFieldConfig";
import {
  dateInputValue,
  editableKey,
  fallbackValue,
  fieldClassName,
  normalizedOptions
} from "./precheckReviewSelectors";

type PrecheckFieldGridProps = {
  disabled: boolean;
  fields: PrecheckFieldSpec[];
  issueLevelByField: Map<string, string>;
  sourceFields: IntakeCaseReviewField[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
};

export function PrecheckFieldGrid({
  disabled,
  fields,
  issueLevelByField,
  sourceFields,
  values,
  onChange
}: PrecheckFieldGridProps): ReactElement {
  return (
    <div className="precheck-form-grid">
      {fields.map((field) => (
        <ReviewField
          disabled={disabled}
          field={field}
          issueLevel={issueLevelByField.get(field.key)}
          key={field.key}
          value={values[field.key] ?? fallbackValue(field.key, sourceFields)}
          onChange={(value) => {
            if (editableKey(field.key, sourceFields)) {
              onChange(field.key, value);
            }
          }}
        />
      ))}
    </div>
  );
}

function ReviewField({
  field,
  value,
  disabled,
  issueLevel,
  onChange
}: {
  field: PrecheckFieldSpec;
  value: string;
  disabled: boolean;
  issueLevel?: string;
  onChange: (value: string) => void;
}): ReactElement {
  const options = normalizedOptions(field.options ?? [], value);
  const inputValue = field.kind === "date" ? dateInputValue(value) : value;
  return (
    <label className={fieldClassName(issueLevel)}>
      <span>{field.label}{field.required ? <b>*</b> : null}</span>
      {field.kind === "select" ? (
        <select disabled={disabled} value={value || options[0] || ""} onChange={(event) => onChange(event.target.value)}>
          {options.map((option) => <option key={option}>{option}</option>)}
        </select>
      ) : (
        <input
          className="draft-field-input"
          disabled={disabled}
          type={field.kind === "date" ? "date" : "text"}
          value={inputValue}
          onChange={(event) => onChange(event.target.value)}
        />
      )}
    </label>
  );
}
