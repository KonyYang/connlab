import { useEffect, useRef, useState, type ReactElement } from "react";
import { UiIcon, type UiIconName } from "../common/UiIcon";
import { CURRENT_USER_DISPLAY_NAME, bootstrapCurrentProfile, refreshCurrentProfile, useCurrentProfile } from "../../currentUser";
import { AccountDialog } from '../../features/local-identity/AccountDialog';
import { getPublicFolderWorkflowContext, openLocalProjectFolder } from "../../api/client";

type SidebarProps = {
  activeRoute: string;
  collapsed?: boolean;
  interactionLocked?: boolean;
  interactionLockedReason?: string;
  onNavigate?: (path: string) => void;
  onToggleCollapsed?: () => void;
  projectId?: string | null;
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
  onToggleCollapsed,
  projectId = null,
}: SidebarProps): ReactElement {
  const [accountDialogOpen, setAccountDialogOpen] = useState(false);
  const profile = useCurrentProfile();
  const accountTrigger = useRef<HTMLButtonElement>(null);
  const displayName = profile.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME;
  const accountLocked = interactionLocked || profile.busy;
  const [folderAvailability, setFolderAvailability] = useState<{ projectId: string; available: boolean } | null>(null);
  const [folderError, setFolderError] = useState<string | null>(null);
  const projectIdRef = useRef(projectId);
  projectIdRef.current = projectId;
  useEffect(() => {
    let active = true;
    let request = 0;
    setFolderAvailability(null);
    setFolderError(null);
    if (!projectId) return;
    const refresh = () => {
      const current = ++request;
      void getPublicFolderWorkflowContext(projectId).then((context) => {
        if (active && current === request && context.project_id === projectId) {
          setFolderAvailability({ projectId, available: context.local_official_folder_available });
        }
      }).catch(() => {
        if (active && current === request) setFolderAvailability(null);
      });
    };
    const onFolderChanged = (event: Event) => {
      if ((event as CustomEvent<string>).detail === projectId) refresh();
    };
    refresh();
    window.addEventListener("focus", refresh);
    window.addEventListener("connlab:project-folder-changed", onFolderChanged);
    return () => {
      active = false;
      window.removeEventListener("focus", refresh);
      window.removeEventListener("connlab:project-folder-changed", onFolderChanged);
    };
  }, [projectId]);

  async function openProjectFolder(): Promise<void> {
    if (!projectId || folderAvailability?.projectId !== projectId || !folderAvailability.available) return;
    setFolderError(null);
    try {
      const result = await openLocalProjectFolder(projectId);
      if (projectIdRef.current !== projectId) return;
      if (result.status !== "opened") {
        if (result.status === "unsupported" && result.local_official_folder_path && navigator.clipboard?.writeText) {
          try {
            await navigator.clipboard.writeText(result.local_official_folder_path);
            if (projectIdRef.current !== projectId) return;
            setFolderError("Project folder path copied. Open it in File Explorer.");
            return;
          } catch { /* Display the path when clipboard access is unavailable. */ }
        }
        setFolderError([result.message, result.local_official_folder_path].filter(Boolean).join(" "));
      }
    } catch (error) {
      if (projectIdRef.current !== projectId) return;
      setFolderError(error instanceof Error ? error.message : "Could not open the project folder.");
    }
  }
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
          const disabled = (item.route === "folders" ? !projectId || folderAvailability?.projectId !== projectId || !folderAvailability.available : Boolean(item.disabled)) || interactionLocked;
          return (
            <button
              aria-disabled={disabled ? true : undefined}
              aria-current={active ? "page" : undefined}
              className={`nav-item${active ? " nav-item-active" : ""}${disabled ? " nav-item-disabled" : ""}`}
              disabled={disabled}
              key={item.route}
              onClick={() => {
                if (!disabled) {
                  if (item.route === "folders") void openProjectFolder();
                  else onNavigate?.(`/${item.route}`);
                }
              }}
              tabIndex={disabled ? -1 : undefined}
              title={interactionLocked ? interactionLockedReason : item.route === "folders" ? disabled ? "Open a project with an available folder first" : "Open project folder" : item.label}
              type="button"
            >
              <span className="nav-icon"><UiIcon name={item.icon} /></span>
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>
      {folderError ? <p role="alert">{folderError}</p> : null}
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
