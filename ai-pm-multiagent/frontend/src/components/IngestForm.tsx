import { useState } from "react";
import { DocumentPlusIcon, SparklesIcon } from "./icons";

export default function IngestForm({
  onSubmit, loading,
}: {
  onSubmit: (payload: { project_name: string; raw_text: string }) => void;
  loading: boolean;
}) {
  const [name, setName] = useState("");
  const [brief, setBrief] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (name && brief) onSubmit({ project_name: name, raw_text: brief });
      }}
      className="bg-white rounded-2xl border border-slate-200 shadow-card p-5 space-y-3.5"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center">
          <DocumentPlusIcon className="w-4.5 h-4.5 text-brand-600" />
        </div>
        <div className="font-bold text-slate-800">Upload a Project Brief</div>
      </div>
      <input
        className="w-full border border-slate-200 bg-slate-50/60 rounded-lg px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500 focus:bg-white transition"
        placeholder="Project name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <textarea
        className="w-full border border-slate-200 bg-slate-50/60 rounded-lg px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 h-32 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500 focus:bg-white transition resize-none"
        placeholder="Paste the project brief / requirements text here..."
        value={brief}
        onChange={(e) => setBrief(e.target.value)}
      />
      <button
        type="submit"
        disabled={loading}
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-gradient text-white text-sm font-semibold rounded-lg shadow-glow hover:brightness-110 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        <SparklesIcon className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        {loading ? "Atlas is planning…" : "Let Atlas Plan This Project"}
      </button>
    </form>
  );
}
