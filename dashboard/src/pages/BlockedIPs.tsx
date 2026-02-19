import { useEffect, useState } from "react";
import { getBlockedIPs, unblockIP, type BlockedIP } from "../lib/api";

export function BlockedIPs() {
  const [ips, setIps] = useState<BlockedIP[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [unblocking, setUnblocking] = useState<string | null>(null);

  useEffect(() => {
    getBlockedIPs()
      .then(setIps)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  async function handleUnblock(ip: string) {
    setUnblocking(ip);
    try {
      await unblockIP(ip);
      setIps((prev) => prev.filter((entry) => entry.ip_address !== ip));
    } catch (e: unknown) {
      setError(String(e));
    } finally {
      setUnblocking(null);
    }
  }

  if (error) {
    return <div className="p-6 text-red-400 text-sm">Error: {error}</div>;
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h2 className="text-white text-xl font-semibold">Blocked IPs</h2>
        <p className="text-gray-500 text-xs mt-0.5">{ips.length} blocked addresses</p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        {ips.length === 0 ? (
          <div className="text-center py-16 text-gray-500 text-sm">
            No blocked IPs
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 text-xs uppercase tracking-wider border-b border-gray-700">
                <th className="px-5 py-3">IP Address</th>
                <th className="px-5 py-3">Reason</th>
                <th className="px-5 py-3">Blocked At</th>
                <th className="px-5 py-3">Expires</th>
                <th className="px-5 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {ips.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-700/40 transition-colors">
                  <td className="px-5 py-3 text-red-300 font-mono font-medium">
                    {entry.ip_address}
                  </td>
                  <td className="px-5 py-3 text-gray-400 text-xs max-w-xs truncate" title={entry.reason ?? ""}>
                    {entry.reason ?? "—"}
                  </td>
                  <td className="px-5 py-3 text-gray-400 text-xs whitespace-nowrap">
                    {entry.created_at ? new Date(entry.created_at).toLocaleString() : "—"}
                  </td>
                  <td className="px-5 py-3 text-gray-400 text-xs whitespace-nowrap">
                    {entry.expires_at ? (
                      new Date(entry.expires_at).toLocaleString()
                    ) : (
                      <span className="text-red-400">Permanent</span>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <button
                      onClick={() => void handleUnblock(entry.ip_address)}
                      disabled={unblocking === entry.ip_address}
                      className="px-3 py-1 rounded bg-gray-700 text-gray-300 text-xs font-medium hover:bg-gray-600 transition-colors disabled:opacity-50"
                    >
                      {unblocking === entry.ip_address ? "Unblocking..." : "Unblock"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
