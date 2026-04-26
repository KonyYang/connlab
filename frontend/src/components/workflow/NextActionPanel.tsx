import type { ReactElement, ReactNode } from "react";
import type { WorkflowStep } from "./WorkflowStepCard";

type NextActionPanelProps = {
  children: ReactNode;
  step: WorkflowStep;
};

export function NextActionPanel({ children, step }: NextActionPanelProps): ReactElement {
  return (
    <section className={`next-action-panel next-action-${step.state}`}>
      <div className="next-action-heading">
        <div>
          <p className="eyebrow">Current step</p>
          <h3>{step.title}</h3>
        </div>
        <span className={`status-badge status-badge-${step.state}`}>
          {step.state}
        </span>
      </div>
      <p className="next-action-copy">{step.nextAction}</p>
      {children}
    </section>
  );
}
