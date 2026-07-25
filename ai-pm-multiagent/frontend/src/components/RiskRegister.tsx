import type { Risk } from "../types";
import { ExclamationTriangleIcon, ShieldIcon, SparklesIcon } from "./icons";

const SEVERITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

const SEVERITY_BAR: Record<string, string> = {
  low: "bg-slate-300",
  medium: "bg-amber-400",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

export default function RiskRegister({ risks }: { risks: Risk[] }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center gap-2">
        <ShieldIcon className="w-4 h-4 text-brand-600" />
        <span className="font-bold text-slate-800">Risk Register</span>
        <span className="text-xs text-slate-400 font-medium">(Sentinel)</span>
      </div>
      <div className="divide-y divide-slate-100">
        {risks.length === 0 && (
          <div className="px-5 py-8 text-sm text-slate-400 text-center">No risks detected yet — Sentinel is watching.</div>
        )}
        {risks.map((r) => (
          <div key={r.id} className="flex gap-3 px-5 py-3.5 hover:bg-slate-50/60 transition-colors">
            <div className={`w-1 rounded-full shrink-0 ${SEVERITY_BAR[r.severity]}`} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-semibold text-slate-800 flex items-center gap-1.5">
                  <ExclamationTriangleIcon className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  {r.title}
                </span>
                <span className={`text-[11px] font-bold uppercase px-2 py-0.5 rounded-full shrink-0 ${SEVERITY_COLORS[r.severity]}`}>
                  {r.severity}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{r.description}</p>
              {r.mitigation_plan && (
                <p className="text-xs text-brand-700 mt-2 bg-brand-50 rounded-lg px-2.5 py-1.5 flex items-start gap-1.5">
                  <SparklesIcon className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                  {r.mitigation_plan}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
