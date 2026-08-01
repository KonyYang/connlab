import { useCallback, useRef, useState } from "react";
import {
  listExternalResources,
  saveExternalResource,
  validateExternalResource,
  type MatrixImportStandardVersionActionRequiredDetail,
  type MatrixImportStandardVersionUnavailableAction,
} from "../../api/client";
import {
  hasDesktopPathPickerBridge,
  pickExternalResourcePathFromDesktop,
} from "../../desktop/pathPickerBridge";

type RetryImport = (action: MatrixImportStandardVersionUnavailableAction) => Promise<void>;

export function useMatrixImportStandardVersionChoice() {
  const [detail, setDetail] = useState<MatrixImportStandardVersionActionRequiredDetail | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const retryRef = useRef<RetryImport | null>(null);

  const close = useCallback((): void => {
    if (busy) {
      return;
    }
    setDetail(null);
    setError(null);
    retryRef.current = null;
  }, [busy]);

  const open = useCallback(
    (nextDetail: MatrixImportStandardVersionActionRequiredDetail, retry: RetryImport): void => {
      setDetail(nextDetail);
      setError(null);
      retryRef.current = retry;
    },
    []
  );

  const chooseFile = useCallback(async (): Promise<void> => {
    if (busy || !retryRef.current) {
      return;
    }
    if (!hasDesktopPathPickerBridge()) {
      setError("File selection is unavailable. Use Skip for now or configure the path in Settings.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const path = await pickExternalResourcePathFromDesktop("standard_record_excel");
      if (!path) {
        return;
      }
      const resources = await listExternalResources();
      const existing = resources.find(
        (resource) => resource.resource_type === "standard_record_excel"
      );
      await saveExternalResource("standard_record_excel", {
        path,
        active: true,
        ...(existing ? { worksheet_name: existing.worksheet_name } : {}),
      });
      const validated = await validateExternalResource("standard_record_excel");
      if (validated.validation_status !== "valid") {
        setError(
          validated.validation_failure_reason ??
            "The selected Standard version file could not be validated."
        );
        return;
      }
      await retryRef.current("prompt_if_unavailable");
      setDetail(null);
      retryRef.current = null;
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "The selected Standard version file could not be validated."
      );
    } finally {
      setBusy(false);
    }
  }, [busy]);

  const skip = useCallback(async (): Promise<void> => {
    if (busy || !retryRef.current) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await retryRef.current("preserve_imported_methods");
      setDetail(null);
      retryRef.current = null;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Matrix import could not be completed.");
    } finally {
      setBusy(false);
    }
  }, [busy]);

  return {
    busy,
    close,
    detail,
    error,
    isOpen: detail !== null,
    open,
    chooseFile,
    skip,
  };
}
