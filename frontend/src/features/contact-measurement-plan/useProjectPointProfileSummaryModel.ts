import { useEffect, useState } from "react";
import { fetchProjectPointProfileSummary, type ProjectPointProfileSummary } from "../../api/client";

export function useProjectPointProfileSummaryModel(projectId: string) {
  const [summary, setSummary] = useState<ProjectPointProfileSummary | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let current = true;
    setLoading(true);
    void fetchProjectPointProfileSummary(projectId)
      .then((next) => { if (current) setSummary(next); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [projectId]);
  return { summary, loading };
}
