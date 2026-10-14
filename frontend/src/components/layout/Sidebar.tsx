import { useEffect, useRef, useState, type ReactElement } from "react";
import { UiIcon, type UiIconName } from "../common/UiIcon";
import { CURRENT_USER_DISPLAY_NAME, bootstrapCurrentIdentity, refreshCurrentIdentity, logoutCurrentIdentity, useCurrentIdentity } from "../../currentUser";
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
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [accountDialogOpen, setAccountDialogOpen] = useState(false);
  const identity = useCurrentIdentity();
  const accountRoot = useRef<HTMLDivElement>(null);
  const accountTrigger = useRef<HTMLButtonElement>(null);
  const displayName = identity.user?.display_name ?? CURRENT_USER_DISPLAY_NAME;
  const accountLocked = interactionLocked || identity.busy;
  useEffect(() => {
    void bootstrapCurrentIdentity();
    const refresh = () => { void refreshCurrentIdentity(); };
    window.addEventListener('focus', refresh);
    return () => window.removeEventListener('focus', refresh);
  }, []);
  useEffect(() => {
    if (!userMenuOpen) return;
    const outside = (event: PointerEvent) => {
      if (event.target instanceof Node && !accountRoot.current?.contains(event.target)) setUserMenuOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setUserMenuOpen(false); accountTrigger.current?.focus(); }
    };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', escape); };
  }, [userMenuOpen]);
  async function signOut(switchAccount = false) {
    try { await logoutCurrentIdentity(); setUserMenuOpen(false); if (switchAccount) setAccountDialogOpen(true); }
    catch { /* Keep the current identity and show the store's error if revocation failed. */ }
  }

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
      <div ref={accountRoot} className="sidebar-account">
        {userMenuOpen ? (
          <div className="sidebar-account-menu" aria-label="User menu" role="menu">
            <div className="sidebar-account-menu-header">
              <strong>{displayName}</strong>
              <span>Offline local</span>
            </div>
            {identity.user ? <>
              <button type="button" className="sidebar-account-menu-item" role="menuitem" disabled={accountLocked} onClick={() => void signOut(true)}>Switch account</button>
              <button type="button" className="sidebar-account-menu-item" role="menuitem" disabled={accountLocked} onClick={() => void signOut()}>Sign out</button>
            </> : <button type="button" className="sidebar-account-menu-item" role="menuitem" disabled={accountLocked}
              onClick={() => { setUserMenuOpen(false); setAccountDialogOpen(true); }}>Sign in / Register</button>}
            {identity.error && <p className="sidebar-account-error" role="alert">{identity.error}</p>}
            <button
              className="sidebar-account-menu-item"
              role="menuitem"
              type="button"
              disabled={accountLocked}
              onClick={() => {
                setUserMenuOpen(false);
                onNavigate?.("/settings");
              }}
            >
              <UiIcon name="settings" />
              <span>Settings</span>
            </button>
          </div>
        ) : null}
        <button
          ref={accountTrigger}
          aria-expanded={userMenuOpen}
          aria-haspopup="menu"
          aria-label={displayName}
          className="sidebar-account-trigger"
          disabled={accountLocked}
          title={interactionLocked ? interactionLockedReason : displayName}
          type="button"
          onClick={() => {
            if (!interactionLocked) {
              setUserMenuOpen((current) => !current);
            }
          }}
        >
          <span className="sidebar-account-avatar"><UiIcon name="user" /></span>
          <span className="sidebar-account-copy">
            <strong>{displayName}</strong>
            <small>Offline local</small>
          </span>
          <span className="sidebar-account-chevron"><UiIcon name="chevron-down" /></span>
        </button>
      </div>
      {accountDialogOpen && <AccountDialog locked={interactionLocked} onClose={() => setAccountDialogOpen(false)} />}
    </aside>
  );
}
