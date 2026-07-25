import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { DashboardResponse } from "../types";
import HealthBadge from "../components/HealthBadge";
import StatCard from "../components/StatCard";
import TaskTable from "../components/TaskTable";
import RiskRegister from "../components/RiskRegister";
import ApprovalQueue from "../components/ApprovalQueue";
import NotificationFeed from "../components/NotificationFeed";
import {
  ArrowTrendingUpIcon, CheckCircleIcon, ClockIcon, ExclamationTriangleIcon, ListBulletIcon, SparklesIcon,
} from "../components/icons";

export default function Dashboard({ projectId }: { projectId: string }) {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const refresh = () => {
    api.getDashboard(projectId).then(setData).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 15000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-700 text-sm bg-red-50 border border-red-200 rounded-xl px-4 py-3">
        <ExclamationTriangleIcon className="w-4 h-4 shrink-0" />
        {error}
      </div>
    );
  }
  if (!data) {
    return (
      <div className="flex items-center gap-2 text-slate-400 text-sm py-8 justify-center">
        <SparklesIcon className="w-4 h-4 animate-spin" />
        Loading dashboard…
      </div>
    );
  }

  const { project, health, tasks, risks, approvals, notifications, task_summary } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">{project.name}</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            <span className="capitalize">{project.methodology?.replace("_", " ") || "Methodology pending"}</span>
            {" · "}complexity {Math.round((project.complexity_score || 0) * 100)}%
          </p>
        </div>
        <div className="flex items-center gap-3">
          <HealthBadge status={health.status} />
          <button
            onClick={async () => {
              setSimulating(true);
              try {
                const res = await api.simulateIssues(projectId);
                setToast(res.message);
                refresh();
              } catch (e) {
                setToast(`Simulation failed: ${e}`);
              } finally {
                setSimulating(false);
              }
            }}
            disabled={simulating}
            title="Demo helper: backdates a task and takes a resource offline so Sentinel has something real to catch"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg border border-orange-200 bg-orange-50 text-orange-700 shadow-sm hover:bg-orange-100 hover:border-orange-300 active:scale-95 disabled:opacity-50 transition"
          >
            <ExclamationTriangleIcon className={`w-3.5 h-3.5 ${simulating ? "animate-spin" : ""}`} />
            {simulating ? "Injecting…" : "Simulate Crisis (Demo)"}
          </button>
          <button
            onClick={async () => {
              setRunning(true);
              try {
                await api.triggerSentinel(projectId);
                setToast("Sentinel pass complete — check Risk Register and Pending Approvals below.");
                refresh();
              } finally { setRunning(false); }
            }}
            disabled={running}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg border border-brand-200 bg-white text-brand-700 shadow-sm hover:bg-brand-50 hover:border-brand-300 active:scale-95 disabled:opacity-50 transition"
          >
            <ClockIcon className={`w-3.5 h-3.5 ${running ? "animate-spin" : ""}`} />
            {running ? "Running…" : "Run Sentinel Pass"}
          </button>
        </div>
      </div>

      {toast && (
        <div className="flex items-start justify-between gap-3 text-sm text-brand-800 bg-brand-50 border border-brand-200 rounded-xl px-4 py-3 animate-fade-in">
          <span className="flex items-start gap-2"><SparklesIcon className="w-4 h-4 shrink-0 mt-0.5" />{toast}</span>
          <button onClick={() => setToast(null)} className="text-brand-400 hover:text-brand-600 shrink-0">✕</button>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard label="Tasks" value={task_summary.total} icon={ListBulletIcon} />
        <StatCard label="Completed" value={task_summary.completed} icon={CheckCircleIcon} accent="emerald" />
        <StatCard label="Overdue" value={task_summary.overdue} icon={ClockIcon} accent="orange" />
        <StatCard
          label="Open Risks" value={health.open_risks} sub={`${health.critical_risks} critical`}
          icon={ExclamationTriangleIcon} accent={health.critical_risks > 0 ? "red" : "brand"}
        />
        <StatCard
          label="Delay Probability" value={`${Math.round(health.delay_probability * 100)}%`}
          icon={ArrowTrendingUpIcon} accent={health.delay_probability > 0.5 ? "red" : "brand"}
        />
      </div>

      <p className="text-sm text-slate-600 bg-gradient-to-r from-brand-50 to-white border border-brand-100 rounded-xl px-4 py-3">
        {health.summary}
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <TaskTable tasks={tasks} />
          <RiskRegister risks={risks} />
        </div>
        <div className="space-y-6">
          <ApprovalQueue
            approvals={approvals}
            onDecide={async (id, decision) => {
              await api.decideApproval(id, decision, "demo-pm@contoso.com");
              refresh();
            }}
          />
          <NotificationFeed notifications={notifications} />
        </div>
      </div>
    </div>
  );
}
