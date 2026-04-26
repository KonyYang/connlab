import type { ReactElement } from "react";

type EmptyStateProps = {
  title: string;
  message: string;
};

export function EmptyState({ title, message }: EmptyStateProps): ReactElement {
  return (
    <div className="state-panel">
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  );
}
