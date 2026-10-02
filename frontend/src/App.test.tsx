import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./components/layout/AppShell", () => ({
  AppShell: ({ children, onNavigate }: { children: ReactNode; onNavigate: (path: string) => void }) => (
    <>
      <nav aria-label="Test sidebar">
        <button type="button" onClick={() => onNavigate("/settings")}>Settings</button>
        <button type="button" onClick={() => onNavigate("/projects")}>Projects</button>
      </nav>
      {children}
    </>
  ),
}));

vi.mock("./components/support/FrontendDiagnosticsReporter", () => ({
  FrontendDiagnosticsReporter: () => null,
}));

vi.mock("./pages/ProjectWorkbenchPage", () => ({
  ProjectWorkbenchPage: ({ onOpenBasicInformation }: { onOpenBasicInformation: () => void }) => (
    <section aria-label="Project Workbench">
      <button type="button" onClick={onOpenBasicInformation}>Basic Information</button>
    </section>
  ),
}));

vi.mock("./pages/ProjectBasicInformationPage", () => ({
  ProjectBasicInformationPage: ({
    projectId,
    initialValuesMode,
    onDraftSaved,
    onBackToWorkbench,
  }: {
    projectId: string;
    initialValuesMode: "draft" | "authoritative";
    onDraftSaved: () => void;
    onBackToWorkbench: (options: { refreshBasicInformation: boolean }) => void;
  }) => (
    <section aria-label="Basic Information">
      <output data-testid="basic-information-entry-mode">
        {projectId}:{initialValuesMode}
      </output>
      <button type="button" onClick={onDraftSaved}>Save draft</button>
      <button
        type="button"
        onClick={() => onBackToWorkbench({ refreshBasicInformation: false })}
      >
        Cancel
      </button>
    </section>
  ),
}));

vi.mock("./pages/SettingsPage", () => ({
  SettingsPage: () => <section aria-label="Settings page" />,
}));

describe("Basic Information route entry behavior", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/projects/P1");
  });

  it("imports authority on normal entry and after Cancel", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("imports authority on a fresh sidebar return", async () => {
    window.history.replaceState({}, "", "/projects/P1");
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await screen.findByTestId("basic-information-entry-mode");
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );

    await user.click(screen.getByRole("button", { name: "Settings" }));
    expect(await screen.findByLabelText("Settings page")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Projects" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("keeps normal authority entry after cancelling and navigating elsewhere", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Settings" }));
    await user.click(await screen.findByRole("button", { name: "Projects" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("loads authority for a direct URL without a saved editing session", async () => {
    window.history.replaceState({}, "", "/projects/P1/basic-information");
    render(<App />);
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("recovers saved session edits on reload without changing fresh-entry behavior", async () => {
    const user = userEvent.setup();
    const mounted = render(<App />);
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await user.click(await screen.findByRole("button", { name: "Save draft" }));
    mounted.unmount();
    render(<App />);
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:draft"
    );
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });
});
