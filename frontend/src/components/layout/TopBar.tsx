import type { ReactElement, ReactNode } from "react";
import { useTopBarHostRegistration } from "./TopBarActionsContext";

type TopBarProps = {
  activeRoute: string;
  titleOverride?: string;
  actions?: ReactNode;
};

const ROUTE_TITLES: Record<string, { title: string }> = {
  projects: {
    title: "Projects"
  },
  intake: {
    title: "New Project"
  },
  workbench: {
    title: "Workspace"
  },
  settings: {
    title: "Settings"
  },
  tools: {
    title: "Tools"
  },
  unknown: {
    title: "ConnLab"
  }
};

export function TopBar({ activeRoute, titleOverride, actions }: TopBarProps): ReactElement {
  const context = ROUTE_TITLES[activeRoute] ?? ROUTE_TITLES.unknown;
  const title = titleOverride ?? context.title;
  const registerHost = useTopBarHostRegistration();

  return (
    <header className={`top-bar top-bar-${activeRoute}`}>
      <div className="top-bar-title-slot">
        <h1 title={title}>{title}</h1>
      </div>
      <div
        className="top-bar-actions"
        ref={registerHost}
        data-top-bar-actions="true"
        aria-label="Page actions"
      >
        {actions}
      </div>
    </header>
  );
}
