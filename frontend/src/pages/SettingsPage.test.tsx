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
});
