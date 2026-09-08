import { Component, type ReactNode } from "react";
import { reportFrontendError } from "../../api/client";
import { diagnosticPagePath } from "../support/FrontendDiagnosticsReporter";

type Props = { children: ReactNode; onReload?: () => void };
type State = { error: Error | null };

function isPageLoadFailure(error: Error): boolean {
  return /failed to fetch dynamically imported module|importing a module script failed|error loading dynamically imported module|unable to preload css|loading chunk .+ failed/i.test(error.message);
}

export class RouteLoadBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error): void {
    void reportFrontendError({
      kind: "window_error",
      message: error.message,
      stack: error.stack ?? null,
      page_path: diagnosticPagePath(window.location.pathname),
    }).catch(() => undefined);
  }

  render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;
    const pageLoadFailed = isPageLoadFailure(error);
    return (
      <section className="state-panel state-panel-error" role="alert">
        <h2>{pageLoadFailed ? "Please refresh to load this page" : "Unable to display this page"}</h2>
        <p>{pageLoadFailed
          ? "A new software version or an interrupted connection may have made this page unavailable."
          : "Please refresh and try again. If the problem continues, contact support."}</p>
        <p>Refreshing may discard unsaved changes. The page will not refresh automatically.</p>
        <button type="button" className="primary-action"
          onClick={() => this.props.onReload ? this.props.onReload() : window.location.reload()}>
          Refresh page
        </button>
      </section>
    );
  }
}
