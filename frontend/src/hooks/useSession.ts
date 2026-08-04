import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { sessionService, type SaveSessionPayload } from "@/services/sessionService";

export function useSessions(skip = 0, limit = 20) {
  return useQuery({
    queryKey: ["sessions", skip, limit],
    queryFn: () => sessionService.list(skip, limit),
  });
}

export function useSession(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => sessionService.get(sessionId as string),
    enabled: Boolean(sessionId),
  });
}

export function useSaveSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SaveSessionPayload) => sessionService.save(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["session", data.id] });
    },
  });
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => sessionService.remove(sessionId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sessions"] }),
  });
}
