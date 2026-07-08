export type BasicInformationFieldKind =
  | "text"
  | "textarea"
  | "date"
  | "readonly"
  | "select"
  | "radio";

export type BasicInformationFieldConfig = {
  key: string;
  label: string;
  kind: BasicInformationFieldKind;
  required?: boolean;
  compact?: boolean;
  defaultValue?: string;
  preserveUnknownOption?: boolean;
  optionSource?: "testTypeInSheet";
  layout?:
    | "full"
    | "twoThirds"
    | "third"
    | "inlineThird"
    | "quarter"
    | "narrowQuarter"
    | "wideQuarter"
    | "wideRemainder";
  options?: string[];
};

export type BasicInformationFieldGroup = {
  title: string;
  layout?: "failedItemWithSheetType";
  fields: BasicInformationFieldConfig[];
};

export type BasicInformationFieldPanel = {
  title: string;
  summary: string;
  groups: BasicInformationFieldGroup[];
};

const MANUFACTURING_SITE_OPTIONS = [
  "AAL",
  "AAOP Berlin",
  "AAP",
  "AAPG-OTHER",
  "AATK",
  "ABR",
  "ACAD",
  "ACAG-OTHER",
  "ACC-DT",
  "ACPA",
  "ACPA - Canada",
  "ACX Bangalore",
  "ADCE",
  "ADS",
  "AGEC",
  "AGIS-OTHER",
  "AGSE",
  "AHSC",
  "AHSC-XMN",
  "AHSI",
  "AHSTNT",
  "AIMG-OTHER",
  "AIPG",
  "AIPG-ATS",
  "AIPG-NT",
  "AIPG-OTHER",
  "AIPG-SZ",
  "AIS",
  "AIST",
  "AJET",
  "AJET-HY",
  "AJET-HZ",
  "ALTW",
  "Amphenol RF",
  "AMTA",
  "ANAM-OTHER",
  "Aorora",
  "APCD",
  "ARDENT",
  "ARFOB",
  "ASAA",
  "ASCA",
  "ASCA-SZ",
  "ASEAN",
  "AST",
  "ASTG-OTHER",
  "ATCS",
  "ATCS-CZ",
  "ATCS-MEX",
  "ATCS-NH",
  "ATPI",
  "ATZ",
  "Bangalore",
  "Berlin",
  "Besancon",
  "Changzhou",
  "Chengdu",
  "Cochin",
  "Dongguan",
  "GES",
  "GPE",
  "HALO-OTHER",
  "Hampton",
  "HSIO CN Canada",
  "HSIO-CZ",
  "HSIO-All",
  "HZP",
  "India",
  "Japan",
  "Jurong",
  "MCP-OTHER",
  "Multi",
  "Nantong",
  "None",
  "Non-ACS",
  "Other",
  "Penang",
  "Positronic Springfield",
  "RFOB-OTHER",
  "Senai",
  "Senjur",
  "SINE",
  "Spectra Strip",
  "TCS-CAA",
  "TCS-CZ",
  "TCS-MAL",
  "TCS-USA",
  "USA",
  "Valley Green",
  "Xgiga",
  "Xiamen",
];

const BUSINESS_UNIT_OPTIONS = [
  "AAPG",
  "ACAG",
  "ACPA",
  "ACPI",
  "ACS",
  "AGIS",
  "AIMG",
  "AIPG",
  "AJET",
  "Amphenol RF",
  "ANAM",
  "AORORA",
  "ARDENT",
  "ARFOB",
  "ASTG",
  "BASICS",
  "CBS",
  "CMIO",
  "Halo",
  "HS Backplane",
  "HS Cable",
  "HS Mezzanine",
  "HSIO",
  "HSIO CA",
  "HSIO CN",
  "HSIO SP",
  "MCP",
  "MEZZ - AIS",
  "MEZZ - MegArray",
  "Multi",
  "Non-ACS",
  "None",
  "Optics",
  "Other",
  "Positronic",
  "Power Solutions",
  "RFOB",
  "Server & Storage",
  "Server & Storage IO",
  "Valley Green",
  "XGIGA",
];

const RESULTS_FORMAT_OPTIONS = [
  "Data and Observations",
  "Formal Report (Internal)",
  "Formal Report (Customer)",
  "Presentation Summary",
];

const SAMPLE_STATUS_OPTIONS = [
  "Prototype",
  "Pre-production",
  "Production",
  "Competitor",
];

const POST_TESTING_DISPOSITION_OPTIONS = [
  "Send Back to Requestor",
  "Scrap",
  "Keep in the Lab",
];

const TEST_RESULT_OPTIONS = ["OK", "Ref", "NG", "In progress", "In-waiting"];

const LAB_PERFORMING_TESTS_OPTIONS = ["Dongguan", "Valley Green"];

const SAMPLE_CONDITION_OPTIONS = ["Acceptable", "Not Acceptable"];

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
    title: "Product information",
    fields: [
      {
        key: "product_description",
        label: "Product Description",
        kind: "textarea",
        required: true,
        compact: true,
      },
      {
        key: "test_item",
        label: "Test Item",
        kind: "textarea",
        required: true,
        compact: true,
      },
      {
        key: "description_pn",
        label: "Description P/N",
        kind: "text",
        compact: true,
        layout: "full",
      },
      {
        key: "tests_to_be_performed",
        label: "Tests to be Performed",
        kind: "textarea",
        required: true,
        compact: true,
      },
      {
        key: "applicable_specifications",
        label: "Applicable Specifications",
        kind: "textarea",
        required: true,
        compact: true,
      },
      {
        key: "project_type",
        label: "Project Type",
        kind: "select",
        required: true,
        layout: "third",
        options: [
          "New Product Development",
          "Product Extension",
          "Innovation",
          "Lab Activities (Lab Use Only)",
          "Operational Support",
          "Cost Reduction",
        ],
      },
      {
        key: "test_type",
        label: "Test Type",
        kind: "select",
        layout: "third",
        options: [
          "Product/Process Development",
          "Product/Process Qualification",
          "Lab/Failure Analysis",
          "Customer Specific Testing",
        ],
      },
      {
        key: "sub_contract",
        label: "Sub-contract",
        kind: "radio",
        layout: "third",
        options: ["Yes", "No"],
        defaultValue: "No",
      },
    ],
  },
  {
    title: "Requester information",
    fields: [
      {
        key: "requested_by",
        label: "Requested by",
        kind: "text",
        required: true,
        layout: "quarter",
      },
      {
        key: "requestor_email",
        label: "E-mail of Requestor",
        kind: "text",
        layout: "wideQuarter",
      },
      { key: "phone", label: "Phone", kind: "text", layout: "quarter" },
      {
        key: "location",
        label: "Mfg. Site",
        kind: "select",
        layout: "narrowQuarter",
        options: MANUFACTURING_SITE_OPTIONS,
      },
    ],
  },
  {
    title: "Application details",
    fields: [
      {
        key: "results_format",
        label: "Results Format",
        kind: "select",
        layout: "third",
        options: RESULTS_FORMAT_OPTIONS,
      },
      {
        key: "business_unit",
        label: "Business Unit",
        kind: "select",
        layout: "third",
        options: BUSINESS_UNIT_OPTIONS,
      },
      { key: "project_no", label: "Project #", kind: "text", layout: "third" },
      {
        key: "requested_completion_date",
        label: "Requested Completion Date",
        kind: "date",
        required: true,
        layout: "third",
      },
      {
        key: "sample_status",
        label: "Test Sample Status",
        kind: "select",
        layout: "third",
        options: SAMPLE_STATUS_OPTIONS,
      },
      {
        key: "post_testing_disposition",
        label: "Post-Testing Sample Disposition",
        kind: "select",
        layout: "third",
        options: POST_TESTING_DISPOSITION_OPTIONS,
      },
      {
        key: "send_copies_recipients",
        label: "Send copies of test results/reports to",
        kind: "text",
        layout: "twoThirds",
      },
      {
        key: "confidential",
        label: "Confidential test or samples",
        kind: "radio",
        required: true,
        layout: "inlineThird",
        options: ["Yes", "No"],
        defaultValue: "No",
      },
    ],
  },
  {
    title: "Laboratory ownership",
    fields: [
      {
        key: "lab_performing_tests",
        label: "Lab Performing",
        kind: "select",
        required: true,
        layout: "quarter",
        options: LAB_PERFORMING_TESTS_OPTIONS,
        defaultValue: "Dongguan",
        preserveUnknownOption: false,
      },
      {
        key: "project_leader",
        label: "Project Leader",
        kind: "text",
        required: true,
        layout: "quarter",
      },
      {
        key: "condition_of_samples_when_received",
        label: "Condition of Samples",
        kind: "select",
        layout: "quarter",
        options: SAMPLE_CONDITION_OPTIONS,
        defaultValue: "Acceptable",
        preserveUnknownOption: false,
      },
      {
        key: "test_result",
        label: "Test Result",
        kind: "select",
        layout: "quarter",
        options: TEST_RESULT_OPTIONS,
        defaultValue: "OK",
        preserveUnknownOption: false,
      },
      {
        key: "date_lab_received_samples",
        label: "Lab Received Samples",
        kind: "date",
        required: true,
        layout: "quarter",
      },
      {
        key: "estimated_completion_date",
        label: "Estimated Completion",
        kind: "date",
        required: true,
        layout: "quarter",
      },
      {
        key: "sample_deposition",
        label: "Sample deposition",
        kind: "textarea",
        layout: "quarter",
      },
      { key: "test_fee", label: "Test Fee", kind: "text", layout: "quarter" },
      { key: "start_test_date", label: "Start Test Date", kind: "date", layout: "quarter" },
      { key: "finish_test_date", label: "Finish Test Date", kind: "date", layout: "quarter" },
      { key: "report_date", label: "Report Date", kind: "date", layout: "quarter" },
      { key: "remarks_po", label: "Remarks (PO)", kind: "textarea", layout: "quarter" },
    ],
  },
  {
    title: "Quantity defaults",
    fields: [
      {
        key: "test_points_per_sample",
        label: "Test points / sample",
        kind: "text",
        layout: "third",
      },
      {
        key: "readings_per_point",
        label: "Readings / point",
        kind: "text",
        layout: "third",
      },
      {
        key: "contact_points_per_sample",
        label: "Contact points / sample",
        kind: "text",
        layout: "third",
      },
    ],
  },
  {
    title: "Result and commercial",
    layout: "failedItemWithSheetType",
    fields: [
      { key: "failed_item", label: "Failed item", kind: "textarea", layout: "wideRemainder" },
      {
        key: "test_type_in_sheet",
        label: "Test Type in sheet",
        kind: "select",
        layout: "narrowQuarter",
        optionSource: "testTypeInSheet",
      },
    ],
  },
  {
    title: "Schedule",
    fields: [],
  },
];

export const BASIC_INFORMATION_FIELD_PANELS: BasicInformationFieldPanel[] = [
  {
    title: "Product and request",
    summary: "Application-form source values for product scope and requester details.",
    groups: BASIC_INFORMATION_FIELD_GROUPS.slice(0, 3),
  },
  {
    title: "Laboratory execution",
    summary: "Lab ownership, result/commercial status, and schedule dates.",
    groups: BASIC_INFORMATION_FIELD_GROUPS.slice(3),
  },
];

export function normalizeBasicInformationFieldValues(
  values: Record<string, string>
): Record<string, string> {
  const normalizedValues = { ...values };
  const postTestingDisposition =
    normalizedValues.post_testing_disposition?.trim() ?? "";
  const sampleDeposition = normalizedValues.sample_deposition?.trim() ?? "";
  if (postTestingDisposition && !sampleDeposition) {
    normalizedValues.sample_deposition = postTestingDisposition;
  }
  const estimatedCompletionDate =
    normalizedValues.estimated_completion_date?.trim() ?? "";
  if (estimatedCompletionDate) {
    if (!normalizedValues.finish_test_date?.trim()) {
      normalizedValues.finish_test_date = estimatedCompletionDate;
    }
    if (!normalizedValues.report_date?.trim()) {
      normalizedValues.report_date = estimatedCompletionDate;
    }
  }
  const fields = BASIC_INFORMATION_FIELD_PANELS.flatMap((panel) =>
    panel.groups.flatMap((group) => group.fields)
  );
  fields.forEach((field) => {
    if (!field.options?.length) {
      return;
    }
    const currentValue = normalizedValues[field.key] ?? "";
    if (
      field.kind === "select" &&
      field.preserveUnknownOption === false &&
      !field.options.includes(currentValue)
    ) {
      normalizedValues[field.key] = field.defaultValue ?? field.options[0] ?? "";
    }
    if (
      field.kind === "radio" &&
      field.defaultValue &&
      !field.options.includes(currentValue)
    ) {
      normalizedValues[field.key] = field.defaultValue ?? field.options[0] ?? "";
    }
  });
  return normalizedValues;
}

export const BASIC_INFORMATION_FIELD_LABELS: Record<string, string> = [
  ...BASIC_INFORMATION_META_FIELDS,
  ...BASIC_INFORMATION_FIELD_GROUPS.flatMap((group) => group.fields),
].reduce<Record<string, string>>((labels, field) => {
  labels[field.key] = field.label;
  return labels;
}, {});
