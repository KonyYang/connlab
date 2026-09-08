import { lazy, Suspense } from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RouteLoadBoundary } from "./RouteLoadBoundary";
import { reportFrontendError } from "../../api/client";

vi.mock("../../api/client", () => ({ reportFrontendError: vi.fn().mockResolvedValue(undefined) }));
beforeEach(() => { vi.mocked(reportFrontendError).mockResolvedValue(undefined); });

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe("route loading recovery", () => {
  it("recovers a rejected lazy page and refreshes only when requested", async () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    const reload = vi.fn();
    const Page = lazy(() => Promise.reject(new TypeError(
      "Failed to fetch dynamically imported module: http://localhost/assets/old-page.js",
    )));
    render(<RouteLoadBoundary onReload={reload}>
      <Suspense fallback={<p>Loading workspace...</p>}><Page /></Suspense>
    </RouteLoadBoundary>);

    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByText(/new software version or an interrupted connection/i)).toBeTruthy();
    expect(screen.queryByText("Loading workspace...")).toBeNull();
    expect(screen.queryByText(/old-page.js/)).toBeNull();
    expect(reload).not.toHaveBeenCalled();
    expect(reportFrontendError).toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Refresh page" }));
    expect(reload).toHaveBeenCalledTimes(1);
  });

  it("does not describe an unrelated render failure as a software update", async () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    function Broken(): never { throw new Error("invalid calculation"); }
    render(<RouteLoadBoundary><Broken /></RouteLoadBoundary>);
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByText("Unable to display this page")).toBeTruthy();
    expect(screen.queryByText(/new software version/)).toBeNull();
  });

  it("keeps normal page edits in place without reloading", () => {
    const reload = vi.fn();
    render(<RouteLoadBoundary onReload={reload}><input aria-label="Draft" /></RouteLoadBoundary>);
    fireEvent.change(screen.getByLabelText("Draft"), { target: { value: "unsaved work" } });
    expect((screen.getByLabelText("Draft") as HTMLInputElement).value).toBe("unsaved work");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(reload).not.toHaveBeenCalled();
  });
});
