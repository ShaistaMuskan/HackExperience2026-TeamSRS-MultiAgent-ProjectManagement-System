import type { Notification } from "../types";
import { BellIcon } from "./icons";

const AGENT_COLORS: Record<string, string> = {
  atlas: "bg-brand-100 text-brand-700",
  sentinel: "bg-purple-100 text-purple-700",
  orchestrator: "bg-teal-100 text-teal-700",
  human_approval: "bg-amber-100 text-amber-700",
};

function initials(agent: string) {
  return agent.replace(/_/g, " ").split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

export default function NotificationFeed({ notifications }: { notifications: Notification[] }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center gap-2">
        <BellIcon className="w-4 h-4 text-brand-600" />
        <span className="font-bold text-slate-800">Teams Activity Feed</span>
      </div>
      <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
        {notifications.length === 0 && (
          <div className="px-5 py-8 text-sm text-slate-400 text-center">No notifications yet.</div>
        )}
        {[...notifications].reverse().map((n) => (
          <div key={n.id} className="flex gap-2.5 px-5 py-3 animate-fade-in">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                AGENT_COLORS[n.sent_by_agent] || "bg-slate-100 text-slate-600"
              }`}
            >
              {initials(n.sent_by_agent)}
            </div>
            <div className="min-w-0">
              <div className="text-[11px] text-slate-400">
                {new Date(n.sent_at).toLocaleString()} · <span className="font-medium text-slate-500">{n.sent_by_agent}</span>
              </div>
              <div className="text-sm text-slate-700 break-words">{n.message}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
