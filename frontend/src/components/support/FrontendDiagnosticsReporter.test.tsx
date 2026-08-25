import { render, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { reportFrontendError } from "../../api/client";
import { FrontendDiagnosticsReporter } from "./FrontendDiagnosticsReporter";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  reportFrontendError: vi.fn().mockResolvedValue(undefined)
}));

describe("FrontendDiagnosticsReporter", () => {
  it("reports an uncaught browser error without query parameters", async () => {
    window.history.replaceState({}, "", "/projects/private-id/matrix-editor?token=secret");
    render(<FrontendDiagnosticsReporter />);

    window.dispatchEvent(new ErrorEvent("error", {
      message: "render failed",
      error: new Error("render failed")
    }));

    await waitFor(() => expect(reportFrontendError).toHaveBeenCalledWith(expect.objectContaining({
      kind: "window_error",
      message: "render failed",
      page_path: "/projects/{project_id}/matrix-editor"
    })));
  });

  it("reports an unhandled promise rejection", async () => {
    vi.mocked(reportFrontendError).mockClear();
    render(<FrontendDiagnosticsReporter />);
    const rejection = new Event("unhandledrejection");
    Object.defineProperty(rejection, "reason", { value: new Error("async failed") });

    window.dispatchEvent(rejection);

    await waitFor(() => expect(reportFrontendError).toHaveBeenCalledWith(expect.objectContaining({
      kind: "unhandled_rejection",
      message: "async failed"
    })));
  });
});
