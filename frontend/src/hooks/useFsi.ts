import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fsiService } from "@/services/fsiService";
import type { FsiEntry } from "@/types/schedules";

export function useFsiEntries(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["fsi-entries", sessionId],
    queryFn: () => fsiService.listEntries(sessionId as string),
    enabled: Boolean(sessionId),
  });
}

export function useCalculateFsi() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ entries, sessionId }: { entries: FsiEntry[]; sessionId?: string }) =>
      fsiService.calculate(entries, sessionId),
    onSuccess: (_data, variables) => {
      if (variables.sessionId) {
        queryClient.invalidateQueries({ queryKey: ["fsi-entries", variables.sessionId] });
        queryClient.invalidateQueries({ queryKey: ["dashboard", variables.sessionId] });
      }
    },
  });
}
