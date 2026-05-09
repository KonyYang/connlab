import type { ReactElement } from "react";
import { UiIcon } from "../common/UiIcon";

type TopBarProps = {
  activeRoute: string;
};

const ROUTE_TITLES: Record<string, { title: string }> = {
  projects: {
    title: "Projects"
  },
  intake: {
    title: "New Project"
  },
  workbench: {
    title: "Project workbench"
  },
  settings: {
    title: "Settings"
  },
  unknown: {
    title: "ConnLab"
  }
};

export function TopBar({ activeRoute }: TopBarProps): ReactElement {
  const context = ROUTE_TITLES[activeRoute] ?? ROUTE_TITLES.unknown;

  return (
    <header className="top-bar">
      <div>
        <h1>{context.title}</h1>
      </div>
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
