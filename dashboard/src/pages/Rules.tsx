import { useEffect, useState } from "react";
import { getRules, toggleRule, type Rule } from "../lib/api";

export function Rules() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<string | null>(null);

  useEffect(() => {
    getRules()
      .then(setRules)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  async function handleToggle(id: string) {
    setToggling(id);
    try {
      const updated = await toggleRule(id);
      setRules((prev) => prev.map((r) => (r.id === id ? updated : r)));
    } catch (e: unknown) {
      setError(String(e));
    } finally {
      setToggling(null);
    }
  }

  if (error) {
    return <div className="p-6 text-red-400 text-sm">Error: {error}</div>;
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h2 className="text-white text-xl font-semibold">WAF Rules</h2>
        <p className="text-gray-500 text-xs mt-0.5">{rules.length} rules loaded</p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        {rules.length === 0 ? (
          <div className="text-center py-16 text-gray-500 text-sm">
            No rules configured yet
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 text-xs uppercase tracking-wider border-b border-gray-700">
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3 hidden lg:table-cell">Pattern</th>
                <th className="px-5 py-3">Score</th>
                <th className="px-5 py-3">Action</th>
                <th className="px-5 py-3">Enabled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {rules.map((rule) => (
                <tr key={rule.id} className="hover:bg-gray-700/40 transition-colors">
                  <td className="px-5 py-3 text-gray-200 font-medium">{rule.name}</td>
                  <td className="px-5 py-3">
                    <span className="px-2 py-0.5 rounded bg-blue-900 text-blue-300 text-xs font-medium">
                      {rule.type}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-400 font-mono text-xs max-w-xs truncate hidden lg:table-cell" title={rule.pattern}>
                    {rule.pattern}
                  </td>
                  <td className="px-5 py-3 text-gray-300 font-mono">+{rule.score}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        rule.action === "block"
                          ? "bg-red-900 text-red-300"
                          : "bg-gray-700 text-gray-300"
                      }`}
                    >
                      {rule.action}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <button
                      onClick={() => void handleToggle(rule.id)}
                      disabled={toggling === rule.id}
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none disabled:opacity-50 ${
                        rule.enabled ? "bg-emerald-600" : "bg-gray-600"
                      }`}
                    >
                      <span
                        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                          rule.enabled ? "translate-x-4" : "translate-x-1"
                        }`}
                      />
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
