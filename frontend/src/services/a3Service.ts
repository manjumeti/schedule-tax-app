import { apiClient } from "@/services/apiClient";
import type { A3Entry, A3Holding, A3ResultRow, A3Summary } from "@/types/schedules";

export interface A3CalculateResponse {
  session_id: string | null;
  rows: A3ResultRow[];
  summary: A3Summary;
}

export const a3Service = {
  calculate: async (entries: A3Entry[], sessionId?: string) => {
    const { data } = await apiClient.post<A3CalculateResponse>("/a3/calculate", {
      session_id: sessionId ?? null,
      entries,
    });
    return data;
  },

  calculateFromLots: async (holding: A3Holding, sessionId?: string) => {
    const { data } = await apiClient.post<A3CalculateResponse>("/a3/calculate-from-lots", {
      session_id: sessionId ?? null,
      holding,
    });
    return data;
  },

  listEntries: async (sessionId: string, skip = 0, limit = 100) => {
    const { data } = await apiClient.get<{ items: A3Entry[]; total: number }>(
      `/a3/session/${sessionId}`,
      { params: { skip, limit } }
    );
    return data;
  },
};

