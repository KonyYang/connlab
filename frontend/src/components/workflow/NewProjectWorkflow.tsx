import type { ReactElement } from "react";

import "./new-project-workflow.css";

export type NewProjectStepKey = "intake" | "precheck" | "ltr" | "folder";

const NEW_PROJECT_STEPS: Array<{ key: NewProjectStepKey; label: string }> = [
  { key: "intake", label: "Intake" },
  { key: "precheck", label: "Precheck" },
  { key: "ltr", label: "LTR Number" },
  { key: "folder", label: "Project Folder" }
];

type NewProjectWorkflowHeaderProps = {
  currentStep: NewProjectStepKey;
};

export function NewProjectWorkflowHeader({ currentStep }: NewProjectWorkflowHeaderProps): ReactElement {
  const currentIndex = currentStepIndex(currentStep);
  const currentLabel = NEW_PROJECT_STEPS[currentIndex].label;

  return (
    <ol className="new-project-stepper" aria-label={`New project step ${currentIndex + 1} of ${NEW_PROJECT_STEPS.length}: ${currentLabel}`}>
      {NEW_PROJECT_STEPS.map((step, index) => {
        const status = stepStatus(index, currentIndex);
        return (
          <li className={`new-project-step new-project-step-${status}`} key={step.key}>
            <span aria-hidden="true">{status === "complete" ? "✓" : index + 1}</span>
            <strong>{step.label}</strong>
          </li>
        );
      })}
    </ol>
  );
}

function currentStepIndex(currentStep: NewProjectStepKey): number {
  const index = NEW_PROJECT_STEPS.findIndex((step) => step.key === currentStep);
  return index >= 0 ? index : 0;
}

function stepStatus(index: number, currentIndex: number): "complete" | "current" | "upcoming" {
  if (index < currentIndex) {
    return "complete";
  }
  if (index === currentIndex) {
    return "current";
  }
  return "upcoming";
}
