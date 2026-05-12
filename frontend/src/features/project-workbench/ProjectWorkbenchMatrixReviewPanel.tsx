import type { ReactElement } from "react";
import type { ProjectTestPlanDraft } from "../../api/client";

type ProjectWorkbenchMatrixReviewPanelProps = {
  draft: ProjectTestPlanDraft | null;
  error: string | null;
  loading: boolean;
};

type MatrixSummary = {
  groupCount: number;
  stepCount: number;
  warningCount: number;
};

export function ProjectWorkbenchMatrixReviewPanel({
  draft,
  error,
  loading
}: ProjectWorkbenchMatrixReviewPanelProps): ReactElement {
  const summary = buildMatrixSummary(draft);

  return (
    <section className="matrix-review-panel">
      <header className="matrix-review-heading">
        <div>
          <h4>Matrix review</h4>
          <p>Use the Project test-plan draft as the primary view before downstream documents.</p>
        </div>
        {draft ? <strong>Draft v{draft.version}</strong> : null}
      </header>
      {loading ? <p className="fine-print">Loading Matrix draft...</p> : null}
      {!loading && error ? <p className="error">Unable to load Matrix draft: {error}</p> : null}
      {!loading && !error && !draft ? (
        <p className="blocking-copy">
          No active Project test-plan draft is available yet. Create or review a draft to start
          Matrix-based project planning.
        </p>
      ) : null}
      {draft ? (
        <>
          <dl className="matrix-review-summary">
            <div>
              <dt>Source document</dt>
              <dd>{draft.source_document_name}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{draft.status}</dd>
            </div>
            <div>
              <dt>Groups</dt>
              <dd>{summary.groupCount}</dd>
            </div>
            <div>
              <dt>Steps</dt>
              <dd>{summary.stepCount}</dd>
            </div>
            <div>
              <dt>Warnings</dt>
              <dd>{summary.warningCount}</dd>
            </div>
          </dl>
          <div className="matrix-review-groups">
            {(draft.payload.groups ?? []).map((group, groupIndex) => (
              <article
                className="matrix-review-group"
                key={`${group.group_key ?? "group"}-${groupIndex}`}
              >
                <header>
                  <strong>{group.group_label ?? `Group ${groupIndex + 1}`}</strong>
                  {typeof group.source_table_index === "number" ? (
                    <span>Table {group.source_table_index}</span>
                  ) : null}
                </header>
                <ul className="matrix-review-step-list">
                  {(group.steps ?? []).map((step, stepIndex) => (
                    <li key={`${step.sequence ?? stepIndex}-${step.test_item ?? "step"}`}>
                      <strong>
                        {step.sequence ? `${step.sequence}. ` : ""}
                        {step.test_item ?? step.step_label ?? "Unspecified test step"}
                      </strong>
                      <span>
                        {step.method_summary ?? step.reference_standard ?? "Method/reference pending"}
                      </span>
                      <em>{durationText(step)}</em>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
          {(draft.payload.warnings ?? []).length > 0 ? (
            <div className="message-list message-list-warning">
              <strong>Draft warnings</strong>
              <ul>
                {(draft.payload.warnings ?? []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

function buildMatrixSummary(draft: ProjectTestPlanDraft | null): MatrixSummary {
  if (!draft) {
    return { groupCount: 0, stepCount: 0, warningCount: 0 };
  }
  const groups = draft.payload.groups ?? [];
  const stepCount = groups.reduce((total, group) => total + (group.steps?.length ?? 0), 0);
  return {
    groupCount: groups.length,
    stepCount,
    warningCount: draft.payload.warnings?.length ?? 0
  };
}

function durationText(step: {
  estimated_duration_hint?: string | null;
  duration_hint?: string | null;
  estimated_duration_days?: number | null;
  duration_days?: number | null;
  estimated_duration_hours?: number | null;
}): string {
  if (step.estimated_duration_hint) {
    return step.estimated_duration_hint;
  }
  if (step.duration_hint) {
    return step.duration_hint;
  }
  if (typeof step.estimated_duration_days === "number") {
    return `${step.estimated_duration_days} day(s)`;
  }
  if (typeof step.duration_days === "number") {
    return `${step.duration_days} day(s)`;
  }
  if (typeof step.estimated_duration_hours === "number") {
    return `${step.estimated_duration_hours} hour(s)`;
  }
  return "Duration pending";
}
