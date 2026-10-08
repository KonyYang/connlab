import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  downloadStandaloneCustomerReport,
  encryptStandaloneCopy,
  readStandaloneCustomerReportJob,
  startStandaloneCustomerReport,
  updateStandaloneEquipmentList,
} from "../api/client";
import { ToolsPage } from "./ToolsPage";

vi.mock("../api/client", () => ({
  downloadStandaloneCustomerReport: vi.fn(),
  encryptStandaloneCopy: vi.fn(),
  readStandaloneCustomerReportJob: vi.fn(),
  startStandaloneCustomerReport: vi.fn(),
  updateStandaloneEquipmentList: vi.fn(),
}));

const startCustomerReportMock = vi.mocked(startStandaloneCustomerReport);
const readCustomerReportMock = vi.mocked(readStandaloneCustomerReportJob);
const downloadCustomerReportMock = vi.mocked(downloadStandaloneCustomerReport);
const encryptCopyMock = vi.mocked(encryptStandaloneCopy);

describe("ToolsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:tools"),
      revokeObjectURL: vi.fn(),
    });
    startCustomerReportMock.mockResolvedValue({
      operation_id: "operation-1",
      status: "queued",
      stage: "queued",
      elapsed_seconds: 0,
      message: null,
    });
    readCustomerReportMock
      .mockResolvedValueOnce({
        operation_id: "operation-1",
        status: "running",
        stage: "cleaning_content",
        elapsed_seconds: 4.2,
        message: null,
      })
      .mockResolvedValueOnce({
        operation_id: "operation-1",
        status: "completed",
        stage: "completed",
        elapsed_seconds: 7.4,
        message: null,
      });
    downloadCustomerReportMock.mockResolvedValue({
      blob: new Blob(["report"]),
      fileName: "sample-CR.docx",
    });
    encryptCopyMock.mockResolvedValue({ blob: new Blob(["secured"]), fileName: "sample_Secured.docx" });
  });

  it("generates and downloads a customer report immediately after choosing its source", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);
    const file = new File(["internal"], "sample.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });

    await user.upload(screen.getByLabelText("Select Internal Report"), file);

    expect((await screen.findByRole("status", { name: "Downloaded File" })).textContent).toBe("sample-CR.docx");
    expect(screen.queryByText(/seconds elapsed/)).toBeNull();
    expect(startCustomerReportMock).toHaveBeenCalledWith(file);
    expect(readCustomerReportMock).toHaveBeenCalledWith("operation-1");
    expect(downloadCustomerReportMock).toHaveBeenCalledWith("operation-1");
  });

  it("shows the backend generation stage and elapsed time while the report is running", async () => {
    let releaseStatus: ((value: {
      operation_id: string;
      status: "running";
      stage: "cleaning_content";
      elapsed_seconds: number;
      message: null;
    }) => void) | undefined;
    readCustomerReportMock.mockReset();
    readCustomerReportMock.mockReturnValue(new Promise((resolve) => {
      releaseStatus = resolve;
    }));
    const user = userEvent.setup();
    render(<ToolsPage />);
    const file = new File(["internal"], "large-report.docx");

    await user.upload(screen.getByLabelText("Select Internal Report"), file);
    expect(await screen.findByText(/Waiting for the previous customer-report task/)).toBeTruthy();

    releaseStatus?.({
      operation_id: "operation-1",
      status: "running",
      stage: "cleaning_content",
      elapsed_seconds: 18.6,
      message: null,
    });

    expect(await screen.findByText(/Cleaning internal-only content/)).toBeTruthy();
    expect(screen.getByText(/19 seconds elapsed/)).toBeTruthy();
  });

  it("identifies the downloaded encrypted copy and keeps password guidance concise", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);
    const file = new File(["internal"], "sample.docx");

    expect(
      screen.getByText(/Uses the ConnLab Office password/i),
    ).toBeTruthy();

    await user.upload(screen.getByLabelText("Select Office file"), file);
    await user.click(screen.getByRole("button", { name: "Create Encrypted Copy" }));

    expect(encryptCopyMock).toHaveBeenCalledWith(file);
    expect((await screen.findByRole("status", { name: "Downloaded File" })).textContent).toBe("sample_Secured.docx");
  });

  it("opens the hidden source picker from its only button and does nothing when cancelled", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);
    const picker = screen.getByLabelText("Select Internal Report") as HTMLInputElement;
    const choose = vi.spyOn(picker, "click");

    await user.click(screen.getByRole("button", { name: "Select Internal Report → Generate Customer Report" }));
    expect(choose).toHaveBeenCalledTimes(1);
    expect(picker.hidden).toBe(true);
    expect(screen.queryByText("Select Internal Report")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Internal Report → Customer Report" })).toBeNull();
    fireEvent.change(picker, { target: { files: [] } });
    expect(startCustomerReportMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByRole("button", { name: "Select Internal Report → Generate Customer Report" })).toBeTruthy();
  });

  it("allows choosing the same report again after failure and preserves feedback when cancelled", async () => {
    startCustomerReportMock.mockRejectedValueOnce(new Error("Choose a compatible Internal Report."));
    const user = userEvent.setup();
    render(<ToolsPage />);
    const picker = screen.getByLabelText("Select Internal Report") as HTMLInputElement;
    const file = new File(["internal"], "sample.docx");
    await user.upload(picker, file);
    expect((await screen.findByRole("alert")).textContent).toContain("compatible Internal Report");
    expect(picker.value).toBe("");
    fireEvent.change(picker, { target: { files: [] } });
    expect(screen.getByRole("alert").textContent).toContain("compatible Internal Report");
    expect(startCustomerReportMock).toHaveBeenCalledTimes(1);
    await user.upload(picker, file);
    expect((await screen.findByRole("status", { name: "Downloaded File" })).textContent).toBe("sample-CR.docx");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(startCustomerReportMock).toHaveBeenCalledTimes(2);
    expect(startCustomerReportMock).toHaveBeenLastCalledWith(file);
  });

  it("blocks repeated selections while starting and discards report completion after leaving Tools", async () => {
    let complete!: (value: Awaited<ReturnType<typeof startStandaloneCustomerReport>>) => void;
    startCustomerReportMock.mockReturnValueOnce(new Promise(done => { complete = done; }));
    const user = userEvent.setup();
    const rendered = render(<ToolsPage />);
    const picker = screen.getByLabelText("Select Internal Report") as HTMLInputElement;
    const file = new File(["internal"], "sample.docx");
    await user.upload(picker, file);
    expect(picker.disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Starting..." }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(picker, { target: { files: [file] } });
    expect(startCustomerReportMock).toHaveBeenCalledTimes(1);
    rendered.unmount();
    await act(async () => complete({ operation_id: "operation-1", status: "completed", stage: "completed", elapsed_seconds: 1, message: null }));
    expect(downloadCustomerReportMock).not.toHaveBeenCalled();
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  });

  it("discards a late customer report download after leaving Tools", async () => {
    startCustomerReportMock.mockResolvedValueOnce({ operation_id: "operation-1", status: "completed", stage: "completed", elapsed_seconds: 1, message: null });
    let complete!: (value: Awaited<ReturnType<typeof downloadStandaloneCustomerReport>>) => void;
    downloadCustomerReportMock.mockReturnValueOnce(new Promise(done => { complete = done; }));
    const user = userEvent.setup();
    const rendered = render(<ToolsPage />);
    await user.upload(screen.getByLabelText("Select Internal Report"), new File(["internal"], "sample.docx"));
    expect(downloadCustomerReportMock).toHaveBeenCalledWith("operation-1");
    rendered.unmount();
    await act(async () => complete({ blob: new Blob(["report"]), fileName: "late-CR.docx" }));
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  });

  it("updates equipment in a downloaded report copy and shows only actual review items", async () => {
    vi.mocked(updateStandaloneEquipmentList).mockResolvedValue({
      blob: new Blob(["updated"]), fileName: "Internal_EquipmentUpdated.docx",
      review: { filled: 2, unmatched: ["DG-Q-9999"], incomplete: [], expired: [],
                omitted: { unmatched: 0, incomplete: 0, expired: 0 } },
    });
    render(<ToolsPage />);
    const report = new File(["original"], "Internal.docx");
    fireEvent.change(screen.getByLabelText("Internal Report for Equipment Update"), {
      target: { files: [report] },
    });
    fireEvent.click(screen.getByLabelText("Enter Equipment IDs"));
    fireEvent.change(screen.getByLabelText("Equipment IDs"), { target: { value: "Q-0033, Q-9999" } });
    fireEvent.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect((await screen.findByRole("status", { name: "Downloaded File" })).textContent).toBe("Internal_EquipmentUpdated.docx");
    expect(screen.getByText(/Not Registered: DG-Q-9999/)).toBeTruthy();
    expect(screen.queryByText(/Missing Information:/)).toBeNull();
    expect(updateStandaloneEquipmentList).toHaveBeenCalledWith(report, { referencesText: "Q-0033, Q-9999" });
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it("uploads equipment selection and hides healthy review information", async () => {
    vi.mocked(updateStandaloneEquipmentList).mockResolvedValue({
      blob: new Blob(["copy"]), fileName: "copy.docx",
      review: { filled: 1, unmatched: [], incomplete: [], expired: [],
                omitted: { unmatched: 0, incomplete: 0, expired: 0 } },
    });
    render(<ToolsPage />);
    const report = new File(["report"], "report.docx");
    const selection = new File(["equipment"], "EquipmentID.docx");
    fireEvent.change(screen.getByLabelText("Internal Report for Equipment Update"), { target: { files: [report] } });
    fireEvent.change(screen.getByLabelText("Select EquipmentID.docx"), { target: { files: [selection] } });
    fireEvent.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect(await screen.findByText("copy.docx")).toBeTruthy();
    expect(updateStandaloneEquipmentList).toHaveBeenCalledWith(report, { equipmentFile: selection });
    expect(screen.queryByRole("alert")).toBeNull();
    fireEvent.click(screen.getByLabelText("Enter Equipment IDs"));
    expect(screen.queryByText("copy.docx")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect(screen.getByRole("alert").textContent).toContain("enter equipment IDs");
    expect(updateStandaloneEquipmentList).toHaveBeenCalledTimes(1);
  });

  it("shows failed update guidance without starting a download", async () => {
    vi.mocked(updateStandaloneEquipmentList).mockRejectedValue(new Error("Check the workbook in Settings."));
    render(<ToolsPage />);
    fireEvent.change(screen.getByLabelText("Internal Report for Equipment Update"), {
      target: { files: [new File(["report"], "report.docx")] },
    });
    fireEvent.click(screen.getByLabelText("Enter Equipment IDs"));
    fireEvent.change(screen.getByLabelText("Equipment IDs"), { target: { value: "Q-0033" } });
    fireEvent.click(screen.getByRole("button", { name: "Update Equipment List" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Settings");
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("prevents repeated requests and discards a completed download after leaving Tools", async () => {
    let resolve!: (value: Awaited<ReturnType<typeof updateStandaloneEquipmentList>>) => void;
    vi.mocked(updateStandaloneEquipmentList).mockReturnValue(new Promise((done) => { resolve = done; }));
    const rendered = render(<ToolsPage />);
    const reportInput = screen.getByLabelText("Internal Report for Equipment Update");
    fireEvent.change(reportInput, { target: { files: [new File(["report"], "report.docx")] } });
    fireEvent.click(screen.getByLabelText("Enter Equipment IDs"));
    fireEvent.change(screen.getByLabelText("Equipment IDs"), { target: { value: "Q-0033" } });
    fireEvent.click(screen.getByRole("button", { name: "Update Equipment List" }));
    const pending = screen.getByRole("button", { name: "Updating..." }) as HTMLButtonElement;
    expect(pending.disabled).toBe(true);
    expect((reportInput as HTMLInputElement).disabled).toBe(true);
    fireEvent.click(pending);
    expect(updateStandaloneEquipmentList).toHaveBeenCalledTimes(1);
    rendered.unmount();
    await act(async () => resolve({ blob: new Blob(["copy"]), fileName: "copy.docx",
      review: { filled: 1, unmatched: [], incomplete: [], expired: [],
                omitted: { unmatched: 0, incomplete: 0, expired: 0 } } }));
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  });
});
