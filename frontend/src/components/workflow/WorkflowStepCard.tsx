import type { ReactElement } from "react";

export type WorkflowStepState = "done" | "current" | "ready" | "blocked" | "warning";

export type WorkflowStep = {
  id: string;
  number: number;
  title: string;
  state: WorkflowStepState;
  summary: string;
  nextAction: string;
};

type WorkflowStepCardProps = {
  active: boolean;
  step: WorkflowStep;
  onSelect: (stepId: string) => void;
};

export function WorkflowStepCard({
  active,
  step,
  onSelect
}: WorkflowStepCardProps): ReactElement {
  const blocked = step.state === "blocked";

  return (
    <button
      className={`workflow-step workflow-step-${step.state} ${active ? "workflow-step-active" : ""}`}
      disabled={blocked}
      type="button"
      onClick={() => onSelect(step.id)}
    >
      <span className="workflow-step-number">{step.number}</span>
      <span>
        <strong>{step.title}</strong>
        <small>{step.summary}</small>
      </span>
      <em>{step.nextAction}</em>
    </button>
  );
}
