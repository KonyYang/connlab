import type { ReactElement } from "react";
import {
  formatPlanningDays,
  type MatrixScheduleCalculation,
  type MatrixScheduleGroupInput,
  type MatrixSchedulePlan,
} from "./matrixSchedulePlanning";

type MatrixSchedulePlanningCardProps = {
  plan: MatrixSchedulePlan;
  groups: MatrixScheduleGroupInput[];
  calculation: MatrixScheduleCalculation;
  onChange: (plan: MatrixSchedulePlan) => void;
};

const DATE_FIELDS: Array<
  keyof Pick<
    MatrixSchedulePlan,
    "sampleReceivedDate" | "plannedTestStartDate" | "plannedTestCompleteDate" | "estimatedCompletionDate"
  >
> = [
  "sampleReceivedDate",
  "plannedTestStartDate",
  "plannedTestCompleteDate",
  "estimatedCompletionDate",
];

type DateField = typeof DATE_FIELDS[number];

export function MatrixSchedulePlanningCard({
  plan,
  groups,
  calculation,
  onChange,
}: MatrixSchedulePlanningCardProps): ReactElement {
  const selectedGroups = groups.filter((group) => group.isSelected);
  const criticalGroup = selectedGroups.find((group) => group.id === calculation.criticalGroupId) ?? null;
  const criticalLabel = criticalGroup ? criticalGroup.name || criticalGroup.id : "No group";
  const updateField = (field: keyof MatrixSchedulePlan, value: string): void => {
    const normalizedValue = isDateField(field) ? normalizeDateInput(value) : value;
    onChange(applyScheduleDateDefaults({ ...plan, [field]: normalizedValue }, field, calculation));
  };
  const needsDateAttention = (field: DateField): boolean =>
    calculation.invalidDateFields[field] === true || plan[field].trim().length === 0;

  const dateAriaInvalid = (field: DateField): true | undefined =>
    needsDateAttention(field) ? true : undefined;
  const dateInputClass = (field: DateField): string | undefined =>
    needsDateAttention(field) ? "is-invalid" : undefined;

  return (
    <section className="matrix-editor-schedule-card" aria-label="Project schedule planning">
      <header className="matrix-editor-schedule-header">
        <div>
          <h3>Project Schedule</h3>
          <p>Calendar days for planning only.</p>
        </div>
        <strong>
          Longest Test Group {criticalLabel}: {formatPlanningDays(calculation.criticalGroupDays)} d
        </strong>
      </header>

      <div className="matrix-editor-schedule-fields">
        <label>
          <span className="matrix-editor-schedule-field-label">
            <span>Post-test buffer</span>
            <span className="matrix-editor-schedule-unit" aria-hidden="true">
              days
            </span>
          </span>
          <input
            className={calculation.bufferErrors.postTestBufferDays ? "is-invalid" : undefined}
            inputMode="decimal"
            value={plan.postTestBufferDays}
            aria-label="Post-test buffer"
            onChange={(event) => updateField("postTestBufferDays", event.target.value)}
          />
        </label>
        <label>
          <span>Sample received</span>
          <input
            className={`matrix-editor-schedule-date-input ${dateInputClass("sampleReceivedDate") ?? ""}`.trim()}
            aria-invalid={dateAriaInvalid("sampleReceivedDate")}
            aria-label="Sample received"
            type="date"
            value={plan.sampleReceivedDate}
            onChange={(event) => updateField("sampleReceivedDate", event.target.value)}
          />
        </label>
        <label>
          <span>Planned start</span>
          <input
            className={`matrix-editor-schedule-date-input ${dateInputClass("plannedTestStartDate") ?? ""}`.trim()}
            aria-invalid={dateAriaInvalid("plannedTestStartDate")}
            aria-label="Planned start"
            type="date"
            value={plan.plannedTestStartDate}
            onChange={(event) => updateField("plannedTestStartDate", event.target.value)}
          />
        </label>
        <label>
          <span>Test complete</span>
          <input
            className={`matrix-editor-schedule-date-input ${dateInputClass("plannedTestCompleteDate") ?? ""}`.trim()}
            aria-invalid={dateAriaInvalid("plannedTestCompleteDate")}
            aria-label="Test complete"
            type="date"
            value={plan.plannedTestCompleteDate}
            onChange={(event) => updateField("plannedTestCompleteDate", event.target.value)}
          />
        </label>
        <label>
          <span>Estimated completion</span>
          <input
            className={`matrix-editor-schedule-date-input ${dateInputClass("estimatedCompletionDate") ?? ""}`.trim()}
            aria-invalid={dateAriaInvalid("estimatedCompletionDate")}
            aria-label="Estimated completion"
            type="date"
            value={plan.estimatedCompletionDate}
            onChange={(event) => updateField("estimatedCompletionDate", event.target.value)}
          />
        </label>
      </div>

      {calculation.bufferErrors.postTestBufferDays ? (
        <p className="matrix-editor-schedule-error">{calculation.bufferErrors.postTestBufferDays}</p>
      ) : null}
      {calculation.dateError ? (
        <p className="matrix-editor-schedule-error">{calculation.dateError}</p>
      ) : null}
    </section>
  );
}

function applyScheduleDateDefaults(
  nextPlan: MatrixSchedulePlan,
  changedField: keyof MatrixSchedulePlan,
  calculation: MatrixScheduleCalculation
): MatrixSchedulePlan {
  if (changedField !== "plannedTestStartDate" && changedField !== "postTestBufferDays" && changedField !== "plannedTestCompleteDate") {
    return nextPlan;
  }
  if (changedField === "plannedTestStartDate") {
    const plannedStart = parseDateInput(nextPlan.plannedTestStartDate);
    if (plannedStart == null) {
      return nextPlan;
    }
    const plannedTestCompleteDate = addDays(plannedStart, Math.ceil(calculation.criticalGroupDays));
    const nextComplete = formatDateInput(plannedTestCompleteDate);
    const estimatedCompletionDate = formatDateInput(
      addDays(plannedTestCompleteDate, Math.ceil(parseNonNegativeDecimal(nextPlan.postTestBufferDays) ?? 0))
    );
    return {
      ...nextPlan,
      plannedTestCompleteDate: nextComplete,
      estimatedCompletionDate,
    };
  }
  if (changedField === "plannedTestCompleteDate") {
    const currentComplete = parseDateInput(nextPlan.plannedTestCompleteDate);
    if (currentComplete == null) {
      return nextPlan;
    }
    const estimatedCompletionDate = formatDateInput(
      addDays(currentComplete, Math.ceil(parseNonNegativeDecimal(nextPlan.postTestBufferDays) ?? 0))
    );
    return {
      ...nextPlan,
      estimatedCompletionDate,
    };
  }
  const currentComplete = parseDateInput(nextPlan.plannedTestCompleteDate);
  if (currentComplete == null) {
    return nextPlan;
  }
  const estimatedCompletion = addDays(currentComplete, Math.ceil(parseNonNegativeDecimal(nextPlan.postTestBufferDays) ?? 0));
  return {
    ...nextPlan,
    estimatedCompletionDate: formatDateInput(estimatedCompletion),
  };
}

function normalizeDateInput(value: string): string {
  const parsed = parseDateInput(value);
  return parsed == null ? value : formatDateInput(parsed);
}

function isDateField(field: keyof MatrixSchedulePlan): field is DateField {
  return (DATE_FIELDS as readonly string[]).includes(field);
}

function parseNonNegativeDecimal(value: string): number | null {
  const text = value.trim();
  if (!text) {
    return 0;
  }
  if (!/^\d+(?:\.\d+)?$/.test(text)) {
    return null;
  }
  return Number.parseFloat(text);
}

function parseDateInput(value: string): number | null {
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

function addDays(dateValue: number, days: number): number {
  return dateValue + days * 24 * 60 * 60 * 1000;
}

function formatDateInput(dateValue: number): string {
  const date = new Date(dateValue);
  const year = String(date.getUTCFullYear()).padStart(4, "0");
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
