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
import { ProjectListPage } from "./pages/ProjectListPage";
import { ProjectWorkbenchPage } from "./pages/ProjectWorkbenchPage";
import { SettingsPage } from "./pages/SettingsPage";
import { getIntakePackageDetail, type ProjectCreationDraft } from "./api/client";
import "./styles.css";

type Route =
  | { name: "projects" }
  | { name: "intake" }
  | { name: "intakePackage"; packageId: string }
  | { name: "intakeCaseReview"; packageId: string }
  | { name: "projectDetail"; projectId: string }
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

  const intakePackageMatch = pathname.match(/^\/intake\/([^/]+)$/);
  if (intakePackageMatch) {
    return { name: "intakePackage", packageId: decodeURIComponent(intakePackageMatch[1]) };
  }

  const intakeCaseReviewMatch = pathname.match(/^\/intake\/([^/]+)\/case-review$/);
  if (intakeCaseReviewMatch) {
    return { name: "intakeCaseReview", packageId: decodeURIComponent(intakeCaseReviewMatch[1]) };
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

function draftSourceMode(draft: ProjectCreationDraft): "msg" | "word" {
  return draft.source_type === "direct_application_form" ? "word" : "msg";
}

export default function App(): ReactElement {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.pathname));
  const [intakeSession, setIntakeSession] =
    useState<IntakeSessionState>(loadIntakeSession);

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    saveIntakeSession(intakeSession);
  }, [intakeSession]);

  const activeRoute =
    route.name === "projectDetail"
      ? "workbench"
      : route.name === "intakePackage" || route.name === "intakeCaseReview"
        ? "intake"
        : route.name;

  return (
    <AppShell activeRoute={activeRoute}>
      {route.name === "projects" && (
        <ProjectListPage
          onContinueDraft={async (draft) => {
            const detail = await getIntakePackageDetail(draft.package_id);
            setIntakeSession({
              packageImport: {
                package_id: detail.package_id,
                source_type: detail.source_type,
                package_status: detail.package_status,
                source_original_name: detail.source_original_name,
                subject: detail.subject,
                sender_name: detail.sender_name,
                sender_email: detail.sender_email,
                received_at: detail.received_at,
                asset_count: detail.asset_count,
                candidate_count: detail.candidate_count,
                next_action: draft.current_step === "precheck"
                  ? "review_selected_application_form"
                  : "review_application_form_candidates",
                assets: detail.assets
              },
              selectedAssetId: draft.selected_form_asset_id ?? null,
              selectedWordAssetId: draft.selected_form_asset_id ?? null,
              selectedPrecheckCaseId: draft.active_case_id ?? null,
              sourceMode: draftSourceMode(draft),
              directWordName: draft.source_type === "direct_application_form" ? draft.source_name : null
            });
            navigate("/intake");
          }}
          onNewProject={() => navigate("/intake")}
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
        <ProjectWorkbenchPage projectId={route.projectId} onBack={() => navigate("/projects")} />
      )}
      {route.name === "settings" && <SettingsPage />}
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
