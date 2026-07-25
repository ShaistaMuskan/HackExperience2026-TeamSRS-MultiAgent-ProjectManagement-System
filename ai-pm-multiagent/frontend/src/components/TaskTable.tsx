import type { TaskItem } from "../types";
import { ListBulletIcon } from "./icons";

const STATUS_COLORS: Record<string, string> = {
  not_started: "bg-slate-100 text-slate-600",
  in_progress: "bg-blue-100 text-blue-700",
  blocked: "bg-red-100 text-red-700",
  completed: "bg-emerald-100 text-emerald-700",
  overdue: "bg-orange-100 text-orange-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const STATUS_DOT: Record<string, string> = {
  not_started: "bg-slate-400",
  in_progress: "bg-blue-500",
  blocked: "bg-red-500",
  completed: "bg-emerald-500",
  overdue: "bg-orange-500",
  cancelled: "bg-slate-300",
};

const PRIORITY_COLORS: Record<string, string> = {
  low: "text-slate-500",
  medium: "text-amber-600",
  high: "text-orange-600",
  critical: "text-red-600 font-semibold",
};

export default function TaskTable({ tasks }: { tasks: TaskItem[] }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center gap-2">
        <ListBulletIcon className="w-4 h-4 text-brand-600" />
        <span className="font-bold text-slate-800">Work Breakdown Structure</span>
        <span className="text-xs text-slate-400 font-medium">({tasks.length})</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50/80 text-slate-500 text-[11px] uppercase tracking-wide">
            <tr>
              <th className="text-left px-5 py-2.5 font-semibold">WBS</th>
              <th className="text-left px-5 py-2.5 font-semibold">Task</th>
              <th className="text-left px-5 py-2.5 font-semibold">Status</th>
              <th className="text-left px-5 py-2.5 font-semibold">Priority</th>
              <th className="text-left px-5 py-2.5 font-semibold">Assignee</th>
              <th className="text-left px-5 py-2.5 font-semibold">Due</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id} className="border-t border-slate-100 hover:bg-brand-50/40 transition-colors">
                <td className="px-5 py-2.5 text-slate-400 font-mono text-xs">{t.wbs_code}</td>
                <td className="px-5 py-2.5 text-slate-800 font-medium">
                  {t.title}
                  {t.tags.includes("critical_path") && (
                    <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-700 font-semibold">
                      critical path
                    </span>
                  )}
                </td>
                <td className="px-5 py-2.5">
                  <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[t.status] || ""}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[t.status] || "bg-slate-400"}`} />
                    {t.status.replace("_", " ")}
                  </span>
                </td>
                <td className={`px-5 py-2.5 capitalize ${PRIORITY_COLORS[t.priority] || "text-slate-600"}`}>{t.priority}</td>
                <td className="px-5 py-2.5 text-slate-600">{t.assignee || "—"}</td>
                <td className="px-5 py-2.5 text-slate-500">{t.due_date ? new Date(t.due_date).toLocaleDateString() : "—"}</td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-sm text-slate-400">No tasks yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
