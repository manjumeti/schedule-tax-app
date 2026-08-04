import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "@/services/dashboardService";

export function useDashboard(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["dashboard", sessionId],
    queryFn: () => dashboardService.get(sessionId as string),
    enabled: Boolean(sessionId),
  });
}
