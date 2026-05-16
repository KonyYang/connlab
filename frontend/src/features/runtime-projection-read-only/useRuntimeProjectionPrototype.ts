import { useEffect, useMemo, useState } from "react";
import {
  getRuntimeProjectionReadOnlySnapshot,
  type RuntimeProjectionSnapshotRequest,
  type RuntimeProjectionSnapshotResponse
} from "../../api/client";

type RuntimeProjectionPrototypeState = {
  loading: boolean;
  error: string | null;
  snapshot: RuntimeProjectionSnapshotResponse | null;
  selectedTokenReference: string | null;
  setSelectedTokenReference: (value: string | null) => void;
  reload: () => Promise<void>;
};

function buildPrototypeRequest(
  selectedTokenReference: string | null
): RuntimeProjectionSnapshotRequest {
  return {
    project_reference: "P-RT-PROTOTYPE",
    matrix_reference: "M-RT-PROTOTYPE",
    selected_token_reference: selectedTokenReference,
    rows: [
      {
        group_identity: "G1",
        group_label: "Group 1",
        row_context: {
          test_item_label: "LLCR",
          section: "6.1",
          method: "EIA-364-23E",
          condition: "20mV max",
          requirement: "Initial <= 0.40mO"
        },
        raw_step_token_value: "2,3(a)",
        projection_state: {
          lifecycle: "in_progress",
          evidence: "missing",
          report_sync: "stale",
          stale: "stale",
          attention: "p1"
        }
      },
      {
        group_identity: "G2",
        group_label: "Group 2",
        row_context: {
          test_item_label: "CR",
          section: "6.2",
          method: "EIA-364-06",
          condition: "1A max",
          requirement: "See spec"
        },
        raw_step_token_value: "2, A"
      }
    ]
  };
}

export function useRuntimeProjectionPrototype(): RuntimeProjectionPrototypeState {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<RuntimeProjectionSnapshotResponse | null>(null);
  const [selectedTokenReference, setSelectedTokenReference] = useState<string | null>(null);

  const request = useMemo(
    () => buildPrototypeRequest(selectedTokenReference),
    [selectedTokenReference]
  );

  const reload = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const response = await getRuntimeProjectionReadOnlySnapshot(request);
      setSnapshot(response);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to load runtime projection snapshot.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void reload();
  }, [request]);

  return {
    loading,
    error,
    snapshot,
    selectedTokenReference,
    setSelectedTokenReference,
    reload
  };
}
