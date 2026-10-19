import { useEffect, useRef, useState } from "react";
import {
  fetchReportUpdateSource, updateReportDraftLlcr, updateReportDraftEquipment,
  selectReportUpdateSource, downloadReportWorkingDraft,
  type CurrentReport, type ReportSectionUpdateResult, type ReportDraftEquipmentResult, type BlobDownloadResponse,
} from "../../api/client";

type EquipmentInput = { file?: File; referencesText?: string };
type Action = { kind: "llcr"; dataset: string } | { kind: "equipment"; input?: EquipmentInput };
type Callbacks = {
  save: (response: BlobDownloadResponse) => void;
  onUpdated: () => unknown;
  onEquipmentRequired: () => void;
  onEquipmentCompleted: (result: Extract<ReportDraftEquipmentResult, { status: "completed" }>) => void;
};

export function useReportDraftUpdates(projectId: string, callbacks: Callbacks) {
  const [source, setSource] = useState<CurrentReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [action, setAction] = useState<"llcr" | "equipment" | "select" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [selectOpen, setSelectOpen] = useState(false);
  const [lastResult, setLastResult] = useState<ReportSectionUpdateResult | null>(null);
  const generation = useRef(0);
  const identity = useRef(projectId);
  identity.current = projectId;
  const sourceRef = useRef<CurrentReport | null>(null);
  const resultRef = useRef<ReportSectionUpdateResult | null>(null);
  const active = useRef(false);
  const pending = useRef<Action | null>(null);
  const events = useRef(callbacks);
  events.current = callbacks;
  const valid = (token: number) => token === generation.current && identity.current === projectId;

  function pin(result: ReportSectionUpdateResult) {
    resultRef.current = result;
    setLastResult(result);
    const next: CurrentReport = { status: "ready", mode: "download_draft", file_name: result.file_name,
      file_sha256: result.current_sha256, report_revision_id: null, draft_revision_id: result.draft_revision_id,
      folder_path: null, official_folder_path: null, can_publish_to_official: false, download_url: result.download_url ?? null };
    sourceRef.current = next;
    setSource(next);
  }

  async function refresh() {
    const token = generation.current;
    try {
      const next = await fetchReportUpdateSource(projectId);
      if (valid(token)) { sourceRef.current = next; setSource(next); setError(null); }
      return next;
    } catch (reason) {
      if (valid(token)) setError("Unable to check the draft source. Retry source status.");
      throw reason;
    }
  }

  useEffect(() => {
    const token = ++generation.current;
    sourceRef.current = null; resultRef.current = null; pending.current = null; active.current = false;
    setSource(null); setLastResult(null); setBusy(false); setError(null); setDownloadError(null); setSelectOpen(false);
    void fetchReportUpdateSource(projectId).then(next => {
      if (!valid(token)) return;
      sourceRef.current = next; setSource(next);
      if (next.mode === "download_draft" && next.draft_revision_id && next.file_name && next.file_sha256) {
        const retained: ReportSectionUpdateResult = { project_id: projectId, mode: "download_draft", file_name: next.file_name,
          current_sha256: next.file_sha256, draft_revision_id: next.draft_revision_id, changed: false, archive_path: null };
        resultRef.current = retained; setLastResult(retained);
      }
    }).catch(() => { if (valid(token)) setError("Unable to check the draft source. Retry source status."); });
    return () => { ++generation.current; };
  }, [projectId]);

  async function save(result: ReportSectionUpdateResult, token: number) {
    if (!result.draft_revision_id) return;
    try {
      const response = await downloadReportWorkingDraft(projectId, result.draft_revision_id);
      if (valid(token)) { events.current.save(response); setDownloadError(null); }
    } catch {
      if (valid(token)) setDownloadError("Download failed. The updated draft is retained; retry its download.");
    }
  }

  async function run(request: Action) {
    if (active.current) return;
    active.current = true;
    const token = generation.current;
    setBusy(true); setAction(request.kind); setError(null);
    try {
      const current = sourceRef.current ?? await refresh();
      if (!valid(token)) return;
      if (current.status === "ambiguous" || current.mode === "official") {
        throw new Error("The official report state changed. Reload before updating it.");
      }
      if (current.status !== "ready" || !current.file_sha256) {
        pending.current = request; setSelectOpen(true); return;
      }
      const result = request.kind === "llcr"
        ? await updateReportDraftLlcr(projectId, request.dataset, current.file_sha256)
        : await updateReportDraftEquipment(projectId, current.file_sha256, request.input);
      if (!valid(token)) return;
      if ("status" in result && result.status === "source_required") { events.current.onEquipmentRequired(); return; }
      pin(result as ReportSectionUpdateResult);
      if (request.kind === "equipment") events.current.onEquipmentCompleted(result as Extract<ReportDraftEquipmentResult, { status: "completed" }>);
      try { await events.current.onUpdated(); }
      catch { if (valid(token)) setError("The draft was updated. Reload to refresh report status."); }
      if (valid(token)) await save(result as ReportSectionUpdateResult, token);
    } catch (reason) {
      if (valid(token)) setError(reason instanceof Error ? reason.message : "The draft could not be updated. Check its source and retry.");
    } finally {
      if (valid(token)) { active.current = false; setBusy(false); }
    }
  }

  async function select(file: File) {
    if (active.current) return;
    if (!file.name.toLowerCase().endsWith(".docx")) { setError("Choose an Internal Report .docx file."); return; }
    active.current = true;
    const token = generation.current;
    setBusy(true); setAction("select"); setError(null);
    let nextAction: Action | null = null;
    try {
      const result = await selectReportUpdateSource(projectId, file, sourceRef.current?.file_sha256 ?? undefined);
      if (!valid(token)) return;
      pin(result); setSelectOpen(false);
      nextAction = pending.current; pending.current = null;
      await events.current.onUpdated();
    } catch (reason) {
      if (valid(token)) setError(reason instanceof Error ? reason.message : "Select this project's Internal Report.");
    } finally {
      if (valid(token)) { active.current = false; setBusy(false); }
    }
    if (valid(token) && nextAction) await run(nextAction);
  }

  async function download() {
    if (active.current || !resultRef.current) return;
    const token = generation.current;
    active.current = true; setBusy(true);
    try { await save(resultRef.current, token); }
    finally { if (valid(token)) { active.current = false; setBusy(false); } }
  }

  return { source, busy, action, error, downloadError, lastResult, selectOpen, refresh, select, download,
    updateLlcr: (dataset: string) => run({ kind: "llcr", dataset }),
    updateEquipment: (input?: EquipmentInput) => run({ kind: "equipment", input }),
    choose: () => { pending.current = null; setError(null); setSelectOpen(true); },
    close: () => { if (!active.current) { pending.current = null; setSelectOpen(false); setError(null); } },
  };
}
