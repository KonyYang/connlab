import { useState } from "react";
import {
  downloadLlcrCrRecordWorkbook,
  generateLlcrCrRecordWorkbook,
  previewLlcrCrRecordWorkbook,
  type LlcrCrRecordWorkbookGenerateResponse,
  type LlcrCrRecordWorkbookPreviewResponse,
  type LlcrCrRecordType,
} from "../../api/client";

export function useLlcrCrSpecializedRecordWorkbookModel(projectId: string, recordType: LlcrCrRecordType) {
  const [preview, setPreview] = useState<LlcrCrRecordWorkbookPreviewResponse | null>(null);
  const [generated, setGenerated] = useState<LlcrCrRecordWorkbookGenerateResponse | null>(null);
  const [busy, setBusy] = useState<"preview" | "generate" | "download" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const previewWorkbook = async (): Promise<void> => {
    if (busy) return;
    setBusy("preview");
    setError(null);
    setGenerated(null);
    try {
      setPreview(await previewLlcrCrRecordWorkbook(projectId, recordType));
    } catch {
      setPreview(null);
      setError(`Unable to preview the ${recordType.toUpperCase()} record workbook.`);
    } finally {
      setBusy(null);
    }
  };

  const generateWorkbook = async (): Promise<void> => {
    if (busy || preview?.status !== "ready" || !preview.preview_fingerprint) return;
    setBusy("generate");
    setError(null);
    try {
      setGenerated(
        await generateLlcrCrRecordWorkbook(projectId, {
          record_type: recordType,
          preview_fingerprint: preview.preview_fingerprint,
        })
      );
    } catch {
      setGenerated(null);
      setError("The confirmed Matrix or Point Profile changed. Preview again before generating.");
    } finally {
      setBusy(null);
    }
  };

  const downloadWorkbook = async (): Promise<void> => {
    if (busy || !generated) return;
    setBusy("download");
    setError(null);
    try {
      const result = await downloadLlcrCrRecordWorkbook(projectId, generated.artifact_id);
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.fileName ?? generated.file_name;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch {
      setError(`Unable to download the ${recordType.toUpperCase()} record workbook.`);
    } finally {
      setBusy(null);
    }
  };

  return {
    preview,
    generated,
    busy,
    error,
    canGenerate: preview?.status === "ready" && Boolean(preview.preview_fingerprint),
    previewWorkbook,
    generateWorkbook,
    downloadWorkbook,
  };
}
