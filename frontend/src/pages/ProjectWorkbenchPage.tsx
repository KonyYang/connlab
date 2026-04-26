import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  generateFolder,
  getLatestPrecheck,
  getProject,
  listProjectLtrs,
  previewFolder,
  registerLtr,
  resolvePrecheckIssue,
  runPrecheck,
  uploadApplicationForm,
  type ApplicationForm,
  type FolderGeneration,
  type FolderPlan,
  type FolderRequest,
  type LtrRecord,
  type PrecheckResult,
  type Project
} from "../api/client";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { PrecheckIssueCard } from "../components/precheck/PrecheckIssueCard";
import { PrecheckSummary } from "../components/precheck/PrecheckSummary";
import { ProjectSummaryPanel } from "../components/project/ProjectSummaryPanel";
import { ApplicationFormActionPanel } from "../components/workflow/ApplicationFormActionPanel";
import { FolderActionPanel } from "../components/workflow/FolderActionPanel";
import { LtrActionPanel } from "../components/workflow/LtrActionPanel";
import { NextActionPanel } from "../components/workflow/NextActionPanel";
import { WorkflowStepper } from "../components/workflow/WorkflowStepper";
import { buildWorkflowSteps, getActiveWorkflowStep } from "../components/workflow/workflowState";
import "../workbench.css";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
};

const EMPTY_FOLDER: FolderRequest = {
  template_path: "",
  target_root: "",
  dl_number: "",
  plan_date: new Date().toISOString().slice(0, 10)
};

export function ProjectWorkbenchPage({
  projectId,
  onBack
}: ProjectWorkbenchPageProps): ReactElement {
  const [project, setProject] = useState<Project | null>(null);
  const [formRecord, setFormRecord] = useState<ApplicationForm | null>(null);
  const [precheck, setPrecheck] = useState<PrecheckResult | null>(null);
  const [ltrs, setLtrs] = useState<LtrRecord[]>([]);
  const [folderInput, setFolderInput] = useState<FolderRequest>(EMPTY_FOLDER);
  const [folderPlan, setFolderPlan] = useState<FolderPlan | null>(null);
  const [folderGeneration, setFolderGeneration] = useState<FolderGeneration | null>(null);
  const [ltrNumber, setLtrNumber] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedStepId, setSelectedStepId] = useState("application");

  const steps = buildWorkflowSteps({
    folderGeneration,
    folderPlan,
    formRecord,
    ltrs,
    precheck,
    project
  });
  const activeStep = getActiveWorkflowStep(steps, selectedStepId);

  useEffect(() => {
    void loadWorkbench();
  }, [projectId]);

  useEffect(() => {
    if (steps.some((step) => step.id === selectedStepId && step.state !== "blocked")) {
      return;
    }
    setSelectedStepId(activeStep.id);
  }, [activeStep.id, selectedStepId, steps]);

  async function loadWorkbench(): Promise<void> {
    try {
      setProject(await getProject(projectId));
      setLtrs(await listProjectLtrs(projectId));
      try {
        setPrecheck(await getLatestPrecheck(projectId));
      } catch {
        setPrecheck(null);
      }
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function uploadForm(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const fileInput = event.currentTarget.elements.namedItem("applicationForm");
    const file = fileInput instanceof HTMLInputElement ? fileInput.files?.[0] : null;
    if (!file) {
      setError("Choose an application form first.");
      return;
    }

    try {
      const uploaded = await uploadApplicationForm(projectId, file);
      setFormRecord(uploaded);
      setPrecheck(null);
      setSelectedStepId("precheck");
      setMessage(`Application form ${uploaded.form_no} Rev ${uploaded.revision} uploaded.`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function runPrecheckNow(): Promise<void> {
    if (!formRecord) {
      setError("Upload an application form before running precheck.");
      return;
    }
    try {
      const result = await runPrecheck(formRecord.form_id);
      setPrecheck(result);
      setSelectedStepId("ltr");
      setMessage(`Precheck status: ${result.status}`);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function resolveIssueNow(issueId: string): Promise<void> {
    try {
      const resolved = await resolvePrecheckIssue(issueId);
      setPrecheck((current) =>
        current
          ? {
              ...current,
              issues: current.issues.map((issue) =>
                issue.issue_id === issueId ? resolved : issue
              )
            }
          : current
      );
      setMessage("Precheck issue marked reviewed.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function submitLtr(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    try {
      const record = await registerLtr(projectId, { ltr_number: ltrNumber });
      setLtrNumber("");
      setLtrs((current) => [record, ...current]);
      setSelectedStepId("folder");
      setMessage(`LTR registered: ${record.ltr_number}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function previewFolderNow(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    try {
      const plan = await previewFolder(projectId, folderInput);
      setFolderPlan(plan);
      setFolderGeneration(null);
      setMessage(plan.conflict ? "Folder preview has conflicts." : "Folder preview is clear.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function generateFolderNow(): Promise<void> {
    try {
      const generated = await generateFolder(projectId, folderInput);
      setFolderGeneration(generated);
      setMessage(`Folder generated: ${generated.project_folder_path}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (!project && !error) {
    return <LoadingState label="Loading project workbench..." />;
  }

  return (
    <section className="workbench-page">
      {error && <ErrorMessage message={error} />}
      {message && <p className="success">{message}</p>}
      {project && (
        <>
          <ProjectSummaryPanel project={project} onBack={onBack} />
          <WorkflowStepper
            activeStepId={activeStep.id}
            steps={steps}
            onSelect={setSelectedStepId}
          />
          <NextActionPanel step={activeStep}>
            {renderStepContent(activeStep.id, {
              disabledPrecheck: !formRecord,
              folderGeneration,
              folderInput,
              folderPlan,
              formRecord,
              ltrNumber,
              ltrs,
              onGenerate: generateFolderNow,
              onPreview: previewFolderNow,
              onRunPrecheck: runPrecheckNow,
              onResolveIssue: resolveIssueNow,
              onSubmitForm: uploadForm,
              onSubmitLtr: submitLtr,
              precheck,
              setFolderInput,
              setLtrNumber
            })}
          </NextActionPanel>
        </>
      )}
    </section>
  );
}

type StepContentProps = {
  disabledPrecheck: boolean;
  folderGeneration: FolderGeneration | null;
  folderInput: FolderRequest;
  folderPlan: FolderPlan | null;
  formRecord: ApplicationForm | null;
  ltrNumber: string;
  ltrs: LtrRecord[];
  onGenerate: () => Promise<void>;
  onPreview: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onRunPrecheck: () => Promise<void>;
  onResolveIssue: (issueId: string) => Promise<void>;
  onSubmitForm: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onSubmitLtr: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  precheck: PrecheckResult | null;
  setFolderInput: (value: FolderRequest) => void;
  setLtrNumber: (value: string) => void;
};

function renderStepContent(stepId: string, props: StepContentProps): ReactElement {
  if (stepId === "precheck") {
    return <PrecheckPanel {...props} />;
  }
  if (stepId === "ltr") {
    return <LtrPanel {...props} />;
  }
  if (stepId === "folder") {
    return <FolderPanel {...props} />;
  }
  return <ApplicationFormPanel {...props} />;
}

function ApplicationFormPanel({ formRecord, onSubmitForm }: StepContentProps): ReactElement {
  return <ApplicationFormActionPanel formRecord={formRecord} onSubmitForm={onSubmitForm} />;
}

function PrecheckPanel({
  disabledPrecheck,
  onRunPrecheck,
  onResolveIssue,
  precheck
}: StepContentProps): ReactElement {
  return (
    <div className="action-panel-body">
      <PrecheckSummary precheck={precheck} />
      <button className="primary-action" disabled={disabledPrecheck} type="button" onClick={() => void onRunPrecheck()}>
        Run precheck
      </button>
      {precheck && precheck.issues.length === 0 && (
        <p className="success">No precheck issues found.</p>
      )}
      {precheck && precheck.issues.length > 0 && (
        <div className="precheck-issue-list">
          {precheck.issues.map((issue) => (
            <PrecheckIssueCard
              issue={issue}
              key={issue.issue_id}
              onResolve={(issueId) => void onResolveIssue(issueId)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function LtrPanel({
  ltrNumber,
  ltrs,
  onSubmitLtr,
  setLtrNumber
}: StepContentProps): ReactElement {
  return (
    <LtrActionPanel
      ltrNumber={ltrNumber}
      ltrs={ltrs}
      onSubmitLtr={onSubmitLtr}
      setLtrNumber={setLtrNumber}
    />
  );
}

function FolderPanel({
  folderGeneration,
  folderInput,
  folderPlan,
  onGenerate,
  onPreview,
  setFolderInput
}: StepContentProps): ReactElement {
  return (
    <FolderActionPanel
      folderGeneration={folderGeneration}
      folderInput={folderInput}
      folderPlan={folderPlan}
      onGenerate={onGenerate}
      onPreview={onPreview}
      setFolderInput={setFolderInput}
    />
  );
}
