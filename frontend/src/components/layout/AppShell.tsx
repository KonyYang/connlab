import { useEffect, useState, type ReactElement, type ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { TopBarActionsProvider } from "./TopBarActionsContext";

type AppShellProps = {
  activeRoute: string;
  topBarTitle?: string;
  topBarLeadingAction?: ReactNode;
  topBarActions?: ReactNode;
  children: ReactNode;
  interactionLocked?: boolean;
  interactionLockedReason?: string;
  onNavigate?: (path: string) => void;
  projectFolderId?: string;
};

function navigate(path: string): void {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function AppShell({
  activeRoute,
  topBarTitle,
  topBarLeadingAction,
  topBarActions,
  children,
  interactionLocked = false,
  interactionLockedReason,
  projectFolderId,
  onNavigate = navigate
}: AppShellProps): ReactElement {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    const raw = window.localStorage.getItem("connlab.sidebar.collapsed");
    return raw !== "0";
  });

  useEffect(() => {
    window.localStorage.setItem("connlab.sidebar.collapsed", sidebarCollapsed ? "1" : "0");
  }, [sidebarCollapsed]);

  return (
    <TopBarActionsProvider>
      <div className={`app-shell${sidebarCollapsed ? " app-shell-sidebar-collapsed" : ""}`}>
        <Sidebar
          activeRoute={activeRoute}
          collapsed={sidebarCollapsed}
          interactionLocked={interactionLocked}
          interactionLockedReason={interactionLockedReason}
          onNavigate={onNavigate}
          onToggleCollapsed={() => setSidebarCollapsed((current) => !current)}
        />
        <div className={`app-workspace${activeRoute === "workbench" ? " app-workspace-workbench" : ""}`}>
          <TopBar
            activeRoute={activeRoute}
            titleOverride={topBarTitle}
            leadingAction={topBarLeadingAction}
            projectFolderId={projectFolderId}
            folderBlockedReason={interactionLocked ? (interactionLockedReason ?? "Current operation is running. Keep this page open.") : undefined}
            actions={topBarActions}
          />
          <div className="app-main-scroll-region">
            <main className="main-work-area">{children}</main>
          </div>
        </div>
      </div>
    </TopBarActionsProvider>
  );
}
