import { Component, type ErrorInfo, type ReactElement, type ReactNode } from "react";
import { MatrixEditorWorkspace } from "../features/matrix-editor/MatrixEditorWorkspace";

type ProjectMatrixEditorPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
  onOpenContactMeasurementSetup?: () => void;
};

export function ProjectMatrixEditorPage({
  projectId,
  onBackToWorkbench,
  onOpenContactMeasurementSetup,
}: ProjectMatrixEditorPageProps): ReactElement {
  return (
    <MatrixEditorErrorBoundary onBackToWorkbench={onBackToWorkbench}>
      <MatrixEditorWorkspace
        projectId={projectId}
        onBackToWorkbench={onBackToWorkbench}
        onOpenContactMeasurementSetup={onOpenContactMeasurementSetup}
      />
    </MatrixEditorErrorBoundary>
  );
}

type MatrixEditorErrorBoundaryProps = {
  children: ReactNode;
  onBackToWorkbench: () => void;
};

type MatrixEditorErrorBoundaryState = {
  hasError: boolean;
  message: string;
};

class MatrixEditorErrorBoundary extends Component<
  MatrixEditorErrorBoundaryProps,
  MatrixEditorErrorBoundaryState
> {
  state: MatrixEditorErrorBoundaryState = {
    hasError: false,
    message: "",
  };

  static getDerivedStateFromError(error: Error): MatrixEditorErrorBoundaryState {
    return {
      hasError: true,
      message: error.message || "Unknown Matrix Editor error",
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Keep operator-visible fallback instead of white screen and log details for debugging.
    console.error("Matrix Editor render error", error, errorInfo);
  }

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }
    return (
      <section className="panel">
        <h2>Matrix editor failed to load</h2>
        <p>{this.state.message}</p>
        <button type="button" onClick={this.props.onBackToWorkbench}>
          Back to Workbench
        </button>
      </section>
    );
  }
}
