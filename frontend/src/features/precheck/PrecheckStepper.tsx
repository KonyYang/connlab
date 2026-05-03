import type { ReactElement } from "react";

export function PrecheckStepper(): ReactElement {
  const steps = ["Intake", "Precheck", "LTR Number", "Project Folder"];
  return (
    <ol className="precheck-stepper" aria-label="New project steps">
      {steps.map((step, index) => (
        <li className={stepClassName(index)} key={step}>
          <span>{index === 0 ? "Done" : index + 1}</span>
          <strong>{step}</strong>
        </li>
      ))}
    </ol>
  );
}

function stepClassName(index: number): string {
  if (index < 1) {
    return "precheck-step precheck-step-done";
  }
  if (index === 1) {
    return "precheck-step precheck-step-active";
  }
  return "precheck-step";
}
