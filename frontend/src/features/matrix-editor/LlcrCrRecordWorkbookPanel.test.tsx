import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { LlcrCrRecordWorkbookPanel } from "./LlcrCrRecordWorkbookPanel";

vi.mock("../../api/client", async (original) => ({
  ...(await original<typeof import("../../api/client")>()),
  previewLlcrCrRecordWorkbook: vi.fn(),
  generateLlcrCrRecordWorkbook: vi.fn(),
  downloadLlcrCrRecordWorkbook: vi.fn(),
}));
const apiMocks = vi.mocked(api);

describe("LlcrCrRecordWorkbookPanel", () => {
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

  it("downloads each record with one click without exposing preview or generate steps", async () => {
    const user = userEvent.setup();
    apiMocks.previewLlcrCrRecordWorkbook.mockImplementation(async (_projectId, recordType) => ({
      project_id: "P1", status: "ready", record_type: recordType,
      confirmed_matrix_id: "M1", confirmed_revision: 2,
      preview_fingerprint: `${recordType}-fingerprint`, row_count: recordType === "llcr" ? 12 : 4,
      point_profile_revision_id: "PP1", point_profile_revision_sequence: 3,
      delta_r_enabled: recordType === "llcr", diagnostics: [],
      sections: [{
        record_type: recordType, confirmed_group_id: "G1", confirmed_row_id: "R1",
        step_sequence: 1, step_suffix_note: "", group_label: "Group 1", source_step: "1",
        sample_count: 2, readings_per_sample: 2, rows: [], stages: [],
        category_id: "ppc-1", category_label: "Signal", record_prefix: "SIG", point_expression: "1-2",
      }],
    }));
    apiMocks.generateLlcrCrRecordWorkbook.mockResolvedValue({
      project_id: "P1", confirmed_matrix_id: "M1", confirmed_revision: 2,
      record_type: "llcr", artifact_id: "A1", file_name: "P1_llcr_record.xlsx", download_url: "/A1",
    });
    apiMocks.downloadLlcrCrRecordWorkbook.mockResolvedValue({
      blob: new Blob(["record"]), fileName: "P1_llcr_record.xlsx",
    });

    render(<LlcrCrRecordWorkbookPanel projectId="P1" />);
    expect(screen.getByRole("heading", { name: "LLCR/CR表" })).toBeTruthy();
    expect(screen.queryAllByText("Preview")).toHaveLength(0);
    expect(screen.queryAllByText("Generate file")).toHaveLength(0);

    await user.click(screen.getByRole("button", { name: "Download LLCR" }));
    await waitFor(() => expect(apiMocks.downloadLlcrCrRecordWorkbook).toHaveBeenCalledWith("P1", "A1"));
    expect(apiMocks.previewLlcrCrRecordWorkbook).toHaveBeenCalledWith("P1", "llcr");
    expect(apiMocks.generateLlcrCrRecordWorkbook).toHaveBeenCalledWith("P1", {
      record_type: "llcr", preview_fingerprint: "llcr-fingerprint",
    });
    expect(screen.getByRole("button", { name: "Download CR" })).toBeTruthy();
    expect(screen.getByText("P1_llcr_record.xlsx downloaded.")).toBeTruthy();
  });
});
