import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  commitLtrLocally,
  generateFolder,
  getLatestPrecheck,
  getLtrReadiness,
  getProject,
  listProjectLtrs,
  placeEvidence,
  previewLtrRegistration,
  previewEvidencePlacement,
  previewFolder,
  resolvePrecheckIssue,
  runPrecheck,
  uploadApplicationForm,
  type ApplicationForm,
  type EvidencePlacementPlan,
  type EvidencePlacementResult,
  type FolderGeneration,
  type FolderPlan,
  type FolderRequest,
  type LtrPreviewRequest,
  type LtrReadiness,
  type LtrRecord,
  type LtrRegistrationPreview,
  type PrecheckResult,
  type Project
} from "../api/client";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { PrecheckIssueCard } from "../components/precheck/PrecheckIssueCard";
import { PrecheckSummary } from "../components/precheck/PrecheckSummary";
import { ProjectLookupPanel } from "../components/project/ProjectLookupPanel";
import { ProjectSummaryPanel } from "../components/project/ProjectSummaryPanel";
import { ApplicationFormActionPanel } from "../components/workflow/ApplicationFormActionPanel";
import { FolderActionPanel } from "../components/workflow/FolderActionPanel";
import { buildLocalCommitRequest, LtrActionPanel } from "../components/workflow/LtrActionPanel";
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

function defaultLtrPreviewInput(): LtrPreviewRequest {
  const now = new Date();
  return {
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    registration_type: "normal",
    mode: "local_only",
    proposed_ltr_number: ""
  };
}

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
  const [evidencePlan, setEvidencePlan] = useState<EvidencePlacementPlan | null>(null);
  const [evidenceResult, setEvidenceResult] = useState<EvidencePlacementResult | null>(null);
  const [ltrReadiness, setLtrReadiness] = useState<LtrReadiness | null>(null);
  const [ltrPreview, setLtrPreview] = useState<LtrRegistrationPreview | null>(null);
  const [ltrPreviewInput, setLtrPreviewInput] = useState<LtrPreviewRequest>(defaultLtrPreviewInput);
  const [ltrRequestedBy, setLtrRequestedBy] = useState("");
  const [ltrOperatorNote, setLtrOperatorNote] = useState("");
  const [ltrCommitConfirmed, setLtrCommitConfirmed] = useState(false);
  const [previewingLtr, setPreviewingLtr] = useState(false);
  const [committingLtr, setCommittingLtr] = useState(false);
  const [previewingEvidence, setPreviewingEvidence] = useState(false);
  const [placingEvidence, setPlacingEvidence] = useState(false);
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
        setLtrReadiness(await getLtrReadiness(projectId));
      } catch {
        setLtrReadiness(null);
      }
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

  async function previewLtrNow(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setPreviewingLtr(true);
    try {
      const preview = await previewLtrRegistration(projectId, normalizedPreviewInput(ltrPreviewInput));
      setLtrPreview(preview);
      setLtrReadiness(preview.readiness);
      setLtrCommitConfirmed(false);
      setMessage("LTR Number preview completed without workbook write.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewingLtr(false);
    }
  }

  async function commitLtrNow(): Promise<void> {
    if (!ltrPreview) {
      setError("Run a no-write LTR Number preview before local commit.");
      return;
    }
    setCommittingLtr(true);
    try {
      const result = await commitLtrLocally(
        projectId,
        buildLocalCommitRequest(
          ltrPreview,
          normalizedPreviewInput(ltrPreviewInput),
          ltrCommitConfirmed,
          ltrRequestedBy,
          ltrOperatorNote
        )
      );
      setLtrs((current) => [result.ltr, ...current]);
      setLtrPreview(result.preview);
      setLtrReadiness(result.preview.readiness);
      setLtrCommitConfirmed(false);
      setSelectedStepId("folder");
      setMessage(`LTR Number committed locally: ${result.ltr.ltr_number}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setCommittingLtr(false);
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
      setEvidencePlan(null);
      setEvidenceResult(null);
      setMessage(`Folder generated: ${generated.project_folder_path}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function previewEvidenceNow(): Promise<void> {
    setPreviewingEvidence(true);
    try {
      const plan = await previewEvidencePlacement(projectId);
      setEvidencePlan(plan);
      setEvidenceResult(null);
      setMessage(plan.conflict ? "Evidence preview has conflicts." : "Evidence preview is clear.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewingEvidence(false);
    }
  }

  async function placeEvidenceNow(): Promise<void> {
    setPlacingEvidence(true);
    try {
      const result = await placeEvidence(projectId);
      setEvidenceResult(result);
      setEvidencePlan(result.plan);
      setMessage(`Evidence placed: ${result.copied_paths.length} files copied.`);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPlacingEvidence(false);
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
          <ProjectLookupPanel projectId={project.project_id} />
          <WorkflowStepper
            activeStepId={activeStep.id}
            steps={steps}
            onSelect={setSelectedStepId}
          />
          <NextActionPanel step={activeStep}>
            {renderStepContent(activeStep.id, {
              disabledPrecheck: !formRecord,
              evidencePlan,
              evidenceResult,
              folderGeneration,
              folderInput,
              folderPlan,
              formRecord,
              committingLtr,
              ltrCommitConfirmed,
              ltrOperatorNote,
              ltrPreview,
              ltrPreviewInput,
              ltrReadiness,
              ltrRequestedBy,
              ltrs,
              onCommitLtr: commitLtrNow,
              onGenerate: generateFolderNow,
              onPlaceEvidence: placeEvidenceNow,
              onPreview: previewFolderNow,
              onPreviewEvidence: previewEvidenceNow,
              onPreviewLtr: previewLtrNow,
              onRunPrecheck: runPrecheckNow,
              onResolveIssue: resolveIssueNow,
              onSubmitForm: uploadForm,
              precheck,
              placingEvidence,
              projectStatus: project.status,
              previewingEvidence,
              previewingLtr,
              setLtrCommitConfirmed,
              setLtrOperatorNote,
              setLtrPreviewInput,
              setLtrRequestedBy,
              setFolderInput,
            })}
          </NextActionPanel>
        </>
      )}
    </section>
  );
}

type StepContentProps = {
  disabledPrecheck: boolean;
  evidencePlan: EvidencePlacementPlan | null;
  evidenceResult: EvidencePlacementResult | null;
  folderGeneration: FolderGeneration | null;
  folderInput: FolderRequest;
  folderPlan: FolderPlan | null;
  formRecord: ApplicationForm | null;
  committingLtr: boolean;
  ltrCommitConfirmed: boolean;
  ltrOperatorNote: string;
  ltrPreview: LtrRegistrationPreview | null;
  ltrPreviewInput: LtrPreviewRequest;
  ltrReadiness: LtrReadiness | null;
  ltrRequestedBy: string;
  ltrs: LtrRecord[];
  onCommitLtr: () => Promise<void>;
  onGenerate: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
  onPreview: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onPreviewEvidence: () => Promise<void>;
  onPreviewLtr: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onRunPrecheck: () => Promise<void>;
  onResolveIssue: (issueId: string) => Promise<void>;
  onSubmitForm: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  precheck: PrecheckResult | null;
  placingEvidence: boolean;
  projectStatus?: string | null;
  previewingEvidence: boolean;
  previewingLtr: boolean;
  setLtrCommitConfirmed: (value: boolean) => void;
  setLtrOperatorNote: (value: string) => void;
  setLtrPreviewInput: (value: LtrPreviewRequest) => void;
  setLtrRequestedBy: (value: string) => void;
  setFolderInput: (value: FolderRequest) => void;
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

function LtrPanel(props: StepContentProps): ReactElement {
  return (
    <LtrActionPanel
      commitConfirmed={props.ltrCommitConfirmed}
      committing={props.committingLtr}
      ltrs={props.ltrs}
      ltrPreview={props.ltrPreview}
      ltrReadiness={props.ltrReadiness}
      onCommitLtr={props.onCommitLtr}
      onPreviewLtr={props.onPreviewLtr}
      operatorNote={props.ltrOperatorNote}
      previewing={props.previewingLtr}
      previewInput={props.ltrPreviewInput}
      projectStatus={props.projectStatus}
      requestedBy={props.ltrRequestedBy}
      setCommitConfirmed={props.setLtrCommitConfirmed}
      setOperatorNote={props.setLtrOperatorNote}
      setPreviewInput={props.setLtrPreviewInput}
      setRequestedBy={props.setLtrRequestedBy}
    />
  );
}

function FolderPanel(props: StepContentProps): ReactElement {
  return (
    <FolderActionPanel
      evidencePlan={props.evidencePlan}
      evidenceResult={props.evidenceResult}
      folderGeneration={props.folderGeneration}
      folderInput={props.folderInput}
      folderPlan={props.folderPlan}
      placingEvidence={props.placingEvidence}
      onGenerate={props.onGenerate}
      onPlaceEvidence={props.onPlaceEvidence}
      onPreview={props.onPreview}
      onPreviewEvidence={props.onPreviewEvidence}
      previewingEvidence={props.previewingEvidence}
      projectStatus={props.projectStatus}
      setFolderInput={props.setFolderInput}
    />
  );
}

function normalizedPreviewInput(input: LtrPreviewRequest): LtrPreviewRequest {
  return {
    ...input,
    mode: "local_only",
    proposed_ltr_number: input.proposed_ltr_number?.trim() || null
  };
}
