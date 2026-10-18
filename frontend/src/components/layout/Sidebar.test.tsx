import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Sidebar } from "./Sidebar";
import { ApiRequestError } from '../../api/client';
import * as profileApi from '../../api/localIdentity';
import { refreshCurrentProfile } from '../../currentUser';
vi.mock('../../api/localIdentity', async original => ({ ...await original<typeof import('../../api/localIdentity')>(),
  getLocalProfile: vi.fn(), saveLocalProfile: vi.fn() }));

describe("Sidebar interaction lock", () => {
  beforeEach(async () => {
    vi.resetAllMocks();
    vi.mocked(profileApi.getLocalProfile).mockResolvedValue({ profile: null });
    await refreshCurrentProfile();
  });
  it('opens the name editor directly and returns focus to the avatar after native Escape', async () => {
    HTMLDialogElement.prototype.showModal = function () {
      this.setAttribute('open', ''); this.querySelector<HTMLInputElement>('input')?.focus();
    };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    const user = userEvent.setup();
    render(<Sidebar activeRoute="tools" />);
    const trigger = screen.getByRole('button', { name: 'Project Leader' });
    expect(trigger.title).toBe('Project Leader: Lab User');
    await user.click(trigger);
    const dialog = screen.getByRole('dialog', { name: 'Project Leader' });
    expect(screen.getByRole('textbox', { name: 'Project Leader' })).toBeTruthy();
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
  it('keeps the old name without stale save alerts after cancel/reopen, and permits a successful retry', async () => {
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    vi.mocked(profileApi.getLocalProfile).mockResolvedValue({ profile: { display_name: '原姓名' } });
    await refreshCurrentProfile();
    vi.mocked(profileApi.saveLocalProfile).mockRejectedValue(new ApiRequestError('Raw origin /api/local-identity/profile trace', 403, null));
    const user = userEvent.setup();
    render(<Sidebar activeRoute="tools" />);
    await user.click(screen.getByRole('button', { name: 'Project Leader' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Project Leader' }), { target: { value: '新姓名' } });
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect((await screen.findByRole('alert')).textContent).toBe('Could not save. Refresh the page and retry.');
    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    await user.click(screen.getByRole('button', { name: 'Project Leader' }));
    expect(screen.queryByRole('alert')).toBeNull();
    expect((screen.getByRole('textbox', { name: 'Project Leader' }) as HTMLInputElement).value).toBe('原姓名');
    expect(screen.queryByText(/Raw origin|\/api\/local-identity/)).toBeNull();
    vi.mocked(profileApi.saveLocalProfile).mockResolvedValue({ profile: { display_name: '新姓名' } });
    fireEvent.change(screen.getByRole('textbox', { name: 'Project Leader' }), { target: { value: '新姓名' } });
    expect(screen.queryByRole('alert')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Save' }));
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(screen.getByRole('button', { name: 'Project Leader' }).title).toBe('Project Leader: 新姓名');
  });
  it('shows a recognized backend field reason once and focuses the editable name after save finishes', async () => {
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
    vi.mocked(profileApi.saveLocalProfile).mockRejectedValue(new ApiRequestError('raw', 400,
      { field: 'display_name', message: '姓名不能包含控制字符或无效字符。' }));
    const user = userEvent.setup();
    render(<Sidebar activeRoute="tools" />);
    await user.click(screen.getByRole('button', { name: 'Project Leader' }));
    const input = screen.getByRole('textbox', { name: 'Project Leader' });
    fireEvent.change(input, { target: { value: '姓名' } });
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect((await screen.findByRole('alert')).textContent).toBe('Remove invalid or control characters from the name.');
    expect(screen.getAllByRole('alert')).toHaveLength(1);
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(document.activeElement).toBe(input);
  });
});
