import { useEffect, useState, type ReactElement } from "react";
import { AppShell } from "./components/layout/AppShell";
import {
  clearIntakeSession,
  EMPTY_INTAKE_SESSION,
  loadIntakeSession,
  saveIntakeSession,
  type IntakeSessionState
} from "./features/intake/intakeSession";
import { IntakeInboxPage } from "./pages/IntakeInboxPage";
import { IntakeCaseReviewPage } from "./pages/IntakeCaseReviewPage";
import { IntakePackageDetailPage } from "./pages/IntakePackageDetailPage";
import { ProjectMatrixEditorPage } from "./pages/ProjectMatrixEditorPage";
import { ProjectFeeEvaluationPage } from "./pages/ProjectFeeEvaluationPage";
import { ProjectBasicInformationPage } from "./pages/ProjectBasicInformationPage";
import { ProjectContactMeasurementSetupPage } from "./pages/ProjectContactMeasurementSetupPage";
import { ProjectListPage } from "./pages/ProjectListPage";
import { ProjectWorkbenchPage } from "./pages/ProjectWorkbenchPage";
import { RuntimeProjectionPrototypePage } from "./pages/RuntimeProjectionPrototypePage";
import { SettingsPage } from "./pages/SettingsPage";
import "./styles.css";

type Route =
  | { name: "projects" }
  | { name: "intake" }
  | { name: "intakePackage"; packageId: string }
  | { name: "intakeCaseReview"; packageId: string }
  | { name: "projectDetail"; projectId: string }
  | { name: "projectMatrixEditor"; projectId: string }
  | { name: "projectFeeEvaluation"; projectId: string }
  | { name: "projectBasicInformation"; projectId: string }
  | { name: "projectContactMeasurementSetup"; projectId: string }
  | { name: "runtimeProjection" }
  | { name: "settings" }
  | { name: "notFound" };

function parseRoute(pathname: string): Route {
  if (pathname === "/" || pathname === "/projects") {
    return { name: "projects" };
  }

  if (pathname === "/intake") {
    return { name: "intake" };
  }

  if (pathname === "/settings") {
    return { name: "settings" };
  }

  if (pathname === "/runtime-projection") {
    return { name: "runtimeProjection" };
  }

  const intakePackageMatch = pathname.match(/^\/intake\/([^/]+)$/);
  if (intakePackageMatch) {
    return { name: "intakePackage", packageId: decodeURIComponent(intakePackageMatch[1]) };
  }

  const intakeCaseReviewMatch = pathname.match(/^\/intake\/([^/]+)\/case-review$/);
  if (intakeCaseReviewMatch) {
    return { name: "intakeCaseReview", packageId: decodeURIComponent(intakeCaseReviewMatch[1]) };
  }

  const matrixEditorMatch = pathname.match(/^\/projects\/([^/]+)\/matrix-editor$/);
  if (matrixEditorMatch) {
    return { name: "projectMatrixEditor", projectId: decodeURIComponent(matrixEditorMatch[1]) };
  }

  const feeEvaluationMatch = pathname.match(/^\/projects\/([^/]+)\/fee-evaluation$/);
  if (feeEvaluationMatch) {
    return { name: "projectFeeEvaluation", projectId: decodeURIComponent(feeEvaluationMatch[1]) };
  }

  const basicInformationMatch = pathname.match(/^\/projects\/([^/]+)\/basic-information$/);
  if (basicInformationMatch) {
    return {
      name: "projectBasicInformation",
      projectId: decodeURIComponent(basicInformationMatch[1]),
    };
  }

  const contactMeasurementSetupMatch = pathname.match(
    /^\/projects\/([^/]+)\/contact-measurement-setup$/
  );
  if (contactMeasurementSetupMatch) {
    return {
      name: "projectContactMeasurementSetup",
      projectId: decodeURIComponent(contactMeasurementSetupMatch[1]),
    };
  }

  const match = pathname.match(/^\/projects\/([^/]+)$/);
  if (match) {
    return { name: "projectDetail", projectId: decodeURIComponent(match[1]) };
  }

  return { name: "notFound" };
}

function navigate(path: string): void {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export default function App(): ReactElement {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.pathname));
  const [intakeSession, setIntakeSession] =
    useState<IntakeSessionState>(loadIntakeSession);
  const [lastProjectRoute, setLastProjectRoute] = useState<string | null>(() => {
    const initialRoute = parseRoute(window.location.pathname);
    return isProjectWorkspaceRoute(initialRoute) ? window.location.pathname : null;
  });
  const [intakeInteractionLockReason, setIntakeInteractionLockReason] = useState<string | null>(null);

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    saveIntakeSession(intakeSession);
  }, [intakeSession]);

  useEffect(() => {
    if (isProjectWorkspaceRoute(route)) {
      setLastProjectRoute(window.location.pathname);
    }
  }, [route]);

  useEffect(() => {
    if (route.name !== "intake" && intakeInteractionLockReason) {
      setIntakeInteractionLockReason(null);
    }
  }, [intakeInteractionLockReason, route.name]);

  function handleShellNavigate(path: string): void {
    if (intakeInteractionLockReason && route.name === "intake") {
      return;
    }
    if (path === "/projects" && route.name !== "projects" && lastProjectRoute) {
      navigate(lastProjectRoute);
      return;
    }
    navigate(path);
  }

  const activeRoute =
    route.name === "projectDetail"
      ? "workbench"
      : route.name === "projectMatrixEditor"
        ? "workbench"
      : route.name === "projectFeeEvaluation"
        ? "workbench"
      : route.name === "projectBasicInformation"
        ? "workbench"
      : route.name === "projectContactMeasurementSetup"
        ? "workbench"
      : route.name === "intakePackage" || route.name === "intakeCaseReview"
        ? "intake"
        : route.name === "runtimeProjection"
          ? "runtime-projection"
        : route.name;
  const topBarTitle =
    route.name === "projectMatrixEditor"
      ? "Matrix Editor"
      : route.name === "projectFeeEvaluation"
        ? "Fee Evaluation"
      : route.name === "projectBasicInformation"
        ? "Basic Information"
      : route.name === "projectContactMeasurementSetup"
        ? "Test Points Setup"
        : undefined;

  return (
    <AppShell
      activeRoute={activeRoute}
      interactionLocked={Boolean(intakeInteractionLockReason)}
      interactionLockedReason={intakeInteractionLockReason ?? undefined}
      topBarTitle={topBarTitle}
      onNavigate={handleShellNavigate}
    >
      {route.name === "projects" && (
        <ProjectListPage
          onOpenProject={(id) => navigate(`/projects/${encodeURIComponent(id)}`)}
        />
      )}
      {route.name === "intake" && (
        <IntakeInboxPage
          session={intakeSession}
          onExit={() => {
            clearIntakeSession();
            setIntakeSession(EMPTY_INTAKE_SESSION);
            navigate("/projects");
          }}
          onProjectCreated={(projectId) => {
            clearIntakeSession();
            setIntakeSession(EMPTY_INTAKE_SESSION);
            navigate(`/projects/${encodeURIComponent(projectId)}`);
          }}
          onInteractionLockChange={setIntakeInteractionLockReason}
          onSessionChange={setIntakeSession}
        />
      )}
      {route.name === "intakePackage" && (
        <IntakePackageDetailPage
          packageId={route.packageId}
          onBack={() => navigate("/intake")}
          onOpenCaseReview={() => navigate(`/intake/${encodeURIComponent(route.packageId)}/case-review`)}
        />
      )}
      {route.name === "intakeCaseReview" && (
        <IntakeCaseReviewPage
          initialCaseId={intakeSession.selectedPrecheckCaseId}
          packageId={route.packageId}
          onExit={() => {
            clearIntakeSession();
            setIntakeSession(EMPTY_INTAKE_SESSION);
            navigate("/projects");
          }}
          onProjectConfirmed={() => {
            clearIntakeSession();
            setIntakeSession(EMPTY_INTAKE_SESSION);
          }}
        />
      )}
      {route.name === "projectDetail" && (
        <ProjectWorkbenchPage
          projectId={route.projectId}
          onBack={() => {
            setLastProjectRoute(null);
            navigate("/projects");
          }}
          onOpenMatrixEditor={() =>
            navigate(`/projects/${encodeURIComponent(route.projectId)}/matrix-editor`)
          }
          onOpenFeeEvaluation={() =>
            navigate(`/projects/${encodeURIComponent(route.projectId)}/fee-evaluation`)
          }
          onOpenBasicInformation={() =>
            navigate(`/projects/${encodeURIComponent(route.projectId)}/basic-information`)
          }
          onOpenSettings={() => navigate("/settings")}
        />
      )}
      {route.name === "projectMatrixEditor" && (
        <ProjectMatrixEditorPage
          projectId={route.projectId}
          onBackToWorkbench={() => navigate(`/projects/${encodeURIComponent(route.projectId)}`)}
          onOpenContactMeasurementSetup={() =>
            navigate(`/projects/${encodeURIComponent(route.projectId)}/contact-measurement-setup`)
          }
        />
      )}
      {route.name === "projectFeeEvaluation" && (
        <ProjectFeeEvaluationPage
          projectId={route.projectId}
          onBackToWorkbench={() => navigate(`/projects/${encodeURIComponent(route.projectId)}`)}
        />
      )}
      {route.name === "projectBasicInformation" && (
        <ProjectBasicInformationPage
          projectId={route.projectId}
          onBackToWorkbench={() => navigate(`/projects/${encodeURIComponent(route.projectId)}`)}
        />
      )}
      {route.name === "projectContactMeasurementSetup" && (
        <ProjectContactMeasurementSetupPage
          projectId={route.projectId}
          onBackToMatrix={() =>
            navigate(`/projects/${encodeURIComponent(route.projectId)}/matrix-editor`)
          }
        />
      )}
      {route.name === "settings" && <SettingsPage />}
      {/* Runtime Projection Prototype - Development only, read-only validation surface for TASK_209 */}
      {route.name === "runtimeProjection" && <RuntimeProjectionPrototypePage />}
      {route.name === "notFound" && (
        <section className="panel">
          <h2>Page not found</h2>
          <button type="button" onClick={() => navigate("/projects")}>
            Back to projects
          </button>
        </section>
      )}
    </AppShell>
  );
}

function isProjectWorkspaceRoute(route: Route): boolean {
  return (
    route.name === "projectDetail" ||
    route.name === "projectMatrixEditor" ||
    route.name === "projectFeeEvaluation" ||
    route.name === "projectBasicInformation"
  );
}
