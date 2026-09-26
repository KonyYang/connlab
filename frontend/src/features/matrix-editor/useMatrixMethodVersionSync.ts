import { useEffect, useRef, useState } from "react";
import {
  suggestMatrixMethodVersions,
  type MatrixMethodVersionSuggestion,
} from "../../api/client";

type MethodRow = { row_id: string; method: string };
type MethodUpdate = Pick<MatrixMethodVersionSuggestion, "row_id" | "current_method" | "proposed_method">;

type MatrixMethodVersionSyncInputs = {
  projectId: string;
  rows: MethodRow[];
  currentSignature: string;
  disabled: boolean;
  onApply: (updates: MethodUpdate[]) => void;
};

export function useMatrixMethodVersionSync({
  projectId,
  rows,
  currentSignature,
  disabled,
  onApply,
}: MatrixMethodVersionSyncInputs) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const latestSignatureRef = useRef(currentSignature);
  const latestProjectIdRef = useRef(projectId);
  const busyRef = useRef(false);
  latestSignatureRef.current = currentSignature;
  latestProjectIdRef.current = projectId;

  useEffect(() => {
    setError(null);
    setMessage(null);
  }, [projectId]);

  const syncMethods = async (): Promise<void> => {
    if (disabled || busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setError(null);
    setMessage(null);
    const requestedSignature = currentSignature;
    const requestedRows = rows.map((row) => ({ ...row }));
    try {
      const result = await suggestMatrixMethodVersions(projectId, { rows: requestedRows });
      if (latestProjectIdRef.current !== projectId || latestSignatureRef.current !== requestedSignature) {
        throw new Error("Matrix changed while checking Method versions. Run the update again.");
      }
      const originalMethods = new Map(requestedRows.map((row) => [row.row_id, row.method]));
      const updates = result.rows.filter((row) => row.selectable && row.proposed_method);
      if (updates.some((row) => originalMethods.get(row.row_id) !== row.current_method)) {
        throw new Error("Matrix changed while checking Method versions. Run the update again.");
      }
      if (updates.length === 0) {
        setMessage("No applicable Method version updates found.");
        return;
      }
      onApply(updates.map(({ row_id, current_method, proposed_method }) => ({
        row_id, current_method, proposed_method,
      })));
      setMessage(`${updates.length} Method version${updates.length === 1 ? "" : "s"} updated in the Matrix draft. Confirm Matrix when ready.`);
    } catch (caught) {
      setError((caught as Error).message || "Unable to update Method versions.");
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };

  return { busy, error, message, syncMethods };
}
