import { useState } from "react";
import {
  downloadLlcrCrRecordWorkbook,
  generateLlcrCrRecordWorkbook,
  previewLlcrCrRecordWorkbook,
  type LlcrCrRecordType,
  type LlcrCrRecordWorkbookPreviewResponse,
} from "../../api/client";

export function useLlcrCrSpecializedRecordWorkbookModel(
  projectId: string,
  recordType: LlcrCrRecordType,
) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const downloadWorkbook = async (): Promise<void> => {
    if (busy) return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const preview = await previewLlcrCrRecordWorkbook(projectId, recordType);
      if (preview.status !== "ready" || !preview.preview_fingerprint) {
        setError(previewFailureMessage(recordType, preview));
        return;
      }
      const generated = await generateLlcrCrRecordWorkbook(projectId, {
        record_type: recordType,
        preview_fingerprint: preview.preview_fingerprint,
      });
      const result = await downloadLlcrCrRecordWorkbook(projectId, generated.artifact_id);
      const fileName = result.fileName ?? generated.file_name;
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setMessage(`${fileName} downloaded.`);
    } catch {
      setError(
        `Unable to generate the ${recordType.toUpperCase()} file. Confirm the Matrix and Test points, then try again.`,
      );
    } finally {
      setBusy(false);
    }
  };

  return { busy, error, message, downloadWorkbook };
}

function previewFailureMessage(
  recordType: LlcrCrRecordType,
  preview: LlcrCrRecordWorkbookPreviewResponse,
): string {
  const label = recordType.toUpperCase();
  if (preview.status === "empty") {
    return `${label} is not required by the confirmed Matrix.`;
  }
  return preview.diagnostics.map((item) => item.message).join(" ")
    || `Confirm the Matrix and Test points before downloading ${label}.`;
}
