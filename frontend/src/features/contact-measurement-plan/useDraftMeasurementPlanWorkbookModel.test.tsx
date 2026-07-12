import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useDraftMeasurementPlanWorkbookModel } from "./useDraftMeasurementPlanWorkbookModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchLatestDraftMeasurementPlanWorkbook: vi.fn().mockResolvedValue(null),
  previewDraftMeasurementPlanWorkbook: vi.fn(),
  generateDraftMeasurementPlanWorkbook: vi.fn(),
}));

describe("useDraftMeasurementPlanWorkbookModel", () => {
  it("loads latest, previews, and exposes nonfatal cleanup warning after generation", async () => {
    vi.mocked(api.previewDraftMeasurementPlanWorkbook).mockResolvedValue(preview());
    vi.mocked(api.generateDraftMeasurementPlanWorkbook).mockResolvedValue({
      project_id: "P1", revision_id: "draft-1", artifact_id: "a".repeat(32),
      file_name: "draft.xlsx", output_label: "DRAFT", download_url: "/download",
      cleanup_warning: "Older draft artifacts could not be cleaned up.",
    });

    const { result } = renderHook(() => useDraftMeasurementPlanWorkbookModel({ projectId: "P1", revisionId: "draft-1" }));
    await waitFor(() => expect(api.fetchLatestDraftMeasurementPlanWorkbook).toHaveBeenCalledWith("P1"));

    await act(async () => { await result.current.previewDraft(); });
    await act(async () => { await result.current.generateDraft(); });

    expect(result.current.preview?.output_label).toBe("DRAFT");
    expect(result.current.artifact?.cleanup_warning).toBe("Older draft artifacts could not be cleaned up.");
    expect(result.current.busy).toBe(false);
  });
});

function preview(): api.DraftMeasurementPlanWorkbookPreview {
  return {
    project_id: "P1", revision_id: "draft-1", revision_sequence: 1, revision_state: "draft",
    revision_fingerprint: "plan", matrix_id: "matrix", matrix_revision: 3,
    matrix_binding_fingerprint: "binding", status: "ready", output_label: "DRAFT",
    preview_fingerprint: "preview", row_count: 1, sections: [], diagnostics: [], generate_allowed: true,
  };
}
