import type { ReactElement } from "react";

type SidebarProps = {
  activeRoute: string;
};

type NavItem = {
  label: string;
  route: string;
  hint: string;
  disabled?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", route: "dashboard", hint: "Project attention overview", disabled: true },
  { label: "Projects", route: "projects", hint: "Project registry" },
  { label: "Intake", route: "intake", hint: "Request material inbox", disabled: true },
  { label: "Precheck", route: "precheck", hint: "Project-scoped review", disabled: true },
  { label: "LTR", route: "ltr", hint: "Project-scoped LTR work", disabled: true },
  { label: "Folders", route: "folders", hint: "Project folder preparation", disabled: true },
  { label: "Settings", route: "settings", hint: "Local runtime settings", disabled: true }
];

export function Sidebar({ activeRoute }: SidebarProps): ReactElement {
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
              title={item.disabled ? `${item.label} is not active in Phase 5 yet` : item.hint}
              type="button"
            >
              <span>{item.label}</span>
              <small>{item.disabled ? "Not active" : item.hint}</small>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
