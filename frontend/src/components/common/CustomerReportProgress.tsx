import "./customer-report-progress.css";

const stages: Record<string, string> = {
  queued: "Waiting for the previous customer-report task to finish...",
  validating: "Validating the Internal Report...",
  preparing_template: "Preparing the approved customer template...",
  opening_word: "Opening documents in Microsoft Word...",
  copying_content: "Copying report content and images...",
  cleaning_content: "Cleaning internal-only content...",
  formatting_document: "Applying customer-report layout and headers...",
  saving_document: "Saving the customer report...",
  verifying_output: "Verifying the generated report...",
  protecting_output: "Restoring document protection...",
  publishing: "Validating and publishing the customer report...",
  completed: "Customer report generation completed.",
  failed: "Customer report generation stopped.",
};

export function CustomerReportProgress({ stage, elapsedSeconds, running = true }: {
  stage: string; elapsedSeconds: number; running?: boolean;
}) {
  return <div className="customer-report-progress" role="status" aria-live="polite">
    {running ? <span className="customer-report-progress-spinner" aria-hidden="true" /> : <span aria-hidden="true">•</span>}
    <span>{stages[stage] ?? "Generating the customer report..."}</span>
    <span>{Math.round(elapsedSeconds)} seconds elapsed</span>
  </div>;
}
