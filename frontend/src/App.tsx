import { Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { DashboardPage } from "@/pages/DashboardPage";
import { FsiPage } from "@/pages/FsiPage";
import { A3Page } from "@/pages/A3Page";
import { SessionsPage } from "@/pages/SessionsPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/fsi" element={<FsiPage />} />
        <Route path="/a3" element={<A3Page />} />
        <Route path="/sessions" element={<SessionsPage />} />
      </Route>
    </Routes>
  );
}
