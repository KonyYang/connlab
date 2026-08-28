import { useRef, useState } from "react";
import {
  exportMatrixEditorLiveXlsx,
  previewMatrixEditorLiveXlsxPublication,
  publishMatrixEditorLiveXlsx,
  type BlobDownloadResponse,
  type MatrixEditorLiveXlsxExportRequest,
  type MatrixEditorLiveXlsxPublicationPreview,
  type MatrixEditorLiveXlsxPublicationRequest,
  type MatrixEditorLiveXlsxPublicationResult,
} from "../../api/client";

type MatrixXlsxExportApis = {
  download: (projectId: string, request: MatrixEditorLiveXlsxExportRequest) => Promise<BlobDownloadResponse>;
  preview: (projectId: string, request: MatrixEditorLiveXlsxExportRequest) => Promise<MatrixEditorLiveXlsxPublicationPreview>;
  publish: (projectId: string, request: MatrixEditorLiveXlsxPublicationRequest) => Promise<MatrixEditorLiveXlsxPublicationResult>;
};

const defaultApis: MatrixXlsxExportApis = {
  download: (projectId, request) => exportMatrixEditorLiveXlsx(projectId, request),
  preview: (projectId, request) =>
    previewMatrixEditorLiveXlsxPublication(projectId, request),
  publish: (projectId, request) => publishMatrixEditorLiveXlsx(projectId, request),
};

export function useMatrixEditorXlsxExport(
  projectId: string,
  apis: MatrixXlsxExportApis = defaultApis
) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [conflict, setConflict] = useState<MatrixEditorLiveXlsxPublicationPreview | null>(null);
  const conflictRequestRef = useRef<MatrixEditorLiveXlsxExportRequest | null>(null);

  const publish = async (
    request: MatrixEditorLiveXlsxExportRequest,
    previewToken: string,
    conflictAction: "none" | "archive" | "recycle"
  ): Promise<void> => {
    const response = await apis.publish(projectId, {
      ...request,
      preview_token: previewToken,
      conflict_action: conflictAction,
    });
    setConflict(null);
    conflictRequestRef.current = null;
    setMessage(
      conflictAction === "archive"
        ? `Saved ${response.file_name}; archived the previous file in History.`
        : conflictAction === "recycle"
          ? `Saved ${response.file_name}; moved the previous file to Recycle Bin.`
          : `Saved ${response.file_name} to Source Book.`
    );
  };

  const downloadDraft = async (request: MatrixEditorLiveXlsxExportRequest): Promise<void> => {
    const response = await apis.download(projectId, request);
    const url = window.URL.createObjectURL(response.blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = response.fileName ?? "Matrix Draft.xlsx";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(url);
    setMessage("Matrix Draft downloaded.");
  };

  const exportSnapshot = async (
    request: MatrixEditorLiveXlsxExportRequest
  ): Promise<void> => {
    if (busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    setConflict(null);
    conflictRequestRef.current = null;
    try {
      const preview = await apis.preview(projectId, request);
      if (preview.mode === "download") {
        await downloadDraft(request);
      } else if (preview.status === "conflict") {
        conflictRequestRef.current = request;
        setConflict(preview);
      } else if (preview.status === "ready") {
        await publish(request, preview.preview_token, "none");
      } else {
        throw new Error(preview.blockers[0] ?? "Formal Matrix publication is blocked.");
      }
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message.trim()
          ? caught.message
          : "Matrix export failed."
      );
    } finally {
      setBusy(false);
    }
  };

  const resolveConflict = async (action: "archive" | "recycle"): Promise<void> => {
    const request = conflictRequestRef.current;
    if (busy || !conflict || !request) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await publish(request, conflict.preview_token, action);
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message.trim()
          ? caught.message
          : "Matrix export failed."
      );
    } finally {
      setBusy(false);
    }
  };

  const cancelConflict = (): void => {
    setConflict(null);
    conflictRequestRef.current = null;
    setMessage("Matrix replacement cancelled.");
  };

  return { busy, error, message, conflict, exportSnapshot, resolveConflict, cancelConflict };
}
