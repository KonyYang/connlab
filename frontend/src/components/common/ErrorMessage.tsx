import type { ReactElement } from "react";

type ErrorMessageProps = {
  message: string;
};

export function ErrorMessage({ message }: ErrorMessageProps): ReactElement {
  return (
    <div className="state-panel state-panel-error" role="alert">
      <strong>Workflow error</strong>
      <p>{message}</p>
    </div>
  );
}
