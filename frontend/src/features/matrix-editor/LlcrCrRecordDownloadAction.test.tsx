import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { LlcrCrRecordDownloadAction } from "./LlcrCrRecordDownloadAction";

vi.mock("../../api/client", async (original) => ({
  ...(await original<typeof import("../../api/client")>()),
  generateMatrixEditorLlcrCrRecordDraftDownload: vi.fn(),
  previewMatrixEditorLlcrCrRecordPublication: vi.fn(),
  publishMatrixEditorLlcrCrRecord: vi.fn(),
}));
const apiMocks = vi.mocked(api);

describe("LlcrCrRecordDownloadAction", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true, value: vi.fn(() => "blob:record"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true, value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  });

  it("downloads a draft only after reviewing its browser destination", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "download", status: "ready", authority_status: "unconfirmed",
      target_path: null, existing_file: false, blockers: [], preview_token: "draft-token",
    });
    apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload.mockResolvedValue({
      blob: new Blob(["record"]), fileName: "P1_llcr_record.xlsx",
    });
    let draftRequest = {
      source: "matrix_editor_current_ui_state" as const,
      groups: [{
        group_key: "group_6",
        group_label: "6",
        sample_quantity_expression: "5",
        sample_note: null,
      }],
      rows: [{
        test_item: "Contact Resistance (Low Level)",
        section: "6.1",
        method: "EIA-364-23D",
        condition: "20 mV, 100 mA",
        requirement: "Initial <= 0.25 mOhm",
        is_sample_row: false,
        group_values: { group_6: "2,6" },
      }],
    };

    render(<>
      <LlcrCrRecordDownloadAction
        projectId="P1"
        recordType="llcr"
        getDraftRequest={() => draftRequest}
      />
      <LlcrCrRecordDownloadAction
        projectId="P1"
        recordType="cr"
        getDraftRequest={() => draftRequest}
      />
    </>);
    // Resolve the live draft at the click, not at mount or during unrelated renders.
    draftRequest = { ...draftRequest, groups: [{ ...draftRequest.groups[0], sample_quantity_expression: "7" }] };

    await user.click(screen.getByRole("button", { name: "LLCR Form" }));
    await waitFor(() => expect(
      apiMocks.previewMatrixEditorLlcrCrRecordPublication
    ).toHaveBeenCalledWith("P1", { ...draftRequest, record_type: "llcr" }));
    expect(apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: "Download LLCR preview?" })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Download preview" }));
    await waitFor(() => expect(
      apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload
    ).toHaveBeenCalledWith("P1", { ...draftRequest, record_type: "llcr", preview_token: "draft-token" }));
    expect(screen.getByRole("button", { name: "CR Form" })).toBeTruthy();
    expect(screen.getByText("P1_llcr_record.xlsx downloaded.")).toBeTruthy();
  });

  it("archives a measured official form before publishing a replacement", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "official", status: "conflict", authority_status: "confirmed",
      target_path: "C:\\project\\Test results\\P1 LLCR Record.xlsx",
      existing_file: true, blockers: [], preview_token: "official-token",
    });
    apiMocks.publishMatrixEditorLlcrCrRecord.mockResolvedValue({
      project_id: "P1", file_name: "P1 LLCR Record.xlsx",
      target_path: "C:\\project\\Test results\\P1 LLCR Record.xlsx",
      archive_path: "C:\\project\\History\\Test results\\P1 LLCR Record old.xlsx",
    });
    const draftRequest = { source: "matrix_editor_current_ui_state" as const, groups: [], rows: [] };
    render(<LlcrCrRecordDownloadAction projectId="P1" recordType="llcr" getDraftRequest={() => draftRequest} />);

    await user.click(screen.getByRole("button", { name: "LLCR Form" }));
    expect(await screen.findByRole("dialog", { name: "Update existing LLCR Form?" })).toBeTruthy();
    expect(apiMocks.publishMatrixEditorLlcrCrRecord).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: /Recycle/i })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Archive old file and save new" }));
    await waitFor(() => expect(apiMocks.publishMatrixEditorLlcrCrRecord).toHaveBeenCalledWith("P1", {
      ...draftRequest, record_type: "llcr", preview_token: "official-token", conflict_action: "archive",
    }));
    expect(screen.getByText(/archived the previous file in History/i)).toBeTruthy();
    expect(apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload).not.toHaveBeenCalled();
  });

  it("leaves a measured official form untouched when the operator cancels", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "official", status: "conflict", authority_status: "confirmed",
      target_path: "C:\\project\\Test results\\P1 LLCR Record.xlsx",
      existing_file: true, blockers: [], preview_token: "conflict-token",
    });
    render(<LlcrCrRecordDownloadAction projectId="P1" recordType="llcr"
      getDraftRequest={() => ({ source: "matrix_editor_current_ui_state", groups: [], rows: [] })} />);

    await user.click(screen.getByRole("button", { name: "LLCR Form" }));
    expect(await screen.findByRole("dialog", { name: "Update existing LLCR Form?" })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(apiMocks.publishMatrixEditorLlcrCrRecord).not.toHaveBeenCalled();
  });

  it("publishes a new official form without a conflict prompt", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "official", status: "ready", authority_status: "confirmed",
      target_path: "C:\\project\\Test results\\P1 CR Record.xlsx",
      existing_file: false, blockers: [], preview_token: "new-token",
    });
    apiMocks.publishMatrixEditorLlcrCrRecord.mockResolvedValue({
      project_id: "P1", file_name: "P1 CR Record.xlsx",
      target_path: "C:\\project\\Test results\\P1 CR Record.xlsx", archive_path: null,
    });
    const draftRequest = { source: "matrix_editor_current_ui_state" as const, groups: [], rows: [] };
    render(<LlcrCrRecordDownloadAction projectId="P1" recordType="cr" getDraftRequest={() => draftRequest} />);

    await user.click(screen.getByRole("button", { name: "CR Form" }));
    await waitFor(() => expect(apiMocks.publishMatrixEditorLlcrCrRecord).toHaveBeenCalledWith("P1", {
      ...draftRequest, record_type: "cr", preview_token: "new-token", conflict_action: "none",
    }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.getByText(/saved P1 CR Record.xlsx to Test results/i)).toBeTruthy();
  });

  it("does not generate or publish when the authority preview is blocked", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "official", status: "blocked", authority_status: "confirmed",
      target_path: null, existing_file: false,
      blockers: ["The Test results folder changed; review the project folder."],
      preview_token: "blocked-token",
    });
    render(<LlcrCrRecordDownloadAction projectId="P1" recordType="cr"
      getDraftRequest={() => ({ source: "matrix_editor_current_ui_state", groups: [], rows: [] })} />);

    await user.click(screen.getByRole("button", { name: "CR Form" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Test results folder changed");
    expect(apiMocks.publishMatrixEditorLlcrCrRecord).not.toHaveBeenCalled();
    expect(apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload).not.toHaveBeenCalled();
  });

  it("sends unsaved Matrix changes to the destination check", async () => {
    const user = userEvent.setup();
    apiMocks.previewMatrixEditorLlcrCrRecordPublication.mockResolvedValue({
      project_id: "P1", mode: "download", status: "ready", authority_status: "unconfirmed",
      target_path: null, existing_file: false, blockers: [], preview_token: "dirty-token",
    });
    const draftRequest = { source: "matrix_editor_current_ui_state" as const, groups: [], rows: [] };
    render(<LlcrCrRecordDownloadAction projectId="P1" recordType="cr"
      getDraftRequest={() => draftRequest} matrixHasPendingChanges />);

    await user.click(screen.getByRole("button", { name: "CR Form" }));
    await waitFor(() => expect(apiMocks.previewMatrixEditorLlcrCrRecordPublication).toHaveBeenCalledWith("P1", {
      ...draftRequest, record_type: "cr", matrix_has_pending_changes: true,
    }));
  });
});
