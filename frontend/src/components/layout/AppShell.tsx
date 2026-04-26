import type { ReactElement, ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

type AppShellProps = {
  activeRoute: string;
  children: ReactNode;
};

export function AppShell({ activeRoute, children }: AppShellProps): ReactElement {
  return (
    <div className="app-shell">
      <Sidebar activeRoute={activeRoute} />
      <div className="app-workspace">
        <TopBar activeRoute={activeRoute} />
        <main className="main-work-area">{children}</main>
      </div>
    </div>
  );
}
