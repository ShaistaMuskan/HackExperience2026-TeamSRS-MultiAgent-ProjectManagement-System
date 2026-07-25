import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { SystemStatus } from "../types";

/**
 * Makes the mock-vs-real architecture visible rather than something you have
 * to explain or dig through logs for. Each pill reflects USE_MOCK_<SERVICE>
 * resolution in backend/app/core/config.py in real time - flip an env var,
 * restart the backend, refresh, and the pill changes color.
 */
export default function IntegrationStatusBar() {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    api.getSystemStatus().then(setStatus).catch(() => {});
    const interval = setInterval(() => {
      api.getSystemStatus().then(setStatus).catch(() => {});
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  if (!status) return null;

  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      <span className="text-[11px] uppercase tracking-wide text-slate-400 font-semibold mr-1">
        Integrations ({status.summary}):
      </span>
      {Object.entries(status.integrations).map(([key, entry]) => (
        <span
          key={key}
          title={entry.label}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border transition-colors ${
            entry.status === "live"
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-slate-100 text-slate-500 border-slate-200"
          }`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${entry.status === "live" ? "bg-emerald-500 animate-pulse-slow" : "bg-slate-400"}`} />
          {entry.label}
          <span className="uppercase text-[9px] opacity-70">{entry.status}</span>
        </span>
      ))}
    </div>
  );
}
