import { useEffect, useState, type ReactElement } from "react";
import { AppShell } from "./components/layout/AppShell";
import { ProjectListPage } from "./pages/ProjectListPage";
import { ProjectWorkbenchPage } from "./pages/ProjectWorkbenchPage";
import "./styles.css";

type Route =
  | { name: "projects" }
  | { name: "projectDetail"; projectId: string }
  | { name: "notFound" };

function parseRoute(pathname: string): Route {
  if (pathname === "/" || pathname === "/projects") {
    return { name: "projects" };
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

  const activeRoute = route.name === "projectDetail" ? "workbench" : route.name;

  return (
    <AppShell activeRoute={activeRoute}>
      {route.name === "projects" && <ProjectListPage onOpenProject={(id) => navigate(`/projects/${encodeURIComponent(id)}`)} />}
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
