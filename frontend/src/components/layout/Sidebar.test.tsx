import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "./Sidebar";

describe("Sidebar interaction lock", () => {
  it("opens the bottom user menu with the existing Settings destination", async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<Sidebar activeRoute="projects" onNavigate={onNavigate} />);

    await user.click(screen.getByRole("button", { name: "Lab User" }));

    const menu = screen.getByRole("menu", { name: "User menu" });
    expect(within(menu).getByText("Offline local")).toBeTruthy();
    await user.click(within(menu).getByRole("menuitem", { name: "Settings" }));

    expect(onNavigate).toHaveBeenCalledWith("/settings");
    expect(screen.queryByRole("menu", { name: "User menu" })).toBeNull();
  });

  it("shows the reserved search placeholder instead of the dashboard item", () => {
    render(<Sidebar activeRoute="projects" />);

    const searchButton = screen.getByRole("button", { name: "Search" });
    expect((searchButton as HTMLButtonElement).disabled).toBe(true);
    expect(searchButton.querySelector("svg")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Dashboard" })).toBeNull();
  });

  it("blocks navigation and collapse while New Project Apply LTR is busy", async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    const onToggleCollapsed = vi.fn();
    render(
      <Sidebar
        activeRoute="intake"
        interactionLocked={true}
        interactionLockedReason="Applying LTR number. Keep this page open."
        onNavigate={onNavigate}
        onToggleCollapsed={onToggleCollapsed}
      />
    );

    const projectsButton = screen.getByRole("button", { name: /Projects/ });
    const toggleButton = screen.getByRole("button", { name: /Collapse sidebar/ });
    expect(screen.queryByRole("button", { name: "Runtime Prototype (Dev)" })).toBeNull();
    expect((projectsButton as HTMLButtonElement).disabled).toBe(true);
    expect(projectsButton.getAttribute("title")).toBe("Applying LTR number. Keep this page open.");
    expect((toggleButton as HTMLButtonElement).disabled).toBe(true);

    await user.click(projectsButton);
    await user.click(toggleButton);

    expect(onNavigate).not.toHaveBeenCalled();
    expect(onToggleCollapsed).not.toHaveBeenCalled();
  });

  it("exposes Tools as an active navigation destination", async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<Sidebar activeRoute="tools" onNavigate={onNavigate} />);

    const toolsButton = screen.getByRole("button", { name: "Tools" });
    expect((toolsButton as HTMLButtonElement).disabled).toBe(false);
    expect(toolsButton.getAttribute("aria-current")).toBe("page");
    await user.click(toolsButton);
    expect(onNavigate).toHaveBeenCalledWith("/tools");
  });
});
