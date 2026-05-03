import type { ReactElement } from "react";
import { UiIcon } from "../common/UiIcon";

type TopBarProps = {
  activeRoute: string;
};

const ROUTE_TITLES: Record<string, { title: string; description: string }> = {
  projects: {
    title: "Projects",
    description: "Project registry and workflow overview."
  },
  intake: {
    title: "New Project",
    description: "Start from a request package or manual entry before project confirmation."
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
      <div className="top-search" role="search">
        <UiIcon name="search" />
        <input
          aria-label="Search ConnLab"
          placeholder="Search projects, LTR Number, product..."
          readOnly
        />
      </div>
      <div className="top-utilities" aria-label="Utilities">
        <button className="utility-button utility-alert" title="Local notifications" type="button">
          <UiIcon name="bell" />
          <span>2</span>
        </button>
        <button className="utility-button" title="Help" type="button">
          <UiIcon name="help" />
        </button>
        <button className="user-menu" type="button">
          <span className="user-avatar"><UiIcon name="user" /></span>
          <span>
            <strong>Lab User</strong>
            <small>Offline local</small>
          </span>
          <UiIcon name="chevron-down" />
        </button>
      </div>
    </header>
  );
}
