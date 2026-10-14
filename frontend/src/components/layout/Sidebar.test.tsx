import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "./Sidebar";

describe("Sidebar interaction lock", () => {
  it('opens the name editor directly and returns focus to the avatar after native Escape', async () => {
    HTMLDialogElement.prototype.showModal = function () {
      this.setAttribute('open', ''); this.querySelector<HTMLInputElement>('input')?.focus();
    };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    const user = userEvent.setup();
    render(<Sidebar activeRoute="tools" />);
    const trigger = screen.getByRole('button', { name: 'Lab User' });
    await user.click(trigger);
    const dialog = screen.getByRole('dialog', { name: 'Project Leader Name' });
    expect(screen.getByLabelText('Display Project Leader Name')).toBeTruthy();
    expect(screen.queryByRole('menu')).toBeNull();
    expect(screen.queryByText(/Sign in|Register|Password|Remember login/i)).toBeNull();
    expect(dialog.contains(document.activeElement)).toBe(true);
    // Native dialogs emit cancel for Escape; jsdom does not implement that browser default.
    await user.keyboard('{Escape}');
    fireEvent(dialog, new Event('cancel', { cancelable: true }));
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(trigger);
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
