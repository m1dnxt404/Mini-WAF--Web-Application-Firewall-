import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { BlockedIPs } from "./pages/BlockedIPs";
import { LiveLogs } from "./pages/LiveLogs";
import { Overview } from "./pages/Overview";
import { Rules } from "./pages/Rules";

export function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-950 text-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/live-logs" element={<LiveLogs />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/blocked-ips" element={<BlockedIPs />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
