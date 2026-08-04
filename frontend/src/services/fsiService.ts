import { apiClient } from "@/services/apiClient";
import type { FsiEntry, FsiResultRow, FsiSummary } from "@/types/schedules";

export interface FsiCalculateResponse {
  session_id: string | null;
  rows: FsiResultRow[];
  summary: FsiSummary;
}

export const fsiService = {
  calculate: async (entries: FsiEntry[], sessionId?: string) => {
    const { data } = await apiClient.post<FsiCalculateResponse>("/fsi/calculate", {
      session_id: sessionId ?? null,
      entries,
    });
    return data;
  },

  listEntries: async (sessionId: string, skip = 0, limit = 100) => {
    const { data } = await apiClient.get<{ items: FsiEntry[]; total: number }>(
      `/fsi/session/${sessionId}`,
      { params: { skip, limit } }
    );
    return data;
  },
};
