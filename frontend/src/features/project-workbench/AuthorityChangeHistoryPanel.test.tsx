import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { AuthorityChangeHistoryPanel } from "./AuthorityChangeHistoryPanel";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixAuthorityHistory: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixAuthorityHistory: apiMocks.fetchConfirmedMatrixAuthorityHistory,
  };
});

describe("AuthorityChangeHistoryPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders empty state when no history entries exist", async () => {
    apiMocks.fetchConfirmedMatrixAuthorityHistory.mockResolvedValue({
      project_id: "P1",
      entries: [],
    });
    render(<AuthorityChangeHistoryPanel projectId="P1" />);
    expect(await screen.findByText("No confirmed authority history yet.")).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("renders current authority and regeneration advisory", async () => {
    apiMocks.fetchConfirmedMatrixAuthorityHistory.mockResolvedValue({
      project_id: "P1",
      entries: [
        {
          confirmed_matrix_id: "cmv-2",
          confirmed_revision: 2,
          is_active_authority: true,
          status: "confirmed",
          confirmed_by: "operator",
          confirmed_at: "2026-05-26T02:00:00+00:00",
          superseded_at: null,
          superseded_reason: null,
          source_snapshot_changed: false,
          group_change_count: 0,
          step_change_count: 0,
          token_change_count: 1,
          record_regeneration_recommended: true,
          change_summary: "Revision 2 changed 0 groups, 0 steps, and 1 matrix tokens.",
        },
      ],
    });
    render(<AuthorityChangeHistoryPanel projectId="P1" />);
    expect(await screen.findByText("Current authority")).toBeTruthy();
    expect(screen.getByText("Record draft may need regeneration.")).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("renders API failure message", async () => {
    apiMocks.fetchConfirmedMatrixAuthorityHistory.mockRejectedValue(new Error("boom"));
    render(<AuthorityChangeHistoryPanel projectId="P1" />);
    await waitFor(() => {
      expect(
        screen.getByText("Unable to load authority history. Try again later.")
      ).toBeTruthy();
    });
  });
});
