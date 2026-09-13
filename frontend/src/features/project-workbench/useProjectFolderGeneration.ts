import { useEffect, useRef, useState } from "react";
import {
  getProjectFolderGeneration, startProjectFolderGeneration,
  resumeProjectFolderGeneration, type OfficialWorkspaceConflictStrategy, type ProjectFolderGeneration,
  previewProjectFolderGeneration, type ProjectFolderGenerationPreview,
} from "../../api/client";

const labels = ["Creating project folder", "Archiving request materials", "Checking project folder structure",
  "Updating Customer Feedback Form", "Updating Fee Form", "Updating Test Record", "Updating Test Status", "Updating Application Form"];
const connectionInterruptedMessage = "Connection interrupted. Generation may still be running; reconnecting to its saved progress.";
type GenerationError = {
  message: string;
  source: "action" | "connection" | "operation" | "completion";
};

export type FolderUpdateReview = {
  preview: ProjectFolderGenerationPreview;
  operationId: string | null;
  resumeRebuild: boolean;
};

export function useProjectFolderGeneration(projectId: string, onCompleted: () => Promise<void> | void, expectedContext: string | null) {
  const [operation, setOperation] = useState<ProjectFolderGeneration | null>(null);
  const [errorState, setErrorState] = useState<GenerationError | null>(null);
  const [starting, setStarting] = useState(false);
  const currentProject = useRef(projectId);
  currentProject.current = projectId;
  const completion = useRef(onCompleted);
  completion.current = onCompleted;
  const seenCompletion = useRef<string | null>(null);
  const requestId = useRef<string | null>(null);
  const alive = useRef(true);
  const requestSequence = useRef(0);
  const updating = useRef(false);
  const pollingStatus = useRef<string | null>(null);
  const schedulePoll = useRef<(delay: number) => void>(() => {});

  function accept(next: ProjectFolderGeneration | null) {
    if (!alive.current || currentProject.current !== projectId) return;
    pollingStatus.current = next?.status ?? null;
    schedulePoll.current(next && ["queued", "running"].includes(next.status) ? 1000 : 30000);
    setOperation(next);
    setErrorState(previous => {
      // The current user action is newer than any operation returned by polling.
      if (previous?.source === "action") return previous;
      if (next === null) {
        return previous?.source === "connection" ? null : previous;
      }
      return ["blocked", "interrupted"].includes(next.status)
        ? { message: next.message ?? "Project folder generation is blocked.", source: "operation" }
        : next.status === "completed" && previous?.source === "completion" ? previous : null;
    });
    if (next?.status === "completed" && seenCompletion.current !== next.operation_id) {
      seenCompletion.current = next.operation_id;
      requestId.current = null;
      const refresh = completion.current;
      void Promise.resolve().then(() => alive.current && currentProject.current === projectId ? refresh() : undefined).catch(() => {
        if (alive.current && currentProject.current === projectId) {
          setErrorState(previous => previous?.source === "action" ? previous : {
            message: "Generation completed, but the displayed folder status could not refresh. Refresh this page to reconnect.",
            source: "completion",
          });
        }
      });
    }
  }

  useEffect(() => {
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    let polling = false;
    const schedule = (delay: number) => {
      clearTimeout(timer);
      if (!disposed) timer = setTimeout(poll, delay);
    };
    schedulePoll.current = schedule;
    pollingStatus.current = null;
    alive.current = true;
    setOperation(null);
    setErrorState(null);
    setStarting(false);
    requestSequence.current += 1;
    seenCompletion.current = null;
    requestId.current = null;
    async function poll() {
      if (disposed || polling) return;
      polling = true;
      clearTimeout(timer);
      const sequence = requestSequence.current;
      let failed = false;
      try {
        const next = await getProjectFolderGeneration(projectId);
        if (!disposed && sequence === requestSequence.current) accept(next);
      } catch {
        failed = true;
        if (!disposed && sequence === requestSequence.current) {
          setErrorState(previous => previous && previous.source !== "connection"
            ? previous
            : { message: connectionInterruptedMessage, source: "connection" });
        }
      }
      polling = false;
      schedule(failed || ["queued", "running"].includes(pollingStatus.current ?? "") ? 1000 : 30000);
    }
    const refresh = () => { if (document.visibilityState !== "hidden") void poll(); };
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", refresh);
    void poll();
    return () => {
      disposed = true;
      alive.current = false;
      clearTimeout(timer);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [projectId]);

  async function start(strategy?: OfficialWorkspaceConflictStrategy, contextOverride?: string, replace = false) {
    if (starting) return;
    setStarting(true);
    setErrorState(null);
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
      if (alive.current && currentProject.current === projectId) {
        setErrorState({ message: (err as Error).message, source: "action" });
      }
    } finally {
      if (alive.current && currentProject.current === projectId) setStarting(false);
    }
  }

  async function update(
    strategy?: OfficialWorkspaceConflictStrategy,
    reviewed?: FolderUpdateReview,
    resumeRebuild = false,
  ): Promise<FolderUpdateReview | void> {
    if (updating.current || starting) return;
    updating.current = true;
    setStarting(true);
    setErrorState(null);
    const sequence = ++requestSequence.current;
    const isCurrent = () => alive.current && currentProject.current === projectId && sequence === requestSequence.current;
    try {
      const latest = await getProjectFolderGeneration(projectId);
      if (!isCurrent()) return;
      if (latest && ["queued", "running"].includes(latest.status)) { accept(latest); return; }
      const preview = await previewProjectFolderGeneration(projectId);
      if (!isCurrent()) return;
      const pending = latest && latest.status !== "completed" ? latest : null;
      const operationId = pending?.operation_id ?? null;
      if ((preview.recovery?.operation_id ?? null) !== operationId) {
        throw new Error("Project folder operation changed. Click Create project folder to check again.");
      }
      if (reviewed && (reviewed.operationId !== operationId || reviewed.preview.expected_context !== preview.expected_context)) {
        throw new Error("Project folder preview changed. Review the latest folder state before choosing again.");
      }
      const recovery = preview.recovery;
      if (strategy && !reviewed) return { preview, operationId, resumeRebuild: false };
      if (!strategy && pending && recovery?.inputs_match && resumeRebuild && reviewed?.resumeRebuild) {
        const next = await resumeProjectFolderGeneration(projectId, pending.operation_id);
        if (isCurrent()) accept(next);
        return;
      }
      if (pending && !pending.can_restart) {
        if (recovery?.inputs_match) {
          return { preview, operationId, resumeRebuild: true };
        }
        throw new Error("The previous publication needs safe recovery before inputs can change. No files were written.");
      }
      const workspace = preview.workspace_preview;
      if (preview.start_blockers?.length) throw new Error(preview.start_blockers.join(" "));
      if (workspace.status === "blocked" || (workspace.blockers.length && workspace.status !== "exists")) {
        throw new Error(workspace.blockers[0] ?? "Project folder needs review before updating.");
      }
      if (!strategy && ["exists", "completed"].includes(workspace.status)) {
        return { preview, operationId, resumeRebuild: false };
      }
      if (strategy && !reviewed) {
        return { preview, operationId, resumeRebuild: false };
      }
      if (strategy === "continue_existing") throw new Error("Choose backup and rebuild or delete and rebuild.");
      const selected = strategy;
      requestId.current ??= crypto.randomUUID();
      if (pending) requestId.current = crypto.randomUUID();
      const next = await startProjectFolderGeneration(projectId, {
        expected_context: preview.expected_context, request_id: requestId.current,
        conflict_strategy: selected,
        overwrite_confirmed: selected === "overwrite_rebuild",
        ...(pending ? { replaces_operation_id: pending.operation_id } : {}),
      });
      if (isCurrent()) accept(next);
    } catch (err) {
      if (isCurrent()) setErrorState({ message: (err as Error).message, source: "action" });
    } finally {
      updating.current = false;
      if (isCurrent()) setStarting(false);
    }
  }

  return { operation, error: errorState?.message ?? null, start, update,
    restart: (strategy?: OfficialWorkspaceConflictStrategy, context?: string) => start(strategy, context, true),
    busy: starting || operation?.status === "queued" || operation?.status === "running",
    canResume: operation?.status === "blocked" || operation?.status === "interrupted",
    canRestart: Boolean(operation?.can_restart && ["blocked", "interrupted"].includes(operation.status)),
    progressLabel: operation && ["queued", "running"].includes(operation.status) ? labels[operation.step] ?? "Completing project folder" : null,
  };
}
