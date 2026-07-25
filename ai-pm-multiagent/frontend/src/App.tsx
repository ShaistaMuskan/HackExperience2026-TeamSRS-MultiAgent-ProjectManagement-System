import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { Project } from "./types";
import IngestForm from "./components/IngestForm";
import Dashboard from "./pages/Dashboard";
import IntegrationStatusBar from "./components/IntegrationStatusBar";
import { ChevronDownIcon, SparklesIcon } from "./components/icons";

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadProjects = () => api.listProjects().then(setProjects).catch(() => {});

  useEffect(() => {
    loadProjects();
  }, []);

  const handleIngest = async (payload: { project_name: string; raw_text: string }) => {
    setLoading(true);
    try {
      const project = await api.ingestBrief(payload);
      await loadProjects();
      setSelectedId(project.id);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-app-bg">
      <header className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 shrink-0 rounded-xl bg-brand-gradient shadow-glow flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-base font-extrabold text-slate-900 tracking-tight truncate">
                AI-Powered Multi-Agent Project Management
              </h1>
              <p className="text-xs text-slate-500 mb-1.5">Atlas · Sentinel · Orchestrator · Human Approval</p>
              <IntegrationStatusBar />
            </div>
          </div>

          <div className="relative shrink-0">
            <select
              className="appearance-none border border-slate-300 bg-white rounded-lg pl-3 pr-9 py-2 text-sm font-medium text-slate-700 shadow-sm hover:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500 transition"
              value={selectedId || ""}
              onChange={(e) => setSelectedId(e.target.value || null)}
            >
              <option value="">Select a project…</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <ChevronDownIcon className="w-4 h-4 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <IngestForm onSubmit={handleIngest} loading={loading} />
        {selectedId ? (
          <Dashboard projectId={selectedId} />
        ) : (
          <div className="flex flex-col items-center justify-center text-center py-20 rounded-2xl border border-dashed border-brand-200 bg-white/60">
            <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center mb-3">
              <SparklesIcon className="w-6 h-6 text-brand-600" />
            </div>
            <p className="text-sm font-medium text-slate-600">No project selected yet</p>
            <p className="text-xs text-slate-400 mt-1">Upload a project brief above, or select an existing project.</p>
          </div>
        )}
      </main>
    </div>
  );
}
