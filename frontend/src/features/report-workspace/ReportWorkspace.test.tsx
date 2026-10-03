import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
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
    fetchCurrentCustomerReport: vi.fn(),
    startStandaloneCustomerReport: vi.fn(),
    readStandaloneCustomerReportJob: vi.fn(),
    downloadStandaloneCustomerReport: vi.fn(),
    inspectLlcrResultWorkbook: vi.fn(),
    confirmLlcrResultImport: vi.fn(),
    generateInitialReportRevision: vi.fn(),
    previewInternalReportGeneration: vi.fn(),
    generateInternalReport: vi.fn(),
    openLocalProjectFolder: vi.fn(),
    getPublicFolderWorkflowContext: vi.fn(),
    previewCurrentReportLlcrUpdate: vi.fn(),
    updateCurrentReportLlcr: vi.fn(),
    previewCurrentReportEquipmentList: vi.fn(),
    updateCurrentReportEquipmentList: vi.fn(),
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

const folderContext: api.PublicFolderWorkflowContext = {
  project_id: "project-1", auto_sync_enabled: false, sync_locked: false, submitted_at: null,
  public_root: null, public_root_class: null, public_folder_year: null, year_source: null, year_evidence: null,
  local_official_folder_path: currentReport.folder_path, local_official_folder_available: true,
  public_open_path: null, public_closed_path: null, blockers: ["The public drive is unavailable."], warnings: [],
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
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue(customerReport);
    vi.mocked(api.getPublicFolderWorkflowContext).mockResolvedValue(folderContext);
    vi.mocked(api.previewInternalReportGeneration).mockResolvedValue({
      project_id: "project-1", status: "ready", preview_token: "c".repeat(64), requires_confirmation: true,
      mode: "official", current_path: currentReport.file_path!, target_path: currentReport.file_path!, blockers: [],
    });
    vi.mocked(api.generateInternalReport).mockResolvedValue({ project_id: "project-1", mode: "official", file_name: currentReport.file_name!,
      file_path: currentReport.file_path!, file_sha256: "d".repeat(64), archive_path: "History/Report/old.docx" });
    vi.mocked(api.openLocalProjectFolder).mockResolvedValue({ project_id: "project-1", status: "opened", message: "Opened", local_official_folder_path: currentReport.folder_path });
    vi.mocked(api.inspectLlcrResultWorkbook).mockResolvedValue(preview);
    vi.mocked(api.previewCurrentReportEquipmentList).mockResolvedValue(equipmentPreview);
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

  it("opens an available project folder from the header before any report exists", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null,
      file_name: null, file_path: null, file_sha256: null, folder_path: null, download_url: null });
    render(<AppShell activeRoute="workbench" topBarTitle="Report Workspace">
      <ReportWorkspace projectId="project-1" onBack={vi.fn()} />
    </AppShell>);
    const internal = await screen.findByRole("region", { name: "Internal Report" });
    const actions = screen.getByLabelText("Report Workspace actions");
    const open = within(actions).getByRole("button", { name: "Open project folder" });
    expect(within(actions).getAllByRole("button").map((button) => button.textContent)).toEqual([
      "Open project folder", "Back to Workspace",
    ]);
    expect(within(internal).queryByRole("button", { name: /Open.*folder/ })).toBeNull();
    await waitFor(() => expect(open.hasAttribute("disabled")).toBe(false));
    await user.click(open);
    expect(api.getPublicFolderWorkflowContext).toHaveBeenCalledWith("project-1");
    expect(api.openLocalProjectFolder).toHaveBeenCalledWith("project-1");
  });

  it("shows only the current filename below Generate and confirms archive regeneration without writing on cancel", async () => {
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
    const generate = within(internal).getByRole("button", { name: "Generate Internal Report" });
    expect(generate.compareDocumentPosition(filename) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
    expect(within(internal).queryByText("Official project report")).toBeNull();
    expect(within(internal).queryByRole("button", { name: "Download current report" })).toBeNull();
    expect(within(internal).queryByRole("button", { name: /Open.*folder/ })).toBeNull();
    await user.click(within(internal).getByRole("button", { name: "Generate Internal Report" }));
    const dialog = await screen.findByRole("dialog", { name: "Archive and regenerate Internal Report" });
    expect(within(dialog).getByText(/manual content, results and photos, will be preserved/)).toBeTruthy();
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("ignores a delayed regeneration preview after changing project", async () => {
    const user = userEvent.setup();
    let resolvePreview!: (preview: api.InternalReportGenerationPreview) => void;
    vi.mocked(api.previewInternalReportGeneration).mockReturnValue(new Promise((resolve) => { resolvePreview = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate Internal Report" }));
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await act(async () => resolvePreview({ project_id: "project-1", status: "ready", preview_token: "c".repeat(64),
      requires_confirmation: true, mode: "official", current_path: currentReport.file_path!, target_path: currentReport.file_path!, blockers: [] }));
    expect(screen.queryByRole("dialog", { name: "Archive and regenerate Internal Report" })).toBeNull();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
  });

  it("keeps the current filename and actionable failure then obtains a new preview for retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.generateInternalReport).mockRejectedValueOnce(new Error("Confirmed authority changed. Preview generation again."));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate Internal Report" }));
    await user.click(await screen.findByRole("button", { name: "Archive and regenerate" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Confirmed authority changed. Preview generation again.");
    expect(screen.getByText(currentReport.file_name!)).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "Archive and regenerate Internal Report" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Generate Internal Report" }));
    expect(api.previewInternalReportGeneration).toHaveBeenCalledTimes(2);
    expect(await screen.findByRole("button", { name: "Archive and regenerate" })).toBeTruthy();
  });

  it("shows backend folder-opening blockers without accepting the displayed path as input", async () => {
    const user = userEvent.setup();
    vi.mocked(api.openLocalProjectFolder).mockResolvedValue({ project_id: "project-1", status: "blocked", message: "Restore or link the project folder.", local_official_folder_path: null });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Open project folder" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Restore or link the project folder.");
    expect(api.openLocalProjectFolder).toHaveBeenCalledWith("project-1");
    const open = screen.getByRole("button", { name: "Open project folder" });
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(open.parentElement?.title).toBe("Restore or link the project folder.");
    expect(screen.getByRole("button", { name: "Generate Internal Report" }).hasAttribute("disabled")).toBe(false);
  });

  it.each([
    [null, "No project folder is linked. Create or link it in Workspace."],
    ["D:\\Unavailable folder", "The project folder is unavailable. Restore or link it in Workspace."],
  ])("explains an unavailable local folder independently of a ready report: %s", async (path, reason) => {
    vi.mocked(api.getPublicFolderWorkflowContext).mockResolvedValue({ ...folderContext,
      local_official_folder_path: path, local_official_folder_available: false });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("region", { name: "Internal Report" });
    const open = screen.getByRole("button", { name: "Open project folder" });
    await waitFor(() => expect(open.parentElement?.title).toBe(reason));
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(screen.getByText(currentReport.file_name!)).toBeTruthy();
    expect(api.openLocalProjectFolder).not.toHaveBeenCalled();
  });

  it("keeps report generation available when checking the project folder fails", async () => {
    const user = userEvent.setup();
    vi.mocked(api.getPublicFolderWorkflowContext).mockRejectedValue(new Error("Folder context unavailable"));
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("region", { name: "Internal Report" });
    const open = screen.getByRole("button", { name: "Open project folder" });
    await waitFor(() => expect(open.parentElement?.title).toBe("Unable to check the project folder. Return to Workspace and retry."));
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(screen.queryByRole("alert")).toBeNull();
    await user.click(screen.getByRole("button", { name: "Generate Internal Report" }));
    expect(await screen.findByRole("dialog", { name: "Archive and regenerate Internal Report" })).toBeTruthy();
  });

  it("ignores delayed folder availability after switching project or unmounting", async () => {
    let resolveOld!: (context: api.PublicFolderWorkflowContext) => void;
    let resolveNew!: (context: api.PublicFolderWorkflowContext) => void;
    vi.mocked(api.getPublicFolderWorkflowContext)
      .mockReturnValueOnce(new Promise((resolve) => { resolveOld = resolve; }))
      .mockReturnValueOnce(new Promise((resolve) => { resolveNew = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("region", { name: "Internal Report" });
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    const open = screen.getByRole("button", { name: "Open project folder" });
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(open.parentElement?.title).toBe("Checking project folder availability...");
    await act(async () => resolveOld(folderContext));
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(open.parentElement?.title).toBe("Checking project folder availability...");
    view.unmount();
    await act(async () => resolveNew({ ...folderContext, project_id: "project-2" }));
    expect(screen.queryByLabelText("Report Workspace actions")).toBeNull();
  });

  it("ignores a delayed folder-opening failure on another project", async () => {
    const user = userEvent.setup();
    let resolveOpen!: (response: api.ProjectFolderOpenResponse) => void;
    vi.mocked(api.openLocalProjectFolder).mockReturnValueOnce(new Promise((resolve) => { resolveOpen = resolve; }));
    const view = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("region", { name: "Internal Report" });
    await user.click(screen.getByRole("button", { name: "Open project folder" }));
    view.rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Open project folder" }).hasAttribute("disabled")).toBe(false));
    await act(async () => resolveOpen({ project_id: "project-1", status: "blocked", message: "Old folder unavailable.", local_official_folder_path: null }));
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByRole("button", { name: "Open project folder" }).hasAttribute("disabled")).toBe(false);
  });

  it("uses a concise transient success after confirmed regeneration", async () => {
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("button", { name: "Generate Internal Report" });
    vi.useFakeTimers();
    try {
      await act(async () => fireEvent.click(screen.getByRole("button", { name: "Generate Internal Report" })));
      await act(async () => fireEvent.click(screen.getByRole("button", { name: "Archive and regenerate" })));
      expect(api.generateInternalReport).toHaveBeenCalledWith("project-1", "c".repeat(64), true);
      expect(screen.getByText("Generated the Internal Report.")).toBeTruthy();
      await act(async () => vi.advanceTimersByTimeAsync(5000));
      expect(screen.queryByText("Generated the Internal Report.")).toBeNull();
    } finally { vi.useRealTimers(); }
  });

  it("shows an explicit loading state while workspace authority is loading", () => {
    vi.mocked(api.fetchReportWorkspace).mockReturnValue(new Promise(() => undefined));
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockReturnValue(new Promise(() => undefined));
    vi.mocked(api.getPublicFolderWorkflowContext).mockReturnValueOnce(new Promise(() => undefined));

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(screen.getByRole("status").textContent).toContain("Loading Report Workspace...");
    const open = within(screen.getByLabelText("Report Workspace actions")).getByRole("button", { name: "Open project folder" });
    expect(open.hasAttribute("disabled")).toBe(true);
    expect(open.parentElement?.title).toBe("Checking project folder availability...");
  });

  it("shares the top bar and combines both report generators above the update section", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(
      <AppShell activeRoute="workbench" topBarTitle="Report Workspace">
        <ReportWorkspace projectId="project-1" identityLabel="DL-001 Connector Qualification Testing" onBack={onBack} />
      </AppShell>
    );
    await screen.findByText(currentReport.file_name!);
    expect(screen.getAllByRole("heading", { name: "Report Workspace" })).toHaveLength(1);
    const actions = screen.getByLabelText("Report Workspace actions");
    expect(screen.getByLabelText("Page actions").contains(actions)).toBe(true);
    expect(within(actions).getByText("DL-001 Connector Qualification Testing")).toBeTruthy();
    expect(screen.getByRole("region", { name: "Internal Report" })).toBeTruthy();
    const updates = screen.getByRole("region", { name: "Update Internal Report" });
    expect(within(updates).getByLabelText("LLCR result workbook")).toBeTruthy();
    expect(within(updates).getByRole("button", { name: "Preview Equipment List" })).toBeTruthy();
    const generation = screen.getByRole("region", { name: "Report generation" });
    expect(within(generation).getByRole("button", { name: "Generate Internal Report" })).toBeTruthy();
    expect(within(generation).getByRole("button", { name: "Generate customer report" })).toBeTruthy();
    expect(within(generation).getByText(customerReport.file_name!)).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "Customer Report" })).toBeNull();
    expect(screen.queryByText("Project project-1")).toBeNull();
    await user.click(within(actions).getByRole("button", { name: "Back to Workspace" }));
    expect(onBack).toHaveBeenCalledOnce();
  });

  it("chooses an existing internal DOCX only when the current report is missing and downloads a copy", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null,
      file_name: null, file_path: null, file_sha256: null, download_url: null });
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({ ...customerReport,
      status: "blocked", can_generate: false, file_name: null, warnings: [],
      blockers: ["A single current Internal Report is required."] });
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue({ operation_id: "uploaded-1",
      status: "completed", stage: "completed", elapsed_seconds: 1, message: null });
    vi.mocked(api.downloadStandaloneCustomerReport).mockResolvedValue({ blob: new Blob(["docx"]), fileName: "Other-CR Report.docx" });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));
    const dialog = await screen.findByRole("dialog", { name: "Select Internal Report" });
    const file = new File(["existing report"], "Other Report.docx");
    fireEvent.change(within(dialog).getByLabelText("Internal Report file"), { target: { files: [file] } });
    await user.click(within(dialog).getByRole("button", { name: "Generate customer report" }));
    expect(await screen.findByText("Other-CR Report.docx")).toBeTruthy();
    expect(screen.queryByText("Customer report generation completed.")).toBeNull();
    expect(screen.queryByText(/seconds elapsed/)).toBeNull();
    expect(api.startStandaloneCustomerReport).toHaveBeenCalledWith(file);
    expect(api.downloadStandaloneCustomerReport).toHaveBeenCalledWith("uploaded-1");
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(api.generateInternalReport).not.toHaveBeenCalled();
    expect(screen.queryByRole("dialog", { name: "Select Internal Report" })).toBeNull();
  });

  it("cancels the source picker, rejects non-DOCX files, and keeps the source file local", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "missing", mode: null, file_name: null });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));
    const dialog = screen.getByRole("dialog", { name: "Select Internal Report" });
    fireEvent.change(within(dialog).getByLabelText("Internal Report file"), { target: { files: [new File(["bad"], "report.pdf")] } });
    expect(within(dialog).getByRole("alert").textContent).toContain(".docx");
    expect(within(dialog).getByRole("button", { name: "Generate customer report" })).toHaveProperty("disabled", true);
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(api.startStandaloneCustomerReport).not.toHaveBeenCalled();
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("does not offer an uploaded source to bypass ambiguous internal reports", async () => {
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({ ...currentReport, status: "ambiguous", file_name: null });
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({ ...customerReport, status: "blocked", can_generate: false });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByRole("button", { name: "Generate customer report" })).toHaveProperty("disabled", true);
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(api.startStandaloneCustomerReport).not.toHaveBeenCalled();
  });

  it("rechecks the default source and does not upload if a project report appeared", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValueOnce({ ...currentReport, status: "missing", file_name: null }).mockResolvedValue(currentReport);
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));
    const dialog = screen.getByRole("dialog", { name: "Select Internal Report" });
    fireEvent.change(within(dialog).getByLabelText("Internal Report file"), { target: { files: [new File(["source"], "Other.docx")] } });
    await user.click(within(dialog).getByRole("button", { name: "Generate customer report" }));
    expect(await screen.findByText("The current Internal Report changed. Review the current report before generating.")).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(api.startStandaloneCustomerReport).not.toHaveBeenCalled();
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("ignores a missing-source check that finishes after changing project", async () => {
    const user = userEvent.setup();
    const missing: api.CurrentReport = { ...currentReport, status: "missing", file_name: null };
    let resolve!: (value: api.CurrentReport) => void;
    vi.mocked(api.fetchCurrentReport).mockResolvedValueOnce(missing)
      .mockImplementationOnce(() => new Promise(r => { resolve = r; })).mockResolvedValue(currentReport);
    const { rerender } = render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));
    const dialog = screen.getByRole("dialog", { name: "Select Internal Report" });
    fireEvent.change(within(dialog).getByLabelText("Internal Report file"), { target: { files: [new File(["source"], "Other.docx")] } });
    await user.click(within(dialog).getByRole("button", { name: "Generate customer report" }));
    rerender(<ReportWorkspace projectId="project-2" onBack={vi.fn()} />);
    await act(async () => { resolve(missing); });
    expect(api.startStandaloneCustomerReport).not.toHaveBeenCalled();
    expect(screen.queryByRole("dialog")).toBeNull();
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
    render(<AppShell activeRoute="workbench" topBarTitle="Report Workspace">
      <ProjectReportWorkspacePage projectId="project-1" onBackToWorkbench={vi.fn()} />
    </AppShell>);
    expect(await screen.findByText("DL-001 Confirmed connector Qualification Testing")).toBeTruthy();
    expect(screen.queryByText(/Unconfirmed edit|Stale description/)).toBeNull();
    expect(screen.getAllByRole("heading", { name: "Report Workspace" })).toHaveLength(1);
  });

  it("keeps report operations available when optional identity lookups fail", async () => {
    vi.mocked(api.getProject).mockRejectedValue(new Error("Project label unavailable"));
    vi.mocked(api.listProjectLtrs).mockResolvedValue([
      { ltr_id: "ltr-1", project_id: "project-1", ltr_number: "DL-001", status: "registered" },
    ]);
    vi.mocked(api.getProjectBasicInformation).mockRejectedValue(new Error("Basic label unavailable"));
    render(<ProjectReportWorkspacePage projectId="project-1" onBackToWorkbench={vi.fn()} />);
    expect(await screen.findByText("DL-001 Connector Project")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open project folder" }).hasAttribute("disabled")).toBe(false);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("keeps LLCR inspection independent of initial report generation without inventing a missing folder", async () => {
    const user = userEvent.setup();
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
    expect(screen.getByRole("button", { name: "Update LLCR results" }).hasAttribute("disabled")).toBe(true);
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));
    expect(await screen.findByRole("dialog", { name: "LLCR import preview" })).toBeTruthy();
    expect(api.inspectLlcrResultWorkbook).toHaveBeenCalledOnce();
    expect(api.generateInitialReportRevision).not.toHaveBeenCalled();
  });

  it("exposes the current report, LLCR import preview, and confirmation", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(<ReportWorkspace projectId="project-1" onBack={onBack} />);

    expect(await screen.findByRole("heading", { name: "Report Workspace" })).toBeTruthy();
    expect(screen.queryByText("Project project-1")).toBeNull();
    expect(screen.getAllByText(currentReport.file_name!).length).toBe(1);
    expect(screen.queryByText("Confirmed Matrix r4")).toBeNull();
    expect(screen.queryByText("Basic Information v2")).toBeNull();
    expect(within(screen.getByRole("region", { name: "Internal Report" })).queryByText("Official project report")).toBeNull();
    expect(screen.getByRole("button", { name: "Generate Internal Report" })).toBeTruthy();

    const fileInput = screen.getByLabelText("LLCR result workbook");
    fireEvent.change(fileInput, {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));

    expect(await screen.findByRole("dialog", { name: "LLCR import preview" })).toBeTruthy();
    expect(screen.getByText("Group 1 / Step 2")).toBeTruthy();
    expect(screen.getByText("0.031 / 0.082 / 0.0565 mΩ")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Confirm LLCR dataset" }));
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
    expect(within(internal).getByRole("button", { name: "Generate Internal Report" }).hasAttribute("disabled")).toBe(true);
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

    const generateButton = await screen.findByRole("button", { name: "Generate Internal Report" });
    expect(generateButton).toHaveProperty("disabled", false);
    await user.click(generateButton);

    expect(api.generateInternalReport).toHaveBeenCalledWith("project-1", "c".repeat(64), false);
  });

  it("blocks an outcome override until a reason is supplied", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report Workspace" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));
    await user.selectOptions(await screen.findByLabelText("Final outcome for Group 1 / Step 2"), "fail");

    expect(screen.getByRole("button", { name: "Confirm LLCR dataset" })).toHaveProperty("disabled", true);
    await user.type(screen.getByLabelText("Override reason for Group 1 / Step 2"), "Visual damage");
    expect(screen.getByRole("button", { name: "Confirm LLCR dataset" })).toHaveProperty("disabled", false);
  });

  it("cancels the staged preview before closing the dialog", async () => {
    const user = userEvent.setup();
    vi.mocked(api.cancelLlcrResultPreview).mockResolvedValue(undefined);
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report Workspace" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));
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
    await user.click(await screen.findByRole("button", { name: "Update LLCR results" }));

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
    expect(screen.getByRole("button", { name: "Download current report" })).toBeTruthy();
    await user.click(
      screen.getByRole("button", { name: "Publish current draft to project folder" })
    );

    expect(api.publishManagedReport).toHaveBeenCalledWith(
      "project-1",
      "a".repeat(64)
    );
    expect(await screen.findByText(/Published the current report to/)).toBeTruthy();
  });

  it("previews EquipmentID matches and requires expired-calibration acknowledgement", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    await user.click(await screen.findByRole("button", { name: "Preview Equipment List" }));

    expect(await screen.findByRole("dialog", { name: "Equipment List preview" })).toBeTruthy();
    expect(screen.getByText("Digital multimeter")).toBeTruthy();
    const updateButton = screen.getByRole("button", { name: "Update Equipment List" });
    expect(updateButton).toHaveProperty("disabled", true);
    await user.click(screen.getByLabelText("I reviewed the expired calibration warning"));
    expect(updateButton).toHaveProperty("disabled", false);
    await user.click(updateButton);

    expect(api.updateCurrentReportEquipmentList).toHaveBeenCalledWith("project-1", {
      expected_report_sha256: "a".repeat(64),
      expected_source_sha256: "b".repeat(64),
      expected_catalog_sha256: "c".repeat(64),
      acknowledge_expired: true,
      external_overrides: [],
      updated_by: "Lab User",
    });
    expect(await screen.findByText(/Updated Equipment List in/)).toBeTruthy();
  });

  it("allows an unmatched device to continue as an ID-only Word-manual row", async () => {
    const user = userEvent.setup();
    const unmatchedPreview: api.EquipmentListPreview = {
      ...equipmentPreview,
      requires_expired_acknowledgement: false,
      warnings: [
        "Equipment reference 'DG-Q-0851' was not found. It will be added with ID only; complete it manually in Word.",
      ],
      rows: [{
        source_reference: "DG-Q-0851",
        status: "unmatched",
        item: "",
        manufacturer: "",
        id_number: "DG-Q-0851",
        last_calibration: "",
        calibration_due: "",
        source_sheet: null,
        expired: false,
        external_reason: null,
      }],
    };
    vi.mocked(api.previewCurrentReportEquipmentList).mockResolvedValue(unmatchedPreview);

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Preview Equipment List" }));

    expect(await screen.findByText(/Rows needing attention keep only confirmed values/)).toBeTruthy();
    await user.type(screen.getByLabelText("Item for DG-Q-0851"), "Thermal shock chamber");
    await user.click(screen.getByRole("button", { name: "Recheck external entries" }));

    await waitFor(() => {
      expect(api.previewCurrentReportEquipmentList).toHaveBeenLastCalledWith(
        "project-1",
        []
      );
    });
    const updateButton = screen.getByRole("button", { name: "Update Equipment List" });
    expect(updateButton).toHaveProperty("disabled", false);
    await user.click(updateButton);

    expect(api.updateCurrentReportEquipmentList).toHaveBeenCalledWith("project-1", {
      expected_report_sha256: "a".repeat(64),
      expected_source_sha256: "b".repeat(64),
      expected_catalog_sha256: "c".repeat(64),
      acknowledge_expired: false,
      external_overrides: [],
      updated_by: "Lab User",
    });
  });

  it("updates a stale customer report from the current internal report with both fingerprints", async () => {
    const user = userEvent.setup();
    vi.mocked(api.startProjectCustomerReportJob).mockResolvedValue({
      ...completedJob,
      result: {
        project_id: "project-1",
        mode: "official",
        file_name: customerReport.file_name!,
        file_sha256: "d".repeat(64),
        source_report_sha256: "a".repeat(64),
        changed: true,
        archive_path: "D:\\Test Project\\DL-001\\History\\Report\\old.docx",
      },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(await screen.findByRole("region", { name: "Customer Report" })).toBeTruthy();
    expect(screen.getByText(customerReport.warnings[0])).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Generate customer report" }));

    expect(api.startProjectCustomerReportJob).toHaveBeenCalledWith("project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: "b".repeat(64),
    });
    expect(await screen.findByText(/Updated the customer report/)).toBeTruthy();
  });

  it("refreshes and asks before regenerating a customer report deleted after preview", async () => {
    const user = userEvent.setup();
    const missingCustomerReport: api.CustomerReportState = {
      ...customerReport,
      status: "missing",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: [],
      download_url: null,
    };
    vi.mocked(api.fetchCurrentCustomerReport)
      .mockResolvedValueOnce(customerReport)
      .mockResolvedValue(missingCustomerReport);
    vi.mocked(api.startProjectCustomerReportJob).mockReset();
    vi.mocked(api.startProjectCustomerReportJob)
      .mockResolvedValueOnce({
        ...completedJob, status: "failed", result: null,
        message: "The customer report was deleted or moved after the page was loaded.",
        error_code: "customer_report_missing_after_preview", can_regenerate: true,
      })
      .mockResolvedValueOnce({
        ...completedJob, operation_id: "operation-2",
        result: {
          project_id: "project-1",
          mode: "official",
          file_name: customerReport.file_name!,
          file_sha256: "d".repeat(64),
          source_report_sha256: "a".repeat(64),
          changed: true,
          archive_path: null,
        },
      });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));

    expect(
      await screen.findByRole("alertdialog", { name: "Customer report not found" })
    ).toBeTruthy();
    expect(
      screen.getByText(/deleted or moved from the project folder/i)
    ).toBeTruthy();
    expect(screen.queryByText("Report workflow failed.")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Generate new customer report" }));

    expect(api.startProjectCustomerReportJob).toHaveBeenNthCalledWith(2, "project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: null,
    });
    expect(
      await screen.findByText(/Generated a new customer report.*No previous file was archived/)
    ).toBeTruthy();
  });

  it("cancels customer report regeneration without creating a replacement", async () => {
    const user = userEvent.setup();
    const missingCustomerReport: api.CustomerReportState = {
      ...customerReport,
      status: "missing",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: [],
      download_url: null,
    };
    vi.mocked(api.fetchCurrentCustomerReport)
      .mockResolvedValueOnce(customerReport)
      .mockResolvedValue(missingCustomerReport);
    vi.mocked(api.startProjectCustomerReportJob).mockReset();
    vi.mocked(api.startProjectCustomerReportJob).mockRejectedValueOnce(
      new api.ApiRequestError(
        "The customer report was deleted or moved after the page was loaded.",
        409,
        {
          code: "customer_report_missing_after_preview",
          message: "The customer report was deleted or moved after the page was loaded.",
          can_regenerate: true,
        }
      )
    );

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));
    await user.click(
      await screen.findByRole("button", { name: "Cancel" })
    );

    expect(screen.queryByRole("alertdialog", { name: "Customer report not found" })).toBeNull();
    expect(api.startProjectCustomerReportJob).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button", { name: "Generate customer report" })).toBeTruthy();
  });

  it("does not claim that an unchanged customer report was archived", async () => {
    const user = userEvent.setup();
    vi.mocked(api.startProjectCustomerReportJob).mockResolvedValue({
      ...completedJob,
      result: {
        project_id: "project-1",
        mode: "official",
        file_name: customerReport.file_name!,
        file_sha256: customerReport.file_sha256!,
        source_report_sha256: customerReport.internal_report_sha256!,
        changed: false,
        archive_path: null,
      },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));

    expect(await screen.findByText(/was already current/)).toBeTruthy();
    expect(screen.queryByText(/archived automatically/)).toBeNull();
  });

  it("downloads the generated customer report when no official project folder exists", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({
      ...customerReport,
      status: "missing",
      mode: "managed_download",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: ["No official project folder is available; generation will download a copy."],
      download_url: null,
    });
    vi.mocked(api.startProjectCustomerReportJob).mockResolvedValue({
      ...completedJob,
      result: { mode: "managed_download", file_name: "Customer.docx", changed: true, archive_path: null },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate customer report" }));

    expect(api.startProjectCustomerReportJob).toHaveBeenCalledWith("project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: null,
    });
    expect(await screen.findByText("Customer.docx")).toBeTruthy();
    expect(screen.queryByText("Generated and downloaded the customer report.")).toBeNull();
    expect(screen.queryByText("Customer report generation completed.")).toBeNull();
  });

  it("recovers real progress above the disabled generation button", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completedJob, status: "running", stage: "formatting_document", elapsed_seconds: 19, result: null,
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Applying customer-report layout and headers...")).toBeTruthy();
    expect(screen.getByText("19 seconds elapsed")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Generating customer report..." }) as HTMLButtonElement).disabled).toBe(true);
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("keeps publication failure visible without claiming generation is still running", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completedJob, status: "failed", stage: "publishing", result: null,
      error_code: "customer_report_publication_failed", message: "The target file changed.",
    });
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Publication failed: The target file changed.")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Generate customer report" }) as HTMLButtonElement).disabled).toBe(false);
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
