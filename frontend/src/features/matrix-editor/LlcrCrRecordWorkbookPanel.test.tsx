import { render, screen } from "@testing-library/react";
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
  beforeEach(() => vi.resetAllMocks());

  it("previews and generates LLCR and CR as independent records", async () => {
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

    render(<LlcrCrRecordWorkbookPanel projectId="P1" />);
    expect(screen.getByRole("heading", { name: "LLCR/CR表" })).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Preview LLCR table" }));
    await user.click(screen.getByRole("button", { name: "Preview CR table" }));
    expect(apiMocks.previewLlcrCrRecordWorkbook).toHaveBeenNthCalledWith(1, "P1", "llcr");
    expect(apiMocks.previewLlcrCrRecordWorkbook).toHaveBeenNthCalledWith(2, "P1", "cr");
    expect(screen.getByText("12 entry rows · ΔR on")).toBeTruthy();
    expect(screen.getByText("4 entry rows")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Generate LLCR file" }));
    expect(apiMocks.generateLlcrCrRecordWorkbook).toHaveBeenCalledWith("P1", {
      record_type: "llcr", preview_fingerprint: "llcr-fingerprint",
    });
    expect(screen.getByRole("button", { name: "Download LLCR file" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Download CR file" })).toBeNull();
  });
});
