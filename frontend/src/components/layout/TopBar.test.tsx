import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppShell } from "./AppShell";
import { TopBar } from "./TopBar";

describe("compact top context bar", () => {
  it("shows the page title and reserves a page-action slot without global placeholder controls", () => {
    render(<TopBar activeRoute="projects" actions={<button type="button">Refresh</button>} />);

    expect(screen.getByRole("heading", { name: "Projects" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
    expect(screen.getByRole("banner").querySelector(".top-bar-actions")).toBeTruthy();
    expect(screen.queryByRole("search")).toBeNull();
    expect(screen.queryByRole("button", { name: "Help" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Local notifications" })).toBeNull();
  });

  it("uses the route title when a page does not provide an override", () => {
    render(<TopBar activeRoute="tools" />);

    expect(screen.getByRole("heading", { name: "Tools" })).toBeTruthy();
  });

  it("uses the compact Workspace title for the project workbench", () => {
    render(<TopBar activeRoute="workbench" />);

    expect(screen.getByRole("heading", { name: "Workspace" })).toBeTruthy();
  });

  it("keeps AppShell top-bar actions compatible while the slot is context-owned", () => {
    render(
      <AppShell activeRoute="projects" topBarActions={<button type="button">Refresh</button>}>
        <p>Project content</p>
      </AppShell>
    );

    expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
    expect(screen.getByLabelText("Page actions").contains(screen.getByRole("button", { name: "Refresh" }))).toBe(true);
  });
});
