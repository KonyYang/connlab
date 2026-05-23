import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { TestRecordPreviewSmokePanel } from "./TestRecordPreviewSmokePanel";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixTestRecordPreview: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixTestRecordPreview: apiMocks.fetchConfirmedMatrixTestRecordPreview,
  };
});

describe("TestRecordPreviewSmokePanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders only selected groups returned by preview API", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      confirmed_matrix_id: "cm-1",
      preview_status: "ready",
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "3",
          step_count: 1,
          steps: [
            {
              sequence: 1,
              raw_token: "1",
              test_item: "Visual",
              section: "6.1",
              method: "",
              condition: "",
              requirement: "",
            },
          ],
        },
      ],
    });

    render(<TestRecordPreviewSmokePanel projectId="P1" />);

    await waitFor(() => {
      expect(apiMocks.fetchConfirmedMatrixTestRecordPreview).toHaveBeenCalledWith("P1");
    });
    expect(await screen.findByText("Group 1 (g1)")).toBeTruthy();
    expect(screen.queryByText("Group 2 (g2)")).toBeNull();
  });

  it("renders not-ready state for 404", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new ApiRequestError("Not Found", 404, null)
    );

    render(<TestRecordPreviewSmokePanel projectId="P1" />);

    expect(
      await screen.findByText("No active confirmed matrix yet. Confirm Matrix authority first.")
    ).toBeTruthy();
  });

  it("renders empty state when preview has no steps", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      confirmed_matrix_id: "cm-1",
      preview_status: "empty",
      groups: [],
    });

    render(<TestRecordPreviewSmokePanel projectId="P1" />);

    expect(
      await screen.findByText("Active confirmed matrix found, but no previewable steps are available.")
    ).toBeTruthy();
  });
});
