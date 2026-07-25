import type { DashboardResponse, Project, SystemStatus } from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", "x-user-role": "project_manager", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

export const api = {
  listProjects: () => request<Project[]>("/projects/"),
  ingestBrief: (payload: { project_name: string; raw_text: string; source_filename?: string }) =>
    request<Project>("/projects/ingest", { method: "POST", body: JSON.stringify(payload) }),
  getDashboard: (projectId: string) => request<DashboardResponse>(`/dashboard/${projectId}`),
  triggerSentinel: (projectId: string) => request(`/agents/sentinel/monitor/${projectId}`, { method: "POST" }),
  decideApproval: (approvalId: string, decision: "approved" | "rejected", reviewer: string) =>
    request(`/approvals/${approvalId}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision, reviewer }),
    }),
  getStatusReport: (projectId: string) => request<{ report: string }>(`/dashboard/${projectId}/status-report`),
  getSystemStatus: () => request<SystemStatus>("/system/status"),
  simulateIssues: (projectId: string) =>
    request<{ message: string; overdue_task: unknown; unavailable_resource: unknown }>(
      `/projects/${projectId}/demo/simulate-issues`, { method: "POST" },
    ),
};
