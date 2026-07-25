"""
Hackathon-MVP persistence: a single in-process repository holding every
domain entity, keyed by id with project_id indices.

>>> POST-HACKATHON <<<
Swap the dict-backed storage in this class for real queries against the
SQLAlchemy models in app/db/models.py (PostgreSQL) or Cosmos DB SDK calls,
without touching any agent/tool/API code - they only depend on this class's
public method signatures.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Optional, TypeVar
from app.models import (
    Project, ProjectBrief, Task, Milestone, Sprint, Dependency, Risk,
    Resource, ApprovalRequest, Notification, PlannerPlan,
)

T = TypeVar("T")


class Repository:
    def __init__(self) -> None:
        self.briefs: dict[str, ProjectBrief] = {}
        self.projects: dict[str, Project] = {}
        self.tasks: dict[str, Task] = {}
        self.milestones: dict[str, Milestone] = {}
        self.sprints: dict[str, Sprint] = {}
        self.dependencies: dict[str, Dependency] = {}
        self.risks: dict[str, Risk] = {}
        self.resources: dict[str, Resource] = {}
        self.approvals: dict[str, ApprovalRequest] = {}
        self.notifications: dict[str, Notification] = {}
        self.planner_plans: dict[str, PlannerPlan] = {}
        self._seed_resources()

    def _seed_resources(self) -> None:
        # NOTE (hackathon-MVP simplification): `weekly_capacity_hours` is used here as a
        # stand-in for "capacity across this project's full engagement window" since the
        # MVP doesn't yet track per-sprint/per-week allocation. Post-hackathon: track
        # allocated_hours per ISO week and compare against a true weekly capacity instead.
        seed = [
            Resource(name="Ava Chen", email="ava.chen@contoso.com", role="Backend Engineer",
                     skills=["python", "fastapi", "azure"], weekly_capacity_hours=300),
            Resource(name="Marcus Lee", email="marcus.lee@contoso.com", role="Frontend Engineer",
                     skills=["react", "typescript"], weekly_capacity_hours=300),
            Resource(name="Priya Nair", email="priya.nair@contoso.com", role="QA Engineer",
                     skills=["testing", "automation"], weekly_capacity_hours=250),
            Resource(name="Daniel Ortiz", email="daniel.ortiz@contoso.com", role="DevOps Engineer",
                     skills=["azure", "docker", "ci-cd"], weekly_capacity_hours=250),
            Resource(name="Sofia Rossi", email="sofia.rossi@contoso.com", role="Solutions Architect",
                     skills=["architecture", "azure ai foundry"], weekly_capacity_hours=250),
        ]
        for r in seed:
            self.resources[r.id] = r

    # generic helpers -------------------------------------------------
    def _project_scoped(self, store: dict[str, T], project_id: str) -> list[T]:
        return [v for v in store.values() if getattr(v, "project_id", None) == project_id]

    # Project -----------------------------------------------------------
    def save_project(self, project: Project) -> Project:
        self.projects[project.id] = project
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.projects.get(project_id)

    def list_projects(self) -> list[Project]:
        return list(self.projects.values())

    # Brief ---------------------------------------------------------------
    def save_brief(self, brief: ProjectBrief) -> ProjectBrief:
        self.briefs[brief.id] = brief
        return brief

    # Tasks -----------------------------------------------------------
    def save_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def save_tasks(self, tasks: list[Task]) -> None:
        for t in tasks:
            self.save_task(t)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list_tasks(self, project_id: str) -> list[Task]:
        return self._project_scoped(self.tasks, project_id)

    # Milestones --------------------------------------------------------
    def save_milestones(self, milestones: list[Milestone]) -> None:
        for m in milestones:
            self.milestones[m.id] = m

    def list_milestones(self, project_id: str) -> list[Milestone]:
        return self._project_scoped(self.milestones, project_id)

    # Sprints -------------------------------------------------------------
    def save_sprints(self, sprints: list[Sprint]) -> None:
        for s in sprints:
            self.sprints[s.id] = s

    def list_sprints(self, project_id: str) -> list[Sprint]:
        return self._project_scoped(self.sprints, project_id)

    # Dependencies --------------------------------------------------------
    def save_dependencies(self, deps: list[Dependency]) -> None:
        for d in deps:
            self.dependencies[d.id] = d

    def list_dependencies(self, project_id: str) -> list[Dependency]:
        return self._project_scoped(self.dependencies, project_id)

    # Risks -----------------------------------------------------------------
    def save_risk(self, risk: Risk) -> Risk:
        self.risks[risk.id] = risk
        return risk

    def save_risks(self, risks: list[Risk]) -> None:
        for r in risks:
            self.save_risk(r)

    def list_risks(self, project_id: str) -> list[Risk]:
        return self._project_scoped(self.risks, project_id)

    # Resources -------------------------------------------------------------
    def list_resources(self) -> list[Resource]:
        return list(self.resources.values())

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        return self.resources.get(resource_id)

    # Approvals ---------------------------------------------------------------
    def save_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.approvals[approval.id] = approval
        return approval

    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self.approvals.get(approval_id)

    def list_approvals(self, project_id: str, pending_only: bool = False) -> list[ApprovalRequest]:
        items = self._project_scoped(self.approvals, project_id)
        if pending_only:
            items = [a for a in items if a.status == "pending"]
        return items

    # Notifications -------------------------------------------------------------
    def save_notification(self, n: Notification) -> Notification:
        self.notifications[n.id] = n
        return n

    def list_notifications(self, project_id: str) -> list[Notification]:
        return self._project_scoped(self.notifications, project_id)

    # Planner plans -------------------------------------------------------------
    def save_planner_plan(self, plan: PlannerPlan) -> PlannerPlan:
        self.planner_plans[plan.id] = plan
        return plan

    def get_planner_plan_for_project(self, project_id: str) -> Optional[PlannerPlan]:
        for p in self.planner_plans.values():
            if p.project_id == project_id:
                return p
        return None


@lru_cache
def get_repository() -> Repository:
    return Repository()
