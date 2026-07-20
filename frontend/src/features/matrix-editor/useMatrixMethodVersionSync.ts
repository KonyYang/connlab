import { useEffect, useState } from "react";
import {
  applyMatrixMethodVersionSync,
  previewMatrixMethodVersionSync,
  type MatrixMethodVersionSyncPreview,
} from "../../api/client";

type MatrixMethodVersionSyncInputs = {
  projectId: string;
  draftId: string | null;
  savedPayloadSignature: string | null;
  disabled: boolean;
  onApplied: (savedPayloadSignature: string) => void;
};

export function useMatrixMethodVersionSync({
  projectId,
  draftId,
  savedPayloadSignature,
  disabled,
  onApplied,
}: MatrixMethodVersionSyncInputs) {
  const [preview, setPreview] = useState<MatrixMethodVersionSyncPreview | null>(null);
  const [selectedRowIds, setSelectedRowIds] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState<"preview" | "apply" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setPreview(null);
    setSelectedRowIds(new Set());
    setError(null);
    setMessage(null);
  }, [projectId, draftId, savedPayloadSignature]);

  const previewMethods = async (): Promise<void> => {
    if (disabled || busy || !draftId || !savedPayloadSignature) return;
    setBusy("preview");
    setError(null);
    setMessage(null);
    try {
      const next = await previewMatrixMethodVersionSync(projectId, {
        project_matrix_draft_id: draftId,
        expected_saved_payload_signature: savedPayloadSignature,
      });
      setPreview(next);
      setSelectedRowIds(
        new Set(next.rows.filter((row) => row.selectable).map((row) => row.draft_row_id))
      );
    } catch (caught) {
      setPreview(null);
      setSelectedRowIds(new Set());
      setError((caught as Error).message || "Unable to check Method versions.");
    } finally {
      setBusy(null);
    }
  };

  const toggleRow = (rowId: string, checked: boolean): void => {
    setSelectedRowIds((current) => {
      const next = new Set(current);
      if (checked) next.add(rowId);
      else next.delete(rowId);
      return next;
    });
  };

  const applySelected = async (): Promise<void> => {
    if (
      disabled ||
      busy ||
      !draftId ||
      !savedPayloadSignature ||
      !preview ||
      selectedRowIds.size === 0
    ) return;
    setBusy("apply");
    setError(null);
    setMessage(null);
    try {
      const result = await applyMatrixMethodVersionSync(projectId, {
        project_matrix_draft_id: draftId,
        expected_saved_payload_signature: savedPayloadSignature,
        preview_fingerprint: preview.preview_fingerprint,
        selected_draft_row_ids: [...selectedRowIds],
        applied_by: "operator",
      });
      setMessage(`${result.applied_row_ids.length} Method update(s) applied.`);
      onApplied(result.saved_payload_signature);
    } catch (caught) {
      setError((caught as Error).message || "Unable to apply Method updates.");
    } finally {
      setBusy(null);
    }
  };

  return {
    preview,
    selectedRowIds,
    busy,
    error,
    message,
    previewMethods,
    toggleRow,
    applySelected,
  };
}
