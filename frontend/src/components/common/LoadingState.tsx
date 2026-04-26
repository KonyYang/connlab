import type { ReactElement } from "react";

type LoadingStateProps = {
  label: string;
};

export function LoadingState({ label }: LoadingStateProps): ReactElement {
  return (
    <div className="state-panel state-panel-loading" aria-busy="true">
      <span className="loading-line" />
      <span className="loading-line loading-line-short" />
      <p>{label}</p>
    </div>
  );
}
