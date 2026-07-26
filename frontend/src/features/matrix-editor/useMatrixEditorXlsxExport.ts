import { useState } from "react";
import {
  exportMatrixEditorLiveXlsx,
  type BlobDownloadResponse,
  type MatrixEditorLiveXlsxExportRequest,
} from "../../api/client";

type ExportApi = (
  projectId: string,
  request: MatrixEditorLiveXlsxExportRequest
) => Promise<BlobDownloadResponse>;

export function useMatrixEditorXlsxExport(
  projectId: string,
  api?: ExportApi
) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const exportSnapshot = async (
    request: MatrixEditorLiveXlsxExportRequest
  ): Promise<void> => {
    if (busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const response = await (api ?? exportMatrixEditorLiveXlsx)(projectId, request);
      const url = window.URL.createObjectURL(response.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = response.fileName ?? "Matrix Draft.xlsx";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
      setMessage("Matrix export downloaded.");
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

  return { busy, error, message, exportSnapshot };
}
