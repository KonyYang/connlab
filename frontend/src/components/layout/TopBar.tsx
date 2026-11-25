import {getRuntimeEnvironment} from "../../runtimeEnvironment";
import type { ReactElement, ReactNode } from "react";
import { ProjectFolderAction } from "./ProjectFolderAction";
import { useTopBarHostRegistration } from "./TopBarActionsContext";

type TopBarProps = {
  activeRoute: string;
  titleOverride?: string;
  leadingAction?: ReactNode;
  actions?: ReactNode;
  projectFolderId?: string;
  folderBlockedReason?: string;
};

const ROUTE_TITLES: Record<string, { title: string }> = {
  reference: { title: "Project Library" },
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

export function TopBar({ activeRoute, titleOverride, leadingAction, actions, projectFolderId, folderBlockedReason }: TopBarProps): ReactElement {
  const context = ROUTE_TITLES[activeRoute] ?? ROUTE_TITLES.unknown;
  const title = titleOverride ?? context.title;
  const registerHost = useTopBarHostRegistration();

  return (
    <header aria-label="Page header" className={`top-bar top-bar-${activeRoute}${projectFolderId ? " top-bar-with-project-folder" : ""}`}>
      <div className="top-bar-title-slot">
        {leadingAction}
        <h1 title={title}>{title}</h1>
        {getRuntimeEnvironment()?.environment === "development" && <span className="runtime-dev-badge">Dev</span>}
        {projectFolderId && <ProjectFolderAction key={projectFolderId} projectId={projectFolderId} blockedReason={folderBlockedReason} />}
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
