import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Overview", icon: "📊" },
  { to: "/live-logs", label: "Live Logs", icon: "⚡" },
  { to: "/rules", label: "Rules", icon: "🛡️" },
  { to: "/blocked-ips", label: "Blocked IPs", icon: "🚫" },
];

export function Sidebar() {
  return (
    <aside className="w-56 min-h-screen bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="px-6 py-5 border-b border-gray-800">
        <h1 className="text-white font-bold text-lg tracking-tight">Mini WAF</h1>
        <p className="text-gray-500 text-xs mt-0.5">Security Dashboard</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`
            }
          >
            <span>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-6 py-4 border-t border-gray-800">
        <p className="text-gray-600 text-xs">v0.1.0</p>
      </div>
    </aside>
  );
}
