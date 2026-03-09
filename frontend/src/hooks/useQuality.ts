import { useCallback, useEffect, useState } from "react";
import { qualityService } from "../services/qualityService";
import type { QualityReport } from "../types/apiTypes";

export function useQuality() {
  const [report, setReport] = useState<QualityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await qualityService.getQualityStatus();
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quality report");
      setReport(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { report, loading, error, refetch: load };
}
