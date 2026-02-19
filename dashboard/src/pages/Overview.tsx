import { useEffect, useState } from "react";
import { StatCard } from "../components/StatCard";
import { ThreatPieChart } from "../components/ThreatPieChart";
import { TimelineChart } from "../components/TimelineChart";
import { getStats, type Stats } from "../lib/api";

export function Overview() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((e: unknown) => setError(String(e)));

    const interval = setInterval(() => {
      getStats().then(setStats).catch(() => null);
    }, 10_000);

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="p-6 text-red-400 text-sm">
        Failed to load stats: {error}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-white text-xl font-semibold">Overview</h2>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Requests"
          value={stats?.total_requests ?? "—"}
          icon="🌐"
          accent="default"
        />
        <StatCard
          label="Blocked"
          value={stats?.blocked_requests ?? "—"}
          icon="🔴"
          accent="red"
        />
        <StatCard
          label="Allowed"
          value={stats?.allowed_requests ?? "—"}
          icon="🟢"
          accent="emerald"
        />
        <StatCard
          label="Rate Limited"
          value={
            stats
              ? stats.total_requests - stats.blocked_requests - stats.allowed_requests
              : "—"
          }
          icon="🟡"
          accent="yellow"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <h3 className="text-gray-300 text-sm font-medium mb-4">Threat Type Distribution</h3>
          <ThreatPieChart data={stats?.threat_distribution ?? []} />
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <h3 className="text-gray-300 text-sm font-medium mb-4">Requests (Last 24h)</h3>
          <TimelineChart data={stats?.requests_over_time ?? []} />
        </div>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
        <h3 className="text-gray-300 text-sm font-medium mb-4">Top Attacking IPs</h3>
        {stats?.top_ips.length === 0 || !stats ? (
          <p className="text-gray-500 text-sm">No data yet</p>
        ) : (
          <div className="space-y-2">
            {stats.top_ips.map(({ ip, count }) => (
              <div key={ip} className="flex items-center gap-3">
                <span className="text-gray-300 font-mono text-sm w-36">{ip}</span>
                <div className="flex-1 bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{
                      width: `${Math.round((count / stats.top_ips[0].count) * 100)}%`,
                    }}
                  />
                </div>
                <span className="text-gray-400 text-xs w-12 text-right">{count}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
