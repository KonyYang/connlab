export type MatrixSchedulePlan = {
  postTestBufferDays: string;
  sampleReceivedDate: string;
  plannedTestStartDate: string;
  plannedTestCompleteDate: string;
  estimatedCompletionDate: string;
};

export type MatrixScheduleRowInput = {
  id: string;
  isSampleRow: boolean;
  dayExpression: string;
  groups: Record<string, string>;
};

export type MatrixScheduleGroupInput = {
  id: string;
  name: string;
  isSelected: boolean;
};

export type MatrixScheduleCalculation = {
  groupDays: Record<string, number>;
  criticalGroupId: string | null;
  criticalGroupDays: number;
  totalCycleDays: number;
  rowErrors: Record<string, string>;
  bufferErrors: Partial<Record<keyof Pick<MatrixSchedulePlan, "postTestBufferDays">, string>>;
  invalidDateFields: Partial<Record<keyof Pick<
    MatrixSchedulePlan,
    "sampleReceivedDate" | "plannedTestStartDate" | "plannedTestCompleteDate" | "estimatedCompletionDate"
  >, true>>;
  dateError: string | null;
  isValid: boolean;
};

type DateField = keyof Pick<
  MatrixSchedulePlan,
  "sampleReceivedDate" | "plannedTestStartDate" | "plannedTestCompleteDate" | "estimatedCompletionDate"
>;

type DateValidationResult = {
  message: string | null;
  invalidFields: Partial<Record<DateField, true>>;
};

const DATE_FIELDS: DateField[] = [
  "sampleReceivedDate",
  "plannedTestStartDate",
  "plannedTestCompleteDate",
  "estimatedCompletionDate",
];

const DAY_PATTERN = /^\d+(?:\.\d+)?x?$/i;
const DECIMAL_PATTERN = /^\d+(?:\.\d+)?$/;

export function emptySchedulePlan(): MatrixSchedulePlan {
  return {
    postTestBufferDays: "",
    sampleReceivedDate: "",
    plannedTestStartDate: "",
    plannedTestCompleteDate: "",
    estimatedCompletionDate: "",
  };
}

export function calculateMatrixSchedule(
  rows: MatrixScheduleRowInput[],
  groups: MatrixScheduleGroupInput[],
  plan: MatrixSchedulePlan
): MatrixScheduleCalculation {
  const selectedGroups = groups.filter((group) => group.isSelected);
  const groupDays: Record<string, number> = {};
  selectedGroups.forEach((group) => {
    groupDays[group.id] = 0;
  });

  const rowErrors: Record<string, string> = {};
  const activeRowIds = new Set<string>();
  rows.forEach((row) => {
    if (row.isSampleRow) {
      return;
    }
    if (
      selectedGroups.some((group) => countStepTokens(row.groups[group.id] ?? "") > 0)
    ) {
      activeRowIds.add(row.id);
    }
  });

  rows.forEach((row) => {
    if (row.isSampleRow || !activeRowIds.has(row.id)) {
      return;
    }
    const parsed = parseDayExpression(row.dayExpression);
    if (parsed.error) {
      rowErrors[row.id] = parsed.error;
      return;
    }
    if (parsed.value == null) {
      return;
    }
    const dayValue = parsed.value;
    selectedGroups.forEach((group) => {
      const tokenCount = countStepTokens(row.groups[group.id] ?? "");
      if (tokenCount === 0) {
        return;
      }
      groupDays[group.id] += parsed.multiplier ? dayValue * tokenCount : dayValue;
    });
  });

  const bufferErrors: MatrixScheduleCalculation["bufferErrors"] = {};
  const postBuffer = parseBufferDays(plan.postTestBufferDays);
  if (postBuffer.error) {
    bufferErrors.postTestBufferDays = postBuffer.error;
  }

  const critical = selectedGroups.reduce(
    (current, group) =>
      groupDays[group.id] > current.days ? { id: group.id, days: groupDays[group.id] } : current,
    { id: null as string | null, days: 0 }
  );
  const totalCycleDays = critical.days + (postBuffer.value ?? 0);
  const dateValidation =
    Object.keys(bufferErrors).length > 0
      ? { message: null, invalidFields: {} }
      : validateDatePlan(plan, critical.days, postBuffer.value ?? 0);

  return {
    groupDays,
    criticalGroupId: critical.id,
    criticalGroupDays: critical.days,
    totalCycleDays,
    rowErrors,
    bufferErrors,
    invalidDateFields: dateValidation.invalidFields,
    dateError: dateValidation.message,
    isValid:
      Object.keys(rowErrors).length === 0 &&
      Object.keys(bufferErrors).length === 0 &&
      dateValidation.message == null,
  };
}

export function formatPlanningDays(value: number): string {
  if (!Number.isFinite(value)) {
    return "0";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
}

function parseDayExpression(value: string): { value: number | null; multiplier: boolean; error: string | null } {
  const text = value.trim();
  if (!text) {
    return { value: null, multiplier: false, error: null };
  }
  if (!DAY_PATTERN.test(text)) {
    return { value: null, multiplier: false, error: "Day must be a non-negative decimal or decimal multiplier." };
  }
  const multiplier = text.toLowerCase().endsWith("x");
  const numericText = multiplier ? text.slice(0, -1) : text;
  const parsed = Number.parseFloat(numericText);
  return { value: parsed, multiplier, error: null };
}

function parseBufferDays(value: string): { value: number | null; error: string | null } {
  const text = value.trim();
  if (!text) {
    return { value: 0, error: null };
  }
  if (!DECIMAL_PATTERN.test(text)) {
    return { value: null, error: "Buffer days must be a non-negative decimal." };
  }
  return { value: Number.parseFloat(text), error: null };
}

function countStepTokens(value: string): number {
  return value.trim().split(/[\s,，、\u040e\u045e]+/).filter((token) => token.trim().length > 0).length;
}

function validateDatePlan(
  plan: MatrixSchedulePlan,
  criticalGroupDays: number,
  postBufferDays: number,
): DateValidationResult {
  const noError: DateValidationResult = { message: null, invalidFields: {} };
  const values = [
    plan.sampleReceivedDate,
    plan.plannedTestStartDate,
    plan.plannedTestCompleteDate,
    plan.estimatedCompletionDate,
  ].map((value) => value.trim());
  if (!values.some(Boolean)) {
    return noError;
  }
  if (!values.every(Boolean)) {
    return {
      message: "All planned date fields are required when any planned date is filled.",
      invalidFields: buildInvalidDateFields(values.map((value) => !value)),
    };
  }
  const [received, start, complete, estimated] = values.map(parseDateValue);
  if (received == null || start == null || complete == null || estimated == null) {
    return {
      message: "Planned dates must use YYYY-MM-DD format.",
      invalidFields: buildInvalidDateFields([
        received == null,
        start == null,
        complete == null,
        estimated == null,
      ]),
    };
  }
  if (start < received) {
    return {
      message: "Planned start is earlier than sample received date.",
      invalidFields: { plannedTestStartDate: true },
    };
  }
  if (complete < addCalendarDays(start, Math.ceil(criticalGroupDays))) {
    return {
      message: "Test complete is earlier than planned start plus critical group days.",
      invalidFields: { plannedTestCompleteDate: true },
    };
  }
  if (estimated < addCalendarDays(complete, Math.ceil(postBufferDays))) {
    return {
      message: "Estimated completion is earlier than test complete plus post-test buffer.",
      invalidFields: { estimatedCompletionDate: true },
    };
  }
  return noError;
}

function parseDateValue(value: string): number | null {
  const isoMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoMatch != null) {
    const [, year, month, day] = isoMatch;
    const date = Date.UTC(Number(year), Number(month) - 1, Number(day));
    if (!Number.isFinite(date)) {
      return null;
    }
    const parsed = new Date(date);
    const parsedYear = String(parsed.getUTCFullYear()).padStart(4, "0");
    const parsedMonth = String(parsed.getUTCMonth() + 1).padStart(2, "0");
    const parsedDay = String(parsed.getUTCDate()).padStart(2, "0");
    return `${parsedYear}-${parsedMonth}-${parsedDay}` === value ? date : null;
  }
  return null;
}

function addCalendarDays(dateValue: number, days: number): number {
  return dateValue + days * 24 * 60 * 60 * 1000;
}

function buildInvalidDateFields(flags: boolean[]): Partial<Record<DateField, true>> {
  return DATE_FIELDS.reduce<Partial<Record<DateField, true>>>((invalidFields, field, index) => {
    if (flags[index]) {
      invalidFields[field] = true;
    }
    return invalidFields;
  }, {});
}
