import { useEffect, useMemo, useState } from "react";
import {
  ApiRequestError,
  collectRequestMaterial,
  confirmProjectTestPlanMatrixDraft,
  createProjectTestPlanDraft,
  executeApprovalPackage,
  executePublicFolderWorkflowPull,
  executePublicFolderWorkflowSubmit,
  executePublicFolderWorkflowSync,
  fetchActiveConfirmedMatrixSnapshot,
  fetchConfirmedMatrixRuntimeProjectionSnapshot,
  fetchOfficialFolderCheck,
  fetchPublicDriveUploadPreview,
  fetchProjectFolderRequiredFormsPreview,
  fetchProjectPackagePreview,
  fetchOfficialWorkspacePreview,
  fetchRequestMaterialPreview,
  getLatestProjectFolder,
  getProjectOutputStatusSummary,
  getPublicFolderWorkflowContext,
  getConfirmedFeeLatest,
  generateProjectFolderRequiredForms,
  fetchProjectSection2SyncPreview,
  getProjectTestPlanDraft,
  getProject,
  getProjectLifecycle,
  getProjectBasicInformation,
  openLocalProjectFolder,
  activateProjectLifecycle,
  closeProjectLifecycle,
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
  previewPublicFolderWorkflowPull,
  previewPublicFolderWorkflowSubmit,
  previewPublicFolderWorkflowSync,
  repairOfficialFolderStructure,
  setPublicFolderWorkflowAutoSync,
  syncProjectSection2FromConfirmedMatrix,
  updateProjectTestPlanMatrixDraft,
  uploadPublicDriveProjectFolder,
  validateProjectTestPlanMatrixDraft,
  writeBackProjectApplicationForm,
  type ApprovalPackageRequest,
  type ApprovalPackageResponse,
  type ConfirmedMatrixSnapshot,
  type ConfirmedFeeLatestResponse,
  type EvidencePlacementPlan,
  type EvidencePlacementResult,
  type ProjectCloseReasonCategory,
  type ExternalResource,
  type FolderGeneration,
  type LtrRecord,
  type MatrixPreviewResponse,
  type MatrixSourceCandidate,
  type MatrixSourceCandidatesResponse,
  type MatrixValidationSummary,
  type Project,
  type ProjectBasicInformationResponse,
  type ProjectLifecycleResponse,
  type ProjectPackagePreview,
  type ProjectFolderRequiredFormsGenerateRequest,
  type ProjectFolderRequiredFormsGenerateResponse,
  type ProjectFolderRequiredFormsPreview,
  type OfficialFolderCheckPreview,
  type OfficialFolderRepairResponse,
  type OfficialWorkspaceCreateResponse,
  type OfficialWorkspaceConflictStrategy,
  type OfficialWorkspacePreview,
  type PublicDriveUploadPreview,
  type PublicDriveUploadResult,
  type PublicFolderWorkflowExecuteInput,
  type PublicFolderWorkflowContext,
  type PublicFolderWorkflowOperationType,
  type PublicFolderWorkflowPreview,
  type PublicFolderWorkflowResult,
  type ProjectFolderOpenResponse,
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

type ProjectFolderBusinessFlowResult =
  | { status: "completed" }
  | { status: "skipped" }
  | { status: "blocked"; message: string };

type RequiredFormsTargetKey = ProjectFolderRequiredFormsPreview["items"][number]["key"];

type PublicFolderWorkflowOperationMap<T> = Record<
  PublicFolderWorkflowOperationType,
  T
>;

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
  outputStatusSummary: ProjectOutputStatusSummary | null;
  lifecycle: ProjectLifecycleResponse | null;
  lifecycleLoading: boolean;
  lifecycleError: string | null;
  activeConfirmedMatrixSnapshot: ConfirmedMatrixSnapshot | null;
  activeConfirmedMatrixLoading: boolean;
  basicInformation: ProjectBasicInformationResponse | null;
  basicInformationLoading: boolean;
  basicInformationError: string | null;
  confirmedFeeLatest: ConfirmedFeeLatestResponse | null;
  packagePreview: ProjectPackagePreview | null;
  packagePreviewLoading: boolean;
  packagePreviewError: string | null;
  officialWorkspacePreview: OfficialWorkspacePreview | null;
  officialWorkspaceLoading: boolean;
  officialWorkspaceCreating: boolean;
  officialWorkspaceProgressLabel: string | null;
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
  publicFolderWorkflowContext: PublicFolderWorkflowContext | null;
  publicFolderWorkflowContextLoading: boolean;
  publicFolderWorkflowContextError: string | null;
  publicFolderWorkflowPreviews: PublicFolderWorkflowOperationMap<
    PublicFolderWorkflowPreview | null
  >;
  publicFolderWorkflowResults: PublicFolderWorkflowOperationMap<
    PublicFolderWorkflowResult | null
  >;
  publicFolderWorkflowBusyOperation: PublicFolderWorkflowOperationType | null;
  publicFolderWorkflowConfirmingOperation: PublicFolderWorkflowOperationType | null;
  publicFolderWorkflowError: string | null;
  publicFolderWorkflowMessage: string | null;
  publicFolderWorkflowAutoSyncBusy: boolean;
  requestMaterialPreview: RequestMaterialPreview | null;
  requestMaterialLoading: boolean;
  requestMaterialCollecting: boolean;
  requestMaterialError: string | null;
  requiredFormsPreview: ProjectFolderRequiredFormsPreview | null;
  requiredFormsLoading: boolean;
  requiredFormsGenerating: boolean;
  requiredFormsError: string | null;
  requiredFormsResult: ProjectFolderRequiredFormsGenerateResponse | null;
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
  onRefreshLifecycle: () => Promise<void>;
  onActivateLifecycle: (reason: string) => Promise<void>;
  onCloseLifecycle: (
    reasonCategory: ProjectCloseReasonCategory,
    note: string
  ) => Promise<void>;
  onRefreshPackagePreview: () => Promise<void>;
  onRefreshOfficialWorkspacePreview: () => Promise<void>;
  onCreateOfficialWorkspace: (
    conflictStrategy?: OfficialWorkspaceConflictStrategy
  ) => Promise<void>;
  onRefreshOfficialFolderCheck: () => Promise<void>;
  onRepairOfficialFolderStructure: () => Promise<void>;
  onRefreshPublicDriveUploadPreview: () => Promise<void>;
  onRefreshPublicFolderWorkflowContext: () => Promise<void>;
  onSetPublicFolderWorkflowAutoSync: (enabled: boolean) => Promise<void>;
  onPreviewPublicFolderWorkflowOperation: (
    operation: PublicFolderWorkflowOperationType
  ) => Promise<void>;
  onOpenLocalProjectFolder: () => Promise<void>;
  onConfirmPublicFolderWorkflowOperation: (
    operation: PublicFolderWorkflowOperationType
  ) => Promise<void>;
  onCancelPublicFolderWorkflowOperation: (
    operation: PublicFolderWorkflowOperationType
  ) => void;
  onRefreshBasicInformation: () => Promise<void>;
  onUploadPublicDriveProjectFolder: () => Promise<void>;
  onRefreshRequestMaterial: () => Promise<void>;
  onCollectRequestMaterial: () => Promise<void>;
  onRefreshRequiredForms: () => Promise<void>;
  onGenerateRequiredForms: () => Promise<void>;
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
  const [lifecycle, setLifecycle] = useState<ProjectLifecycleResponse | null>(null);
  const [lifecycleLoading, setLifecycleLoading] = useState(false);
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);
  const [activeConfirmedMatrixSnapshot, setActiveConfirmedMatrixSnapshot] =
    useState<ConfirmedMatrixSnapshot | null>(null);
  const [activeConfirmedMatrixLoading, setActiveConfirmedMatrixLoading] = useState(true);
  const [basicInformation, setBasicInformation] =
    useState<ProjectBasicInformationResponse | null>(null);
  const [basicInformationLoading, setBasicInformationLoading] = useState(false);
  const [basicInformationError, setBasicInformationError] = useState<string | null>(null);
  const [confirmedFeeLatest, setConfirmedFeeLatest] =
    useState<ConfirmedFeeLatestResponse | null>(null);
  const [packagePreview, setPackagePreview] = useState<ProjectPackagePreview | null>(null);
  const [packagePreviewLoading, setPackagePreviewLoading] = useState(false);
  const [packagePreviewError, setPackagePreviewError] = useState<string | null>(null);
  const [officialWorkspacePreview, setOfficialWorkspacePreview] =
    useState<OfficialWorkspacePreview | null>(null);
  const [officialWorkspaceLoading, setOfficialWorkspaceLoading] = useState(false);
  const [officialWorkspaceCreating, setOfficialWorkspaceCreating] = useState(false);
  const [officialWorkspaceProgressLabel, setOfficialWorkspaceProgressLabel] =
    useState<string | null>(null);
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
  const [publicFolderWorkflowContext, setPublicFolderWorkflowContext] =
    useState<PublicFolderWorkflowContext | null>(null);
  const [publicFolderWorkflowContextLoading, setPublicFolderWorkflowContextLoading] =
    useState(false);
  const [publicFolderWorkflowContextError, setPublicFolderWorkflowContextError] =
    useState<string | null>(null);
  const [publicFolderWorkflowPreviews, setPublicFolderWorkflowPreviews] =
    useState<PublicFolderWorkflowOperationMap<PublicFolderWorkflowPreview | null>>(
      createPublicFolderWorkflowOperationMap(null)
    );
  const [publicFolderWorkflowResults, setPublicFolderWorkflowResults] =
    useState<PublicFolderWorkflowOperationMap<PublicFolderWorkflowResult | null>>(
      createPublicFolderWorkflowOperationMap(null)
    );
  const [publicFolderWorkflowBusyOperation, setPublicFolderWorkflowBusyOperation] =
    useState<PublicFolderWorkflowOperationType | null>(null);
  const [
    publicFolderWorkflowConfirmingOperation,
    setPublicFolderWorkflowConfirmingOperation,
  ] = useState<PublicFolderWorkflowOperationType | null>(null);
  const [publicFolderWorkflowError, setPublicFolderWorkflowError] =
    useState<string | null>(null);
  const [publicFolderWorkflowMessage, setPublicFolderWorkflowMessage] =
    useState<string | null>(null);
  const [publicFolderWorkflowAutoSyncBusy, setPublicFolderWorkflowAutoSyncBusy] =
    useState(false);
  const [requestMaterialPreview, setRequestMaterialPreview] =
    useState<RequestMaterialPreview | null>(null);
  const [requestMaterialLoading, setRequestMaterialLoading] = useState(false);
  const [requestMaterialCollecting, setRequestMaterialCollecting] = useState(false);
  const [requestMaterialError, setRequestMaterialError] = useState<string | null>(null);
  const [requiredFormsPreview, setRequiredFormsPreview] =
    useState<ProjectFolderRequiredFormsPreview | null>(null);
  const [requiredFormsLoading, setRequiredFormsLoading] = useState(false);
  const [requiredFormsGenerating, setRequiredFormsGenerating] = useState(false);
  const [requiredFormsError, setRequiredFormsError] = useState<string | null>(null);
  const [requiredFormsResult, setRequiredFormsResult] =
    useState<ProjectFolderRequiredFormsGenerateResponse | null>(null);
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
    void onRefreshRequiredForms();
    void onRefreshOfficialFolderCheck();
    void onRefreshPublicDriveUploadPreview();
    void onRefreshPublicFolderWorkflowContext();
    void onRefreshBasicInformation();
    void onRefreshLifecycle();
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
        title: "Folder inputs",
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

  async function onCreateOfficialWorkspace(
    conflictStrategy?: OfficialWorkspaceConflictStrategy
  ): Promise<void> {
    setOfficialWorkspaceCreating(true);
    setOfficialWorkspaceProgressLabel("Creating or updating project folder");
    const timings: ProjectFolderFlowTiming[] = [];
    try {
      const result = await timeProjectFolderStep(
        timings,
        "createOfficialWorkspace",
        () =>
          createOfficialWorkspace(
            projectId,
            conflictStrategy ? { conflict_strategy: conflictStrategy } : {}
          )
      );
      setOfficialWorkspaceResult(result);
      setMessage(
        conflictStrategy
          ? "Project folder rebuilt."
          : "Project folder workflow updated."
      );
      setError(null);
      setOfficialWorkspaceError(null);
      setOfficialWorkspaceProgressLabel("Checking project folder paths");
      await timeProjectFolderStep(
        timings,
        "officialWorkspacePreview.afterCreate",
        () => onRefreshOfficialWorkspacePreview()
      );
      const flowResult = await runProjectFolderBusinessFlowAfterCreate(timings);
      if (flowResult.status === "blocked") {
        setMessage(`Project folder update blocked: ${flowResult.message}`);
      }
    } catch (err) {
      setOfficialWorkspaceError((err as Error).message);
    } finally {
      logProjectFolderFlowTiming(projectId, conflictStrategy ?? "direct", timings);
      setOfficialWorkspaceCreating(false);
      setOfficialWorkspaceProgressLabel(null);
    }
  }

  async function runProjectFolderBusinessFlowAfterCreate(
    timings?: ProjectFolderFlowTiming[]
  ): Promise<ProjectFolderBusinessFlowResult> {
    await timeProjectFolderStep(timings, "requestMaterial.collect", () =>
      collectRequestMaterialAfterFolderCreate()
    );
    await timeProjectFolderStep(timings, "officialFolderCheck.afterCollect", () =>
      refreshOfficialFolderCheckAfterFolderCreate()
    );
    const requiredFormsResult = await generateRequiredFormsAfterFolderCreate(timings);
    if (requiredFormsResult.status === "blocked") {
      return requiredFormsResult;
    }
    await timeProjectFolderStep(timings, "applicationForm.writeBack", () =>
      writeBackApplicationFormAfterFolderCreate()
    );
    await timeProjectFolderStep(timings, "projectPackage.preview", () =>
      onRefreshPackagePreview()
    );
    await timeProjectFolderStep(timings, "publicDrive.preview", () =>
      onRefreshPublicDriveUploadPreview()
    );
    return { status: "completed" };
  }

  async function collectRequestMaterialAfterFolderCreate(): Promise<void> {
    setOfficialWorkspaceProgressLabel("Archiving request materials");
    try {
      const result = await collectRequestMaterial(projectId);
      setRequestMaterialPreview(result);
      setRequestMaterialError(null);
    } catch (err) {
      setRequestMaterialError((err as Error).message);
      try {
        setRequestMaterialPreview(await fetchRequestMaterialPreview(projectId));
      } catch {
        setRequestMaterialPreview(null);
      }
    }
  }

  async function refreshOfficialFolderCheckAfterFolderCreate(): Promise<void> {
    setOfficialWorkspaceProgressLabel("Checking project folder structure");
    try {
      setOfficialFolderCheckPreview(await fetchOfficialFolderCheck(projectId));
      setOfficialFolderCheckError(null);
    } catch (err) {
      setOfficialFolderCheckPreview(null);
      setOfficialFolderCheckError((err as Error).message);
    }
  }

  async function generateRequiredFormsAfterFolderCreate(
    timings?: ProjectFolderFlowTiming[]
  ): Promise<ProjectFolderBusinessFlowResult> {
    setOfficialWorkspaceProgressLabel("Checking Fee Form and Customer Feedback");
    try {
      const preview = await timeProjectFolderStep(
        timings,
        "requiredForms.preview",
        () => fetchProjectFolderRequiredFormsPreview(projectId)
      );
      setRequiredFormsPreview(preview);
      setRequiredFormsError(null);
      if (preview.status === "blocked") {
        const blocker = formatRequiredFormsPreviewBlocker(preview);
        setRequiredFormsError(blocker);
        return { status: "blocked", message: blocker };
      }
      if (preview.status !== "ready" && preview.status !== "conflict") {
        return { status: "skipped" };
      }
      if (!preview.items.some((item) => item.action === "generate" || item.action === "update")) {
        return { status: "skipped" };
      }
      const generationResults: ProjectFolderRequiredFormsGenerateResponse[] = [];
      for (const batch of requiredFormsGenerationBatches(preview)) {
        setOfficialWorkspaceProgressLabel(batch.progressLabel);
        const result = await timeProjectFolderStep(
          timings,
          batch.timingLabel,
          () =>
            generateProjectFolderRequiredForms(
              projectId,
              buildRequiredFormsGenerateRequest(preview, batch.keys)
            )
        );
        if (result.timings?.length) {
          console.info("[required-forms-generate]", {
            projectId,
            targetKeys: batch.keys,
            timings: result.timings,
          });
        }
        generationResults.push(result);
      }
      const mergedResult = mergeRequiredFormsGenerateResults(generationResults);
      if (mergedResult) {
        setRequiredFormsResult(mergedResult);
      }
      setRequiredFormsPreview(
        await timeProjectFolderStep(timings, "requiredForms.previewAfterGenerate", () =>
          fetchProjectFolderRequiredFormsPreview(projectId)
        )
      );
      await timeProjectFolderStep(timings, "officialFolderCheck.afterRequiredForms", () =>
        refreshOfficialFolderCheckAfterFolderCreate()
      );
      await timeProjectFolderStep(timings, "outputStatus.afterRequiredForms", () =>
        refreshOutputStatus(projectId, setOutputStatusSummary)
      );
      return { status: "completed" };
    } catch (err) {
      const message = (err as Error).message;
      setRequiredFormsError(message);
      return { status: "blocked", message };
    }
  }

  async function syncSection2AfterFolderCreate(): Promise<void> {
    setOfficialWorkspaceProgressLabel("Syncing Matrix Section 2 dates");
    try {
      const preview = await fetchProjectSection2SyncPreview(projectId);
      setSection2SyncPreview(preview);
      setSection2SyncError(null);
      if (
        preview.status !== "ready" ||
        !preview.confirmed_matrix_id ||
        preview.confirmed_revision === null
      ) {
        return;
      }
      const result = await syncProjectSection2FromConfirmedMatrix(projectId, {
        expected_confirmed_matrix_id: preview.confirmed_matrix_id,
        expected_confirmed_revision: preview.confirmed_revision,
        operator: null,
      });
      setSection2SyncPreview(result);
    } catch (err) {
      setSection2SyncError((err as Error).message);
    }
  }

  async function writeBackApplicationFormAfterFolderCreate(): Promise<void> {
    setOfficialWorkspaceProgressLabel("Updating Application Form");
    try {
      await writeBackProjectApplicationForm(projectId);
      setSection2SyncError(null);
      await refreshOutputStatus(projectId, setOutputStatusSummary);
    } catch (err) {
      setSection2SyncError((err as Error).message);
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
          ? "Folder inputs collected. Review undecided attachments before controlled placement."
          : result.status === "partial"
          ? "Folder inputs partially collected. Review missing files."
          : "Folder inputs collected."
      );
      await onRefreshPackagePreview();
      await onRefreshOfficialFolderCheck();
      await onRefreshRequiredForms();
      await onRefreshPublicDriveUploadPreview();
      await onRefreshPublicFolderWorkflowContext();
    } catch (err) {
      setRequestMaterialError((err as Error).message);
    } finally {
      setRequestMaterialCollecting(false);
    }
  }

  async function onRefreshRequiredForms(): Promise<void> {
    setRequiredFormsLoading(true);
    try {
      const preview = await fetchProjectFolderRequiredFormsPreview(projectId);
      setRequiredFormsPreview(preview);
      setRequiredFormsError(null);
    } catch (err) {
      setRequiredFormsPreview(null);
      setRequiredFormsError((err as Error).message);
    } finally {
      setRequiredFormsLoading(false);
    }
  }

  async function onGenerateRequiredForms(): Promise<void> {
    if (!requiredFormsPreview) {
      setRequiredFormsError("Refresh Required forms before generating controlled files.");
      return;
    }
    if (requiredFormsPreview.status === "blocked") {
      setRequiredFormsError(formatRequiredFormsPreviewBlocker(requiredFormsPreview));
      return;
    }
    setRequiredFormsGenerating(true);
    try {
      const result = await generateProjectFolderRequiredForms(
        projectId,
        buildRequiredFormsGenerateRequest(requiredFormsPreview)
      );
      setRequiredFormsResult(result);
      setRequiredFormsError(null);
      setRequiredFormsPreview(await fetchProjectFolderRequiredFormsPreview(projectId));
      setMessage(
        result.status === "partial"
          ? "Required forms partially generated. Review remaining items."
          : "Required forms generated in the Project Folder."
      );
      await refreshOutputStatus(projectId, setOutputStatusSummary);
      await onRefreshOfficialFolderCheck();
      await onRefreshPublicDriveUploadPreview();
      await onRefreshPublicFolderWorkflowContext();
      await onRefreshPackagePreview();
    } catch (err) {
      setRequiredFormsError((err as Error).message);
    } finally {
      setRequiredFormsGenerating(false);
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

  async function onRefreshPublicFolderWorkflowContext(): Promise<void> {
    setPublicFolderWorkflowContextLoading(true);
    try {
      const context = await getPublicFolderWorkflowContext(projectId);
      setPublicFolderWorkflowContext(context);
      setPublicFolderWorkflowContextError(null);
    } catch (err) {
      setPublicFolderWorkflowContext(null);
      setPublicFolderWorkflowContextError(
        err instanceof Error ? err.message : "Failed to load public folder workflow."
      );
    } finally {
      setPublicFolderWorkflowContextLoading(false);
    }
  }

  async function onSetPublicFolderWorkflowAutoSync(enabled: boolean): Promise<void> {
    setPublicFolderWorkflowAutoSyncBusy(true);
    try {
      const state = await setPublicFolderWorkflowAutoSync(projectId, enabled);
      setPublicFolderWorkflowContext((previous) =>
        previous
          ? {
              ...previous,
              auto_sync_enabled: state.auto_sync_enabled,
              sync_locked: state.sync_locked,
              submitted_at: state.submitted_at,
            }
          : previous
      );
      setPublicFolderWorkflowError(null);
      setPublicFolderWorkflowMessage(
        state.auto_sync_enabled ? "Auto sync enabled." : "Auto sync disabled."
      );
      await onRefreshPublicFolderWorkflowContext();
    } catch (err) {
      setPublicFolderWorkflowError(
        err instanceof Error ? err.message : "Failed to update Auto sync."
      );
    } finally {
      setPublicFolderWorkflowAutoSyncBusy(false);
    }
  }

  async function onOpenLocalProjectFolder(): Promise<void> {
    setPublicFolderWorkflowError(null);
    setPublicFolderWorkflowMessage(null);
    try {
      const result = await openLocalProjectFolder(projectId);
      setPublicFolderWorkflowMessage(
        await projectFolderOpenMessage(result, publicFolderWorkflowContext)
      );
    } catch (err) {
      const fallbackPath = publicFolderWorkflowContext?.local_official_folder_path ?? null;
      if (fallbackPath) {
        setPublicFolderWorkflowMessage(
          await projectFolderOpenFallbackMessage(fallbackPath)
        );
      } else {
        setPublicFolderWorkflowError(
          err instanceof Error ? err.message : "Project folder is not available yet."
        );
      }
    }
  }

  async function onPreviewPublicFolderWorkflowOperation(
    operation: PublicFolderWorkflowOperationType
  ): Promise<void> {
    setPublicFolderWorkflowBusyOperation(operation);
    setPublicFolderWorkflowConfirmingOperation(null);
    setPublicFolderWorkflowError(null);
    setPublicFolderWorkflowMessage(null);
    try {
      const preview = await previewPublicFolderWorkflowOperation(projectId, operation);
      setPublicFolderWorkflowPreviews((previous) => ({
        ...previous,
        [operation]: preview,
      }));
      setPublicFolderWorkflowResults((previous) => ({
        ...previous,
        [operation]: null,
      }));
      const issue = selectPublicFolderWorkflowPreviewIssue(preview);
      if (preview.status !== "ready" || issue || !preview.preview_hash) {
        setPublicFolderWorkflowMessage(
          issue ?? "Preview cannot be confirmed yet."
        );
        return;
      }
      setPublicFolderWorkflowConfirmingOperation(operation);
      setPublicFolderWorkflowMessage("Preview can be confirmed.");
    } catch (err) {
      setPublicFolderWorkflowPreviews((previous) => ({
        ...previous,
        [operation]: null,
      }));
      setPublicFolderWorkflowError(
        err instanceof Error ? err.message : `Failed to preview ${operation}.`
      );
    } finally {
      setPublicFolderWorkflowBusyOperation(null);
    }
  }

  async function onConfirmPublicFolderWorkflowOperation(
    operation: PublicFolderWorkflowOperationType
  ): Promise<void> {
    const preview = publicFolderWorkflowPreviews[operation];
    if (!preview?.preview_hash) {
      setPublicFolderWorkflowError("Refresh preview before confirming.");
      return;
    }
    setPublicFolderWorkflowBusyOperation(operation);
    setPublicFolderWorkflowError(null);
    setPublicFolderWorkflowMessage(null);
    try {
      const result = await executePublicFolderWorkflowOperation(projectId, operation, {
        preview_hash: preview.preview_hash,
        confirmed: true,
        confirm_directory_creation: preview.required_confirmations.includes(
          "create_missing_public_directories"
        ),
        operator: null,
      });
      setPublicFolderWorkflowResults((previous) => ({
        ...previous,
        [operation]: result,
      }));
      setPublicFolderWorkflowPreviews((previous) => ({
        ...previous,
        [operation]: result.preview,
      }));
      setPublicFolderWorkflowConfirmingOperation(null);
      setPublicFolderWorkflowMessage(`${publicFolderWorkflowOperationLabel(operation)} completed.`);
      await onRefreshPublicFolderWorkflowContext();
      await onRefreshOfficialFolderCheck();
      await onRefreshPackagePreview();
    } catch (err) {
      setPublicFolderWorkflowError(
        err instanceof Error ? err.message : `Failed to execute ${operation}.`
      );
    } finally {
      setPublicFolderWorkflowBusyOperation(null);
    }
  }

  function onCancelPublicFolderWorkflowOperation(
    operation: PublicFolderWorkflowOperationType
  ): void {
    setPublicFolderWorkflowConfirmingOperation((previous) =>
      previous === operation ? null : previous
    );
    setPublicFolderWorkflowMessage(null);
  }

  async function onRefreshBasicInformation(): Promise<void> {
    setBasicInformationLoading(true);
    try {
      const nextBasicInformation = await getProjectBasicInformation(projectId);
      setBasicInformation(nextBasicInformation);
      setBasicInformationError(null);
    } catch (err) {
      setBasicInformation(null);
      setBasicInformationError(
        err instanceof Error ? err.message : "Failed to load Basic Information."
      );
    } finally {
      setBasicInformationLoading(false);
    }
  }

  async function onRefreshLifecycle(): Promise<void> {
    setLifecycleLoading(true);
    try {
      const nextLifecycle = await getProjectLifecycle(projectId);
      setLifecycle(nextLifecycle);
      setLifecycleError(null);
    } catch (err) {
      setLifecycle(null);
      setLifecycleError(
        err instanceof Error ? err.message : "Failed to load project lifecycle."
      );
    } finally {
      setLifecycleLoading(false);
    }
  }

  async function onActivateLifecycle(reason: string): Promise<void> {
    const normalizedReason = normalizeRequiredLifecycleText(
      reason,
      "Activation note is required."
    );
    setLifecycleLoading(true);
    try {
      const nextLifecycle = await activateProjectLifecycle(projectId, {
        reason: normalizedReason,
        operator: null,
      });
      setLifecycle(nextLifecycle);
      setProject(await getProject(projectId));
      setLifecycleError(null);
      setMessage("Project activated. Editing and project work are available again.");
    } catch (err) {
      setLifecycleError(
        err instanceof Error ? err.message : "Failed to activate project lifecycle."
      );
      throw err;
    } finally {
      setLifecycleLoading(false);
    }
  }

  async function onCloseLifecycle(
    reasonCategory: ProjectCloseReasonCategory,
    note: string
  ): Promise<void> {
    const normalizedNote = normalizeRequiredLifecycleText(
      note,
      "Close note is required."
    );
    setLifecycleLoading(true);
    try {
      const nextLifecycle = await closeProjectLifecycle(projectId, {
        reason_category: reasonCategory,
        note: normalizedNote,
        operator: null,
      });
      setLifecycle(nextLifecycle);
      setProject(await getProject(projectId));
      await refreshOutputStatus(projectId, setOutputStatusSummary);
      setLifecycleError(null);
      setMessage("Project closed with a business reason. Activate it if work should continue later.");
    } catch (err) {
      setLifecycleError((err as Error).message);
      throw err;
    } finally {
      setLifecycleLoading(false);
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
    outputStatusSummary,
    lifecycle,
    lifecycleLoading,
    lifecycleError,
    activeConfirmedMatrixSnapshot,
    activeConfirmedMatrixLoading,
    basicInformation,
    basicInformationLoading,
    basicInformationError,
    confirmedFeeLatest,
    packagePreview,
    packagePreviewLoading,
    packagePreviewError,
    officialWorkspacePreview,
    officialWorkspaceLoading,
    officialWorkspaceCreating,
    officialWorkspaceProgressLabel,
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
    publicFolderWorkflowContext,
    publicFolderWorkflowContextLoading,
    publicFolderWorkflowContextError,
    publicFolderWorkflowPreviews,
    publicFolderWorkflowResults,
    publicFolderWorkflowBusyOperation,
    publicFolderWorkflowConfirmingOperation,
    publicFolderWorkflowError,
    publicFolderWorkflowMessage,
    publicFolderWorkflowAutoSyncBusy,
    requestMaterialPreview,
    requestMaterialLoading,
    requestMaterialCollecting,
    requestMaterialError,
    requiredFormsPreview,
    requiredFormsLoading,
    requiredFormsGenerating,
    requiredFormsError,
    requiredFormsResult,
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
    onRefreshLifecycle,
    onActivateLifecycle,
    onCloseLifecycle,
    onRefreshPackagePreview,
    onRefreshOfficialWorkspacePreview,
    onCreateOfficialWorkspace,
    onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure,
    onRefreshPublicDriveUploadPreview,
    onRefreshPublicFolderWorkflowContext,
    onSetPublicFolderWorkflowAutoSync,
    onOpenLocalProjectFolder,
    onPreviewPublicFolderWorkflowOperation,
    onConfirmPublicFolderWorkflowOperation,
    onCancelPublicFolderWorkflowOperation,
    onRefreshBasicInformation,
    onUploadPublicDriveProjectFolder,
    onRefreshRequestMaterial,
    onCollectRequestMaterial,
    onRefreshRequiredForms,
    onGenerateRequiredForms,
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

type ProjectFolderFlowTiming = {
  label: string;
  elapsedMs: number;
};

async function timeProjectFolderStep<T>(
  timings: ProjectFolderFlowTiming[] | undefined,
  label: string,
  action: () => Promise<T>
): Promise<T> {
  const startedAt = performance.now();
  try {
    return await action();
  } finally {
    timings?.push({
      label,
      elapsedMs: Math.round(performance.now() - startedAt),
    });
  }
}

function logProjectFolderFlowTiming(
  projectId: string,
  mode: string,
  timings: ProjectFolderFlowTiming[]
): void {
  const totalMs = timings.reduce((total, item) => total + item.elapsedMs, 0);
  console.info("[project-folder-flow]", {
    projectId,
    mode,
    totalMs,
    timings,
  });
}

function buildRequiredFormsGenerateRequest(
  preview: ProjectFolderRequiredFormsPreview,
  targetKeys?: readonly RequiredFormsTargetKey[]
): ProjectFolderRequiredFormsGenerateRequest {
  const officialProjectFolderPath = preview.official_project_folder_path;
  const confirmedMatrixId = preview.confirmed_matrix_id;
  const confirmedRevision = preview.confirmed_revision;
  const confirmedFeeId = preview.confirmed_fee_id;
  const confirmedFeeRevision = preview.confirmed_fee_revision;
  const confirmedFeePricingDraftEditId = preview.confirmed_fee_pricing_draft_edit_id;
  const confirmedBasicInformationVersion = preview.confirmed_basic_information_version;
  const confirmedBasicInformationSourceSignatureHash =
    preview.confirmed_basic_information_source_signature_hash;
  const customerFeedbackTemplatePath = preview.customer_feedback_template_path;
  if (
    !officialProjectFolderPath ||
    !confirmedMatrixId ||
    confirmedRevision === null ||
    !confirmedFeeId ||
    confirmedFeeRevision === null ||
    !confirmedFeePricingDraftEditId ||
    confirmedBasicInformationVersion === null ||
    !confirmedBasicInformationSourceSignatureHash ||
    !customerFeedbackTemplatePath
  ) {
    throw new Error("Required forms preview is missing generation context.");
  }
  const requestedKeys = targetKeys ? new Set(targetKeys) : null;
  const expectedTargets = preview.items
    .filter((item) => item.action === "generate" || item.action === "update")
    .filter((item) => (requestedKeys ? requestedKeys.has(item.key) : true))
    .map((item) => {
      if (!item.target_path) {
        throw new Error(`${item.label} target path is missing.`);
      }
      return {
        key: item.key,
        target_path: item.target_path
      };
    });
  if (expectedTargets.length === 0) {
    throw new Error("No Required forms need generation.");
  }
  return {
    expected_official_project_folder_path: officialProjectFolderPath,
    expected_confirmed_matrix_id: confirmedMatrixId,
    expected_confirmed_revision: confirmedRevision,
    expected_confirmed_fee_id: confirmedFeeId,
    expected_confirmed_fee_revision: confirmedFeeRevision,
    expected_confirmed_fee_pricing_draft_edit_id: confirmedFeePricingDraftEditId,
    expected_confirmed_basic_information_version: confirmedBasicInformationVersion,
    expected_confirmed_basic_information_source_signature_hash:
      confirmedBasicInformationSourceSignatureHash,
    expected_customer_feedback_template_path: customerFeedbackTemplatePath,
    expected_targets: expectedTargets
  };
}

function requiredFormsGenerationBatches(
  preview: ProjectFolderRequiredFormsPreview
): Array<{
  keys: RequiredFormsTargetKey[];
  progressLabel: string;
  timingLabel: string;
}> {
  const writableKeys = new Set(
    preview.items
      .filter((item) => item.action === "generate" || item.action === "update")
      .map((item) => item.key)
  );
  const batches: Array<{
    keys: RequiredFormsTargetKey[];
    progressLabel: string;
    timingLabel: string;
  }> = [
    {
      keys: ["customer_feedback_form"],
      progressLabel: "Updating Customer Feedback Form",
      timingLabel: "requiredForms.customerFeedback.generate",
    },
    {
      keys: ["fee_form"],
      progressLabel: "Updating Fee Form",
      timingLabel: "requiredForms.feeForm.generate",
    },
    {
      keys: ["test_record"],
      progressLabel: "Updating Test Record",
      timingLabel: "requiredForms.testRecord.generate",
    },
  ];
  return batches
    .map((batch) => ({
      ...batch,
      keys: batch.keys.filter((key) => writableKeys.has(key)),
    }))
    .filter((batch) => batch.keys.length > 0);
}

function mergeRequiredFormsGenerateResults(
  results: ProjectFolderRequiredFormsGenerateResponse[]
): ProjectFolderRequiredFormsGenerateResponse | null {
  if (results.length === 0) {
    return null;
  }
  const last = results[results.length - 1];
  const statuses = results.map((result) => result.status);
  const status: ProjectFolderRequiredFormsGenerateResponse["status"] =
    statuses.includes("blocked")
      ? "blocked"
      : statuses.includes("conflict")
        ? "conflict"
        : statuses.includes("partial")
          ? "partial"
          : "generated";
  return {
    ...last,
    status,
    items: results.flatMap((result) => result.items),
    warnings: results.flatMap((result) => result.warnings),
    timings: results.flatMap((result) => result.timings ?? []),
  };
}

function formatRequiredFormsPreviewBlocker(
  preview: ProjectFolderRequiredFormsPreview
): string {
  return (
    preview.blockers[0] ??
    preview.items.find((item) => item.status === "blocked")?.message ??
    "Resolve Required forms blockers before generating controlled files."
  );
}

function createPublicFolderWorkflowOperationMap<T>(
  value: T
): PublicFolderWorkflowOperationMap<T> {
  return {
    sync: value,
    submit: value,
    pull: value,
  };
}

function previewPublicFolderWorkflowOperation(
  projectId: string,
  operation: PublicFolderWorkflowOperationType
): Promise<PublicFolderWorkflowPreview> {
  if (operation === "sync") {
    return previewPublicFolderWorkflowSync(projectId);
  }
  if (operation === "submit") {
    return previewPublicFolderWorkflowSubmit(projectId);
  }
  return previewPublicFolderWorkflowPull(projectId);
}

function executePublicFolderWorkflowOperation(
  projectId: string,
  operation: PublicFolderWorkflowOperationType,
  input: PublicFolderWorkflowExecuteInput
): Promise<PublicFolderWorkflowResult> {
  if (operation === "sync") {
    return executePublicFolderWorkflowSync(projectId, input);
  }
  if (operation === "submit") {
    return executePublicFolderWorkflowSubmit(projectId, input);
  }
  return executePublicFolderWorkflowPull(projectId, input);
}

async function projectFolderOpenMessage(
  result: ProjectFolderOpenResponse,
  context: PublicFolderWorkflowContext | null
): Promise<string> {
  if (result.status === "opened") {
    return result.message || "Project folder opened.";
  }
  const path =
    result.local_official_folder_path ??
    context?.local_official_folder_path ??
    null;
  if (result.status === "unsupported" && path) {
    return projectFolderOpenFallbackMessage(path);
  }
  return appendProjectFolderPath(
    result.message || "Project folder is not available yet.",
    path
  );
}

async function projectFolderOpenFallbackMessage(path: string): Promise<string> {
  if (await copyProjectFolderPath(path)) {
    return "Project folder path copied. Open it in File Explorer.";
  }
  return appendProjectFolderPath("Copy this path from the folder context.", path);
}

async function copyProjectFolderPath(path: string): Promise<boolean> {
  const clipboard = globalThis.navigator?.clipboard;
  if (!clipboard?.writeText) {
    return false;
  }
  try {
    await clipboard.writeText(path);
    return true;
  } catch {
    return false;
  }
}

function appendProjectFolderPath(message: string, path: string | null): string {
  return path ? `${message} ${path}` : message;
}

function selectPublicFolderWorkflowPreviewIssue(
  preview: PublicFolderWorkflowPreview
): string | null {
  return preview.blockers[0] ?? preview.conflicts[0] ?? null;
}

function publicFolderWorkflowOperationLabel(
  operation: PublicFolderWorkflowOperationType
): string {
  if (operation === "sync") {
    return "Sync";
  }
  if (operation === "submit") {
    return "Submit";
  }
  return "Pull";
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

function normalizeRequiredLifecycleText(value: string, message: string): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new Error(message);
  }
  return normalized;
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
