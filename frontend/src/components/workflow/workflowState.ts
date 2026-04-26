import type {
  ApplicationForm,
  FolderGeneration,
  FolderPlan,
  LtrRecord,
  PrecheckResult,
  Project
} from "../../api/client";
import type { WorkflowStep } from "./WorkflowStepCard";

export type WorkflowStepId = "application" | "precheck" | "ltr" | "folder";

type WorkflowStateInput = {
  folderGeneration: FolderGeneration | null;
  folderPlan: FolderPlan | null;
  formRecord: ApplicationForm | null;
  ltrs: LtrRecord[];
  precheck: PrecheckResult | null;
  project: Project | null;
};

export function buildWorkflowSteps({
  folderGeneration,
  folderPlan,
  formRecord,
  ltrs,
  precheck,
  project
}: WorkflowStateInput): WorkflowStep[] {
  const applicationDone = Boolean(formRecord || precheck);
  const precheckDone = Boolean(precheck);
  const precheckWarning = Boolean(precheck?.issues.some((issue) => !issue.resolved));
  const ltrDone = ltrs.length > 0;
  const folderDone = Boolean(folderGeneration || project?.status === "folder_created");
  const folderReady = applicationDone && precheckDone && ltrDone;

  return [
    {
      id: "application",
      number: 1,
      title: "Application Form",
      state: applicationDone ? "done" : "current",
      summary: applicationDone ? "Application material registered" : "Waiting for DOCX upload",
      nextAction: applicationDone ? "Review extracted form context" : "Upload the application form"
    },
    {
      id: "precheck",
      number: 2,
      title: "Precheck",
      state: !applicationDone ? "blocked" : precheckWarning ? "warning" : precheckDone ? "done" : "current",
      summary: !applicationDone ? "Blocked by missing form" : precheck?.status ?? "Ready to run",
      nextAction: !applicationDone ? "Upload application form first" : precheckDone ? "Review issues and continue" : "Run deterministic precheck"
    },
    {
      id: "ltr",
      number: 3,
      title: "LTR",
      state: !precheckDone ? "blocked" : ltrDone ? "done" : "current",
      summary: !precheckDone ? "Blocked by precheck" : ltrs[0]?.ltr_number ?? "LTR not registered",
      nextAction: !precheckDone ? "Complete precheck first" : ltrDone ? "Confirm latest LTR" : "Register LTR number"
    },
    {
      id: "folder",
      number: 4,
      title: "Project Folder",
      state: !folderReady ? "blocked" : folderDone ? "done" : folderPlan?.conflict ? "warning" : "current",
      summary: !folderReady ? "Blocked by prior steps" : folderDone ? "Folder generated" : folderPlan ? "Preview ready" : "Folder not previewed",
      nextAction: !folderReady ? "Complete form, precheck, and LTR first" : folderDone ? "Verify generated folder" : "Preview folder before generation"
    }
  ];
}

export function getActiveWorkflowStep(
  steps: WorkflowStep[],
  selectedStepId: string
): WorkflowStep {
  const fallbackStep = steps.find((step) => step.state === "current") ?? steps[0];
  const selectedStep = steps.find((step) => step.id === selectedStepId);
  return selectedStep?.state === "blocked" ? fallbackStep : selectedStep ?? fallbackStep;
}
