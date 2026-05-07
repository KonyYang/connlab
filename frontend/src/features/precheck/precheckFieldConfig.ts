import type { IntakePrecheckLookupOptions } from "../../api/client";

export type PrecheckFieldSpec = {
  key: string;
  label: string;
  required?: boolean;
  kind?: "input" | "select" | "date";
  lookupGroup?: keyof IntakePrecheckLookupOptions;
  options?: string[];
};

export type PrecheckSampleRow = Record<string, string>;

export type PrecheckSampleColumn = {
  key: string;
  label: string;
};

export type PrecheckRequestedTestingRow = {
  test_to_be_performed: string;
  applicable_specification: string;
};

export const PRECHECK_REQUESTED_TESTING_COLUMNS = [
  { key: "test_to_be_performed", label: "Tests to be Performed" },
  { key: "applicable_specification", label: "Applicable Specifications" }
] as const;

export const PRECHECK_SAMPLE_COLUMNS: PrecheckSampleColumn[] = [
  { key: "product_name", label: "Product Name" },
  { key: "part_number", label: "Part Number / Revision" },
  { key: "lot_or_traceability", label: "Traceability Manufacturing Lot Info" },
  { key: "material", label: "Contact Base Material" },
  { key: "plating", label: "Contact Plating" },
  { key: "lubricant", label: "Contact Lubricant" },
  { key: "housing_material", label: "Housing Material" },
  { key: "quantity", label: "Quantity" }
];

export const PRECHECK_PROJECT_FIELDS: PrecheckFieldSpec[] = [
  { key: "requester", label: "Requested By", required: true },
  { key: "phone", label: "Phone #", required: true },
  { key: "request_date", label: "Date", required: true, kind: "date" },
  { key: "email", label: "Email", required: true },
  {
    key: "business_unit",
    label: "Business Unit",
    required: true,
    kind: "select",
    lookupGroup: "business_unit"
  },
  {
    key: "manufacturing_site",
    label: "Mfg. Site",
    required: true,
    kind: "select",
    lookupGroup: "manufacturing_site"
  },
  { key: "project_no", label: "Project #" },
  {
    key: "results_format",
    label: "Results Format",
    required: true,
    kind: "select",
    lookupGroup: "results_format"
  },
  { key: "requested_completion_date", label: "Requested Completion Date", required: true, kind: "date" },
  {
    key: "test_type",
    label: "Test Type",
    required: true,
    kind: "select",
    lookupGroup: "test_type"
  },
  {
    key: "sample_status",
    label: "Test Sample Status",
    required: true,
    kind: "select",
    lookupGroup: "sample_status"
  },
  {
    key: "project_type",
    label: "Project Type",
    required: true,
    kind: "select",
    lookupGroup: "project_type"
  },
  {
    key: "post_testing_disposition",
    label: "Post-Testing Sample Disposition",
    required: true,
    kind: "select",
    lookupGroup: "post_testing_disposition"
  },
  { key: "send_copies_recipients", label: "Send copies of test results/reports to", required: true }
];

export function emptyPrecheckSampleRow(): PrecheckSampleRow {
  return Object.fromEntries(PRECHECK_SAMPLE_COLUMNS.map((column) => [column.key, ""]));
}

export function emptyPrecheckRequestedTestingRow(): PrecheckRequestedTestingRow {
  return {
    test_to_be_performed: "",
    applicable_specification: ""
  };
}
