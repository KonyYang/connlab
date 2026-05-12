import { useEffect, useMemo, useState } from "react";
import {
  executeApprovalPackage,
  getProjectTestPlanDraft,
  getProject,
  listProjectTestPlanDrafts,
  listExternalResources,
  listProjectLtrs,
  placeEvidence,
  previewApprovalPackage,
  previewEvidencePlacement,
  type ApprovalPackageRequest,
  type ApprovalPackageResponse,
  type EvidencePlacementPlan,
  type EvidencePlacementResult,
  type ExternalResource,
  type FolderGeneration,
  type LtrRecord,
  type ProjectTestPlanDraft,
  type Project
} from "../../api/client";
import { configuredFolderResources } from "./projectFolderResourceSelectors";

export type WorkbenchBaselineItem = {
  title: string;
  value: string;
};

export type ProjectWorkbenchModel = {
  approvalInput: ApprovalPackageRequest;
  approvalPreview: ApprovalPackageResponse | null;
  approvalResult: ApprovalPackageResponse | null;
  baselineItems: WorkbenchBaselineItem[];
  error: string | null;
  evidencePlan: EvidencePlacementPlan | null;
  evidenceResult: EvidencePlacementResult | null;
  executingApprovalPackage: boolean;
  folderReady: boolean;
  folderResources: {
    outputRoot: ExternalResource | null;
    template: ExternalResource | null;
  };
  latestLtr: string | null;
  message: string | null;
  matrixDraft: ProjectTestPlanDraft | null;
  matrixDraftError: string | null;
  matrixDraftLoading: boolean;
  placingEvidence: boolean;
  previewingApprovalPackage: boolean;
  previewingEvidence: boolean;
  project: Project | null;
  projectId: string;
  setApprovalInput: (next: ApprovalPackageRequest) => void;
  onFolderCreated: (generation: FolderGeneration) => Promise<void>;
  onExecuteApprovalPackage: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
  onPreviewApprovalPackage: () => Promise<void>;
  onPreviewEvidence: () => Promise<void>;
};

export function useProjectWorkbenchModel(projectId: string): ProjectWorkbenchModel {
  const [project, setProject] = useState<Project | null>(null);
  const [ltrs, setLtrs] = useState<LtrRecord[]>([]);
  const [resources, setResources] = useState<ExternalResource[]>([]);
  const [evidencePlan, setEvidencePlan] = useState<EvidencePlacementPlan | null>(null);
  const [evidenceResult, setEvidenceResult] = useState<EvidencePlacementResult | null>(null);
  const [previewingEvidence, setPreviewingEvidence] = useState(false);
  const [placingEvidence, setPlacingEvidence] = useState(false);
  const [approvalInput, setApprovalInput] = useState<ApprovalPackageRequest>({
    project_folder_path: "",
    completed_application_form_path: "",
    test_record_output_path: "",
    fee_evaluation_output_path: null,
    evidence_source_paths: [],
    overwrite: false
  });
  const [approvalPreview, setApprovalPreview] = useState<ApprovalPackageResponse | null>(null);
  const [approvalResult, setApprovalResult] = useState<ApprovalPackageResponse | null>(null);
  const [previewingApprovalPackage, setPreviewingApprovalPackage] = useState(false);
  const [executingApprovalPackage, setExecutingApprovalPackage] = useState(false);
  const [matrixDraft, setMatrixDraft] = useState<ProjectTestPlanDraft | null>(null);
  const [matrixDraftLoading, setMatrixDraftLoading] = useState(false);
  const [matrixDraftError, setMatrixDraftError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkbench(projectId, setProject, setLtrs, setResources, setError);
    void loadMatrixDraft(projectId, setMatrixDraft, setMatrixDraftLoading, setMatrixDraftError);
  }, [projectId]);

  const folderReady = project?.status === "folder_created";
  const latestLtr = ltrs.length > 0 ? ltrs[ltrs.length - 1].ltr_number : null;
  const folderResources = configuredFolderResources(resources);
  const baselineItems = useMemo(
    () => [
      { title: "Created project", value: project ? "Yes" : "Loading" },
      {
        title: "LTR Number registered",
        value: latestLtr ? `Yes (${latestLtr})` : "No"
      },
      { title: "Project folder", value: folderReady ? "Created" : "Not recorded" },
      {
        title: "Source materials",
        value: folderReady ? "Evidence placement available" : "Available after folder creation"
      }
    ],
    [folderReady, latestLtr, project]
  );

  async function onPreviewEvidence(): Promise<void> {
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

  async function onPlaceEvidence(): Promise<void> {
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

  async function onFolderCreated(_generation: FolderGeneration): Promise<void> {
    setEvidencePlan(null);
    setEvidenceResult(null);
    setApprovalPreview(null);
    setApprovalResult(null);
    setMessage("Project folder created. Evidence placement is now available.");
    await loadWorkbench(projectId, setProject, setLtrs, setResources, setError);
  }

  async function onPreviewApprovalPackage(): Promise<void> {
    setPreviewingApprovalPackage(true);
    try {
      const result = await previewApprovalPackage(projectId, approvalInput);
      setApprovalPreview(result);
      setApprovalResult(null);
      setMessage(
        result.blockers.length > 0
          ? "Approval package preview has blockers."
          : "Approval package preview is ready."
      );
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewingApprovalPackage(false);
    }
  }

  async function onExecuteApprovalPackage(): Promise<void> {
    setExecutingApprovalPackage(true);
    try {
      const result = await executeApprovalPackage(projectId, approvalInput);
      setApprovalResult(result);
      setApprovalPreview(result);
      setMessage("Approval package placement completed.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setExecutingApprovalPackage(false);
    }
  }

  return {
    approvalInput,
    approvalPreview,
    approvalResult,
    baselineItems,
    error,
    evidencePlan,
    evidenceResult,
    executingApprovalPackage,
    folderReady,
    folderResources,
    latestLtr,
    message,
    matrixDraft,
    matrixDraftError,
    matrixDraftLoading,
    placingEvidence,
    previewingApprovalPackage,
    previewingEvidence,
    project,
    projectId,
    setApprovalInput,
    onFolderCreated,
    onExecuteApprovalPackage,
    onPlaceEvidence,
    onPreviewApprovalPackage,
    onPreviewEvidence
  };
}

async function loadWorkbench(
  projectId: string,
  setProject: (project: Project | null) => void,
  setLtrs: (ltrs: LtrRecord[]) => void,
  setResources: (resources: ExternalResource[]) => void,
  setError: (message: string | null) => void
): Promise<void> {
  try {
    setProject(await getProject(projectId));
    setLtrs(await listProjectLtrs(projectId));
    setResources(await listExternalResources());
    setError(null);
  } catch (err) {
    setError((err as Error).message);
  }
}

async function loadMatrixDraft(
  projectId: string,
  setMatrixDraft: (draft: ProjectTestPlanDraft | null) => void,
  setMatrixDraftLoading: (loading: boolean) => void,
  setMatrixDraftError: (message: string | null) => void
): Promise<void> {
  setMatrixDraftLoading(true);
  try {
    const drafts = await listProjectTestPlanDrafts(projectId);
    const activeDraftSummary = drafts.find((draft) => draft.status !== "superseded");
    if (!activeDraftSummary) {
      setMatrixDraft(null);
      setMatrixDraftError(null);
      return;
    }
    const draft = await getProjectTestPlanDraft(projectId, activeDraftSummary.draft_id);
    setMatrixDraft(draft);
    setMatrixDraftError(null);
  } catch (err) {
    setMatrixDraft(null);
    setMatrixDraftError((err as Error).message);
  } finally {
    setMatrixDraftLoading(false);
  }
}
