import { useState } from "react";
import {
  generateMatrixEditorLlcrCrRecordDraftDownload,
  type LlcrCrRecordType,
  type MatrixEditorTestRecordDraftRequest,
} from "../../api/client";

export function useLlcrCrSpecializedRecordWorkbookModel(
  projectId: string,
  recordType: LlcrCrRecordType,
  draftRequest: MatrixEditorTestRecordDraftRequest,
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
      const result = await generateMatrixEditorLlcrCrRecordDraftDownload(projectId, {
        ...draftRequest,
        record_type: recordType,
      });
      const fileName = result.fileName
        ?? `${projectId}_${recordType}_record_Preview_Unconfirmed_Matrix_draft.xlsx`;
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setMessage(`${fileName} downloaded.`);
    } catch (error) {
      setError(error instanceof Error && error.message.trim()
        ? error.message
        : `Unable to generate the ${recordType.toUpperCase()} draft file. Review the current Matrix and Test points, then try again.`);
    } finally {
      setBusy(false);
    }
  };

  return { busy, error, message, downloadWorkbook };
}
