import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixTestRecordPreview: vi.fn(),
  generateConfirmedMatrixTestRecordDraftDownload: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixTestRecordPreview: apiMocks.fetchConfirmedMatrixTestRecordPreview,
    generateConfirmedMatrixTestRecordDraftDownload: apiMocks.generateConfirmedMatrixTestRecordDraftDownload,
  };
});

describe("ProjectWorkbenchMatrixProjectionPanel", () => {
  const createObjectUrlMock = vi.fn(() => "blob:test-record");
  const revokeObjectUrlMock = vi.fn();
  const anchorClickMock = vi.fn();

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders confirmed groups as matrix columns and step tokens as clickable cells", async () => {
    const onTokenSelect = vi.fn();
    const onOpenMatrixEditor = vi.fn();
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
    apiMocks.generateConfirmedMatrixTestRecordDraftDownload.mockResolvedValue({
      blob: new Blob(["docx"]),
      fileName: "DL-001 Test Record.docx",
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(anchorClickMock);
    vi.stubGlobal("URL", {
      createObjectURL: createObjectUrlMock,
      revokeObjectURL: revokeObjectUrlMock,
    });

    render(
      <ProjectWorkbenchMatrixProjectionPanel
        projectId="P1"
        onOpenMatrixEditor={onOpenMatrixEditor}
        onTokenSelect={onTokenSelect}
      />
    );

    await waitFor(() => {
      expect(apiMocks.fetchConfirmedMatrixTestRecordPreview).toHaveBeenCalledWith("P1");
    });
    await screen.findByRole("columnheader", { name: "Group 1" });
    expect(screen.getByRole("button", { name: "Matrix" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Test record" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Test record" }).hasAttribute("disabled")).toBe(false);
    expect(screen.queryByText("Authority Change History")).toBeNull();
    expect(screen.queryByRole("button", { name: "Generate Test Record Draft" })).toBeNull();
    expect(screen.queryByText("Confirmed: cm-1")).toBeNull();
    expect(screen.queryByText("Rows: 1")).toBeNull();
    expect(screen.queryByText("Tokens: 2")).toBeNull();
    expect(screen.queryByText("Not started")).toBeNull();
    expect(screen.queryByText("In progress")).toBeNull();
    expect(screen.queryByText("Pass")).toBeNull();
    expect(screen.queryByText("Failed")).toBeNull();
    expect(screen.getByRole("columnheader", { name: "Group 1" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "Group 2" })).toBeTruthy();
    expect(screen.queryByRole("columnheader", { name: "Seq" })).toBeNull();
    expect(screen.queryByRole("columnheader", { name: "Section" })).toBeNull();
    expect(screen.queryByText("Samples: 3")).toBeNull();
    expect(screen.queryByText("Samples: 5")).toBeNull();
    expect(screen.getByText("Sample sizes")).toBeTruthy();
    expect(screen.getByText("Estimated completion date")).toBeTruthy();
    expect(screen.getByText("Status")).toBeTruthy();
    const sampleSizesRow = screen.getByText("Sample sizes").closest("tr");
    expect(sampleSizesRow).toBeTruthy();
    expect(within(sampleSizesRow as HTMLElement).getByText("3")).toBeTruthy();
    expect(within(sampleSizesRow as HTMLElement).getByText("5")).toBeTruthy();
    expect(screen.getAllByText("Not scheduled")).toHaveLength(2);
    expect(screen.getAllByText("Pending execution data")).toHaveLength(2);
    expect(screen.queryByText("Review required")).toBeNull();
    expect(screen.queryByText("Reopened / retest")).toBeNull();

    const tokens = screen.getAllByRole("button", { name: "1" });
    fireEvent.click(screen.getByRole("button", { name: "Matrix" }));
    expect(onOpenMatrixEditor).toHaveBeenCalledTimes(1);
    fireEvent.click(tokens[0]);
    expect(screen.queryByLabelText("Record Step Workspace")).toBeNull();
    expect(screen.queryByText("Selected token: Group 1 / 1")).toBeNull();
    expect(onTokenSelect.mock.calls.length).toBeGreaterThanOrEqual(2);
    const lastCall = onTokenSelect.mock.calls[onTokenSelect.mock.calls.length - 1];
    expect(lastCall?.[0]?.groupLabel).toBe("Group 1");
    expect(lastCall?.[0]?.rawToken).toBe("1");

    fireEvent.click(screen.getByRole("button", { name: "Test record" }));
    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixTestRecordDraftDownload).toHaveBeenCalledWith("P1");
    });
    expect(createObjectUrlMock).toHaveBeenCalledTimes(1);
    expect(anchorClickMock).toHaveBeenCalledTimes(1);
  });

  it("renders not-ready state for missing active confirmed matrix", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new ApiRequestError("Not Found", 404, null)
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("No active confirmed matrix yet. Confirm Matrix authority first.")
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Test record" }).hasAttribute("disabled")).toBe(true);
    expect(screen.queryByRole("button", { name: "Generate Test Record Draft" })).toBeNull();
  });

  it("merges same row context across groups even when token sequence differs", async () => {
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

    await screen.findByRole("columnheader", { name: "Group 1" });
    expect(screen.getByRole("button", { name: "Matrix" })).toBeTruthy();
    const table = await screen.findByRole("table");
    const visualRows = within(table).getAllByRole("row").filter((row) => within(row).queryByText("Visual"));
    expect(visualRows).toHaveLength(1);
    expect(screen.getAllByText("Visual")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "1" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "3" })).toBeTruthy();
  });

  it("renders empty state for active matrix with no previewable tokens", async () => {
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
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new Error("boom")
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("Unable to load Matrix projection. Try again after confirming Matrix authority.")
    ).toBeTruthy();
  });

  it("shows backend generation error message when Test record generation fails", async () => {
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
      ],
    });
    apiMocks.generateConfirmedMatrixTestRecordDraftDownload.mockRejectedValue(
      new ApiRequestError("Test record template path is not configured.", 422, {
        detail: "Test record template path is not configured.",
      })
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    await screen.findByRole("columnheader", { name: "Group 1" });
    fireEvent.click(screen.getByRole("button", { name: "Test record" }));

    expect(
      await screen.findByText("Test record template path is not configured.")
    ).toBeTruthy();
  });
});
