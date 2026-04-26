import type { ReactElement } from "react";
import { WorkflowStepCard, type WorkflowStep } from "./WorkflowStepCard";

type WorkflowStepperProps = {
  activeStepId: string;
  steps: WorkflowStep[];
  onSelect: (stepId: string) => void;
};

export function WorkflowStepper({
  activeStepId,
  steps,
  onSelect
}: WorkflowStepperProps): ReactElement {
  return (
    <nav className="workflow-stepper" aria-label="Project workflow">
      {steps.map((step) => (
        <WorkflowStepCard
          active={step.id === activeStepId}
          key={step.id}
          step={step}
          onSelect={onSelect}
        />
      ))}
    </nav>
  );
}
