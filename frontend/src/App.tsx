import { useEffect, useState, type ReactElement } from "react";
import { AppShell } from "./components/layout/AppShell";
import { IntakeInboxPage } from "./pages/IntakeInboxPage";
import { IntakeCaseReviewPage } from "./pages/IntakeCaseReviewPage";
import { IntakePackageDetailPage } from "./pages/IntakePackageDetailPage";
import { ProjectListPage } from "./pages/ProjectListPage";
import { ProjectWorkbenchPage } from "./pages/ProjectWorkbenchPage";
import "./styles.css";

type Route =
  | { name: "projects" }
  | { name: "intake" }
  | { name: "intakePackage"; packageId: string }
  | { name: "intakeCaseReview"; packageId: string }
  | { name: "projectDetail"; projectId: string }
  | { name: "notFound" };

function parseRoute(pathname: string): Route {
  if (pathname === "/" || pathname === "/projects") {
    return { name: "projects" };
  }

  if (pathname === "/intake") {
    return { name: "intake" };
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

export default function App(): ReactElement {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.pathname));

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const activeRoute =
    route.name === "projectDetail"
      ? "workbench"
      : route.name === "intakePackage" || route.name === "intakeCaseReview"
        ? "intake"
        : route.name;

  return (
    <AppShell activeRoute={activeRoute}>
      {route.name === "projects" && <ProjectListPage onOpenProject={(id) => navigate(`/projects/${encodeURIComponent(id)}`)} />}
      {route.name === "intake" && <IntakeInboxPage onOpenPackage={(id) => navigate(`/intake/${encodeURIComponent(id)}`)} />}
      {route.name === "intakePackage" && (
        <IntakePackageDetailPage
          packageId={route.packageId}
          onBack={() => navigate("/intake")}
          onOpenCaseReview={() => navigate(`/intake/${encodeURIComponent(route.packageId)}/case-review`)}
        />
      )}
      {route.name === "intakeCaseReview" && (
        <IntakeCaseReviewPage
          packageId={route.packageId}
          onBack={() => navigate(`/intake/${encodeURIComponent(route.packageId)}`)}
        />
      )}
      {route.name === "projectDetail" && (
        <ProjectWorkbenchPage projectId={route.projectId} onBack={() => navigate("/projects")} />
      )}
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
