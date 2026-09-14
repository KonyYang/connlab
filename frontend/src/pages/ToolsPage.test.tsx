import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  downloadStandaloneCustomerReport,
  encryptStandaloneCopy,
  readStandaloneCustomerReportJob,
  startStandaloneCustomerReport,
} from "../api/client";
import { ToolsPage } from "./ToolsPage";

vi.mock("../api/client", () => ({
  downloadStandaloneCustomerReport: vi.fn(),
  encryptStandaloneCopy: vi.fn(),
  readStandaloneCustomerReportJob: vi.fn(),
  startStandaloneCustomerReport: vi.fn(),
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

  it("converts a selected Internal Report and downloads the returned customer report", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);
    const file = new File(["internal"], "sample.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });

    await user.upload(screen.getByLabelText("Select Internal Report"), file);
    await user.click(screen.getByRole("button", { name: "Generate customer report" }));

    expect(await screen.findByText("Customer report generated and downloaded.")).toBeTruthy();
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
    await user.click(screen.getByRole("button", { name: "Generate customer report" }));
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

  it("explains that encryption leaves the original untouched", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);
    const file = new File(["internal"], "sample.docx");

    expect(
      screen.getByText(/same ConnLab Office password is required to open and edit the copy/i),
    ).toBeTruthy();

    await user.upload(screen.getByLabelText("Select Office file"), file);
    await user.click(screen.getByRole("button", { name: "Create encrypted copy" }));

    expect(encryptCopyMock).toHaveBeenCalledWith(file);
    expect(await screen.findByText(/original file was not changed/)).toBeTruthy();
  });

  it("requires a file before running a tool", async () => {
    const user = userEvent.setup();
    render(<ToolsPage />);

    await user.click(screen.getByRole("button", { name: "Generate customer report" }));

    expect((await screen.findByRole("alert")).textContent).toContain("Select a file first.");
  });
});
