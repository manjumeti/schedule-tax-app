import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { a3Service } from "@/services/a3Service";
import type { A3Entry, A3Holding } from "@/types/schedules";

export function useA3Entries(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["a3-entries", sessionId],
    queryFn: () => a3Service.listEntries(sessionId as string),
    enabled: Boolean(sessionId),
  });
}

export function useCalculateA3() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ entries, sessionId }: { entries: A3Entry[]; sessionId?: string }) =>
      a3Service.calculate(entries, sessionId),
    onSuccess: (_data, variables) => {
      if (variables.sessionId) {
        queryClient.invalidateQueries({ queryKey: ["a3-entries", variables.sessionId] });
        queryClient.invalidateQueries({ queryKey: ["dashboard", variables.sessionId] });
      }
    },
  });
}

export function useCalculateA3FromLots() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ holding, sessionId }: { holding: A3Holding; sessionId?: string }) =>
      a3Service.calculateFromLots(holding, sessionId),
    onSuccess: (_data, variables) => {
      if (variables.sessionId) {
        queryClient.invalidateQueries({ queryKey: ["a3-entries", variables.sessionId] });
        queryClient.invalidateQueries({ queryKey: ["dashboard", variables.sessionId] });
      }
    },
  });
}

