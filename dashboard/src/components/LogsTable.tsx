import type { LogEntry } from "../lib/api";

interface Props {
  logs: LogEntry[];
}

const actionStyle: Record<string, string> = {
  block: "bg-red-900 text-red-300",
  allow: "bg-emerald-900 text-emerald-300",
  rate_limit: "bg-yellow-900 text-yellow-300",
};

const rowStyle: Record<string, string> = {
  block: "border-l-2 border-red-600",
  allow: "border-l-2 border-emerald-600",
  rate_limit: "border-l-2 border-yellow-500",
};

export function LogsTable({ logs }: Props) {
  if (logs.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500 text-sm">
        No logs yet. Waiting for requests...
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 text-xs uppercase tracking-wider border-b border-gray-700">
            <th className="pb-3 pr-4">Time</th>
            <th className="pb-3 pr-4">IP</th>
            <th className="pb-3 pr-4">Method</th>
            <th className="pb-3 pr-4">Endpoint</th>
            <th className="pb-3 pr-4">Score</th>
            <th className="pb-3 pr-4">Action</th>
            <th className="pb-3">Threats</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {logs.map((log) => (
            <tr
              key={log.id}
              className={`${rowStyle[log.action_taken] ?? ""} hover:bg-gray-800/50 transition-colors`}
            >
              <td className="py-2.5 pr-4 text-gray-400 font-mono text-xs whitespace-nowrap pl-3">
                {new Date(log.created_at).toLocaleTimeString()}
              </td>
              <td className="py-2.5 pr-4 text-gray-300 font-mono">{log.ip_address}</td>
              <td className="py-2.5 pr-4 text-gray-400 font-mono">{log.method}</td>
              <td className="py-2.5 pr-4 text-gray-300 max-w-xs truncate" title={log.endpoint}>
                {log.endpoint}
              </td>
              <td className="py-2.5 pr-4 text-gray-300 font-mono">{log.threat_score}</td>
              <td className="py-2.5 pr-4">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${
                    actionStyle[log.action_taken] ?? "bg-gray-700 text-gray-300"
                  }`}
                >
                  {log.action_taken}
                </span>
              </td>
              <td className="py-2.5 text-gray-400 text-xs">
                {(log.threat_types ?? []).join(", ") || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
