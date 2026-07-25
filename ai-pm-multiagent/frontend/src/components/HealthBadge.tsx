import type { HealthStatus } from "../types";

const STYLES: Record<HealthStatus, string> = {
  on_track: "bg-emerald-50 text-emerald-700 border-emerald-200",
  at_risk: "bg-amber-50 text-amber-700 border-amber-200",
  off_track: "bg-orange-50 text-orange-700 border-orange-200",
  critical: "bg-red-50 text-red-700 border-red-200",
};

const DOT_STYLES: Record<HealthStatus, string> = {
  on_track: "bg-emerald-500",
  at_risk: "bg-amber-500",
  off_track: "bg-orange-500",
  critical: "bg-red-500 animate-pulse-slow",
};

const LABELS: Record<HealthStatus, string> = {
  on_track: "On Track", at_risk: "At Risk", off_track: "Off Track", critical: "Critical",
};

export default function HealthBadge({ status }: { status: HealthStatus }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border shadow-sm ${STYLES[status]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${DOT_STYLES[status]}`} />
      {LABELS[status]}
    </span>
  );
}
