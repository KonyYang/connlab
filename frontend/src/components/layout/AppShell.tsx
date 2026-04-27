import type { ReactElement, ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

type AppShellProps = {
  activeRoute: string;
  children: ReactNode;
};

function navigate(path: string): void {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function AppShell({ activeRoute, children }: AppShellProps): ReactElement {
  return (
    <div className="app-shell">
      <Sidebar activeRoute={activeRoute} onNavigate={navigate} />
      <div className="app-workspace">
        <TopBar activeRoute={activeRoute} />
        <main className="main-work-area">{children}</main>
      </div>
    </div>
  );
}
