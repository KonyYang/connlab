import type { ReactElement, ReactNode } from "react";

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

  return (
    <header className={`top-bar top-bar-${activeRoute}`}>
      <div className="top-bar-title-slot">
        <h1 title={title}>{title}</h1>
      </div>
      <div className="top-bar-actions" data-top-bar-actions="true" aria-label="Page actions">{actions}</div>
    </header>
  );
}
