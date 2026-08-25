import { useEffect, type ReactElement } from "react";
import { reportFrontendError, type FrontendErrorReport } from "../../api/client";

export function FrontendDiagnosticsReporter(): ReactElement | null {
  useEffect(() => {
    const send = (report: FrontendErrorReport) => {
      void reportFrontendError(report).catch(() => undefined);
    };
    const onError = (event: ErrorEvent) => {
      send({
        kind: "window_error",
        message: event.message || "Unhandled browser error",
        stack: event.error instanceof Error ? event.error.stack : null,
        page_path: diagnosticPagePath(window.location.pathname)
      });
    };
    const onUnhandledRejection = (event: PromiseRejectionEvent) => {
      const reason = event.reason;
      send({
        kind: "unhandled_rejection",
        message: reason instanceof Error ? reason.message : String(reason),
        stack: reason instanceof Error ? reason.stack : null,
        page_path: diagnosticPagePath(window.location.pathname)
      });
    };
    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onUnhandledRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onUnhandledRejection);
    };
  }, []);

  return null;
}

function diagnosticPagePath(pathname: string): string {
  return pathname
    .replace(/^\/projects\/[^/]+/, "/projects/{project_id}")
    .replace(/^\/intake\/[^/]+/, "/intake/{package_id}");
}
