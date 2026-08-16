import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { listExternalResources } from "../api/client";
import { SettingsPage } from "./SettingsPage";

vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  listExternalResources: vi.fn()
}));

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.mocked(listExternalResources).mockReset();
    vi.mocked(listExternalResources).mockResolvedValue([]);
  });

  it("loads only non-secret external resource settings", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        configured: false,
        overridden_by_environment: false,
        password: null
      })
    } as Response);

    render(<SettingsPage />);

    expect(await screen.findByText("Editable file locations")).toBeTruthy();
    await waitFor(() => expect(listExternalResources).toHaveBeenCalledTimes(1));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("LTR workbook password")).toBeNull();
    fetchMock.mockRestore();
  });

  it("does not repeat a missing file path in the validation message", async () => {
    vi.mocked(listExternalResources).mockResolvedValue([
      {
        resource_id: "standard-version",
        resource_type: "standard_record_excel",
        path: "D:\\Source\\Foreign file directory.xls",
        active: true,
        validation_status: "invalid",
        last_validated_at: null,
        validation_failure_reason:
          "Expected an existing file: D:\\Source\\Foreign file directory.xls",
        worksheet_name: "认可标准"
      }
    ]);

    render(<SettingsPage />);

    const input = await screen.findByLabelText("Standard version file path");
    expect(input.getAttribute("title")).toBe("File does not exist.");
    expect(input.getAttribute("title")).not.toContain("D:\\Source");
  });
});
