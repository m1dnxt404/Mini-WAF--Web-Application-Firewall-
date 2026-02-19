import { useEffect, useRef } from "react";
import { LogsTable } from "../components/LogsTable";
import { useWebSocket } from "../hooks/useWebSocket";

export function LiveLogs() {
  const { messages, connected, paused, setPaused } = useWebSocket();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!paused) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, paused]);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-white text-xl font-semibold">Live Logs</h2>
          <p className="text-gray-500 text-xs mt-0.5">
            {messages.length} entries (last 100)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs text-gray-400">
            <span
              className={`inline-block w-2 h-2 rounded-full ${
                connected ? "bg-emerald-400 animate-pulse" : "bg-red-500"
              }`}
            />
            {connected ? "Connected" : "Reconnecting..."}
          </span>
          <button
            onClick={() => setPaused(!paused)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              paused
                ? "bg-emerald-700 text-emerald-100 hover:bg-emerald-600"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            {paused ? "▶ Resume" : "⏸ Pause"}
          </button>
        </div>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
        <LogsTable logs={messages} />
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
