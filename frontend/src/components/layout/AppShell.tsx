import { useEffect, useState, type ReactElement, type ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

type AppShellProps = {
  activeRoute: string;
  topBarTitle?: string;
  topBarActions?: ReactNode;
  children: ReactNode;
  interactionLocked?: boolean;
  interactionLockedReason?: string;
  onNavigate?: (path: string) => void;
};

function navigate(path: string): void {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function AppShell({
  activeRoute,
  topBarTitle,
  topBarActions,
  children,
  interactionLocked = false,
  interactionLockedReason,
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
    <div className={`app-shell${sidebarCollapsed ? " app-shell-sidebar-collapsed" : ""}`}>
      <Sidebar
        activeRoute={activeRoute}
        collapsed={sidebarCollapsed}
        interactionLocked={interactionLocked}
        interactionLockedReason={interactionLockedReason}
        onNavigate={onNavigate}
        onToggleCollapsed={() => setSidebarCollapsed((current) => !current)}
      />
      <div className="app-workspace">
        <TopBar activeRoute={activeRoute} titleOverride={topBarTitle} actions={topBarActions} />
        <main className="main-work-area">{children}</main>
      </div>
    </div>
  );
}
