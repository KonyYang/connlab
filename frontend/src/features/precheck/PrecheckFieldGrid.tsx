import { useLayoutEffect, useRef, type ReactElement } from "react";

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
  missingRequiredByField?: Set<string>;
  sourceFields: IntakeCaseReviewField[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
};

export function PrecheckFieldGrid({
  disabled,
  fields,
  issueLevelByField,
  missingRequiredByField,
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
          issueLevel={missingRequiredByField?.has(field.key) ? "error" : issueLevelByField.get(field.key)}
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
  const recipientsMultiline = field.key === "send_copies_recipients";
  const options = normalizedOptions(field.options ?? [], value);
  const inputValue = field.kind === "date" ? dateInputValue(value) : value;
  const selectOptions = value ? options : ["", ...options.filter(Boolean)];
  return (
    <label className={fieldClassName(issueLevel)}>
      <span>{field.label}{field.required ? <b>*</b> : null}</span>
      {field.kind === "select" ? (
        <select disabled={disabled} value={value} onChange={(event) => onChange(event.target.value)}>
          {selectOptions.map((option) => (
            <option key={option || "__blank"} value={option}>
              {option || "Select..."}
            </option>
          ))}
        </select>
      ) : recipientsMultiline ? (
        <AutoGrowFieldTextarea
          disabled={disabled}
          value={value}
          onChange={onChange}
        />
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

function AutoGrowFieldTextarea({
  disabled,
  value,
  onChange
}: {
  disabled: boolean;
  value: string;
  onChange: (value: string) => void;
}): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight + 2}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      className="draft-field-input draft-field-textarea"
      disabled={disabled}
      rows={1}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
