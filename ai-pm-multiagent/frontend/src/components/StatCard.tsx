import type { ComponentType, SVGProps } from "react";

export default function StatCard({
  label, value, sub, icon: Icon, accent = "brand",
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon?: ComponentType<SVGProps<SVGSVGElement>>;
  accent?: "brand" | "emerald" | "orange" | "red";
}) {
  const accentStyles: Record<string, string> = {
    brand: "bg-brand-50 text-brand-600",
    emerald: "bg-emerald-50 text-emerald-600",
    orange: "bg-orange-50 text-orange-600",
    red: "bg-red-50 text-red-600",
  };
  return (
    <div className="group bg-white rounded-2xl border border-slate-200 p-4 shadow-card hover:shadow-glow hover:-translate-y-0.5 hover:border-brand-200 transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-slate-500 font-medium">{label}</div>
        {Icon && (
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${accentStyles[accent]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="text-2xl font-extrabold text-slate-900 mt-1.5">{value}</div>
      {sub && <div className="text-xs text-slate-400 mt-1">{sub}</div>}
    </div>
  );
}
