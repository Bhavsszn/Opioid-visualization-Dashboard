import { useCallback, useEffect, useState } from "react";
import { pipelineService } from "../services/pipelineService";
import type { PipelineSummary } from "../types/apiTypes";

export function usePipeline() {
  const [summary, setSummary] = useState<PipelineSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await pipelineService.getPipelineSummary();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load pipeline summary");
      setSummary(pipelineService.emptySummary());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { summary, loading, error, refetch: load };
}
