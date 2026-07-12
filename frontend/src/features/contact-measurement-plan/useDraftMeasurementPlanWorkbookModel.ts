import { useEffect, useState } from "react";
import {
  ApiRequestError,
  fetchLatestDraftMeasurementPlanWorkbook,
  generateDraftMeasurementPlanWorkbook,
  previewDraftMeasurementPlanWorkbook,
  type DraftMeasurementPlanWorkbookArtifact,
  type DraftMeasurementPlanWorkbookPreview,
} from "../../api/client";

type Args = { projectId: string; revisionId: string | null };

export function useDraftMeasurementPlanWorkbookModel({ projectId, revisionId }: Args) {
  const [preview, setPreview] = useState<DraftMeasurementPlanWorkbookPreview | null>(null);
  const [artifact, setArtifact] = useState<DraftMeasurementPlanWorkbookArtifact | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchLatestDraftMeasurementPlanWorkbook(projectId).then(setArtifact).catch(() => setArtifact(null));
  }, [projectId]);

  useEffect(() => {
    setPreview(null);
    setError(null);
  }, [revisionId]);

  async function previewDraft(): Promise<void> {
    if (!revisionId || busy) return;
    setBusy(true);
    setError(null);
    setArtifact(null);
    try {
      setPreview(await previewDraftMeasurementPlanWorkbook(projectId, revisionId));
    } catch (cause) {
      setPreview(null);
      setError(messageFor(cause));
    } finally {
      setBusy(false);
    }
  }

  async function generateDraft(): Promise<void> {
    if (!revisionId || !preview?.preview_fingerprint || !preview.generate_allowed || busy) return;
    setBusy(true);
    setError(null);
    try {
      setArtifact(await generateDraftMeasurementPlanWorkbook(projectId, revisionId, preview.preview_fingerprint));
    } catch (cause) {
      setError(messageFor(cause));
      setPreview(null);
    } finally {
      setBusy(false);
    }
  }

  return { preview, artifact, busy, error, previewDraft, generateDraft };
}

function messageFor(cause: unknown): string {
  if (cause instanceof ApiRequestError && cause.status === 409) {
    return "Measurement plan changed. Preview again before generating.";
  }
  return cause instanceof Error ? cause.message : "Unable to prepare draft workbook.";
}
