import type { ReactElement } from "react";

type TopBarProps = {
  activeRoute: string;
};

const ROUTE_TITLES: Record<string, { title: string; description: string }> = {
  projects: {
    title: "Projects",
    description: "Create, resume, and inspect MVP project workflow."
  },
  intake: {
    title: "Intake inbox",
    description: "Review incoming request packages before project confirmation."
  },
  workbench: {
    title: "Project workbench",
    description: "Review the current project state and next action."
  },
  unknown: {
    title: "ConnLab",
    description: "Offline connector laboratory workbench."
  }
};

export function TopBar({ activeRoute }: TopBarProps): ReactElement {
  const context = ROUTE_TITLES[activeRoute] ?? ROUTE_TITLES.unknown;

  return (
    <header className="top-bar">
      <div>
        <p className="eyebrow">ConnLab MVP</p>
        <h1>{context.title}</h1>
      </div>
      <p className="top-bar-description">{context.description}</p>
      <span className="environment-badge">Offline local</span>
    </header>
  );
}
