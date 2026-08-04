import { apiClient } from "@/services/apiClient";
import type { A3Entry, FsiEntry, SessionDetail, SessionSummary } from "@/types/schedules";

export interface SaveSessionPayload {
  session_id?: string | null;
  name: string;
  assessment_year: string;
  fsi_entries?: FsiEntry[];
  a3_entries?: A3Entry[];
}

export const sessionService = {
  save: async (payload: SaveSessionPayload) => {
    const { data } = await apiClient.post<SessionDetail>("/session/save", payload);
    return data;
  },

  get: async (sessionId: string) => {
    const { data } = await apiClient.get<SessionDetail>(`/session/${sessionId}`);
    return data;
  },

  list: async (skip = 0, limit = 20) => {
    const { data } = await apiClient.get<{ items: SessionSummary[]; total: number }>("/session", {
      params: { skip, limit },
    });
    return data;
  },

  remove: async (sessionId: string) => {
    await apiClient.delete(`/session/${sessionId}`);
  },
};
