import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { LlcrCrRecordDownloadAction } from "./LlcrCrRecordDownloadAction";

vi.mock("../../api/client", async (original) => ({
  ...(await original<typeof import("../../api/client")>()),
  previewMatrixEditorIrDwvRecordPublication: vi.fn(),
  generateMatrixEditorIrDwvRecordDraftDownload: vi.fn(),
  publishMatrixEditorIrDwvRecord: vi.fn(),
}));
const mocks = vi.mocked(api);
const request = { source: "matrix_editor_current_ui_state" as const, groups: [], rows: [],
  point_profile: { categories: [], delta_r_enabled: true, electrical_point_pairs: "Odd&Even" } };

beforeEach(() => vi.resetAllMocks());

it("offers an IR&DWV preview only after checking the destination and shows missing equipment information", async () => {
  mocks.previewMatrixEditorIrDwvRecordPublication.mockResolvedValue({
    project_id: "P1", mode: "download", status: "ready", authority_status: "unconfirmed", target_path: null,
    existing_file: false, blockers: [], information: ["No equipment selected; calibration fields are blank."], preview_token: "reviewed",
  });
  const user = userEvent.setup();
  render(<LlcrCrRecordDownloadAction projectId="P1" recordType="ir_dwv" getDraftRequest={() => request} matrixHasPendingChanges />);
  await user.click(screen.getByRole("button", { name: "IR&DWV Form" }));
  expect(await screen.findByRole("dialog", { name: "Download IR&DWV preview?" })).toBeTruthy();
  expect(screen.getByText("No equipment selected; calibration fields are blank.")).toBeTruthy();
  expect(mocks.previewMatrixEditorIrDwvRecordPublication).toHaveBeenCalledWith("P1", { ...request, record_type: "ir_dwv", matrix_has_pending_changes: true });
  expect(mocks.generateMatrixEditorIrDwvRecordDraftDownload).not.toHaveBeenCalled();
});

it("requires archive approval for measured IR/DWV results and reports publish failure without claiming success", async () => {
  mocks.previewMatrixEditorIrDwvRecordPublication.mockResolvedValue({
    project_id: "P1", mode: "official", status: "conflict", authority_status: "confirmed", target_path: "Test results/IR&DWV.xlsx",
    existing_file: true, blockers: [], preview_token: "reviewed",
  });
  mocks.publishMatrixEditorIrDwvRecord.mockRejectedValue(new Error("Template changed; preview again"));
  const user = userEvent.setup();
  render(<LlcrCrRecordDownloadAction projectId="P1" recordType="ir_dwv" getDraftRequest={() => request} />);
  await user.click(screen.getByRole("button", { name: "IR&DWV Form" }));
  await screen.findByRole("dialog", { name: "Update existing IR&DWV Form?" });
  expect(mocks.publishMatrixEditorIrDwvRecord).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Archive old file and save new" }));
  expect((await screen.findByRole("alert")).textContent).toContain("Template changed; preview again");
  expect(mocks.publishMatrixEditorIrDwvRecord).toHaveBeenCalledWith("P1", { ...request, record_type: "ir_dwv", preview_token: "reviewed", conflict_action: "archive" });
});

it("shows missing authority information after creating a new official form", async () => {
  mocks.previewMatrixEditorIrDwvRecordPublication.mockResolvedValue({
    project_id: "P1", mode: "official", status: "ready", authority_status: "confirmed", target_path: "Test results/IR&DWV.xlsx",
    existing_file: false, blockers: [], information: ["No equipment selected; calibration fields are blank."], preview_token: "new",
  });
  mocks.publishMatrixEditorIrDwvRecord.mockResolvedValue({ project_id: "P1", file_name: "IR&DWV.xlsx", target_path: "Test results/IR&DWV.xlsx", archive_path: null });
  const user = userEvent.setup();
  render(<LlcrCrRecordDownloadAction projectId="P1" recordType="ir_dwv" getDraftRequest={() => request} />);
  await user.click(screen.getByRole("button", { name: "IR&DWV Form" }));
  expect(await screen.findByRole("status")).toBeTruthy();
  expect(screen.getByText("No equipment selected; calibration fields are blank.")).toBeTruthy();
});
