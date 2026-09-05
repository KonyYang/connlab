import { useEffect, useRef, useState } from "react";
import {
  getProjectFolderGeneration, startProjectFolderGeneration,
  resumeProjectFolderGeneration, type OfficialWorkspaceConflictStrategy, type ProjectFolderGeneration,
} from "../../api/client";

const labels = ["Creating project folder", "Archiving request materials", "Checking project folder structure",
  "Updating Customer Feedback Form", "Updating Fee Form", "Updating Test Record", "Updating Test Status", "Updating Application Form"];

export function useProjectFolderGeneration(projectId: string, onCompleted: () => Promise<void> | void, expectedContext: string | null) {
  const [operation, setOperation] = useState<ProjectFolderGeneration | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const currentProject = useRef(projectId);
  currentProject.current = projectId;
  const completion = useRef(onCompleted);
  completion.current = onCompleted;
  const seenCompletion = useRef<string | null>(null);
  const requestId = useRef<string | null>(null);
  const alive = useRef(true);
  const requestSequence = useRef(0);

  function accept(next: ProjectFolderGeneration | null) {
    if (!alive.current || currentProject.current !== projectId) return;
    setOperation(next);
    setError(previous => next && ["blocked", "interrupted"].includes(next.status) ? next.message
      : next?.status === "completed" && previous?.startsWith("Generation completed, but") ? previous : null);
    if (next?.status === "completed" && seenCompletion.current !== next.operation_id) {
      seenCompletion.current = next.operation_id;
      requestId.current = null;
      const refresh = completion.current;
      void Promise.resolve().then(() => alive.current && currentProject.current === projectId ? refresh() : undefined).catch(() => {
        if (alive.current && currentProject.current === projectId) {
          setError("Generation completed, but the displayed folder status could not refresh. Refresh this page to reconnect.");
        }
      });
    }
  }

  useEffect(() => {
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    alive.current = true;
    setOperation(null);
    setError(null);
    setStarting(false);
    requestSequence.current += 1;
    seenCompletion.current = null;
    requestId.current = null;
    async function poll() {
      const sequence = requestSequence.current;
      try {
        const next = await getProjectFolderGeneration(projectId);
        if (!disposed && sequence === requestSequence.current) accept(next);
      } catch {
        if (!disposed) setError("Connection interrupted. Generation may still be running; reconnecting to its saved progress.");
      }
      if (!disposed) timer = setTimeout(poll, 1000);
    }
    void poll();
    return () => { disposed = true; alive.current = false; clearTimeout(timer); };
  }, [projectId]);

  async function start(strategy?: OfficialWorkspaceConflictStrategy, contextOverride?: string, replace = false) {
    if (starting) return;
    setStarting(true);
    requestSequence.current += 1;
    try {
      // Re-read before dispatch so an earlier lost response cannot create another operation.
      const latest = await getProjectFolderGeneration(projectId);
      if (!alive.current || currentProject.current !== projectId) return;
      if (replace && (!latest?.can_restart || !["blocked", "interrupted"].includes(latest.status))) {
        throw new Error("The previous operation needs safe recovery before a new generation can start.");
      }
      if (latest && latest.status !== "completed" && !replace) {
        accept(["blocked", "interrupted"].includes(latest.status)
          ? await resumeProjectFolderGeneration(projectId, latest.operation_id) : latest);
      } else {
        const context = contextOverride ?? expectedContext;
        if (!context) throw new Error("Refresh the project folder preview before starting generation.");
        if (replace) requestId.current = crypto.randomUUID();
        requestId.current ??= crypto.randomUUID();
        accept(await startProjectFolderGeneration(projectId, {
          expected_context: context, request_id: requestId.current, conflict_strategy: strategy,
          ...(replace ? { replaces_operation_id: latest!.operation_id } : {}),
        }));
      }
    } catch (err) {
      if (alive.current && currentProject.current === projectId) setError((err as Error).message);
    } finally {
      if (alive.current && currentProject.current === projectId) setStarting(false);
    }
  }

  return { operation, error, start,
    restart: (strategy?: OfficialWorkspaceConflictStrategy, context?: string) => start(strategy, context, true),
    busy: starting || operation?.status === "queued" || operation?.status === "running",
    canResume: operation?.status === "blocked" || operation?.status === "interrupted",
    canRestart: Boolean(operation?.can_restart && ["blocked", "interrupted"].includes(operation.status)),
    progressLabel: operation && ["queued", "running"].includes(operation.status) ? labels[operation.step] ?? "Completing project folder" : null,
  };
}
