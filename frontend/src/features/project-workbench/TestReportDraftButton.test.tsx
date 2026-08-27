import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TestReportDraftButton } from "./TestReportDraftButton";

const apiMocks = vi.hoisted(() => ({
  generateTestReportDraftDownload: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  generateTestReportDraftDownload: apiMocks.generateTestReportDraftDownload,
}));

describe("TestReportDraftButton", () => {
  beforeEach(() => {
    apiMocks.generateTestReportDraftDownload.mockReset();
    globalThis.URL.createObjectURL = vi.fn(() => "blob:report");
    globalThis.URL.revokeObjectURL = vi.fn();
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
  });

  it("downloads the server-provided report filename", async () => {
    let clickedDownloadName = "";
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement
    ) {
      clickedDownloadName = this.download;
    });
    apiMocks.generateTestReportDraftDownload.mockResolvedValue({
      blob: new Blob(["docx"]),
      fileName: "DL-001 Qualification Testing Report_Rev_A_Draft.docx",
    });
    render(<TestReportDraftButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Test Report" }));

    await waitFor(() => {
      expect(apiMocks.generateTestReportDraftDownload).toHaveBeenCalledWith("P1");
    });
    const anchor = document.querySelector("a[download]") as HTMLAnchorElement | null;
    expect(anchor).toBeNull();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
    expect(clickedDownloadName).toBe(
      "DL-001 Qualification Testing Report_Rev_A_Draft.docx"
    );
  });

  it("is disabled until Basic Information and Active Confirmed Matrix are ready", () => {
    render(<TestReportDraftButton projectId="P1" ready={false} />);

    const button = screen.getByRole("button", { name: "Test Report" });
    expect(button.hasAttribute("disabled")).toBe(true);
    expect(button.getAttribute("title")).toContain("Confirm Basic Information");
  });

  it("shows the backend error without losing the action", async () => {
    apiMocks.generateTestReportDraftDownload.mockRejectedValue(
      new Error("E-3707_H test report template not found in Template folder.")
    );
    render(<TestReportDraftButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Test Report" }));

    expect(
      await screen.findByText(
        "E-3707_H test report template not found in Template folder."
      )
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Test Report" })).toBeTruthy();
  });
});
