const WAF_URL = import.meta.env.VITE_WAF_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${WAF_URL}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ──────────────────────────────────────────────────────────────────

export interface LogEntry {
  id: string;
  ip_address: string;
  method: string;
  endpoint: string;
  threat_score: number;
  action_taken: "allow" | "block" | "rate_limit";
  threat_types: string[];
  created_at: string;
}

export interface Stats {
  total_requests: number;
  blocked_requests: number;
  allowed_requests: number;
  top_ips: { ip: string; count: number }[];
  threat_distribution: { type: string; count: number }[];
  requests_over_time: { hour: string; count: number }[];
}

export interface Rule {
  id: string;
  name: string;
  type: string;
  pattern: string;
  score: number;
  action: string;
  enabled: boolean;
  created_at: string;
}

export interface BlockedIP {
  id: string;
  ip_address: string;
  reason: string | null;
  expires_at: string | null;
  created_at: string;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const getLogs = (limit = 50, offset = 0) =>
  request<LogEntry[]>(`/api/logs?limit=${limit}&offset=${offset}`);

export const getStats = () => request<Stats>("/api/stats");

export const getRules = () => request<Rule[]>("/api/rules");

export const toggleRule = (id: string) =>
  request<Rule>(`/api/rules/${id}/toggle`, { method: "PATCH" });

export const getBlockedIPs = () => request<BlockedIP[]>("/api/blocked-ips");

export const unblockIP = (ip: string) =>
  request<{ message: string }>(`/api/blocked-ips/${encodeURIComponent(ip)}`, {
    method: "DELETE",
  });
