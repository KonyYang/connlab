import { useEffect, useRef, useState, type ReactElement } from "react";
import { UiIcon, type UiIconName } from "../common/UiIcon";
import { CURRENT_USER_DISPLAY_NAME, bootstrapCurrentProfile, refreshCurrentProfile, useCurrentProfile } from "../../currentUser";
import { AccountDialog } from '../../features/local-identity/AccountDialog';

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
  { label: "Search", route: "search", hint: null, icon: "search", disabled: true },
  { label: "New Project", route: "intake", hint: null, icon: "new-project" },
  { label: "Projects", route: "projects", hint: null, icon: "project-overview" },
  { label: "Reports", route: "reports", hint: null, icon: "reports", disabled: true },
  { label: "Folders", route: "folders", hint: null, icon: "folder", disabled: true },
  { label: "Tools", route: "tools", hint: null, icon: "tools" },
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
  const [accountDialogOpen, setAccountDialogOpen] = useState(false);
  const profile = useCurrentProfile();
  const accountTrigger = useRef<HTMLButtonElement>(null);
  const displayName = profile.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME;
  const accountLocked = interactionLocked || profile.busy;
  useEffect(() => {
    void bootstrapCurrentProfile();
    const refresh = () => { void refreshCurrentProfile(); };
    window.addEventListener('focus', refresh);
    return () => window.removeEventListener('focus', refresh);
  }, []);

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
      <div className="sidebar-account">
        <button
          ref={accountTrigger}
          aria-expanded={accountDialogOpen}
          aria-haspopup="dialog"
          aria-label="Project Leader"
          className="sidebar-account-trigger"
          disabled={accountLocked}
          title={interactionLocked ? interactionLockedReason : `Project Leader: ${displayName}`}
          type="button"
          onClick={() => {
            if (!interactionLocked) {
              setAccountDialogOpen(true);
            }
          }}
        >
          <span className="sidebar-account-avatar"><UiIcon name="user" /></span>
          <span className="sidebar-account-copy">
            <strong>{displayName}</strong>
            <small>Project Leader</small>
          </span>
          <span className="sidebar-account-chevron"><UiIcon name="chevron-down" /></span>
        </button>
      </div>
      {accountDialogOpen && <AccountDialog locked={interactionLocked} returnFocus={accountTrigger.current}
        onClose={() => setAccountDialogOpen(false)} />}
    </aside>
  );
}
