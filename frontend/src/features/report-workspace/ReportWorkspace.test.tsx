import "../../api/runtime.testHelpers";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as authoring from "../../api/reportAuthoring";
import * as customerContent from "../../api/customerContent";
vi.mock("../../api/customerContent", () => ({inspectUploadedCustomerSource:vi.fn(),inspectProjectCustomerSource:vi.fn(),startInspectedCustomerReport:vi.fn(),discardCustomerInput:vi.fn().mockResolvedValue(undefined)}));
import * as api from "../../api/client";
import { ReportWorkspace } from "./ReportWorkspace";
import { AppShell } from "../../components/layout/AppShell";
import { ProjectReportWorkspacePage } from "../../pages/ProjectReportWorkspacePage";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return {
    ...actual,
    getProject: vi.fn(),
    listProjectLtrs: vi.fn(),
    getProjectBasicInformation: vi.fn(),
    fetchReportWorkspace: vi.fn(),
    fetchCurrentReport: vi.fn(),
    fetchReportUpdateSource: vi.fn(), updateReportDraftLlcr: vi.fn(), updateReportDraftEquipment: vi.fn(),
    selectReportUpdateSource: vi.fn(), downloadReportWorkingDraft: vi.fn(),
    fetchCurrentCustomerReport: vi.fn(),
    startStandaloneCustomerReport: vi.fn(),
    readStandaloneCustomerReportJob: vi.fn(),
    downloadStandaloneCustomerReport: vi.fn(),
    inspectLlcrResultWorkbook: vi.fn(),
    confirmLlcrResultImport: vi.fn(),
    generateInitialReportRevision: vi.fn(),
    previewInternalReportGeneration: vi.fn(),
    generateInternalReport: vi.fn(),
    downloadInternalReportDraft: vi.fn(),
    openLocalProjectFolder: vi.fn(),
    getPublicFolderWorkflowContext: vi.fn(),
    previewCurrentReportLlcrUpdate: vi.fn(),
    updateCurrentReportLlcr: vi.fn(),
    previewCurrentReportEquipmentList: vi.fn(),
    updateCurrentReportEquipmentList: vi.fn(),
    updateEquipmentListOneClick: vi.fn(),
    publishManagedReport: vi.fn(),
    downloadCurrentReport: vi.fn(),
    generateCurrentCustomerReport: vi.fn(),
    startProjectCustomerReportJob: vi.fn(),
    fetchLatestProjectCustomerReportJob: vi.fn(),
    readProjectCustomerReportJob: vi.fn(),
    downloadProjectCustomerReportJob: vi.fn(),
    downloadCurrentCustomerReport: vi.fn(),
    cancelLlcrResultPreview: vi.fn(),
  };
});

vi.mock("../../api/reportAuthoring", async () => ({
  ...await vi.importActual<typeof import('../../api/reportAuthoring')>('../../api/reportAuthoring'),
  getReportAuthoring: vi.fn(), selectReportBase: vi.fn(), adoptCurrentReportWorkingCopy: vi.fn(),
}));

const state: api.ReportWorkspaceState = {
  project_id: "project-1",
  basic_information_status: "confirmed",
  confirmed_basic_information_version: 2,
  active_confirmed_matrix_id: "matrix-1",
  active_confirmed_matrix_revision: 4,
  latest_report_revision: null,
  datasets: [],
  report_revisions: [],
};

const currentReport: api.CurrentReport = {
  status: "ready",
  mode: "official",
  file_name: "DL-001 Qualification Testing Report_Rev_A.docx",
  file_path: "D:\\Test Project\\DL-001\\Official Test\\DL-001 Qualification Testing Report_Rev_A.docx",
  file_sha256: "a".repeat(64),
  report_revision_id: null,
  folder_path: "D:\\Test Project\\DL-001\\Official Test",
  official_folder_path: "D:\\Test Project\\DL-001\\Official Test",
  can_publish_to_official: false,
  download_url: "/api/projects/project-1/report-workspace/current-report/download",
};

const customerReport: api.CustomerReportState = {
  project_id: "project-1",
  status: "stale",
  mode: "official",
  file_name: "DL-001-CR Qualification Testing Report_Rev_A.docx",
  file_sha256: "b".repeat(64),
  internal_report_sha256: "a".repeat(64),
  generated_from_internal_sha256: "c".repeat(64),
  can_generate: true,
  blockers: [],
  warnings: ["The current Internal Report changed after this customer report was generated."],
  download_url: "/api/projects/project-1/report-workspace/current-customer-report/download",
};

const completedJob = {
  operation_id: "operation-1", project_id: "project-1", status: "completed" as const,
  stage: "completed", elapsed_seconds: 22, message: null, error_code: null,
};

const preview: api.LlcrImportPreview = {
  preview_id: "preview-1",
  project_id: "project-1",
  confirmed_matrix_id: "matrix-1",
  confirmed_matrix_revision: 4,
  source: { file_name: "LLCR.xlsx", sha256: "sha", size_bytes: 500 },
  parser_profile_version: "connlab-llcr-v1",
  detected_sheets: ["Summary", "P"],
  can_confirm: true,
  sample_count: 6,
  test_point_count: 24,
  result_count: 1,
  diagnostics: [],
  entries: [
    {
      result_id: "result-1",
      group_label: "1",
      matrix_step_token: "2",
      stage: "initial",
      stage_label: "Initial",
      requirement: "≤ 0.198 mΩ",
      unit: "mΩ",
      measurement_count: 24,
      summary_min: "0.031",
      summary_max: "0.082",
      summary_average: "0.0565",
      provisional_outcome: "pass",
      confirmed_outcome: null,
      override_reason: null,
      source_range: "P!B10:Y10",
      report_target: "Group 1 / Step 2",
    },
  ],
};

const equipmentPreview: api.EquipmentListPreview = {
  project_id: "project-1",
  status: "ready",
  current_report: currentReport,
  source_file_name: "EquipmentID.docx",
  source_sha256: "b".repeat(64),
  catalog_file_name: "equipment.xlsx",
  catalog_sha256: "c".repeat(64),
  rows: [
    {
      source_reference: "DG-Q-0033",
      status: "matched",
      item: "Digital multimeter",
      manufacturer: "Keysight",
      id_number: "DG-Q-0033",
      last_calibration: "01 Jan 2025",
      calibration_due: "01 Jan 2026",
      source_sheet: "All Equip.",
      expired: true,
      external_reason: null,
    },
  ],
  blockers: [],
  warnings: ["Calibration is expired for DG-Q-0033 (01 Jan 2026)."],
  requires_expired_acknowledgement: true,
};

describe("ReportWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(authoring.adoptCurrentReportWorkingCopy).mockImplementation(async id => authoring.getReportAuthoring(id));
    vi.mocked(authoring.getReportAuthoring).mockResolvedValue({ project_id: 'project-1', revision: 0,
      sources: [], mappings: [], outputs: [], base_source_id: null,
      context: { dl_number: 'DL-001', matrix_id: 'matrix-1', steps: [] } });
    sessionStorage.clear();
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(null);
    vi.mocked(api.startProjectCustomerReportJob).mockReset();
    vi.mocked(api.downloadProjectCustomerReportJob).mockResolvedValue({ blob: new Blob(["customer"]), fileName: "Customer.docx" });
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:customer-report"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue(state);
    vi.mocked(api.fetchCurrentReport).mockResolvedValue(currentReport);
    vi.mocked(api.fetchReportUpdateSource).mockResolvedValue(currentReport);
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue(customerReport);
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64), requires_confirmation: true,
      mode: "official", current_path: currentReport.file_path!, target_path: currentReport.file_path!, blockers: [],
    });
    vi.mocked(api.generateInternalReport).mockResolvedValue({ project_id: "project-1", mode: "official", file_name: currentReport.file_name!,
      file_path: currentReport.file_path!, file_sha256: "d".repeat(64), archive_path: "History/Report/old.docx" });
    vi.mocked(api.inspectLlcrResultWorkbook).mockResolvedValue(preview);
    vi.mocked(api.previewCurrentReportEquipmentList).mockResolvedValue(equipmentPreview);
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValue({
      status: "completed", project_id: "project-1", file_name: currentReport.file_name!,
      changed: true, current_sha256: "d".repeat(64), archive_path: "History/Report/old.docx",
      statistics: { filled: 1, unmatched: [], incomplete: [], expired: ["DG-Q-0033"] },
    });
    vi.mocked(api.updateCurrentReportEquipmentList).mockResolvedValue({
      project_id: "project-1",
      file_name: currentReport.file_name!,
      mode: "official",
      changed: true,
      current_sha256: "d".repeat(64),
      archive_path: "C:\\Project\\History\\Report\\old.docx",
      updated_by: "Lab User",
    });
    vi.mocked(api.confirmLlcrResultImport).mockResolvedValue({
      dataset_id: "dataset-1",
      dataset_type: "llcr",
      revision: 1,
      project_id: "project-1",
      confirmed_matrix_id: "matrix-1",
      confirmed_matrix_revision: 4,
      source_file_name: "LLCR.xlsx",
      source_sha256: "sha",
      parser_profile_version: "connlab-llcr-v1",
      validation_status: "confirmed",
      confirmed_at: "2026-08-29T09:00:00Z",
      confirmed_by: "Lab User",
      entries: [{ ...preview.entries[0], confirmed_outcome: "pass" }],
    });
  });

  it("mutually locks authoring and legacy report operations until their real requests settle", async () => {
    const authoringState: authoring.ReportAuthoringState = { project_id: 'project-1', revision: 1,
      base_source_id: null, mappings: [], outputs: [], context: { dl_number: 'DL-001', matrix_id: 'matrix-1', steps: [] },
      sources: [{ source_id: 'source', role: 'original', file_name: 'Original.docx', sha256: 'a', size_bytes: 1,
        created_at: '', report_dl: 'DL-001', download_url: '/source' }] };
    vi.mocked(authoring.getReportAuthoring).mockResolvedValue(authoringState);
    let finishBase!: (value: authoring.ReportAuthoringState) => void;
    vi.mocked(authoring.selectReportBase).mockReturnValue(new Promise(resolve => { finishBase = resolve; }));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole('region', { name: 'Internal Report' });
    await userEvent.click(screen.getByText('Report content', { selector: 'summary' }));
    await userEvent.click(await screen.findByText('Use as report base'));
    expect(screen.getByText('Update Equipment List').matches(':disabled')).toBe(true);
    expect(screen.getByText('Regenerate internal report…').matches(':disabled')).toBe(true);
    await userEvent.click(screen.getByText('Update Equipment List'));
    expect(api.updateEquipmentListOneClick).not.toHaveBeenCalled();
    await act(async () => finishBase({ ...authoringState, revision: 2 }));
    expect(screen.getByText('Update Equipment List').matches(':disabled')).toBe(false);
    let failEquipment!: (error: Error) => void;
    vi.mocked(api.updateEquipmentListOneClick).mockReturnValue(new Promise((_resolve, reject) => { failEquipment = reject; }));
    await userEvent.click(screen.getByText('Update Equipment List'));
    expect(screen.getByText('Use as report base').matches(':disabled')).toBe(true);
    expect(screen.getByText('Reload saved evidence').matches(':disabled')).toBe(true);
    await act(async () => failEquipment(new Error('Temporary equipment error')));
    expect(screen.getByText('Use as report base').matches(':disabled')).toBe(false);
  });

  it("keeps internal report visible when customer status fails and retries without generation", async () => {
    vi.mocked(api.fetchCurrentCustomerReport).mockRejectedValueOnce(new Error("Internal Server Error"));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByRole("region", { name: "Internal Report" })).toBeTruthy();
    expect(await screen.findByText(/Unable to check the customer report/)).toBeTruthy();
    expect(screen.queryByText("Internal Server Error")).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: "Retry report status" }));
    await waitFor(() => expect(screen.queryByText(/Unable to check the customer report/)).toBeNull());
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("shows a customer read blocker without hiding the internal report", async () => {
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({ ...customerReport,
      status: "blocked", can_generate: false, download_url: null,
      blockers: ["The protected customer report could not be read. Check its password protection."],
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByRole("region", { name: "Internal Report" })).toBeTruthy();
    expect(await screen.findByText(/protected customer report could not be read/)).toBeTruthy();
  });

  it("places a visible Back button after the project identity", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(<ReportWorkspace projectId="project-1" identityLabel="DL-001 Connector Testing" onBack={onBack} />);
    await screen.findByRole("region", { name: "Report generation" });
    expect(screen.getByRole("heading", { name: "Report", exact: true })).toBeTruthy();
    const actions = screen.getByLabelText("Report Workspace actions");
    const back = within(actions).getByRole("button", { name: "Back To Workspace", exact: true });
    expect(back.textContent?.trim()).toBe("Back");
    expect(back.title).toBe("Back To Workspace");
    expect(actions.lastElementChild).toBe(back);
    expect(within(actions).queryByRole("button", { name: "Open Project Folder", exact: true })).toBeNull();
    await user.click(back);
    expect(onBack).toHaveBeenCalledOnce();
  });

  it("prioritizes the resumable current filename before regeneration and confirms archive regeneration without writing on cancel", async () => {
    const user = userEvent.setup();
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64),
      requires_confirmation: true, mode: "official", current_path: currentReport.file_path!,
      target_path: currentReport.file_path!, blockers: [],
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    const internal = await screen.findByRole("region", { name: "Internal Report" });
    const filename = within(internal).getByText(currentReport.file_name!);
    expect(within(internal).queryByText(currentReport.file_path!)).toBeNull();
    const generate = within(internal).getByRole("button", { name: "Regenerate internal report…" });
    expect(filename.compareDocumentPosition(generate) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
    expect(within(internal).queryByText("Official project report")).toBeNull();
    expect(within(internal).queryByRole("button", { name: "Download Current Report" })).toBeNull();
    expect(within(internal).queryByRole("button", { name: /Open.*folder/ })).toBeNull();
    await user.click(within(internal).getByRole("button", { name: "Regenerate internal report…" }));
    const dialog = await screen.findByRole("dialog", { name: "Archive and regenerate Internal Report" });
    expect(within(dialog).getByText(/manual content, results and photos, will be preserved/)).toBeTruthy();
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("requires a fresh choice when the official report disappears before regeneration preview", async () => {
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({ project_id: "project-1",
      status: "ready", preview_token: "c".repeat(64), requires_confirmation: false, mode: "official",
      target_path: currentReport.file_path!, current_path: null, blockers: [] });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    const regenerate = await screen.findByRole("button", { name: "Regenerate internal report…" });
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null,
      file_name: null, file_path: null, file_sha256: null });
    await userEvent.click(regenerate);
    await screen.findByText(/The official report changed/);
    expect(screen.getByRole("button", { name: "Create a new internal report" })).toBeTruthy();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("ignores a delayed regeneration preview after changing project", async () => {
    const user = userEvent.setup();
    let resolvePreview!: (preview: api.InternalReportGenerationPreview) => void;
    vi.mocked(api.previewInternalReportGeneration).mockReturnValue(new Promise((resolve) => { resolvePreview = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Regenerate internal report…" }));
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await act(async () => resolvePreview({ project_id: "project-1", status: "ready", preview_token: "c".repeat(64),
      requires_confirmation: true, mode: "official", current_path: currentReport.file_path!, target_path: currentReport.file_path!, blockers: [] }));
    expect(screen.queryByRole("dialog", { name: "Archive and regenerate Internal Report" })).toBeNull();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it.each(["managed_draft", "download_draft"] as const)("downloads a %s copy without publishing or archiving the current report", async (mode) => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, mode: "managed_draft" });
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64),
      requires_confirmation: true, mode, current_path: currentReport.file_path!,
      target_path: null, blockers: [],
    });
    vi.mocked(api.downloadInternalReportDraft).mockResolvedValue({blob: new Blob(["draft"]), fileName: "Internal Report draft.docx"});
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", {name: "Generate another internal report…"}));
    expect(await screen.findByText("Downloaded draft: Internal Report draft.docx")).toBeTruthy();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
    expect(screen.queryByRole("dialog", {name: "Archive and regenerate Internal Report"})).toBeNull();
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(screen.getByText(currentReport.file_name!)).toBeTruthy();
  });

  it("does not download a late draft after switching projects", async () => {
    const user = userEvent.setup();
    let finish!: (value: api.BlobDownloadResponse) => void;
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null, file_name: null, file_sha256: null });
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64), requires_confirmation: false,
      mode: "download_draft", current_path: null, target_path: null, blockers: [],
    });
    vi.mocked(api.downloadInternalReportDraft).mockReturnValue(new Promise(resolve => { finish = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", {name: "Create a new internal report"}));
    await waitFor(() => expect(api.downloadInternalReportDraft).toHaveBeenCalled());
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await act(async () => finish({blob: new Blob(["draft"]), fileName: "Old project draft.docx"}));
    expect(URL.createObjectURL).not.toHaveBeenCalled();
    expect(screen.queryByText(/Downloaded draft:/)).toBeNull();
  });

  it("uses the retained draft fingerprint for one-click download when no official internal report exists", async () => {
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({...currentReport, status:"missing",mode:null,file_name:null,file_sha256:null});
    vi.mocked(api.fetchReportUpdateSource).mockResolvedValue({...currentReport,status:"ready",mode:"download_draft",file_name:"Manual draft.docx",file_sha256:"e".repeat(64)});
    vi.mocked(customerContent.inspectProjectCustomerSource).mockResolvedValue(inspection);
    vi.mocked(customerContent.startInspectedCustomerReport).mockResolvedValue({operation_id:"j",status:"completed",stage:"done",elapsed_seconds:0,message:null});
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByText("Manual draft.docx");
    fireEvent.click(screen.getByRole("button",{name:"Generate customer report"}));
    await waitFor(() => expect(customerContent.inspectProjectCustomerSource).toHaveBeenCalledWith("project-1",{source_sha256:"e".repeat(64)}));
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(screen.queryByRole("button",{name:"Review and save to project…"})).toBeNull();
  });

  it("updates and downloads equipment from an available draft even when there is no current official report", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null,
      file_name: null, file_path: null, file_sha256: null });
    vi.mocked(api.fetchReportUpdateSource).mockResolvedValue({ ...currentReport, mode: "download_draft",
      file_name: "DL-001 Report_Draft.docx", folder_path: null });
    vi.mocked(api.updateReportDraftEquipment).mockResolvedValue({ status: "completed", project_id: "project-1", mode: "download_draft",
      file_name: "DL-001 Report_Draft.docx", current_sha256: "e".repeat(64), changed: true, archive_path: null,
      draft_revision_id: "1".repeat(32), statistics: { filled: 1, unmatched: [], incomplete: [], expired: [] } });
    vi.mocked(api.downloadReportWorkingDraft).mockResolvedValue({ blob: new Blob(["updated"]), fileName: "DL-001 Report_Draft.docx" });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Update Equipment List" })).toHaveProperty("disabled", false));
    await user.click(screen.getByRole("button", { name: "Update Equipment List" }));
    await waitFor(() => expect(api.downloadReportWorkingDraft).toHaveBeenCalledWith("project-1", "1".repeat(32)));
    expect(api.updateEquipmentListOneClick).not.toHaveBeenCalled();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it("shows draft download failure without publishing and allows retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null, file_name: null, file_sha256: null });
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64), requires_confirmation: false,
      mode: "download_draft", current_path: null, target_path: null, blockers: [],
    });
    vi.mocked(api.downloadInternalReportDraft).mockRejectedValueOnce(new Error("Check the approved template and retry."))
      .mockResolvedValueOnce({blob: new Blob(["draft"]), fileName: "Report draft.docx"});
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", {name: "Create a new internal report"}));
    expect((await screen.findByRole("alert")).textContent).toContain("Check the approved template and retry.");
    expect(URL.createObjectURL).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", {name: "Create a new internal report"}));
    expect(await screen.findByText("Downloaded draft: Report draft.docx")).toBeTruthy();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("keeps the current filename and actionable failure then obtains a new preview for retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.generateInternalReport).mockRejectedValueOnce(new Error("Confirmed authority changed. Preview generation again."));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Regenerate internal report…" }));
    await user.click(await screen.findByRole("button", { name: "Archive And Regenerate" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Confirmed authority changed. Preview generation again.");
    expect(screen.getByText(currentReport.file_name!)).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "Archive and regenerate Internal Report" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Regenerate internal report…" }));
    expect(api.previewInternalReportGeneration).toHaveBeenCalledTimes(2);
    expect(await screen.findByRole("button", { name: "Archive And Regenerate" })).toBeTruthy();
  });

  it("uses a concise transient success after confirmed regeneration", async () => {
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("button", { name: "Regenerate internal report…" });
    vi.useFakeTimers();
    try {
      await act(async () => fireEvent.click(screen.getByRole("button", { name: "Regenerate internal report…" })));
      await act(async () => fireEvent.click(screen.getByRole("button", { name: "Archive And Regenerate" })));
      expect(api.generateInternalReport).toHaveBeenCalledWith("project-1", "c".repeat(64), true);
      expect(screen.getByText("Generated the Internal Report.")).toBeTruthy();
      await act(async () => vi.advanceTimersByTimeAsync(5000));
      expect(screen.queryByText("Generated the Internal Report.")).toBeNull();
    } finally { vi.useRealTimers(); }
  });

  it("shows an explicit loading state while workspace authority is loading", () => {
    vi.mocked(api.fetchReportWorkspace).mockReturnValue(new Promise(() => undefined));
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockReturnValue(new Promise(() => undefined));
    vi.mocked(api.fetchReportUpdateSource).mockReturnValue(new Promise(() => undefined));

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(screen.getByRole("status").textContent).toContain("Loading Report Workspace...");
  });

  it("shares the top bar and combines both report generators above the update section", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(
      <AppShell activeRoute="workbench" topBarTitle="Report">
        <ReportWorkspace projectId="project-1" identityLabel="DL-001 Connector Qualification Testing" onBack={onBack} />
      </AppShell>
    );
    await screen.findByText(currentReport.file_name!);
    expect(screen.getAllByRole("heading", { name: "Report" })).toHaveLength(1);
    const actions = screen.getByLabelText("Report Workspace actions");
    expect(screen.getByLabelText("Page actions").contains(actions)).toBe(true);
    expect(within(actions).getByText("DL-001 Connector Qualification Testing")).toBeTruthy();
    expect(screen.getByRole("region", { name: "Internal Report" })).toBeTruthy();
    const updates = screen.getByRole("region", { name: "Update Internal Report" });
    expect(within(updates).getByLabelText("LLCR result workbook")).toBeTruthy();
    expect(within(updates).getByRole("button", { name: "Update Equipment List" })).toBeTruthy();
    const generation = screen.getByRole("region", { name: "Report generation" });
    expect(within(generation).getByRole("button", { name: "Regenerate internal report…" })).toBeTruthy();
    expect(within(generation).getByRole("button", { name: "Review and save to project…" })).toBeTruthy();
    expect(within(generation).getByText(customerReport.file_name!)).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "Customer Report" })).toBeNull();
    expect(screen.queryByText("Project project-1")).toBeNull();
    await user.click(within(actions).getByRole("button", { name: "Back To Workspace" }));
    expect(onBack).toHaveBeenCalledOnce();
  });

  const inspection = {input_id:"checked", source_sha256:"sha", decisions:{}, fields:[], samples:[], temperatures:[]};
  it.each(["registered", "uploaded"] as const)("downloads the %s report in one action and leaves the official files alone", async kind => {
    vi.mocked(customerContent.inspectProjectCustomerSource).mockResolvedValue(inspection);
    vi.mocked(customerContent.inspectUploadedCustomerSource).mockResolvedValue(inspection);
    vi.mocked(customerContent.startInspectedCustomerReport).mockResolvedValue({ operation_id:"job", status:"completed",
      stage:"completed", message:null, elapsed_seconds:1, notices:["Check the missing test description."] });
    vi.mocked(api.downloadStandaloneCustomerReport).mockResolvedValue({blob:new Blob(["report"]),fileName:"Customer.docx"});
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()}/>);
    const action = await screen.findByRole("button", {name:"Generate customer report"});
    if (kind === "registered") {
      fireEvent.click(action);
      await waitFor(() => expect(customerContent.inspectProjectCustomerSource).toHaveBeenCalledWith("project-1",{source_sha256:currentReport.file_sha256}));
    } else {
      const file = new File(["hand-reviewed"],"Finished Word.docx");
      fireEvent.change(screen.getByLabelText("Select Internal Report"), {target:{files:[file]}});
      await waitFor(() => expect(customerContent.inspectUploadedCustomerSource).toHaveBeenCalledWith(file));
    }
    expect((await screen.findByRole("status",{name:"Downloaded File"})).textContent).toBe("Customer.docx");
    expect(screen.getByText("1 item to review in Word")).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(customerContent.startInspectedCustomerReport).toHaveBeenCalledWith("checked",{});
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("shows a specific Word format error before uploading", async () => {
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()}/>);
    await screen.findByRole("button",{name:"Generate customer report"});
    fireEvent.change(screen.getByLabelText("Select Internal Report"),{target:{files:[new File(["bad"],"report.pdf")]}});
    expect(await screen.findByText("Select an internal Word report in .docx format.")).toBeTruthy();
    expect(customerContent.inspectUploadedCustomerSource).not.toHaveBeenCalled();
  });

  it("refuses a changed default source without silently switching to an upload or an official write", async () => {
    vi.mocked(customerContent.inspectProjectCustomerSource).mockRejectedValue(new Error("Internal report changed. Refresh and try again."));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button",{name:"Generate customer report"}));
    expect(await screen.findByText("Internal report changed. Refresh and try again.")).toBeTruthy();
    expect(customerContent.inspectUploadedCustomerSource).not.toHaveBeenCalled();
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("discards a late source inspection after changing projects", async () => {
    let complete!: (value: typeof inspection) => void;
    vi.mocked(customerContent.inspectProjectCustomerSource).mockReturnValueOnce(new Promise(r => { complete=r; }));
    const {rerender}=render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button",{name:"Generate customer report"}));
    rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()}/>);
    await act(async () => complete(inspection));
    expect(customerContent.discardCustomerInput).toHaveBeenCalledWith("checked");
    expect(customerContent.startInspectedCustomerReport).not.toHaveBeenCalled();
  });

  it("shows the registered LTR and confirmed Basic Information, not draft or stale project descriptions", async () => {
    vi.mocked(api.getProject).mockResolvedValue({
      project_id: "project-1", project_no: "OLD-REF", product_name: "Stale product",
      sample_description: "Stale description", test_item: "Stale test", requestor: "Lab User", status: "active",
    });
    vi.mocked(api.listProjectLtrs).mockResolvedValue([
      { ltr_id: "ltr-1", project_id: "project-1", ltr_number: "DL-001", status: "registered" },
    ]);
    vi.mocked(api.getProjectBasicInformation).mockResolvedValue({
      project_id: "project-1", status: "confirmed",
      draft: { values: { product_description: "Unconfirmed edit", test_item: "Draft test" } },
      latest_confirmed: {
        record_id: "basic-2", project_id: "project-1", status: "confirmed", version: 2,
        values: { product_description: "Confirmed connector", test_item: "Qualification Testing" },
        source_signature: "basic-sha", created_at: "2026-10-02", updated_at: "2026-10-02",
      },
      field_suggestions: {}, changed_source_fields: [], missing_required_fields: [],
      missing_required_labels: [], blockers: [], warnings: [],
    });
    render(<AppShell activeRoute="workbench" topBarTitle="Report">
      <ProjectReportWorkspacePage projectId="project-1" onBackToWorkbench={vi.fn()} />
    </AppShell>);
    expect(await screen.findByText("DL-001 Confirmed connector Qualification Testing")).toBeTruthy();
    expect(screen.queryByText(/Unconfirmed edit|Stale description/)).toBeNull();
    expect(screen.getAllByRole("heading", { name: "Report" })).toHaveLength(1);
  });

  it("keeps report operations available when optional identity lookups fail", async () => {
    vi.mocked(api.getProject).mockRejectedValue(new Error("Project label unavailable"));
    vi.mocked(api.listProjectLtrs).mockResolvedValue([
      { ltr_id: "ltr-1", project_id: "project-1", ltr_number: "DL-001", status: "registered" },
    ]);
    vi.mocked(api.getProjectBasicInformation).mockRejectedValue(new Error("Basic label unavailable"));
    render(<ProjectReportWorkspacePage projectId="project-1" onBackToWorkbench={vi.fn()} />);
    expect(await screen.findByText("DL-001 Connector Project")).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("keeps LLCR inspection independent of initial report generation without inventing a missing folder", async () => {
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({
      ...currentReport, status: "missing", mode: null, file_name: null, file_sha256: null,
      folder_path: null, download_url: null,
    });
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({
      ...customerReport, status: "blocked", mode: "managed_download", file_name: null,
      can_generate: false, internal_report_sha256: null, warnings: [],
      blockers: ["A single current Internal Report is required."], download_url: null,
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("region", { name: "Update Internal Report" });
    expect(screen.queryByText("Browser download (no official project folder)")).toBeNull();
    expect(screen.queryByRole("button", { name: "Update LLCR Results" })).toBeNull();
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    expect(await screen.findByRole("dialog", { name: "LLCR import preview" })).toBeTruthy();
    expect(api.inspectLlcrResultWorkbook).toHaveBeenCalledOnce();
    expect(api.generateInitialReportRevision).not.toHaveBeenCalled();
  });

  it("shows the workbook readings and locates a missing stage before confirmation", async () => {
    const point = {
      group_label: "A", sample_index: 2, position: "P1", raw_unit: "mΩ", unit: "mΩ", source_sheet: "P",
    };
    vi.mocked(api.inspectLlcrResultWorkbook).mockResolvedValue({
      ...preview, can_confirm: false, entries: [],
      readings: [
        { ...point, step_token: "2", stage_label: "Initial", stage: "initial",
          raw_source_cell: "D12", raw_value: "2.10", source_cell: "M12", value: "0.20" },
        { ...point, step_token: "5", stage_label: "Final", stage: "delta",
          raw_source_cell: "D20", raw_value: null, source_cell: "M20", value: null },
      ],
      diagnostics: [{code:"missing", severity:"blocked", group_label:"A", step_token:"5",
        message:"Group A, Final, sample 2, P1: fill in P!D20."}],
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    fireEvent.change(await screen.findByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    const dialog = await screen.findByRole("dialog", { name: "LLCR import preview" });
    const table = within(dialog).getByRole("table", { name: /Group A/ });
    expect(within(table).getByRole("columnheader", { name: /Final/ })).toBeTruthy();
    expect(within(table).getByRole("cell", { name: /2.10 mΩ/ })).toBeTruthy();
    expect(within(table).getByRole("cell", { name: /Missing.*P!D20/ })).toBeTruthy();
    expect(within(dialog).getByText(/fill in P!D20/)).toBeTruthy();
    expect(within(dialog).getByRole("button", { name: "Confirm LLCR Dataset" })).toHaveProperty("disabled", true);
  });

  it("exposes the current report, LLCR import preview, and confirmation", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(<ReportWorkspace projectId="project-1" onBack={onBack} />);

    expect(await screen.findByRole("heading", { name: "Report" })).toBeTruthy();
    expect(screen.queryByText("Project project-1")).toBeNull();
    expect(screen.getAllByText(currentReport.file_name!).length).toBe(1);
    expect(screen.queryByText("Confirmed Matrix r4")).toBeNull();
    expect(screen.queryByText("Basic Information v2")).toBeNull();
    expect(within(screen.getByRole("region", { name: "Internal Report" })).queryByText("Official project report")).toBeNull();
    expect(screen.getByRole("button", { name: "Regenerate internal report…" })).toBeTruthy();

    const fileInput = screen.getByLabelText("LLCR result workbook");
    fireEvent.change(fileInput, {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    expect(await screen.findByRole("dialog", { name: "LLCR import preview" })).toBeTruthy();
    expect(screen.getByText("Group 1 / Step 2")).toBeTruthy();
    expect(screen.getByText("0.031 / 0.082 / 0.0565 mΩ")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Confirm LLCR Dataset" }));
    await waitFor(() => expect(api.confirmLlcrResultImport).toHaveBeenCalledTimes(1));
    expect(api.confirmLlcrResultImport).toHaveBeenCalledWith(
      "project-1",
      expect.objectContaining({
        preview_id: "preview-1",
        decisions: [{ result_id: "result-1", outcome: "pass", override_reason: null }],
      })
    );
  });

  it.each([
    { authority: { ...state, basic_information_status: "unconfirmed" as const }, blocker: "Confirm Basic Information before generating a report draft." },
    { authority: { ...state, active_confirmed_matrix_id: null, active_confirmed_matrix_revision: null }, blocker: "Activate a Confirmed Matrix before generating a report draft." },
  ])("keeps the actionable initial-report blocker: $blocker", async ({ authority, blocker }) => {
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue(authority);
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({
      ...currentReport, status: "missing", mode: null, file_name: null, file_sha256: null, download_url: null,
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    const internal = await screen.findByRole("region", { name: "Internal Report" });
    expect(within(internal).getByText(blocker)).toBeTruthy();
    expect(within(internal).getByRole("button", { name: "Create a new internal report" }).hasAttribute("disabled")).toBe(true);
    expect(screen.queryByText("Basic Information v2")).toBeNull();
    expect(screen.queryByText("Confirmed Matrix r4")).toBeNull();
  });

  it("initializes a missing report after an absence-bound preview without archive confirmation", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({
      status: "missing",
      mode: null,
      file_name: null,
      file_sha256: null,
      report_revision_id: null,
      folder_path: null,
      official_folder_path: null,
      can_publish_to_official: false,
      download_url: null,
    });
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64), requires_confirmation: false,
      mode: "official", current_path: null, target_path: currentReport.file_path!, blockers: [],
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    const generateButton = await screen.findByRole("button", { name: "Create a new internal report" });
    expect(generateButton).toHaveProperty("disabled", false);
    await user.click(generateButton);

    expect(api.generateInternalReport).toHaveBeenCalledWith("project-1", "c".repeat(64), false);
  });

  it("blocks an outcome override until a reason is supplied", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.selectOptions(await screen.findByLabelText("Final outcome for Group 1 / Step 2"), "fail");

    expect(screen.getByRole("button", { name: "Confirm LLCR Dataset" })).toHaveProperty("disabled", true);
    await user.type(screen.getByLabelText("Override reason for Group 1 / Step 2"), "Visual damage");
    expect(screen.getByRole("button", { name: "Confirm LLCR Dataset" })).toHaveProperty("disabled", false);
  });

  it("cancels the staged preview before closing the dialog", async () => {
    const user = userEvent.setup();
    vi.mocked(api.cancelLlcrResultPreview).mockResolvedValue(undefined);
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(await screen.findByRole("button", { name: /^Cancel$/ }));

    await waitFor(() => expect(api.cancelLlcrResultPreview).toHaveBeenCalledWith(
      "project-1",
      "preview-1"
    ));
    expect(screen.queryByRole("dialog", { name: "LLCR import preview" })).toBeNull();
  });

  it("updates only the LLCR region of the current report without selecting a revision", async () => {
    const user = userEvent.setup();
    const dataset = {
      dataset_id: "dataset-1",
      dataset_type: "llcr" as const,
      revision: 1,
      project_id: "project-1",
      confirmed_matrix_id: "matrix-1",
      confirmed_matrix_revision: 4,
      source_file_name: "LLCR.xlsx",
      source_sha256: "sha",
      parser_profile_version: "connlab-llcr-v1",
      validation_status: "confirmed",
      confirmed_at: "2026-08-29T09:00:00Z",
      confirmed_by: "Lab User",
      entries: [{ ...preview.entries[0], confirmed_outcome: "pass" as const }],
    };
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue({
      ...state,
      datasets: [dataset],
    });
    vi.mocked(api.previewCurrentReportLlcrUpdate).mockResolvedValue({
      project_id: "project-1",
      dataset_id: "dataset-1",
      status: "ready",
      current_report: currentReport,
      blockers: [],
      warnings: [],
    });
    vi.mocked(api.updateCurrentReportLlcr).mockResolvedValue({
      project_id: "project-1",
      dataset_id: "dataset-1",
      file_name: currentReport.file_name!,
      mode: "official",
      changed: true,
      current_sha256: "b".repeat(64),
      archive_path: "C:\\Project\\History\\Report\\old.docx",
      updated_by: "Lab User",
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(
      await screen.findByText("LLCR Result and Comment cells and Appendix A")
    ).toBeTruthy();
    await user.click(await screen.findByRole("button", { name: "Update LLCR Results" }));

    expect(api.previewCurrentReportLlcrUpdate).toHaveBeenCalledWith(
      "project-1",
      "dataset-1"
    );
    expect(api.updateCurrentReportLlcr).toHaveBeenCalledWith("project-1", {
      dataset_id: "dataset-1",
      expected_report_sha256: "a".repeat(64),
      updated_by: "Lab User",
    });
    expect(await screen.findByText(/Updated LLCR results in/)).toBeTruthy();
    expect(screen.queryByText("Report draft history")).toBeNull();
  });

  it("publishes the current managed draft to the official project folder explicitly", async () => {
    const user = userEvent.setup();
    const managed: api.CurrentReport = {
      ...currentReport,
      mode: "managed_draft",
      file_name: "DL-001 Qualification Testing Report_Rev_A_Draft (9).docx",
      file_path: "D:\\PythonProject\\connlab\\data\\generated_test_reports\\project-1\\DL-001 Qualification Testing Report_Rev_A_Draft (9).docx",
      folder_path: "D:\\PythonProject\\connlab\\data\\generated_test_reports\\project-1",
      official_folder_path: "D:\\Test Project\\DL-001\\Official Test",
      can_publish_to_official: true,
    };
    vi.mocked(api.fetchCurrentReport).mockResolvedValue(managed);
    vi.mocked(api.publishManagedReport).mockResolvedValue({
      ...currentReport,
      file_name: "DL-001 Qualification Testing Report_Rev_A.docx",
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(await screen.findByText(managed.file_name!)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Download Current Report" })).toBeTruthy();
    await user.click(
      screen.getByRole("button", { name: "Publish Current Draft To Project Folder" })
    );

    expect(api.publishManagedReport).toHaveBeenCalledWith(
      "project-1",
      "a".repeat(64)
    );
    expect(await screen.findByText(/Published the current report to/)).toBeTruthy();
  });

  it.each([false, true])("finishes a healthy equipment update without opening a completion dialog (changed=%s)", async (changed) => {
    const user = userEvent.setup();
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValue({
      status: "completed", project_id: "project-1", file_name: currentReport.file_name!,
      changed, current_sha256: "a".repeat(64), archive_path: changed ? "History/Report/old.docx" : null,
      statistics: { filled: 9, unmatched: [], incomplete: [], expired: [] },
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Update Equipment List" })).toHaveProperty("disabled", false));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.queryByText(/Equipment rows filled/)).toBeNull();
    expect(screen.getByRole("status", { name: "Equipment List update status" }).textContent).toBe(
      changed ? "Equipment List Updated." : "Equipment List Is Up To Date.",
    );
  });

  it("shows only actual equipment issues with guidance after updating", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValue({
      status: "completed", project_id: "project-1", file_name: currentReport.file_name!,
      changed: true, current_sha256: "d".repeat(64), archive_path: "History/Report/old.docx",
      statistics: { filled: 3, unmatched: ["DG-Q-9999"], incomplete: ["DG-Q-0022"], expired: [] },
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    const dialog = await screen.findByRole("dialog", { name: "Equipment List Needs Review" });
    expect(within(dialog).getByText(/DG-Q-9999/).textContent).toBe(
      "Equipment IDs not found in the calibration workbook: DG-Q-9999. Use DG-Q-XXXX or DG-L-XXXX with four digits (e.g., DG-Q-0913). If an ID is correct but missing, add it to the workbook.",
    );
    expect(within(dialog).getByText(/DG-Q-0022/).textContent).toContain("Complete equipment details");
    expect(within(dialog).queryByText(/Expired Calibration/)).toBeNull();
    expect(within(dialog).queryByText(/Equipment rows filled|History\/Report|Report_Rev_A/)).toBeNull();
    await user.click(within(dialog).getByRole("button", { name: "Close" }));
    expect(screen.getByRole("status", { name: "Equipment List update status" }).textContent).toBe("Equipment List Updated.");
  });

  it("clears equipment completion on retry and project change without claiming a failed request succeeded", async () => {
    const user = userEvent.setup();
    const completed: api.EquipmentListOneClickResult = {
      status: "completed", project_id: "project-1", file_name: currentReport.file_name!,
      changed: true, current_sha256: "d".repeat(64), archive_path: "History/Report/old.docx",
      statistics: { filled: 3, unmatched: [], incomplete: [], expired: [] },
    };
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValue(completed);
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    expect(await screen.findByRole("status", { name: "Equipment List update status" })).toBeTruthy();
    await waitFor(() => expect(screen.getByRole("button", { name: "Update Equipment List" })).toHaveProperty("disabled", false));
    let rejectRequest!: (reason: Error) => void;
    vi.mocked(api.updateEquipmentListOneClick).mockImplementationOnce(() => new Promise((_resolve, reject) => { rejectRequest = reject; }));
    await user.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect(screen.queryByRole("status", { name: "Equipment List update status" })).toBeNull();
    await act(async () => rejectRequest(new Error("Report is locked. Close it and retry.")));
    expect(await screen.findByText("Report is locked. Close it and retry.")).toBeTruthy();
    expect(screen.queryByRole("status", { name: "Equipment List update status" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect(await screen.findByRole("status", { name: "Equipment List update status" })).toBeTruthy();
    await waitFor(() => expect(screen.getByRole("button", { name: "Update Equipment List" })).toHaveProperty("disabled", false));
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    expect(screen.queryByRole("status", { name: "Equipment List update status" })).toBeNull();
    await waitFor(() => expect(screen.getByRole("button", { name: "Update Equipment List" })).toHaveProperty("disabled", false));
  });

  it("updates equipment in one click and shows expired statistics only afterwards", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    const dialog = await screen.findByRole("dialog", { name: "Equipment List Needs Review" });
    expect(within(dialog).getByText(/Expired Calibration.*DG-Q-0033/)).toBeTruthy();
    expect(within(dialog).queryByText(/Equipment IDs not found|Incomplete Information/)).toBeNull();
    expect(api.updateEquipmentListOneClick).toHaveBeenCalledWith("project-1", undefined);
    expect(api.previewCurrentReportEquipmentList).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("I reviewed the expired calibration warning")).toBeNull();
  });

  it("asks for missing equipment IDs, saves pasted selection and then updates", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValueOnce({ status: "source_required", project_id: "project-1" });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    const dialog = await screen.findByRole("dialog", { name: "Provide equipment IDs" });
    await user.type(within(dialog).getByLabelText("Equipment IDs"), "DG-Q-0033");
    await user.click(within(dialog).getByRole("button", { name: "Save And Update" }));
    expect(api.updateEquipmentListOneClick).toHaveBeenLastCalledWith("project-1", { referencesText: "DG-Q-0033" });
    expect(await screen.findByRole("dialog", { name: "Equipment List Needs Review" })).toBeTruthy();
  });

  it("canceling missing equipment selection makes no second request", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValueOnce({ status: "source_required", project_id: "project-1" });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    await user.click(within(await screen.findByRole("dialog", { name: "Provide equipment IDs" })).getByRole("button", { name: "Cancel" }));
    expect(api.updateEquipmentListOneClick).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("sends a selected equipment DOCX only when the default source is missing", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateEquipmentListOneClick).mockResolvedValueOnce({ status: "source_required", project_id: "project-1" });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    const file = new File(["equipment"], "EquipmentID.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    await user.upload(within(await screen.findByRole("dialog", { name: "Provide equipment IDs" })).getByLabelText("EquipmentID document"), file);
    await user.click(screen.getByRole("button", { name: "Save And Update" }));
    expect(api.updateEquipmentListOneClick).toHaveBeenLastCalledWith("project-1", { file });
  });

  it("starts one equipment request on double click and ignores a delayed result after changing projects", async () => {
    let finish!: (result: api.EquipmentListOneClickResult) => void;
    vi.mocked(api.updateEquipmentListOneClick).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    const button = await screen.findByRole("button", { name: "Update Equipment List" });
    fireEvent.click(button);
    fireEvent.click(button);
    expect(api.updateEquipmentListOneClick).toHaveBeenCalledTimes(1);
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await act(async () => finish({ status: "source_required", project_id: "project-1" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("does not display a delayed equipment failure after unmount", async () => {
    let fail!: (reason: Error) => void;
    vi.mocked(api.updateEquipmentListOneClick).mockImplementationOnce(() => new Promise((_resolve, reject) => { fail = reject; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button", { name: "Update Equipment List" }));
    view.unmount();
    await act(async () => fail(new Error("Equipment update failed")));
    expect(screen.queryByText("Equipment update failed")).toBeNull();
  });

  it.each(["ready","stale","untracked"] as const)("uses a reviewed working copy when saving over a %s customer report", async status => {
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({...customerReport,status});
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()}/>);
    const menu = await screen.findByText('Report file actions');
    expect(menu.closest('details')?.open).toBe(false);
    fireEvent.click(menu);
    const save = screen.getByRole('button',{name:'Review and save to project…'});
    fireEvent.click(save);
    await waitFor(() => expect(authoring.adoptCurrentReportWorkingCopy).toHaveBeenCalledWith("project-1",
      expect.objectContaining({source_mode:"official",source_sha256:currentReport.file_sha256})));
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(api.generateCurrentCustomerReport).not.toHaveBeenCalled();
  });

  it("recovers real progress above the disabled generation button", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completedJob, status: "running", stage: "formatting_document", elapsed_seconds: 19, result: null,
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Applying customer-report layout and headers...")).toBeTruthy();
    expect(screen.getByText("19 seconds elapsed")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Generate customer report" }) as HTMLButtonElement).disabled).toBe(true);
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("keeps publication failure visible without claiming generation is still running", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completedJob, status: "failed", stage: "publishing", result: null,
      error_code: "customer_report_publication_failed", message: "The target file changed.",
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Publication failed: The target file changed.")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Review and save to project…" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("restores an official result without repeating its filename in a permanent success notice", async () => {
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({ ...customerReport, status: "ready",
      file_name: "Customer.docx", warnings: [] });
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completedJob,
      result: { mode: "official", file_name: "Customer.docx", changed: true, archive_path: null },
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Customer.docx")).toBeTruthy();
    expect(screen.queryByText("Customer report generation completed.")).toBeNull();
    expect(screen.queryByText(/seconds elapsed/)).toBeNull();
    expect(screen.queryByText(/Customer report is ready/)).toBeNull();
    expect(screen.queryByText(/Updated the customer report|archived automatically/)).toBeNull();
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });
});
