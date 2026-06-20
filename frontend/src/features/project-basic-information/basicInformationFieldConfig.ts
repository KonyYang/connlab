export type BasicInformationFieldKind = "text" | "textarea" | "date" | "readonly";

export type BasicInformationFieldConfig = {
  key: string;
  label: string;
  kind: BasicInformationFieldKind;
  required?: boolean;
};

export type BasicInformationFieldGroup = {
  title: string;
  fields: BasicInformationFieldConfig[];
};

export const BASIC_INFORMATION_META_FIELDS: BasicInformationFieldConfig[] = [
  {
    key: "dl_number",
    label: "DL/LTR Number",
    kind: "readonly",
    required: true,
  },
];

export const BASIC_INFORMATION_FIELD_GROUPS: BasicInformationFieldGroup[] = [
  {
    title: "Project scope",
    fields: [
      { key: "project_type", label: "Project Type", kind: "text", required: true },
      { key: "description_pn", label: "Description P/N", kind: "text" },
      { key: "product_description", label: "Product Description", kind: "textarea" },
      { key: "test_item", label: "Test Item", kind: "textarea", required: true },
      { key: "applicable_specifications", label: "Applicable Specifications", kind: "textarea" },
      { key: "test_type", label: "Test Type", kind: "text" },
    ],
  },
  {
    title: "Ownership",
    fields: [
      { key: "requested_by", label: "Requested by", kind: "text", required: true },
      { key: "phone", label: "Phone", kind: "text" },
      { key: "requestor_email", label: "E-mail of Requestor", kind: "text" },
      { key: "location", label: "Location", kind: "text" },
      { key: "project_leader", label: "Project Leader", kind: "text", required: true },
      {
        key: "lab_performing_tests",
        label: "Lab Performing the Tests",
        kind: "text",
        required: true,
      },
    ],
  },
  {
    title: "Result and commercial",
    fields: [
      { key: "test_result", label: "Test Result", kind: "text" },
      { key: "failed_item", label: "Failed item", kind: "textarea" },
      { key: "sample_deposition", label: "Sample deposition", kind: "textarea" },
      { key: "sub_contract", label: "Sub-contract", kind: "text" },
      { key: "test_fee", label: "Test Fee", kind: "text" },
      { key: "remarks_po", label: "Remarks (PO)", kind: "textarea" },
      {
        key: "condition_of_samples_when_received",
        label: "Condition of Samples when Received",
        kind: "text",
      },
    ],
  },
  {
    title: "Schedule",
    fields: [
      { key: "date_lab_received_samples", label: "Date Lab Received Samples", kind: "text" },
      { key: "estimated_completion_date", label: "Estimated Completion Date", kind: "text" },
      { key: "start_test_date", label: "Start Test Date", kind: "text" },
      { key: "finish_test_date", label: "Finish Test Date", kind: "text" },
      { key: "report_date", label: "Report Date", kind: "text" },
    ],
  },
];

export const BASIC_INFORMATION_FIELD_LABELS: Record<string, string> = [
  ...BASIC_INFORMATION_META_FIELDS,
  ...BASIC_INFORMATION_FIELD_GROUPS.flatMap((group) => group.fields),
].reduce<Record<string, string>>((labels, field) => {
  labels[field.key] = field.label;
  return labels;
}, {});
