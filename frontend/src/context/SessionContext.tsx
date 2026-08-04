import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

interface SessionContextValue {
  sessionId: string | undefined;
  setSessionId: (id: string | undefined) => void;
}

const STORAGE_KEY = "schedule-tax-app.currentSessionId";

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionIdState] = useState<string | undefined>(
    () => localStorage.getItem(STORAGE_KEY) ?? undefined
  );

  const setSessionId = (id: string | undefined) => {
    setSessionIdState(id);
    if (id) {
      localStorage.setItem(STORAGE_KEY, id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const value = useMemo(() => ({ sessionId, setSessionId }), [sessionId]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useCurrentSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useCurrentSession must be used within a SessionProvider");
  }
  return ctx;
}
