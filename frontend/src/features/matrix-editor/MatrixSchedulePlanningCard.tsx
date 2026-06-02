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

export function MatrixSchedulePlanningCard({
  plan,
  groups,
  calculation,
  onChange,
}: MatrixSchedulePlanningCardProps): ReactElement {
  const selectedGroups = groups.filter((group) => group.isSelected);
  const criticalGroup = selectedGroups.find((group) => group.id === calculation.criticalGroupId) ?? null;
  const criticalLabel = criticalGroup?.name || criticalGroup?.id || "None";
  const updateField = (field: keyof MatrixSchedulePlan, value: string): void => {
    onChange({ ...plan, [field]: value });
  };

  return (
    <section className="matrix-editor-schedule-card" aria-label="Project schedule planning">
      <header className="matrix-editor-schedule-header">
        <div>
          <h3>Project Schedule</h3>
          <p>Calendar days for planning only.</p>
        </div>
        <strong>
          Critical: {criticalLabel} | {formatPlanningDays(calculation.criticalGroupDays)} d
        </strong>
      </header>

      <dl className="matrix-editor-schedule-summary">
        {selectedGroups.map((group) => (
          <div key={group.id}>
            <dt>{group.name || group.id}</dt>
            <dd>{formatPlanningDays(calculation.groupDays[group.id] ?? 0)} d</dd>
          </div>
        ))}
        <div>
          <dt>Total cycle</dt>
          <dd>{formatPlanningDays(calculation.totalCycleDays)} d</dd>
        </div>
      </dl>

      <div className="matrix-editor-schedule-fields">
        <label>
          <span>Pre-test buffer</span>
          <input
            className={calculation.bufferErrors.preTestBufferDays ? "is-invalid" : undefined}
            inputMode="decimal"
            value={plan.preTestBufferDays}
            onChange={(event) => updateField("preTestBufferDays", event.target.value)}
          />
        </label>
        <label>
          <span>Post-test buffer</span>
          <input
            className={calculation.bufferErrors.postTestBufferDays ? "is-invalid" : undefined}
            inputMode="decimal"
            value={plan.postTestBufferDays}
            onChange={(event) => updateField("postTestBufferDays", event.target.value)}
          />
        </label>
        <label>
          <span>Sample received</span>
          <input
            className={calculation.invalidDateFields.sampleReceivedDate ? "is-invalid" : undefined}
            aria-invalid={calculation.invalidDateFields.sampleReceivedDate ? true : undefined}
            type="date"
            value={plan.sampleReceivedDate}
            onChange={(event) => updateField("sampleReceivedDate", event.target.value)}
          />
        </label>
        <label>
          <span>Planned start</span>
          <input
            className={calculation.invalidDateFields.plannedTestStartDate ? "is-invalid" : undefined}
            aria-invalid={calculation.invalidDateFields.plannedTestStartDate ? true : undefined}
            type="date"
            value={plan.plannedTestStartDate}
            onChange={(event) => updateField("plannedTestStartDate", event.target.value)}
          />
        </label>
        <label>
          <span>Test complete</span>
          <input
            className={calculation.invalidDateFields.plannedTestCompleteDate ? "is-invalid" : undefined}
            aria-invalid={calculation.invalidDateFields.plannedTestCompleteDate ? true : undefined}
            type="date"
            value={plan.plannedTestCompleteDate}
            onChange={(event) => updateField("plannedTestCompleteDate", event.target.value)}
          />
        </label>
        <label>
          <span>Estimated completion</span>
          <input
            className={calculation.invalidDateFields.estimatedCompletionDate ? "is-invalid" : undefined}
            aria-invalid={calculation.invalidDateFields.estimatedCompletionDate ? true : undefined}
            type="date"
            value={plan.estimatedCompletionDate}
            onChange={(event) => updateField("estimatedCompletionDate", event.target.value)}
          />
        </label>
      </div>

      {calculation.bufferErrors.preTestBufferDays ? (
        <p className="matrix-editor-schedule-error">{calculation.bufferErrors.preTestBufferDays}</p>
      ) : null}
      {calculation.bufferErrors.postTestBufferDays ? (
        <p className="matrix-editor-schedule-error">{calculation.bufferErrors.postTestBufferDays}</p>
      ) : null}
      {calculation.dateError ? (
        <p className="matrix-editor-schedule-error">{calculation.dateError}</p>
      ) : null}
    </section>
  );
}
