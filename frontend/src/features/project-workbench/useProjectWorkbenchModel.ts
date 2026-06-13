import { useEffect, useMemo, useState } from "react";
import {
  ApiRequestError,
  collectRequestMaterial,
  confirmProjectTestPlanMatrixDraft,
  createProjectTestPlanDraft,
  executeApprovalPackage,
  fetchActiveConfirmedMatrixSnapshot,
  fetchConfirmedMatrixRuntimeProjectionSnapshot,
  fetchOfficialFolderCheck,
  fetchPublicDriveUploadPreview,
  fetchProjectPackagePreview,
  fetchOfficialWorkspacePreview,
  fetchRequestMaterialPreview,
  getLatestProjectFolder,
  getProjectOutputStatusSummary,
  getConfirmedFeeLatest,
  fetchProjectSection2SyncPreview,
  getProjectTestPlanDraft,
  getProject,
  getRuntimeProjectionReadOnlySnapshot,
  listProjectTestPlanSourceCandidates,
  previewProjectTestPlanMatrixFromSourceCandidate,
  createOfficialWorkspace,
  previewProjectTestPlanMatrixFromPath,
  listProjectTestPlanDrafts,
  listExternalResources,
  listProjectLtrs,
  placeEvidence,
  previewApprovalPackage,
  previewEvidencePlacement,
  repairOfficialFolderStructure,
  syncProjectSection2FromConfirmedMatrix,
  updateProjectTestPlanMatrixDraft,
  uploadPublicDriveProjectFolder,
  validateProjectTestPlanMatrixDraft,
  type ApprovalPackageRequest,
  type ApprovalPackageResponse,
  type ConfirmedMatrixSnapshot,
  type ConfirmedFeeLatestResponse,
  type EvidencePlacementPlan,
  type EvidencePlacementResult,
  type ExternalResource,
  type FolderGeneration,
  type LtrRecord,
  type MatrixPreviewResponse,
  type MatrixSourceCandidate,
  type MatrixSourceCandidatesResponse,
  type MatrixValidationSummary,
  type Project,
  type ProjectPackagePreview,
  type OfficialFolderCheckPreview,
  type OfficialFolderRepairResponse,
  type OfficialWorkspaceCreateResponse,
  type OfficialWorkspacePreview,
  type PublicDriveUploadPreview,
  type PublicDriveUploadResult,
  type RequestMaterialPreview,
  type ProjectSection2SyncRequest,
  type ProjectSection2SyncResponse,
  type ProjectTestPlanDraftGroup,
  type ProjectTestPlanDraft,
  type ProjectOutputStatusSummary,
  type RuntimeProjectionSnapshotRequest,
  type RuntimeProjectionSnapshotResponse
} from "../../api/client";
import {
  deriveWorkbenchVersionStatus,
  type WorkbenchVersionStatus
} from "./projectWorkbenchVersionSelectors";
import { configuredFolderResources } from "./projectFolderResourceSelectors";
import {
  buildDraftCreateRequestFromPreview,
  buildManualStarterDraftCreateRequest
} from "./projectWorkbenchMatrixHelpers";

export type WorkbenchBaselineItem = {
  title: string;
  value: string;
};

export type ProjectWorkbenchModel = {
  approvalInput: ApprovalPackageRequest;
  approvalInputSources: ApprovalInputSources;
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
  activeConfirmedMatrixSnapshot: ConfirmedMatrixSnapshot | null;
  activeConfirmedMatrixLoading: boolean;
  confirmedFeeLatest: ConfirmedFeeLatestResponse | null;
  packagePreview: ProjectPackagePreview | null;
  packagePreviewLoading: boolean;
  packagePreviewError: string | null;
  officialWorkspacePreview: OfficialWorkspacePreview | null;
  officialWorkspaceLoading: boolean;
  officialWorkspaceCreating: boolean;
  officialWorkspaceError: string | null;
  officialWorkspaceResult: OfficialWorkspaceCreateResponse | null;
  officialFolderCheckPreview: OfficialFolderCheckPreview | null;
  officialFolderCheckLoading: boolean;
  officialFolderCheckRepairing: boolean;
  officialFolderCheckError: string | null;
  officialFolderRepairResult: OfficialFolderRepairResponse | null;
  publicDriveUploadPreview: PublicDriveUploadPreview | null;
  publicDriveUploadLoading: boolean;
  publicDriveUploading: boolean;
  publicDriveUploadError: string | null;
  publicDriveUploadResult: PublicDriveUploadResult | null;
  requestMaterialPreview: RequestMaterialPreview | null;
  requestMaterialLoading: boolean;
  requestMaterialCollecting: boolean;
  requestMaterialError: string | null;
  section2SyncPreview: ProjectSection2SyncResponse | null;
  section2SyncLoading: boolean;
  section2SyncSyncing: boolean;
  section2SyncError: string | null;
  matrixAuthorityDraft: ProjectTestPlanDraft | null;
  matrixCandidateDraft: ProjectTestPlanDraft | null;
  matrixDraft: ProjectTestPlanDraft | null;
  matrixDraftEditableGroups: ProjectTestPlanDraftGroup[];
  matrixDraftError: string | null;
  matrixDraftLoading: boolean;
  matrixSaving: boolean;
  matrixValidating: boolean;
  matrixConfirming: boolean;
  matrixValidation: MatrixValidationSummary | null;
  matrixSourceCandidates: MatrixSourceCandidate[];
  matrixSourceCandidateWarnings: string[];
  matrixSourceCandidatesLoading: boolean;
  matrixSelectedSourceAssetId: string | null;
  runtimeProjectionError: string | null;
  runtimeProjectionLoading: boolean;
  runtimeProjectionSnapshot: RuntimeProjectionSnapshotResponse | null;
  runtimeAuthoritySync: {
    authorityVersion: number | null;
    candidateVersion: number | null;
    projectionMatrixReference: string | null;
    projectionMatchesAuthority: boolean | null;
    hasUnconfirmedCandidate: boolean;
    selectedTokenCleared: boolean;
  };
  runtimeSelectedTokenReference: string | null;
  matrixStarterBrowseHint: string | null;
  matrixStarterSourcePath: string;
  matrixStarterPreview: MatrixPreviewResponse | null;
  matrixStarterPreviewing: boolean;
  matrixStarterCreatingFromPreview: boolean;
  matrixStarterCreatingManual: boolean;
  matrixStarterError: string | null;
  versionStatus: WorkbenchVersionStatus;
  placingEvidence: boolean;
  previewingApprovalPackage: boolean;
  previewingEvidence: boolean;
  project: Project | null;
  projectId: string;
  setApprovalInput: (next: ApprovalPackageRequest) => void;
  setRuntimeSelectedTokenReference: (value: string | null) => void;
  setMatrixStarterSourcePath: (value: string) => void;
  setMatrixSelectedSourceAssetId: (value: string | null) => void;
  setMatrixDraftEditableGroups: (groups: ProjectTestPlanDraftGroup[]) => void;
  onPreviewMatrixStarterFromCandidate: () => Promise<void>;
  onPreviewMatrixStarterFromPath: () => Promise<void>;
  onBrowseMatrixStarterFallback: () => void;
  onCreateMatrixDraftFromPreview: () => Promise<void>;
  onCreateManualMatrixDraft: () => Promise<void>;
  onSaveMatrixDraft: () => Promise<void>;
  onValidateMatrixDraft: () => Promise<void>;
  onConfirmMatrixDraft: () => Promise<void>;
  onFolderCreated: (generation: FolderGeneration) => Promise<void>;
  onRefreshPackagePreview: () => Promise<void>;
  onRefreshOfficialWorkspacePreview: () => Promise<void>;
  onCreateOfficialWorkspace: () => Promise<void>;
  onRefreshOfficialFolderCheck: () => Promise<void>;
  onRepairOfficialFolderStructure: () => Promise<void>;
  onRefreshPublicDriveUploadPreview: () => Promise<void>;
  onUploadPublicDriveProjectFolder: () => Promise<void>;
  onRefreshRequestMaterial: () => Promise<void>;
  onCollectRequestMaterial: () => Promise<void>;
  onRefreshSection2Sync: () => Promise<void>;
  onSyncSection2: (input: ProjectSection2SyncRequest) => Promise<void>;
  onExecuteApprovalPackage: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
  onPreviewApprovalPackage: () => Promise<void>;
  onPreviewEvidence: () => Promise<void>;
};

export type ApprovalInputSource = "auto" | "manual";

export type ApprovalInputSources = {
  project_folder_path: ApprovalInputSource;
  completed_application_form_path: ApprovalInputSource;
  test_record_output_path: ApprovalInputSource;
  fee_evaluation_output_path: ApprovalInputSource;
  evidence_source_paths: ApprovalInputSource;
};

const DEFAULT_APPROVAL_INPUT_SOURCES: ApprovalInputSources = {
  project_folder_path: "auto",
  completed_application_form_path: "auto",
  test_record_output_path: "auto",
  fee_evaluation_output_path: "auto",
  evidence_source_paths: "auto"
};

export function useProjectWorkbenchModel(projectId: string): ProjectWorkbenchModel {
  const [project, setProject] = useState<Project | null>(null);
  const [ltrs, setLtrs] = useState<LtrRecord[]>([]);
  const [resources, setResources] = useState<ExternalResource[]>([]);
  const [evidencePlan, setEvidencePlan] = useState<EvidencePlacementPlan | null>(null);
  const [evidenceResult, setEvidenceResult] = useState<EvidencePlacementResult | null>(null);
  const [previewingEvidence, setPreviewingEvidence] = useState(false);
  const [placingEvidence, setPlacingEvidence] = useState(false);
  const [approvalInput, setApprovalInputState] = useState<ApprovalPackageRequest>({
    project_folder_path: "",
    completed_application_form_path: "",
    test_record_output_path: "",
    fee_evaluation_output_path: null,
    evidence_source_paths: [],
    overwrite: false
  });
  const [approvalInputSources, setApprovalInputSources] = useState<ApprovalInputSources>(
    DEFAULT_APPROVAL_INPUT_SOURCES
  );
  const [approvalPreview, setApprovalPreview] = useState<ApprovalPackageResponse | null>(null);
  const [approvalResult, setApprovalResult] = useState<ApprovalPackageResponse | null>(null);
  const [previewingApprovalPackage, setPreviewingApprovalPackage] = useState(false);
  const [executingApprovalPackage, setExecutingApprovalPackage] = useState(false);
  const [matrixDraft, setMatrixDraft] = useState<ProjectTestPlanDraft | null>(null);
  const [matrixAuthorityDraft, setMatrixAuthorityDraft] = useState<ProjectTestPlanDraft | null>(null);
  const [matrixCandidateDraft, setMatrixCandidateDraft] = useState<ProjectTestPlanDraft | null>(null);
  const [matrixDraftEditableGroups, setMatrixDraftEditableGroups] = useState<
    ProjectTestPlanDraftGroup[]
  >([]);
  const [matrixDraftLoading, setMatrixDraftLoading] = useState(false);
  const [matrixDraftError, setMatrixDraftError] = useState<string | null>(null);
  const [matrixSaving, setMatrixSaving] = useState(false);
  const [matrixValidating, setMatrixValidating] = useState(false);
  const [matrixConfirming, setMatrixConfirming] = useState(false);
  const [matrixValidation, setMatrixValidation] = useState<MatrixValidationSummary | null>(null);
  const [matrixSourceCandidates, setMatrixSourceCandidates] = useState<MatrixSourceCandidate[]>([]);
  const [matrixSourceCandidateWarnings, setMatrixSourceCandidateWarnings] = useState<string[]>([]);
  const [matrixSourceCandidatesLoading, setMatrixSourceCandidatesLoading] = useState(false);
  const [matrixSelectedSourceAssetId, setMatrixSelectedSourceAssetIdState] = useState<string | null>(null);
  const [runtimeProjectionSnapshot, setRuntimeProjectionSnapshot] =
    useState<RuntimeProjectionSnapshotResponse | null>(null);
  const [runtimeProjectionLoading, setRuntimeProjectionLoading] = useState(false);
  const [runtimeProjectionError, setRuntimeProjectionError] = useState<string | null>(null);
  const [runtimeSelectedTokenReference, setRuntimeSelectedTokenReference] = useState<string | null>(null);
  const [runtimeSelectedTokenCleared, setRuntimeSelectedTokenCleared] = useState(false);
  const [matrixStarterBrowseHint, setMatrixStarterBrowseHint] = useState<string | null>(null);
  const [matrixStarterSourcePath, setMatrixStarterSourcePathState] = useState("");
  const [matrixStarterPreview, setMatrixStarterPreview] = useState<MatrixPreviewResponse | null>(null);
  const [matrixStarterPreviewSourceAssetId, setMatrixStarterPreviewSourceAssetId] = useState<string | null>(null);
  const [matrixStarterPreviewing, setMatrixStarterPreviewing] = useState(false);
  const [matrixStarterCreatingFromPreview, setMatrixStarterCreatingFromPreview] = useState(false);
  const [matrixStarterCreatingManual, setMatrixStarterCreatingManual] = useState(false);
  const [matrixStarterError, setMatrixStarterError] = useState<string | null>(null);
  const [trackedDraftVersion, setTrackedDraftVersion] = useState<number | null>(null);
  const [outputStatusSummary, setOutputStatusSummary] = useState<ProjectOutputStatusSummary | null>(
    null
  );
  const [latestProjectFolderPath, setLatestProjectFolderPath] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeConfirmedMatrixSnapshot, setActiveConfirmedMatrixSnapshot] =
    useState<ConfirmedMatrixSnapshot | null>(null);
  const [activeConfirmedMatrixLoading, setActiveConfirmedMatrixLoading] = useState(true);
  const [confirmedFeeLatest, setConfirmedFeeLatest] =
    useState<ConfirmedFeeLatestResponse | null>(null);
  const [packagePreview, setPackagePreview] = useState<ProjectPackagePreview | null>(null);
  const [packagePreviewLoading, setPackagePreviewLoading] = useState(false);
  const [packagePreviewError, setPackagePreviewError] = useState<string | null>(null);
  const [officialWorkspacePreview, setOfficialWorkspacePreview] =
    useState<OfficialWorkspacePreview | null>(null);
  const [officialWorkspaceLoading, setOfficialWorkspaceLoading] = useState(false);
  const [officialWorkspaceCreating, setOfficialWorkspaceCreating] = useState(false);
  const [officialWorkspaceError, setOfficialWorkspaceError] = useState<string | null>(null);
  const [officialWorkspaceResult, setOfficialWorkspaceResult] =
    useState<OfficialWorkspaceCreateResponse | null>(null);
  const [officialFolderCheckPreview, setOfficialFolderCheckPreview] =
    useState<OfficialFolderCheckPreview | null>(null);
  const [officialFolderCheckLoading, setOfficialFolderCheckLoading] = useState(false);
  const [officialFolderCheckRepairing, setOfficialFolderCheckRepairing] = useState(false);
  const [officialFolderCheckError, setOfficialFolderCheckError] = useState<string | null>(null);
  const [officialFolderRepairResult, setOfficialFolderRepairResult] =
    useState<OfficialFolderRepairResponse | null>(null);
  const [publicDriveUploadPreview, setPublicDriveUploadPreview] =
    useState<PublicDriveUploadPreview | null>(null);
  const [publicDriveUploadLoading, setPublicDriveUploadLoading] = useState(false);
  const [publicDriveUploading, setPublicDriveUploading] = useState(false);
  const [publicDriveUploadError, setPublicDriveUploadError] = useState<string | null>(null);
  const [publicDriveUploadResult, setPublicDriveUploadResult] =
    useState<PublicDriveUploadResult | null>(null);
  const [requestMaterialPreview, setRequestMaterialPreview] =
    useState<RequestMaterialPreview | null>(null);
  const [requestMaterialLoading, setRequestMaterialLoading] = useState(false);
  const [requestMaterialCollecting, setRequestMaterialCollecting] = useState(false);
  const [requestMaterialError, setRequestMaterialError] = useState<string | null>(null);
  const [section2SyncPreview, setSection2SyncPreview] =
    useState<ProjectSection2SyncResponse | null>(null);
  const [section2SyncLoading, setSection2SyncLoading] = useState(false);
  const [section2SyncSyncing, setSection2SyncSyncing] = useState(false);
  const [section2SyncError, setSection2SyncError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkbench(
      projectId,
      setProject,
      setLtrs,
      setResources,
      setLatestProjectFolderPath,
      setOutputStatusSummary,
      setConfirmedFeeLatest,
      setError
    );
    void reloadMatrixDraft();
    void loadActiveConfirmedMatrixSnapshot(
      projectId,
      setActiveConfirmedMatrixSnapshot,
      setActiveConfirmedMatrixLoading
    );
    void onRefreshSection2Sync();
    void onRefreshPackagePreview();
    void onRefreshOfficialWorkspacePreview();
    void onRefreshRequestMaterial();
    void onRefreshOfficialFolderCheck();
    void onRefreshPublicDriveUploadPreview();
    void loadMatrixSourceCandidates(
      projectId,
      setMatrixSourceCandidates,
      setMatrixSourceCandidateWarnings,
      setMatrixSourceCandidatesLoading,
      setMatrixSelectedSourceAssetIdState
    );
  }, [projectId]);

  useEffect(() => {
    const autofill = deriveApprovalInputAutofill({
      latestProjectFolderPath,
      evidencePlan,
      approvalPreview,
      approvalResult
    });
    if (!autofill) {
      return;
    }
    setApprovalInputState((previous) =>
      mergeApprovalInput(previous, autofill, approvalInputSources)
    );
  }, [
    approvalInputSources,
    approvalPreview,
    approvalResult,
    evidencePlan,
    latestProjectFolderPath
  ]);

  useEffect(() => {
    if (!matrixAuthorityDraft) {
      setTrackedDraftVersion(null);
      return;
    }
    if (trackedDraftVersion === null) {
      setTrackedDraftVersion(matrixAuthorityDraft.version);
    }
  }, [matrixAuthorityDraft, trackedDraftVersion]);

  const versionStatus = useMemo(
    () =>
      deriveWorkbenchVersionStatus({
        activeDraftVersion: matrixAuthorityDraft?.version ?? null,
        trackedDraftVersion,
        outputStatusSummary,
        approvalInput,
        approvalInputSources,
        approvalPreview,
        approvalResult
      }),
    [
      approvalInput,
      approvalInputSources,
      approvalPreview,
      approvalResult,
      matrixAuthorityDraft,
      outputStatusSummary,
      trackedDraftVersion
    ]
  );

  useEffect(() => {
    if (!project) {
      setRuntimeProjectionSnapshot(null);
      setRuntimeProjectionError(null);
      return;
    }

    if (activeConfirmedMatrixSnapshot) {
      setRuntimeProjectionLoading(true);
      setRuntimeProjectionError(null);
      void fetchConfirmedMatrixRuntimeProjectionSnapshot(
        projectId,
        runtimeSelectedTokenReference
      )
        .then((snapshot) => setRuntimeProjectionSnapshot(snapshot))
        .catch((err) =>
          setRuntimeProjectionError(
            err instanceof Error ? err.message : "Failed to load runtime projection snapshot."
          )
        )
        .finally(() => setRuntimeProjectionLoading(false));
      return;
    }

    const projectionDraft = matrixAuthorityDraft ?? matrixDraft;
    if (!projectionDraft) {
      setRuntimeProjectionSnapshot(null);
      setRuntimeProjectionError(null);
      return;
    }

    const request = buildRuntimeProjectionRequest({
      project,
      draft: projectionDraft,
      selectedTokenReference: runtimeSelectedTokenReference,
      versionStatus,
      validation: matrixValidation
    });
    if (request.rows.length === 0) {
      setRuntimeProjectionSnapshot(null);
      setRuntimeProjectionError(null);
      return;
    }

    setRuntimeProjectionLoading(true);
    setRuntimeProjectionError(null);
    void getRuntimeProjectionReadOnlySnapshot(request)
      .then((snapshot) => setRuntimeProjectionSnapshot(snapshot))
      .catch((err) =>
        setRuntimeProjectionError(
          err instanceof Error ? err.message : "Failed to load runtime projection snapshot."
        )
      )
      .finally(() => setRuntimeProjectionLoading(false));
  }, [
    activeConfirmedMatrixSnapshot,
    matrixAuthorityDraft,
    matrixDraft,
    matrixValidation,
    project,
    projectId,
    runtimeSelectedTokenReference,
    versionStatus
  ]);

  useEffect(() => {
    if (!runtimeProjectionSnapshot || !runtimeSelectedTokenReference) {
      setRuntimeSelectedTokenCleared(false);
      return;
    }
    const tokenExists = runtimeProjectionSnapshot.matrix_overview.groups.some((group) =>
      group.tokens.some((token) => token.token_reference === runtimeSelectedTokenReference)
    );
    if (!tokenExists) {
      setRuntimeSelectedTokenReference(null);
      setRuntimeSelectedTokenCleared(true);
      setMessage("Selected step token is no longer available in the current projection and was cleared.");
    } else {
      setRuntimeSelectedTokenCleared(false);
    }
  }, [runtimeProjectionSnapshot, runtimeSelectedTokenReference]);

  const runtimeAuthoritySync = useMemo(() => {
    const authorityVersion = matrixAuthorityDraft?.version ?? null;
    const candidateVersion = matrixCandidateDraft?.version ?? null;
    const projectionMatrixReference = runtimeProjectionSnapshot?.matrix_reference ?? null;
    const expectedProjectionReference = matrixAuthorityDraft
      ? `${matrixAuthorityDraft.draft_id}:v${matrixAuthorityDraft.version}`
      : null;
    const projectionMatchesAuthority =
      expectedProjectionReference && projectionMatrixReference
        ? expectedProjectionReference === projectionMatrixReference
        : null;
    return {
      authorityVersion,
      candidateVersion,
      projectionMatrixReference,
      projectionMatchesAuthority,
      hasUnconfirmedCandidate: matrixCandidateDraft !== null,
      selectedTokenCleared: runtimeSelectedTokenCleared
    };
  }, [matrixAuthorityDraft, matrixCandidateDraft, runtimeProjectionSnapshot, runtimeSelectedTokenCleared]);

  const hasCompletedOfficialWorkspace = officialWorkspacePreview?.status === "completed";
  const folderReady = project?.status === "folder_created" || hasCompletedOfficialWorkspace;
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
    await loadWorkbench(
      projectId,
      setProject,
      setLtrs,
      setResources,
      setLatestProjectFolderPath,
      setOutputStatusSummary,
      setConfirmedFeeLatest,
      setError
    );
    await onRefreshPackagePreview();
  }

  async function onRefreshPackagePreview(): Promise<void> {
    setPackagePreviewLoading(true);
    try {
      const preview = await fetchProjectPackagePreview(projectId);
      setPackagePreview(preview);
      setPackagePreviewError(null);
    } catch (err) {
      setPackagePreview(null);
      setPackagePreviewError((err as Error).message);
    } finally {
      setPackagePreviewLoading(false);
    }
  }

  async function onRefreshOfficialWorkspacePreview(): Promise<void> {
    setOfficialWorkspaceLoading(true);
    try {
      const preview = await fetchOfficialWorkspacePreview(projectId);
      setOfficialWorkspacePreview(preview);
      setOfficialWorkspaceError(null);
    } catch (err) {
      setOfficialWorkspacePreview(null);
      setOfficialWorkspaceError((err as Error).message);
    } finally {
      setOfficialWorkspaceLoading(false);
    }
  }

  async function onCreateOfficialWorkspace(): Promise<void> {
    setOfficialWorkspaceCreating(true);
    try {
      const result = await createOfficialWorkspace(projectId);
      setOfficialWorkspaceResult(result);
      setMessage("Local project folder created.");
      setError(null);
      setOfficialWorkspaceError(null);
      await onRefreshOfficialWorkspacePreview();
      await onRefreshPackagePreview();
      await onRefreshRequestMaterial();
      await onRefreshOfficialFolderCheck();
      await onRefreshPublicDriveUploadPreview();
    } catch (err) {
      setOfficialWorkspaceError((err as Error).message);
    } finally {
      setOfficialWorkspaceCreating(false);
    }
  }

  async function onRefreshOfficialFolderCheck(): Promise<void> {
    setOfficialFolderCheckLoading(true);
    try {
      const preview = await fetchOfficialFolderCheck(projectId);
      setOfficialFolderCheckPreview(preview);
      setOfficialFolderCheckError(null);
    } catch (err) {
      setOfficialFolderCheckPreview(null);
      setOfficialFolderCheckError((err as Error).message);
    } finally {
      setOfficialFolderCheckLoading(false);
    }
  }

  async function onRepairOfficialFolderStructure(): Promise<void> {
    setOfficialFolderCheckRepairing(true);
    try {
      const result = await repairOfficialFolderStructure(projectId);
      setOfficialFolderRepairResult(result);
      setOfficialFolderCheckPreview(result.preview);
      setOfficialFolderCheckError(null);
      setMessage(
        result.repair_status === "partial"
          ? "Folder repair partially completed. Review remaining folder issues."
          : "Folder structure repaired."
      );
      await onRefreshPackagePreview();
      await onRefreshPublicDriveUploadPreview();
    } catch (err) {
      setOfficialFolderCheckError((err as Error).message);
    } finally {
      setOfficialFolderCheckRepairing(false);
    }
  }

  async function onRefreshRequestMaterial(): Promise<void> {
    setRequestMaterialLoading(true);
    try {
      const preview = await fetchRequestMaterialPreview(projectId);
      setRequestMaterialPreview(preview);
      setRequestMaterialError(null);
    } catch (err) {
      setRequestMaterialPreview(null);
      setRequestMaterialError((err as Error).message);
    } finally {
      setRequestMaterialLoading(false);
    }
  }

  async function onCollectRequestMaterial(): Promise<void> {
    setRequestMaterialCollecting(true);
    try {
      const result = await collectRequestMaterial(projectId);
      setRequestMaterialPreview(result);
      setRequestMaterialError(null);
      setMessage(
        result.status === "review_required"
          ? "Request material collected. Review undecided attachments before Submitted Material placement."
          : result.status === "partial"
          ? "Request material partially collected. Review missing request material."
          : "Request material collected."
      );
      await onRefreshPackagePreview();
      await onRefreshOfficialFolderCheck();
      await onRefreshPublicDriveUploadPreview();
    } catch (err) {
      setRequestMaterialError((err as Error).message);
    } finally {
      setRequestMaterialCollecting(false);
    }
  }

  async function onRefreshPublicDriveUploadPreview(): Promise<void> {
    setPublicDriveUploadLoading(true);
    try {
      const preview = await fetchPublicDriveUploadPreview(projectId);
      setPublicDriveUploadPreview(preview);
      setPublicDriveUploadError(null);
    } catch (err) {
      setPublicDriveUploadPreview(null);
      setPublicDriveUploadError((err as Error).message);
    } finally {
      setPublicDriveUploadLoading(false);
    }
  }

  async function onUploadPublicDriveProjectFolder(): Promise<void> {
    setPublicDriveUploading(true);
    try {
      const result = await uploadPublicDriveProjectFolder(projectId);
      setPublicDriveUploadResult(result);
      setPublicDriveUploadPreview(result.preview);
      setPublicDriveUploadError(null);
      setMessage(
        result.upload_status === "partial"
          ? "Public-drive upload partially completed. Review remaining items."
          : "Project Folder uploaded to public drive."
      );
    } catch (err) {
      setPublicDriveUploadError((err as Error).message);
    } finally {
      setPublicDriveUploading(false);
    }
  }

  async function onRefreshSection2Sync(): Promise<void> {
    setSection2SyncLoading(true);
    try {
      const preview = await fetchProjectSection2SyncPreview(projectId);
      setSection2SyncPreview(preview);
      setSection2SyncError(null);
    } catch (err) {
      setSection2SyncPreview(null);
      setSection2SyncError((err as Error).message);
    } finally {
      setSection2SyncLoading(false);
    }
  }

  async function onSyncSection2(input: ProjectSection2SyncRequest): Promise<void> {
    setSection2SyncSyncing(true);
    try {
      const result = await syncProjectSection2FromConfirmedMatrix(projectId, input);
      setSection2SyncPreview(result);
      setSection2SyncError(null);
      setMessage("Section 2 dates synced from Confirmed Matrix.");
      await onRefreshPackagePreview();
      setError(null);
    } catch (err) {
      setSection2SyncError((err as Error).message);
    } finally {
      setSection2SyncSyncing(false);
    }
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
      if (matrixAuthorityDraft) {
        setTrackedDraftVersion(matrixAuthorityDraft.version);
      }
      await refreshOutputStatus(projectId, setOutputStatusSummary);
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
      if (matrixAuthorityDraft) {
        setTrackedDraftVersion(matrixAuthorityDraft.version);
      }
      await refreshOutputStatus(projectId, setOutputStatusSummary);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setExecutingApprovalPackage(false);
    }
  }

  function setApprovalInput(next: ApprovalPackageRequest): void {
    setApprovalInputSources((previous) => ({
      project_folder_path:
        next.project_folder_path !== approvalInput.project_folder_path
          ? "manual"
          : previous.project_folder_path,
      completed_application_form_path:
        next.completed_application_form_path !== approvalInput.completed_application_form_path
          ? "manual"
          : previous.completed_application_form_path,
      test_record_output_path:
        next.test_record_output_path !== approvalInput.test_record_output_path
          ? "manual"
          : previous.test_record_output_path,
      fee_evaluation_output_path:
        (next.fee_evaluation_output_path ?? null) !==
        (approvalInput.fee_evaluation_output_path ?? null)
          ? "manual"
          : previous.fee_evaluation_output_path,
      evidence_source_paths:
        normalizeLines(next.evidence_source_paths) !==
        normalizeLines(approvalInput.evidence_source_paths)
          ? "manual"
          : previous.evidence_source_paths
    }));
    setApprovalInputState(next);
  }

  function setMatrixStarterSourcePath(value: string): void {
    setMatrixStarterSourcePathState(value);
    setMatrixStarterError(null);
    setMatrixStarterBrowseHint(null);
  }

  function setMatrixSelectedSourceAssetId(value: string | null): void {
    setMatrixSelectedSourceAssetIdState(value);
    setMatrixStarterError(null);
    setMatrixStarterBrowseHint(null);
  }

  function onBrowseMatrixStarterFallback(): void {
    setMatrixStarterBrowseHint(
      "Browse is available in the desktop workspace. In browser mode, paste the full `.docx` path."
    );
  }

  async function onPreviewMatrixStarterFromCandidate(): Promise<void> {
    if (!matrixSelectedSourceAssetId) {
      setMatrixStarterError("Select a project source candidate first.");
      return;
    }
    setMatrixStarterPreviewing(true);
    try {
      const preview = await previewProjectTestPlanMatrixFromSourceCandidate(
        projectId,
        matrixSelectedSourceAssetId
      );
      setMatrixStarterPreview(preview);
      setMatrixStarterPreviewSourceAssetId(matrixSelectedSourceAssetId);
      setMatrixStarterError(null);
      setMatrixStarterBrowseHint(null);
      setMessage(
        preview.blockers.length > 0
          ? "Matrix preview has blockers."
          : "Matrix preview is ready for draft creation."
      );
      setError(null);
    } catch (err) {
      setMatrixStarterError((err as Error).message);
    } finally {
      setMatrixStarterPreviewing(false);
    }
  }

  async function onPreviewMatrixStarterFromPath(): Promise<void> {
    const sourcePath = matrixStarterSourcePath.trim();
    if (!sourcePath) {
      setMatrixStarterError("Source path is required.");
      return;
    }
    setMatrixStarterPreviewing(true);
    try {
      const preview = await previewProjectTestPlanMatrixFromPath({
        source_path: sourcePath,
        project_id: projectId
      });
      setMatrixStarterPreview(preview);
      setMatrixStarterPreviewSourceAssetId(null);
      setMatrixStarterError(null);
      setMessage(
        preview.blockers.length > 0
          ? "Matrix preview has blockers."
          : "Matrix preview is ready for draft creation."
      );
      setError(null);
    } catch (err) {
      setMatrixStarterError((err as Error).message);
    } finally {
      setMatrixStarterPreviewing(false);
    }
  }

  async function onCreateMatrixDraftFromPreview(): Promise<void> {
    if (!matrixStarterPreview) {
      setMatrixStarterError("Preview the source Matrix before creating a draft.");
      return;
    }
    if (matrixStarterPreview.blockers.length > 0) {
      setMatrixStarterError("Resolve preview blockers before creating a draft.");
      return;
    }
    setMatrixStarterCreatingFromPreview(true);
    try {
      await createProjectTestPlanDraft(
        projectId,
        buildDraftCreateRequestFromPreview(
          matrixStarterPreview,
          matrixStarterPreviewSourceAssetId
        )
      );
      setMessage("Project test-plan draft created from source preview.");
      setError(null);
      setMatrixStarterError(null);
      setMatrixStarterPreview(null);
      setMatrixStarterPreviewSourceAssetId(null);
      await reloadMatrixDraft();
      await refreshOutputStatus(projectId, setOutputStatusSummary);
    } catch (err) {
      setMatrixStarterError((err as Error).message);
    } finally {
      setMatrixStarterCreatingFromPreview(false);
    }
  }

  async function onCreateManualMatrixDraft(): Promise<void> {
    setMatrixStarterCreatingManual(true);
    try {
      await createProjectTestPlanDraft(
        projectId,
        buildManualStarterDraftCreateRequest()
      );
      setMessage("Manual Matrix draft created with explicit Group 1 identity.");
      setError(null);
      setMatrixStarterError(null);
      setMatrixStarterPreview(null);
      setMatrixStarterPreviewSourceAssetId(null);
      await reloadMatrixDraft();
      await refreshOutputStatus(projectId, setOutputStatusSummary);
    } catch (err) {
      setMatrixStarterError((err as Error).message);
    } finally {
      setMatrixStarterCreatingManual(false);
    }
  }

  async function onValidateMatrixDraft(): Promise<void> {
    if (!matrixDraft) {
      return;
    }
    setMatrixValidating(true);
    try {
      const response = await validateProjectTestPlanMatrixDraft(
        projectId,
        matrixDraft.draft_id,
        matrixDraftEditableGroups
      );
      setMatrixValidation(response.validation);
      setMessage(
        response.validation.blockers.length > 0
          ? "Matrix validation has blockers."
          : "Matrix validation passed."
      );
      setError(null);
      setMatrixDraftError(null);
    } catch (err) {
      setMatrixDraftError((err as Error).message);
    } finally {
      setMatrixValidating(false);
    }
  }

  async function onSaveMatrixDraft(): Promise<void> {
    if (!matrixDraft) {
      return;
    }
    setMatrixSaving(true);
    try {
      const response = await updateProjectTestPlanMatrixDraft(
        projectId,
        matrixDraft.draft_id,
        matrixDraftEditableGroups
      );
      setMatrixDraft(response.draft);
      if (response.draft.status === "reviewed") {
        setMatrixAuthorityDraft(response.draft);
        setMatrixCandidateDraft(null);
      } else {
        setMatrixCandidateDraft(response.draft);
      }
      setMatrixDraftEditableGroups(cloneGroups(response.draft.payload.groups));
      setMatrixValidation(response.validation);
      setMessage(
        response.created_new_draft
          ? "Matrix draft was reviewed before edit. A new draft version is created."
          : "Matrix draft saved."
      );
      await refreshOutputStatus(projectId, setOutputStatusSummary);
      setError(null);
      setMatrixDraftError(null);
    } catch (err) {
      setMatrixDraftError((err as Error).message);
    } finally {
      setMatrixSaving(false);
    }
  }

  async function onConfirmMatrixDraft(): Promise<void> {
    if (!matrixDraft) {
      return;
    }
    setMatrixConfirming(true);
    try {
      const response = await confirmProjectTestPlanMatrixDraft(
        projectId,
        matrixDraft.draft_id,
        matrixDraftEditableGroups
      );
      setMatrixDraft(response.draft);
      setMatrixAuthorityDraft(response.draft);
      setMatrixCandidateDraft(null);
      setMatrixDraftEditableGroups(cloneGroups(response.draft.payload.groups));
      setMatrixValidation(response.validation);
      setMessage("Matrix draft confirmed as project test-plan authority.");
      await refreshOutputStatus(projectId, setOutputStatusSummary);
      await onRefreshPackagePreview();
      setError(null);
      setMatrixDraftError(null);
    } catch (err) {
      setMatrixDraftError((err as Error).message);
    } finally {
      setMatrixConfirming(false);
    }
  }

  return {
    approvalInput,
    approvalInputSources,
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
    activeConfirmedMatrixSnapshot,
    activeConfirmedMatrixLoading,
    confirmedFeeLatest,
    packagePreview,
    packagePreviewLoading,
    packagePreviewError,
    officialWorkspacePreview,
    officialWorkspaceLoading,
    officialWorkspaceCreating,
    officialWorkspaceError,
    officialWorkspaceResult,
    officialFolderCheckPreview,
    officialFolderCheckLoading,
    officialFolderCheckRepairing,
    officialFolderCheckError,
    officialFolderRepairResult,
    publicDriveUploadPreview,
    publicDriveUploadLoading,
    publicDriveUploading,
    publicDriveUploadError,
    publicDriveUploadResult,
    requestMaterialPreview,
    requestMaterialLoading,
    requestMaterialCollecting,
    requestMaterialError,
    section2SyncPreview,
    section2SyncLoading,
    section2SyncSyncing,
    section2SyncError,
    matrixAuthorityDraft,
    matrixCandidateDraft,
    matrixDraft,
    matrixDraftEditableGroups,
    matrixDraftError,
    matrixDraftLoading,
    matrixSaving,
    matrixValidating,
    matrixConfirming,
    matrixValidation,
    matrixSourceCandidates,
    matrixSourceCandidateWarnings,
    matrixSourceCandidatesLoading,
    matrixSelectedSourceAssetId,
    runtimeProjectionError,
    runtimeProjectionLoading,
    runtimeProjectionSnapshot,
    runtimeAuthoritySync,
    runtimeSelectedTokenReference,
    matrixStarterBrowseHint,
    matrixStarterSourcePath,
    matrixStarterPreview,
    matrixStarterPreviewing,
    matrixStarterCreatingFromPreview,
    matrixStarterCreatingManual,
    matrixStarterError,
    versionStatus,
    placingEvidence,
    previewingApprovalPackage,
    previewingEvidence,
    project,
    projectId,
    setApprovalInput,
    setRuntimeSelectedTokenReference,
    setMatrixStarterSourcePath,
    setMatrixSelectedSourceAssetId,
    setMatrixDraftEditableGroups,
    onPreviewMatrixStarterFromCandidate,
    onPreviewMatrixStarterFromPath,
    onBrowseMatrixStarterFallback,
    onCreateMatrixDraftFromPreview,
    onCreateManualMatrixDraft,
    onSaveMatrixDraft,
    onValidateMatrixDraft,
    onConfirmMatrixDraft,
    onFolderCreated,
    onRefreshPackagePreview,
    onRefreshOfficialWorkspacePreview,
    onCreateOfficialWorkspace,
    onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure,
    onRefreshPublicDriveUploadPreview,
    onUploadPublicDriveProjectFolder,
    onRefreshRequestMaterial,
    onCollectRequestMaterial,
    onRefreshSection2Sync,
    onSyncSection2,
    onExecuteApprovalPackage,
    onPlaceEvidence,
    onPreviewApprovalPackage,
    onPreviewEvidence
  };

  async function reloadMatrixDraft(): Promise<void> {
    await loadMatrixDraft(
      projectId,
      setMatrixAuthorityDraft,
      setMatrixCandidateDraft,
      setMatrixDraft,
      setMatrixDraftEditableGroups,
      setMatrixValidation,
      setMatrixDraftLoading,
      setMatrixDraftError
    );
  }
}

async function loadWorkbench(
  projectId: string,
  setProject: (project: Project | null) => void,
  setLtrs: (ltrs: LtrRecord[]) => void,
  setResources: (resources: ExternalResource[]) => void,
  setLatestProjectFolderPath: (path: string | null) => void,
  setOutputStatusSummary: (summary: ProjectOutputStatusSummary | null) => void,
  setConfirmedFeeLatest: (summary: ConfirmedFeeLatestResponse | null) => void,
  setError: (message: string | null) => void
): Promise<void> {
  try {
    setProject(await getProject(projectId));
    setLtrs(await listProjectLtrs(projectId));
    setResources(await listExternalResources());
    try {
      const folder = await getLatestProjectFolder(projectId);
      setLatestProjectFolderPath(folder.project_folder_path);
    } catch {
      setLatestProjectFolderPath(null);
    }
    try {
      const outputStatus = await getProjectOutputStatusSummary(projectId);
      setOutputStatusSummary(outputStatus);
    } catch {
      setOutputStatusSummary(null);
    }
    try {
      const confirmedFee = await getConfirmedFeeLatest(projectId);
      setConfirmedFeeLatest(confirmedFee);
    } catch {
      setConfirmedFeeLatest(null);
    }
    setError(null);
  } catch (err) {
    setError((err as Error).message);
  }
}

async function loadActiveConfirmedMatrixSnapshot(
  projectId: string,
  setActiveConfirmedMatrixSnapshot: (snapshot: ConfirmedMatrixSnapshot | null) => void,
  setActiveConfirmedMatrixLoading: (loading: boolean) => void
): Promise<void> {
  setActiveConfirmedMatrixLoading(true);
  try {
    const snapshot = await fetchActiveConfirmedMatrixSnapshot(projectId);
    setActiveConfirmedMatrixSnapshot(snapshot);
  } catch (err) {
    if (err instanceof ApiRequestError && err.status === 404) {
      setActiveConfirmedMatrixSnapshot(null);
    } else {
      setActiveConfirmedMatrixSnapshot(null);
    }
  } finally {
    setActiveConfirmedMatrixLoading(false);
  }
}

async function loadMatrixDraft(
  projectId: string,
  setMatrixAuthorityDraft: (draft: ProjectTestPlanDraft | null) => void,
  setMatrixCandidateDraft: (draft: ProjectTestPlanDraft | null) => void,
  setMatrixDraft: (draft: ProjectTestPlanDraft | null) => void,
  setMatrixDraftEditableGroups: (groups: ProjectTestPlanDraftGroup[]) => void,
  setMatrixValidation: (summary: MatrixValidationSummary | null) => void,
  setMatrixDraftLoading: (loading: boolean) => void,
  setMatrixDraftError: (message: string | null) => void
): Promise<void> {
  setMatrixDraftLoading(true);
  try {
    const drafts = await listProjectTestPlanDrafts(projectId);
    const authoritySummary = drafts.find((draft) => draft.status === "reviewed") ?? null;
    const candidateSummary = drafts.find((draft) => draft.status === "draft") ?? null;
    const editTargetSummary = candidateSummary ?? authoritySummary;
    if (!editTargetSummary) {
      setMatrixAuthorityDraft(null);
      setMatrixCandidateDraft(null);
      setMatrixDraft(null);
      setMatrixDraftEditableGroups([]);
      setMatrixValidation(null);
      setMatrixDraftError(null);
      return;
    }
    let authorityDraft: ProjectTestPlanDraft | null = null;
    let candidateDraft: ProjectTestPlanDraft | null = null;
    if (authoritySummary) {
      authorityDraft = await getProjectTestPlanDraft(projectId, authoritySummary.draft_id);
    }
    if (candidateSummary) {
      candidateDraft = await getProjectTestPlanDraft(projectId, candidateSummary.draft_id);
    }
    const draft = candidateDraft ?? authorityDraft;
    setMatrixAuthorityDraft(authorityDraft);
    setMatrixCandidateDraft(candidateDraft);
    setMatrixDraft(draft);
    setMatrixDraftEditableGroups(cloneGroups(draft?.payload.groups));
    setMatrixValidation({
      blockers: draft?.payload.blockers ?? [],
      warnings: draft?.payload.warnings ?? [],
      group_count: draft?.payload.groups?.length ?? 0,
      step_count: (draft?.payload.groups ?? []).reduce(
        (total, group) => total + (group.steps?.length ?? 0),
        0
      )
    });
    setMatrixDraftError(null);
  } catch (err) {
    setMatrixAuthorityDraft(null);
    setMatrixCandidateDraft(null);
    setMatrixDraft(null);
    setMatrixDraftEditableGroups([]);
    setMatrixValidation(null);
    setMatrixDraftError((err as Error).message);
  } finally {
    setMatrixDraftLoading(false);
  }
}

async function loadMatrixSourceCandidates(
  projectId: string,
  setCandidates: (items: MatrixSourceCandidate[]) => void,
  setWarnings: (items: string[]) => void,
  setLoading: (value: boolean) => void,
  setSelectedSourceAssetId: (value: string | null) => void
): Promise<void> {
  setLoading(true);
  try {
    const response: MatrixSourceCandidatesResponse = await listProjectTestPlanSourceCandidates(projectId);
    setCandidates(response.candidates);
    setWarnings(response.warnings);
    setSelectedSourceAssetId(response.candidates[0]?.source_asset_id ?? null);
  } catch {
    setCandidates([]);
    setWarnings([]);
    setSelectedSourceAssetId(null);
  } finally {
    setLoading(false);
  }
}

async function refreshOutputStatus(
  projectId: string,
  setOutputStatusSummary: (summary: ProjectOutputStatusSummary | null) => void
): Promise<void> {
  try {
    setOutputStatusSummary(await getProjectOutputStatusSummary(projectId));
  } catch {
    setOutputStatusSummary(null);
  }
}

function deriveApprovalInputAutofill(input: {
  latestProjectFolderPath: string | null;
  evidencePlan: EvidencePlacementPlan | null;
  approvalPreview: ApprovalPackageResponse | null;
  approvalResult: ApprovalPackageResponse | null;
}): ApprovalPackageRequest | null {
  const { latestProjectFolderPath, evidencePlan, approvalPreview, approvalResult } = input;
  const items = approvalResult?.items ?? approvalPreview?.items ?? [];
  const evidenceItems = evidencePlan?.items ?? [];

  const projectFolderPath =
    evidencePlan?.project_folder_path ??
    approvalResult?.project_folder_path ??
    approvalPreview?.project_folder_path ??
    latestProjectFolderPath ??
    "";

  const completedApplicationFormPath =
    findPathByClassification(items, "application_form") ??
    findPathByCategory(evidenceItems, "application_form") ??
    "";

  const testRecordOutputPath =
    findPathByClassification(items, "test_record") ??
    findPathByName(evidenceItems.map((item) => item.source_path), /(test[_\s-]*record|record)/i) ??
    "";

  const feeEvaluationOutputPath =
    findPathByClassification(items, "fee_evaluation") ??
    findPathByName(evidenceItems.map((item) => item.source_path), /(fee|quotation|price|cost)/i) ??
    null;

  const evidenceSourcePaths = uniquePaths(
    evidenceItems.map((item) => item.source_path)
  );

  if (
    !projectFolderPath &&
    !completedApplicationFormPath &&
    !testRecordOutputPath &&
    !feeEvaluationOutputPath &&
    evidenceSourcePaths.length === 0
  ) {
    return null;
  }

  return {
    project_folder_path: projectFolderPath,
    completed_application_form_path: completedApplicationFormPath,
    test_record_output_path: testRecordOutputPath,
    fee_evaluation_output_path: feeEvaluationOutputPath,
    evidence_source_paths: evidenceSourcePaths,
    overwrite: false
  };
}

function mergeApprovalInput(
  current: ApprovalPackageRequest,
  autofill: ApprovalPackageRequest,
  sources: ApprovalInputSources
): ApprovalPackageRequest {
  return {
    project_folder_path:
      sources.project_folder_path === "auto" && autofill.project_folder_path
        ? autofill.project_folder_path
        : current.project_folder_path,
    completed_application_form_path:
      sources.completed_application_form_path === "auto" &&
      autofill.completed_application_form_path
        ? autofill.completed_application_form_path
        : current.completed_application_form_path,
    test_record_output_path:
      sources.test_record_output_path === "auto" && autofill.test_record_output_path
        ? autofill.test_record_output_path
        : current.test_record_output_path,
    fee_evaluation_output_path:
      sources.fee_evaluation_output_path === "auto"
        ? (autofill.fee_evaluation_output_path ?? current.fee_evaluation_output_path)
        : current.fee_evaluation_output_path,
    evidence_source_paths:
      sources.evidence_source_paths === "auto" && autofill.evidence_source_paths.length > 0
        ? autofill.evidence_source_paths
        : current.evidence_source_paths,
    overwrite: current.overwrite
  };
}

function findPathByClassification(
  items: ApprovalPackageResponse["items"],
  classification: string
): string | null {
  const match = items.find((item) => item.classification === classification);
  return match ? match.source_path : null;
}

function findPathByCategory(
  items: EvidencePlacementPlan["items"],
  category: string
): string | null {
  const match = items.find((item) => item.category === category);
  return match ? match.source_path : null;
}

function findPathByName(paths: string[], pattern: RegExp): string | null {
  const match = paths.find((path) => pattern.test(path));
  return match ?? null;
}

function uniquePaths(paths: string[]): string[] {
  const unique = new Set<string>();
  for (const path of paths) {
    const value = path.trim();
    if (value.length > 0) {
      unique.add(value);
    }
  }
  return [...unique];
}

function normalizeLines(lines: string[]): string {
  return lines.map((line) => line.trim()).filter(Boolean).join("\n");
}

function cloneGroups(groups: ProjectTestPlanDraftGroup[] | undefined): ProjectTestPlanDraftGroup[] {
  if (!groups) {
    return [];
  }
  return groups.map((group) => ({
    ...group,
    steps: (group.steps ?? []).map((step) => ({ ...step }))
  }));
}

function buildRuntimeProjectionRequest(input: {
  project: Project;
  draft: ProjectTestPlanDraft;
  selectedTokenReference: string | null;
  versionStatus: WorkbenchVersionStatus;
  validation: MatrixValidationSummary | null;
}): RuntimeProjectionSnapshotRequest {
  const rows = (input.draft.payload.groups ?? []).flatMap((group, groupIndex) =>
    (group.steps ?? []).map((step, stepIndex) => ({
      group_identity: group.group_key?.trim() || `group_${groupIndex + 1}`,
      group_label: group.group_label?.trim() || `Group ${groupIndex + 1}`,
      row_context: {
        test_item_label: step.test_item ?? step.step_label ?? "Unspecified test step",
        section: step.source_section ?? "Not specified",
        method: step.method_summary ?? step.reference_standard ?? "Method pending",
        condition: step.condition_summary ?? "Condition pending",
        requirement: step.judgement_criteria ?? "Requirement pending"
      },
      raw_step_token_value: normalizeRuntimeStepToken(step.sequence, step.raw_token, stepIndex),
      projection_state: buildRuntimeProjectionState(input.versionStatus, input.validation)
    }))
  );

  return {
    project_reference: input.project.project_no || input.project.project_id,
    matrix_reference: `${input.draft.draft_id}:v${input.draft.version}`,
    selected_token_reference: input.selectedTokenReference,
    rows
  };
}

function buildRuntimeProjectionState(
  versionStatus: WorkbenchVersionStatus,
  validation: MatrixValidationSummary | null
): RuntimeProjectionSnapshotRequest["rows"][number]["projection_state"] {
  const hasBlockers = (validation?.blockers.length ?? 0) > 0;
  const hasWarnings = (validation?.warnings.length ?? 0) > 0;

  return {
    lifecycle: hasBlockers ? "blocked" : "not_started",
    evidence: "unknown",
    report_sync: versionStatus.hasStaleOutputs ? "stale" : "unknown",
    stale: versionStatus.hasStaleOutputs ? "stale" : "fresh",
    attention: hasBlockers ? "p0" : versionStatus.hasStaleOutputs ? "p2" : hasWarnings ? "p4" : "none"
  };
}

function normalizeRuntimeStepToken(
  sequence: number | null | undefined,
  rawToken: string | null | undefined,
  stepIndex: number
): string {
  const normalizedRaw = rawToken?.trim();
  if (normalizedRaw) {
    return normalizedRaw;
  }
  if (typeof sequence === "number") {
    return `${sequence}`;
  }
  return `${stepIndex + 1}`;
}
