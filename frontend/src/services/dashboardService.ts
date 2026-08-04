import { apiClient } from "@/services/apiClient";
import type { DashboardData } from "@/types/schedules";

export const dashboardService = {
  get: async (sessionId: string) => {
    const { data } = await apiClient.get<DashboardData>(`/dashboard/${sessionId}`);
    return data;
  },
};
