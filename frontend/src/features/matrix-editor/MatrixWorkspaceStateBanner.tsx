import { type ReactElement } from "react";
import { type MatrixWorkspaceBannerModel } from "./matrixWorkspaceClarityModel";

type MatrixWorkspaceStateBannerProps = {
  model: MatrixWorkspaceBannerModel;
};

export function MatrixWorkspaceStateBanner({
  model,
}: MatrixWorkspaceStateBannerProps): ReactElement {
  return (
    <section
      className={`matrix-workspace-state-banner matrix-workspace-state-banner-${model.tone}`}
      aria-label="Matrix workspace state"
    >
      <div>
        <span>Current State</span>
        <strong>{model.title}</strong>
      </div>
      <p>{model.consequence}</p>
    </section>
  );
}
