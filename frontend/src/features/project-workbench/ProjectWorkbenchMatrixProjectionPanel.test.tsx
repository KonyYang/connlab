import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixTestRecordPreview: vi.fn(),
  generateConfirmedMatrixTestRecordDraft: vi.fn(),
  fetchConfirmedMatrixAuthorityHistory: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixTestRecordPreview: apiMocks.fetchConfirmedMatrixTestRecordPreview,
    generateConfirmedMatrixTestRecordDraft: apiMocks.generateConfirmedMatrixTestRecordDraft,
    fetchConfirmedMatrixAuthorityHistory: apiMocks.fetchConfirmedMatrixAuthorityHistory,
  };
});

describe("ProjectWorkbenchMatrixProjectionPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  function mockHistory(): void {
    apiMocks.fetchConfirmedMatrixAuthorityHistory.mockResolvedValue({
      project_id: "P1",
      entries: [],
    });
  }

  it("renders confirmed groups as matrix columns and step tokens as clickable cells", async () => {
    mockHistory();
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      project_id: "P1",
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
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
        {
          group_key: "g2",
          group_label: "Group 2",
          sample_quantity_expression: "5",
          step_count: 1,
          steps: [
            {
              sequence: 1,
              raw_token: "1",
              test_item: "Visual",
              section: "6.1",
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
      ],
    });

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    await waitFor(() => {
      expect(apiMocks.fetchConfirmedMatrixTestRecordPreview).toHaveBeenCalledWith("P1");
    });
    expect(await screen.findByText("Matrix execution projection")).toBeTruthy();
    expect(screen.getByText("Authority Change History")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate Test Record Draft" })).toBeTruthy();
    expect(screen.getByText("Confirmed: cm-1")).toBeTruthy();
    expect(screen.getByText("Group 1")).toBeTruthy();
    expect(screen.getByText("Group 2")).toBeTruthy();
    expect(screen.getByText("Samples: 3")).toBeTruthy();
    expect(screen.getByText("Samples: 5")).toBeTruthy();

    const tokens = screen.getAllByRole("button", { name: "1" });
    fireEvent.click(tokens[0]);
    const detail = screen.getByLabelText("Record Step Workspace");
    expect(detail).toBeTruthy();
    expect(within(detail).getByText("Visual")).toBeTruthy();
    expect(within(detail).getByText("No damage")).toBeTruthy();
    expect(within(detail).getByText("Record draft")).toBeTruthy();
    expect(within(detail).getByText("Evidence / data")).toBeTruthy();
    expect(within(detail).getByText("Review")).toBeTruthy();
  });

  it("renders not-ready state for missing active confirmed matrix", async () => {
    mockHistory();
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new ApiRequestError("Not Found", 404, null)
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("No active confirmed matrix yet. Confirm Matrix authority first.")
    ).toBeTruthy();
    expect(
      screen.getByRole("button", { name: "Generate Test Record Draft" }).hasAttribute("disabled")
    ).toBe(true);
  });

  it("merges same row context across groups even when token sequence differs", async () => {
    mockHistory();
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      project_id: "P1",
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
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
        {
          group_key: "g2",
          group_label: "Group 2",
          sample_quantity_expression: "5",
          step_count: 1,
          steps: [
            {
              sequence: 3,
              raw_token: "3",
              test_item: "Visual",
              section: "6.1",
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
      ],
    });

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(await screen.findByText("Matrix execution projection")).toBeTruthy();
    const table = screen.getByRole("table");
    const bodyRows = within(table).getAllByRole("row").slice(1);
    expect(bodyRows).toHaveLength(1);
    expect(screen.getAllByText("Visual")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "1" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "3" })).toBeTruthy();
  });

  it("renders empty state for active matrix with no previewable tokens", async () => {
    mockHistory();
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      project_id: "P1",
      confirmed_matrix_id: "cm-1",
      preview_status: "empty",
      groups: [],
    });

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("Active confirmed matrix found, but no previewable Matrix tokens are available.")
    ).toBeTruthy();
  });

  it("renders error state for unexpected API failure", async () => {
    mockHistory();
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new Error("boom")
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("Unable to load Matrix projection. Try again after confirming Matrix authority.")
    ).toBeTruthy();
  });
});
