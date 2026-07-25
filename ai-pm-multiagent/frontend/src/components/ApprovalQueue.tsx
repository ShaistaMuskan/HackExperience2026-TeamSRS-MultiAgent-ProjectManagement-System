import type { Approval } from "../types";
import { CheckCircleIcon, ClipboardIcon, XCircleIcon } from "./icons";

export default function ApprovalQueue({
  approvals, onDecide,
}: {
  approvals: Approval[];
  onDecide: (approvalId: string, decision: "approved" | "rejected") => void;
}) {
  const pending = approvals.filter((a) => a.status === "pending");
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-card overflow-hidden">
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center gap-2">
        <ClipboardIcon className="w-4 h-4 text-brand-600" />
        <span className="font-bold text-slate-800">Pending Approvals</span>
        {pending.length > 0 && (
          <span className="text-xs font-bold text-white bg-red-500 rounded-full w-5 h-5 flex items-center justify-center animate-pulse-slow">
            {pending.length}
          </span>
        )}
      </div>
      <div className="divide-y divide-slate-100">
        {pending.length === 0 && (
          <div className="px-5 py-8 text-sm text-slate-400 text-center">Nothing awaiting approval.</div>
        )}
        {pending.map((a) => (
          <div key={a.id} className="px-5 py-3.5 animate-fade-in">
            <div className="text-sm font-semibold text-slate-800">{a.title}</div>
            <div className="text-xs text-slate-500 mt-1">{a.description}</div>
            <div className="text-[11px] text-slate-400 mt-1.5">
              Requested by <span className="font-medium text-slate-500">{a.requested_by_agent}</span> · {a.action_type}
            </div>
            <div className="flex gap-2 mt-2.5">
              <button
                onClick={() => onDecide(a.id, "approved")}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 text-white shadow-sm hover:bg-emerald-700 active:scale-95 transition"
              >
                <CheckCircleIcon className="w-3.5 h-3.5" />
                Approve
              </button>
              <button
                onClick={() => onDecide(a.id, "rejected")}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 active:scale-95 transition"
              >
                <XCircleIcon className="w-3.5 h-3.5" />
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
