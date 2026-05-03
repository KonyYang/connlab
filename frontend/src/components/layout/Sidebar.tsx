import type { ReactElement } from "react";
import { UiIcon, type UiIconName } from "../common/UiIcon";

type SidebarProps = {
  activeRoute: string;
  onNavigate?: (path: string) => void;
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
  { label: "Projects", route: "projects", hint: null, icon: "projects" },
  { label: "New Project", route: "intake", hint: null, icon: "new-project" },
  { label: "Reports", route: "reports", hint: null, icon: "reports", disabled: true },
  { label: "Folders", route: "folders", hint: null, icon: "folder", disabled: true },
  { label: "Templates", route: "templates", hint: null, icon: "templates", disabled: true },
  { label: "Reference Library", route: "reference", hint: null, icon: "library", disabled: true },
  { label: "Settings", route: "settings", hint: null, icon: "settings", disabled: true }
];

export function Sidebar({ activeRoute, onNavigate }: SidebarProps): ReactElement {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="sidebar-brand">
        <img className="brand-mark" src="/connlab-icon.svg" alt="" aria-hidden="true" />
        <div>
          <strong>ConnLab</strong>
          <small>Local workbench</small>
        </div>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const active = item.route === activeRoute;
          return (
            <button
              aria-current={active ? "page" : undefined}
              className={`nav-item${active ? " nav-item-active" : ""}`}
              disabled={item.disabled}
              key={item.route}
              onClick={() => {
                if (!item.disabled) {
                  onNavigate?.(`/${item.route}`);
                }
              }}
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
