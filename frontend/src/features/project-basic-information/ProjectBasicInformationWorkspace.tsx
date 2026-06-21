import { useLayoutEffect, useRef, type ReactElement } from "react";
import {
  BASIC_INFORMATION_FIELD_PANELS,
  type BasicInformationFieldConfig,
  type BasicInformationFieldGroup,
} from "./basicInformationFieldConfig";
import {
  selectBasicInformationMissingLabels,
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
  const missingLabels = selectCurrentMissingLabels(
    model.values,
    selectBasicInformationMissingLabels(model.response)
  );
  const dateValidation = selectDateValidation(model.values);
  const changedSourceLabels = selectChangedSourceFieldLabels(model.response);
  const confirmBlocked =
    model.loading ||
    model.confirming ||
    model.saving ||
    missingLabels.length > 0 ||
    dateValidation.messages.length > 0;
  const panelIdentity = model.values.dl_number?.trim() || model.identityLabel;

  return (
    <section className="basic-information-page" aria-label="Project Basic Information">
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

          <section className="basic-information-ltr-card" aria-label="LTR information">
            <span className="basic-information-panel-identity">{panelIdentity}</span>
            <button type="button" disabled>
              Update LTR
            </button>
          </section>

          <section className="basic-information-panel-grid">
            {BASIC_INFORMATION_FIELD_PANELS.map((panel) => (
              <section
                key={panel.title}
                className="basic-information-functional-panel"
                aria-label={panel.title}
              >
                {panel.groups.map((group) => (
                  <BasicInformationFieldGroupView
                    key={group.title}
                    group={group}
                    values={model.values}
                    missingLabels={missingLabels}
                    missingDateLabels={dateValidation.missingLabels}
                    invalidDateLabels={dateValidation.invalidLabels}
                    onChange={model.updateValue}
                  />
                ))}
                {panel.title === "Laboratory execution" &&
                dateValidation.messages.length > 0 ? (
                  <div
                    className="basic-information-panel-hints"
                    role="status"
                    aria-label="Date validation"
                  >
                    <strong>Date checks</strong>
                    <ul>
                      {dateValidation.messages.map((message) => (
                        <li key={message}>{message}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </section>
            ))}
          </section>
        </section>
      )}

      <footer className="basic-information-completion-dock">
        {model.saving ? <span>Saving draft automatically...</span> : null}
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

function BasicInformationFieldGroupView({
  group,
  values,
  missingLabels,
  missingDateLabels,
  invalidDateLabels,
  onChange,
}: {
  group: BasicInformationFieldGroup;
  values: Record<string, string>;
  missingLabels: string[];
  missingDateLabels: string[];
  invalidDateLabels: string[];
  onChange: (key: string, value: string) => void;
}): ReactElement {
  const missingLabelSet = new Set(missingLabels);
  const missingDateLabelSet = new Set(missingDateLabels);
  const invalidDateLabelSet = new Set(invalidDateLabels);
  return (
    <section className="basic-information-field-group">
      {[
        "Product information",
        "Requester information",
        "Application details",
        "Laboratory ownership",
        "Result and commercial",
        "Schedule",
      ].includes(group.title) ? null : (
        <h4>{group.title}</h4>
      )}
      <div className="basic-information-field-grid">
        {group.fields.map((field) => (
          <BasicInformationField
            key={field.key}
            field={field}
            value={values[field.key] ?? ""}
            missingRequired={missingLabelSet.has(field.label)}
            missingDate={missingDateLabelSet.has(field.label)}
            invalidDateSequence={invalidDateLabelSet.has(field.label)}
            onChange={onChange}
          />
        ))}
      </div>
    </section>
  );
}

function BasicInformationField({
  field,
  value,
  missingRequired,
  missingDate,
  invalidDateSequence,
  onChange,
}: {
  field: BasicInformationFieldConfig;
  value: string;
  missingRequired: boolean;
  missingDate: boolean;
  invalidDateSequence: boolean;
  onChange: (key: string, value: string) => void;
}): ReactElement {
  const label =
    field.required && field.kind !== "select" && field.kind !== "radio"
      ? `${field.label} *`
      : field.label;
  const displayValue = field.kind === "date" ? normalizeDateInputValue(value) : value;
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const shouldAutoGrowText = field.kind === "textarea" || field.kind === "text";
  const fieldClassName = [
    "basic-information-field",
    shouldAutoGrowText ? "is-textarea" : "",
    field.compact ? "is-compact" : "",
    field.layout === "full" ? "is-full" : "",
    field.layout === "twoThirds" ? "is-two-thirds" : "",
    field.layout === "third" ? "is-third" : "",
    field.layout === "inlineThird" ? "is-inline-third" : "",
    field.layout === "quarter" ? "is-quarter" : "",
    field.layout === "narrowQuarter" ? "is-narrow-quarter" : "",
    field.layout === "wideQuarter" ? "is-wide-quarter" : "",
    missingDate ? "is-missing-date" : "",
    missingRequired ? "is-missing-required" : "",
    invalidDateSequence ? "is-invalid-sequence" : "",
  ]
    .filter(Boolean)
    .join(" ");

  useLayoutEffect(() => {
    if (!shouldAutoGrowText || !textareaRef.current) {
      return;
    }
    const textarea = textareaRef.current;
    textarea.style.height = "auto";
    if (textarea.scrollHeight > 0) {
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [shouldAutoGrowText, value]);

  if (shouldAutoGrowText) {
    return (
      <label className={fieldClassName}>
        <span>{label}</span>
        <textarea
          ref={textareaRef}
          aria-label={field.label}
          rows={1}
          value={value}
          onChange={(event) => onChange(field.key, event.target.value)}
        />
      </label>
    );
  }
  if (field.kind === "select") {
    const shouldPreserveUnknownOption = field.preserveUnknownOption !== false;
    const selectValue = field.options?.includes(value)
      ? value
      : shouldPreserveUnknownOption
        ? value
        : field.defaultValue ?? field.options?.[0] ?? "";
    return (
      <label className={fieldClassName}>
        <span>{label}</span>
        <select
          aria-label={field.label}
          value={selectValue}
          onChange={(event) => onChange(field.key, event.target.value)}
        >
          {(
            shouldPreserveUnknownOption && value && !field.options?.includes(value)
              ? [value]
              : []
          ).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
          {(field.options ?? []).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }
  if (field.kind === "radio") {
    return (
      <fieldset className={`${fieldClassName} basic-information-radio-field`}>
        <legend>{label}</legend>
        <div className="basic-information-radio-options">
          {(field.options ?? []).map((option) => (
            <label key={option} className="basic-information-radio-option">
              <input
                type="radio"
                name={field.key}
                value={option}
                checked={value === option}
                onChange={(event) => onChange(field.key, event.target.value)}
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      </fieldset>
    );
  }
  return (
    <label className={fieldClassName}>
      <span>{label}</span>
      <input
        aria-label={field.label}
        type={field.kind === "date" ? "date" : "text"}
        value={displayValue}
        readOnly={field.kind === "readonly"}
        onChange={(event) => onChange(field.key, event.target.value)}
      />
    </label>
  );
}

function selectCurrentMissingLabels(
  values: Record<string, string>,
  responseMissingLabels: string[]
): string[] {
  const missingLabels = new Set(responseMissingLabels);
  BASIC_INFORMATION_FIELD_PANELS.flatMap((panel) =>
    panel.groups.flatMap((group) => group.fields)
  ).forEach((field) => {
    if (!field.required) {
      return;
    }
    if (!(values[field.key] ?? "").trim()) {
      missingLabels.add(field.label);
    } else {
      missingLabels.delete(field.label);
    }
  });
  return Array.from(missingLabels);
}

type DateValidationResult = {
  missingLabels: string[];
  invalidLabels: string[];
  messages: string[];
};

function selectDateValidation(values: Record<string, string>): DateValidationResult {
  const missingLabels = new Set<string>();
  const invalidLabels = new Set<string>();
  const messages = new Set<string>();
  const dates = {
    dateLabReceivedSamples: {
      label: "Lab Received Samples",
      value: values.date_lab_received_samples,
      date: parseBasicInformationDate(values.date_lab_received_samples),
    },
    startTestDate: {
      label: "Start Test Date",
      value: values.start_test_date,
      date: parseBasicInformationDate(values.start_test_date),
    },
    requestedCompletionDate: {
      label: "Requested Completion Date",
      value: values.requested_completion_date,
      date: parseBasicInformationDate(values.requested_completion_date),
    },
    estimatedCompletionDate: {
      label: "Estimated Completion",
      value: values.estimated_completion_date,
      date: parseBasicInformationDate(values.estimated_completion_date),
    },
    finishTestDate: {
      label: "Finish Test Date",
      value: values.finish_test_date,
      date: parseBasicInformationDate(values.finish_test_date),
    },
    reportDate: {
      label: "Report Date",
      value: values.report_date,
      date: parseBasicInformationDate(values.report_date),
    },
  };

  Object.values(dates).forEach((dateField) => {
    if (!normalizeDateInputValue(dateField.value ?? "")) {
      missingLabels.add(dateField.label);
    }
  });

  const markIfAfter = (
    earlierKey: keyof typeof dates,
    laterKey: keyof typeof dates,
    message: string
  ) => {
    const earlier = dates[earlierKey];
    const later = dates[laterKey];
    if (earlier.date && later.date && earlier.date.getTime() > later.date.getTime()) {
      invalidLabels.add(earlier.label);
      invalidLabels.add(later.label);
      messages.add(message);
    }
  };

  markIfAfter(
    "dateLabReceivedSamples",
    "startTestDate",
    "Lab Received Samples must not be later than Start Test Date."
  );
  markIfAfter(
    "dateLabReceivedSamples",
    "requestedCompletionDate",
    "Lab Received Samples must not be later than Requested Completion Date."
  );
  markIfAfter(
    "startTestDate",
    "requestedCompletionDate",
    "Start Test Date must not be later than Requested Completion Date."
  );
  markIfAfter(
    "dateLabReceivedSamples",
    "estimatedCompletionDate",
    "Lab Received Samples must not be later than Estimated Completion."
  );
  markIfAfter(
    "startTestDate",
    "estimatedCompletionDate",
    "Start Test Date must not be later than Estimated Completion."
  );
  markIfAfter(
    "startTestDate",
    "finishTestDate",
    "Finish Test Date must not be earlier than Start Test Date."
  );
  markIfAfter(
    "finishTestDate",
    "reportDate",
    "Finish Test Date must not be later than Report Date."
  );
  markIfAfter(
    "startTestDate",
    "reportDate",
    "Report Date must not be earlier than Start Test Date."
  );

  return {
    missingLabels: Array.from(missingLabels),
    invalidLabels: Array.from(invalidLabels),
    messages: Array.from(messages),
  };
}

function parseBasicInformationDate(value: string | undefined): Date | null {
  const normalizedValue = normalizeDateInputValue(value ?? "");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(normalizedValue)) {
    return null;
  }
  const [year, month, day] = normalizedValue.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function normalizeDateInputValue(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed;
  }
  const match = trimmed.match(/^(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})$/);
  if (!match) {
    return trimmed;
  }
  const month = monthNumber(match[2]);
  if (!month) {
    return trimmed;
  }
  return `${match[3]}-${month}-${match[1].padStart(2, "0")}`;
}

function monthNumber(monthName: string): string | null {
  const month = monthName.slice(0, 3).toLowerCase();
  const months: Record<string, string> = {
    jan: "01",
    feb: "02",
    mar: "03",
    apr: "04",
    may: "05",
    jun: "06",
    jul: "07",
    aug: "08",
    sep: "09",
    oct: "10",
    nov: "11",
    dec: "12",
  };
  return months[month] ?? null;
}
