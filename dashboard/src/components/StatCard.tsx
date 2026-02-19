interface StatCardProps {
  label: string;
  value: number | string;
  icon: string;
  accent?: "default" | "red" | "emerald" | "yellow";
}

const accentMap = {
  default: "text-blue-400",
  red: "text-red-400",
  emerald: "text-emerald-400",
  yellow: "text-yellow-400",
};

export function StatCard({ label, value, icon, accent = "default" }: StatCardProps) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 flex items-center gap-4">
      <div className="text-3xl">{icon}</div>
      <div>
        <p className="text-gray-400 text-xs font-medium uppercase tracking-wider">{label}</p>
        <p className={`text-2xl font-bold mt-0.5 ${accentMap[accent]}`}>{value}</p>
      </div>
    </div>
  );
}
