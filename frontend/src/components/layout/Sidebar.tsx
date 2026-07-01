import type { ReactElement } from "react";
import { UiIcon, type UiIconName } from "../common/UiIcon";

type SidebarProps = {
  activeRoute: string;
  collapsed?: boolean;
  interactionLocked?: boolean;
  interactionLockedReason?: string;
  onNavigate?: (path: string) => void;
  onToggleCollapsed?: () => void;
};

type NavItem = {
  label: string;
  route: string;
  hint: string | null;
  icon: UiIconName;
  disabled?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", route: "dashboard", hint: null, icon: "dashboard", disabled: true },
  { label: "New Project", route: "intake", hint: null, icon: "new-project" },
  { label: "Projects", route: "projects", hint: null, icon: "projects" },
  { label: "Runtime Prototype (Dev)", route: "runtime-projection", hint: null, icon: "grid" },
  { label: "Reports", route: "reports", hint: null, icon: "reports", disabled: true },
  { label: "Folders", route: "folders", hint: null, icon: "folder", disabled: true },
  { label: "Templates", route: "templates", hint: null, icon: "templates", disabled: true },
  { label: "Reference Library", route: "reference", hint: null, icon: "library", disabled: true },
  { label: "Settings", route: "settings", hint: null, icon: "settings" }
];

export function Sidebar({
  activeRoute,
  collapsed,
  interactionLocked = false,
  interactionLockedReason = "Current operation is running. Keep this page open.",
  onNavigate,
  onToggleCollapsed
}: SidebarProps): ReactElement {
  return (
    <aside className={`sidebar${collapsed ? " sidebar-collapsed" : ""}`} aria-label="Primary navigation">
      <div className="sidebar-brand">
        <img className="brand-mark" src="/connlab-icon.svg" alt="" aria-hidden="true" />
        <strong>ConnLab</strong>
        <button
          aria-label={collapsed ? "Open sidebar" : "Collapse sidebar"}
          className="sidebar-toggle"
          disabled={interactionLocked}
          title={interactionLocked ? interactionLockedReason : collapsed ? "Open sidebar" : "Collapse sidebar"}
          type="button"
          onClick={() => {
            if (!interactionLocked) {
              onToggleCollapsed?.();
            }
          }}
        >
          <UiIcon name="columns" />
        </button>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const active = item.route === activeRoute;
          const disabled = Boolean(item.disabled) || interactionLocked;
          return (
            <button
              aria-disabled={disabled ? true : undefined}
              aria-current={active ? "page" : undefined}
              className={`nav-item${active ? " nav-item-active" : ""}${disabled ? " nav-item-disabled" : ""}`}
              disabled={disabled}
              key={item.route}
              onClick={() => {
                if (!disabled) {
                  onNavigate?.(`/${item.route}`);
                }
              }}
              tabIndex={disabled ? -1 : undefined}
              title={interactionLocked ? interactionLockedReason : item.label}
              type="button"
            >
              <span className="nav-icon"><UiIcon name={item.icon} /></span>
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
