import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { DraftMeasurementPlanWorkbookPanel } from "./DraftMeasurementPlanWorkbookPanel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchLatestDraftMeasurementPlanWorkbook: vi.fn().mockResolvedValue(null),
  previewDraftMeasurementPlanWorkbook: vi.fn(),
  generateDraftMeasurementPlanWorkbook: vi.fn(),
}));

describe("DraftMeasurementPlanWorkbookPanel", () => {
  it("shows NEEDS REVIEW preview and enables explicit generation", async () => {
    vi.mocked(api.previewDraftMeasurementPlanWorkbook).mockResolvedValue({
      project_id: "P1", revision_id: "draft-1", revision_sequence: 2,
      revision_state: "needs_review", revision_fingerprint: "plan", matrix_id: "matrix",
      matrix_revision: 3, matrix_binding_fingerprint: "binding", status: "review_required",
      output_label: "NEEDS REVIEW", preview_fingerprint: "preview", row_count: 4,
      sections: [], diagnostics: [{ code: "review", severity: "review_required", message: "Review before formal use." }], generate_allowed: true,
    });
    const onBusyChange = vi.fn();

    render(<DraftMeasurementPlanWorkbookPanel projectId="P1" revisionId="draft-1" disabled={false} onBusyChange={onBusyChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Preview draft workbook" }));

    await waitFor(() => expect(screen.getByText("NEEDS REVIEW")).toBeTruthy());
    expect((screen.getByRole("button", { name: "Generate draft workbook" }) as HTMLButtonElement).disabled).toBe(false);
    expect(api.previewDraftMeasurementPlanWorkbook).toHaveBeenCalledWith("P1", "draft-1");
  });

  it("shows a published cleanup warning without hiding the download", async () => {
    vi.mocked(api.previewDraftMeasurementPlanWorkbook).mockResolvedValue({
      project_id: "P1", revision_id: "draft-1", revision_sequence: 2, revision_state: "draft",
      revision_fingerprint: "plan", matrix_id: "matrix", matrix_revision: 3,
      matrix_binding_fingerprint: "binding", status: "ready", output_label: "DRAFT",
      preview_fingerprint: "preview", row_count: 1, sections: [], diagnostics: [], generate_allowed: true,
    });
    vi.mocked(api.generateDraftMeasurementPlanWorkbook).mockResolvedValue({
      project_id: "P1", revision_id: "draft-1", artifact_id: "a".repeat(32),
      file_name: "draft.xlsx", output_label: "DRAFT", download_url: "/download",
      cleanup_warning: "Older draft artifacts could not be cleaned up.",
    });

    render(<DraftMeasurementPlanWorkbookPanel projectId="P1" revisionId="draft-1" disabled={false} onBusyChange={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Preview draft workbook" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate draft workbook" })).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: "Generate draft workbook" }));

    await waitFor(() => expect(screen.getByText("Older draft artifacts could not be cleaned up.")).toBeTruthy());
    expect(screen.getByRole("link", { name: "Download draft workbook" })).toBeTruthy();
  });
});
