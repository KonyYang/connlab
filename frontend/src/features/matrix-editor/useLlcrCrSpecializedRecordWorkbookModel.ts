import { useState } from "react";
import {
  generateMatrixEditorLlcrCrRecordDraftDownload,
  previewMatrixEditorLlcrCrRecordPublication,
  publishMatrixEditorLlcrCrRecord,
  type LlcrCrRecordType,
  type MatrixEditorLlcrCrRecordPublicationPreview,
  type MatrixEditorTestRecordDraftRequest,
} from "../../api/client";

export function useLlcrCrSpecializedRecordWorkbookModel(
  projectId: string,
  recordType: LlcrCrRecordType,
  getDraftRequest: () => MatrixEditorTestRecordDraftRequest,
  matrixHasPendingChanges = false,
) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState<MatrixEditorLlcrCrRecordPublicationPreview | null>(null);
  const currentRequest = () => ({
    ...getDraftRequest(), record_type: recordType,
    ...(matrixHasPendingChanges ? { matrix_has_pending_changes: true } : {}),
  });

  const downloadWorkbook = async (): Promise<void> => {
    if (busy) return;
    setBusy(true);
    setError(null);
    setMessage(null);
    setPending(null);
    try {
      const request = currentRequest();
      const preview = await previewMatrixEditorLlcrCrRecordPublication(projectId, request);
      if (preview.status === "blocked") {
        throw new Error(preview.blockers[0] ?? `${recordType.toUpperCase()} form cannot be generated.`);
      }
      if (preview.mode === "download" || preview.status === "conflict") {
        setPending(preview);
        return;
      }
      const result = await publishMatrixEditorLlcrCrRecord(projectId, {
        ...request, preview_token: preview.preview_token, conflict_action: "none",
      });
      setMessage(`Saved ${result.file_name} to Test results.`);
    } catch (error) {
      setError(_message(error, recordType));
    } finally {
      setBusy(false);
    }
  };

  const confirmDownload = async (): Promise<void> => {
    if (busy || pending?.mode !== "download") return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await generateMatrixEditorLlcrCrRecordDraftDownload(projectId, {
        ...currentRequest(), preview_token: pending.preview_token,
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
      setPending(null);
      setMessage(`${fileName} downloaded.`);
    } catch (error) {
      setPending(null);
      setError(_message(error, recordType));
    } finally {
      setBusy(false);
    }
  };

  const archiveAndPublish = async (): Promise<void> => {
    if (busy || pending?.mode !== "official" || pending.status !== "conflict") return;
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await publishMatrixEditorLlcrCrRecord(projectId, {
        ...currentRequest(),
        preview_token: pending.preview_token, conflict_action: "archive",
      });
      setPending(null);
      setMessage(result.archive_path
        ? `Saved ${result.file_name} to Test results; archived the previous file in History.`
        : `Saved ${result.file_name} to Test results.`);
    } catch (error) {
      setPending(null);
      setError(_message(error, recordType));
    } finally {
      setBusy(false);
    }
  };

  return {
    busy, error, message, pending, downloadWorkbook, confirmDownload,
    archiveAndPublish, cancel: () => setPending(null),
  };
}

function _message(error: unknown, recordType: LlcrCrRecordType): string {
  return error instanceof Error && error.message.trim()
    ? error.message
    : `Unable to generate the ${recordType.toUpperCase()} file. Review the current Matrix and Test points, then try again.`;
}
