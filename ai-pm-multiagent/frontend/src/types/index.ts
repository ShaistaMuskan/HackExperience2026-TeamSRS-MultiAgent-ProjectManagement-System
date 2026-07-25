export type Methodology = "agile_scrum" | "kanban" | "waterfall" | "prince2" | "hybrid";
export type HealthStatus = "on_track" | "at_risk" | "off_track" | "critical";
export type TaskStatus = "not_started" | "in_progress" | "blocked" | "completed" | "overdue" | "cancelled";
export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";

export interface Project {
  id: string;
  name: string;
  description: string;
  methodology: Methodology | null;
  methodology_rationale: string | null;
  complexity_score: number | null;
  health: HealthStatus;
  teams_channel_id: string | null;
  sharepoint_folder_url: string | null;
  planner_plan_id: string | null;
}

export interface TaskItem {
  id: string;
  title: string;
  status: TaskStatus;
  priority: string;
  assignee: string | null;
  due_date: string | null;
  wbs_code: string | null;
  tags: string[];
}

export interface Milestone {
  id: string;
  name: string;
  due_date: string;
  is_deliverable: boolean;
  completed: boolean;
}

export interface Risk {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: RiskSeverity;
  probability: number;
  impact_score: number;
  mitigation_plan: string | null;
  resolved: boolean;
}

export interface ProjectHealth {
  status: HealthStatus;
  tasks_total: number;
  tasks_completed: number;
  tasks_overdue: number;
  open_risks: number;
  critical_risks: number;
  delay_probability: number;
  budget_risk_score: number;
  resource_bottleneck_score: number;
  summary: string;
}

export interface Approval {
  id: string;
  project_id: string;
  requested_by_agent: string;
  action_type: string;
  title: string;
  description: string;
  status: ApprovalStatus;
}

export interface Notification {
  id: string;
  channel: string;
  title: string;
  message: string;
  sent_by_agent: string;
  sent_at: string;
}

export interface IntegrationEntry {
  label: string;
  status: "mock" | "live";
}

export interface SystemStatus {
  app_name: string;
  environment: string;
  integrations: Record<string, IntegrationEntry>;
  summary: string;
}

export interface DashboardResponse {
  project: Project;
  health: ProjectHealth;
  tasks: TaskItem[];
  milestones: Milestone[];
  risks: Risk[];
  approvals: Approval[];
  notifications: Notification[];
  task_summary: { total: number; completed: number; in_progress: number; overdue: number; not_started: number };
}
