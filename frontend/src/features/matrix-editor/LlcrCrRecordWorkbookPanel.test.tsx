import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { LlcrCrRecordWorkbookPanel } from "./LlcrCrRecordWorkbookPanel";

vi.mock("../../api/client", async (original) => ({
  ...(await original<typeof import("../../api/client")>()),
  generateMatrixEditorLlcrCrRecordDraftDownload: vi.fn(),
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
    apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload.mockResolvedValue({
      blob: new Blob(["record"]), fileName: "P1_llcr_record.xlsx",
    });
    const draftRequest = {
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

    render(<LlcrCrRecordWorkbookPanel projectId="P1" draftRequest={draftRequest} />);
    expect(screen.getByRole("heading", { name: "LLCR/CR表" })).toBeTruthy();
    expect(screen.queryAllByText("Preview")).toHaveLength(0);
    expect(screen.queryAllByText("Generate file")).toHaveLength(0);

    await user.click(screen.getByRole("button", { name: "Download LLCR" }));
    await waitFor(() => expect(
      apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload
    ).toHaveBeenCalledWith("P1", { ...draftRequest, record_type: "llcr" }));
    expect(screen.getByRole("button", { name: "Download CR" })).toBeTruthy();
    expect(screen.getByText("P1_llcr_record.xlsx downloaded.")).toBeTruthy();
  });
});
