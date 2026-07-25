"""
Tool: Risk detection, prediction, and mitigation - used by Sentinel.
Rule-based risk engine (deterministic, explainable) rather than a black-box
LLM risk score, per Responsible-AI guidance for PM decision support.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from app.models import (
    Task, TaskStatus, Dependency, Resource, Risk, RiskCategory, RiskSeverity,
    Project, ProjectHealth, HealthStatus,
)
from app.core.logging import get_logger

logger = get_logger("tools.risk")


def detect_late_tasks(tasks: list[Task], now: Optional[datetime] = None) -> list[Risk]:
    now = now or datetime.utcnow()
    risks = []
    for t in tasks:
        if t.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            continue
        if t.due_date and t.due_date < now:
            days_late = (now - t.due_date).days
            severity = RiskSeverity.CRITICAL if days_late > 5 else RiskSeverity.HIGH if days_late > 2 else RiskSeverity.MEDIUM
            risks.append(Risk(
                project_id=t.project_id, title=f"Task overdue: {t.title}",
                description=f"Task '{t.title}' was due {t.due_date.date()} and is {days_late} day(s) late.",
                category=RiskCategory.SCHEDULE, severity=severity,
                probability=1.0, impact_score=min(0.3 + 0.1 * days_late, 1.0),
                related_task_ids=[t.id],
            ))
    return risks


def detect_dependency_violations(tasks: list[Task], dependencies: list[Dependency]) -> list[Risk]:
    risks = []
    tasks_by_id = {t.id: t for t in tasks}
    for dep in dependencies:
        pred = tasks_by_id.get(dep.predecessor_task_id)
        succ = tasks_by_id.get(dep.successor_task_id)
        if not pred or not succ:
            continue
        if pred.status != TaskStatus.COMPLETED and succ.status == TaskStatus.IN_PROGRESS:
            dep.is_violated = True
            risks.append(Risk(
                project_id=succ.project_id,
                title=f"Dependency violation: '{succ.title}' started before '{pred.title}' finished",
                description=f"Successor task started while predecessor is still '{pred.status}'.",
                category=RiskCategory.DEPENDENCY, severity=RiskSeverity.HIGH,
                probability=0.9, impact_score=0.6,
                related_task_ids=[pred.id, succ.id],
            ))
    return risks


def detect_resource_conflicts(resources: list[Resource]) -> list[Risk]:
    risks = []
    for r in resources:
        if r.utilization > 1.0:
            risks.append(Risk(
                project_id="", title=f"Resource over-allocated: {r.name}",
                description=f"{r.name} is allocated {r.allocated_hours}h against a {r.weekly_capacity_hours}h capacity "
                             f"({int(r.utilization * 100)}% utilization).",
                category=RiskCategory.RESOURCE, severity=RiskSeverity.HIGH if r.utilization > 1.25 else RiskSeverity.MEDIUM,
                probability=0.8, impact_score=min(r.utilization - 1.0 + 0.4, 1.0),
            ))
        if not r.is_available:
            risks.append(Risk(
                project_id="", title=f"Resource unavailable: {r.name}",
                description=f"{r.name} ({r.role}) is currently marked unavailable.",
                category=RiskCategory.RESOURCE, severity=RiskSeverity.HIGH,
                probability=1.0, impact_score=0.7,
            ))
    return risks


def suggest_mitigation(risk: Risk, resources: list[Resource], tasks: list[Task]) -> str:
    """
    Mirrors the spec's example flow:
      Developer unavailable -> find available engineer -> estimate impact ->
      suggest reassignment -> (caller then requests approval)
    """
    if risk.category == RiskCategory.RESOURCE and "unavailable" in risk.title.lower():
        affected = [t for t in tasks if t.assignee and any(r.name in risk.title for r in resources if r.email == t.assignee)]
        candidates = [r for r in resources if r.is_available and r.utilization < 0.85]
        if candidates:
            best = min(candidates, key=lambda r: r.utilization)
            return (
                f"Reassign affected task(s) to {best.name} ({best.role}, current utilization "
                f"{int(best.utilization * 100)}%). Estimated schedule impact: "
                f"{len(affected)} task(s), ~{sum((t.estimated_hours or 0) for t in affected):.0f}h of work."
            )
        return "No available engineer found with capacity; recommend deadline extension or scope reduction."

    if risk.category == RiskCategory.SCHEDULE:
        return (
            "Recommend: (1) notify assignee and confirm blocker, (2) evaluate fast-tracking downstream tasks, "
            "(3) if unresolved in 48h, escalate and request deadline change approval."
        )
    if risk.category == RiskCategory.DEPENDENCY:
        return "Recommend pausing the successor task until the predecessor completes, or formally re-sequencing the WBS."
    if risk.category == RiskCategory.RESOURCE:
        return "Recommend rebalancing workload across the team or requesting temporary contractor support."
    return "Recommend PM review; insufficient signal for an automated mitigation suggestion."


def find_reassignment_candidate(risk: Risk, resources: list[Resource], tasks: list[Task]) -> Optional[dict]:
    """
    Structured counterpart to suggest_mitigation(): when a 'resource unavailable'
    risk has exactly one affected task and at least one resource with spare
    capacity, returns the concrete {task_id, resource_id} pairing Sentinel can
    attach to a REASSIGN_RESOURCE approval request - meaning approving it
    auto-executes the reassignment (HumanApprovalAgent._execute) instead of
    just recording a decision with no downstream effect. Returns None for
    anything ambiguous (multiple affected tasks, no spare capacity), in which
    case the caller falls back to a generic escalation for manual PM handling.
    """
    if not (risk.category == RiskCategory.RESOURCE and "unavailable" in risk.title.lower()):
        return None
    # Scope to tasks actively blocked right now (IN_PROGRESS), not the
    # resource's whole future backlog - a person typically owns several
    # not-yet-started tasks, and auto-reassigning all of them on one approval
    # click would be overreach. Only the in-flight task is genuinely urgent;
    # the rest stay with the resource for normal replanning once they're back.
    affected = [
        t for t in tasks
        if t.status == TaskStatus.IN_PROGRESS and t.assignee
        and any(r.name in risk.title for r in resources if r.email == t.assignee)
    ]
    candidates = [r for r in resources if r.is_available and r.utilization < 0.85]
    if len(affected) != 1 or not candidates:
        return None
    best = min(candidates, key=lambda r: r.utilization)
    return {"task_id": affected[0].id, "resource_id": best.id, "resource_name": best.name}


def calculate_project_risk(
    project: Project, tasks: list[Task], risks: list[Risk], resources: list[Resource],
) -> ProjectHealth:
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    overdue = sum(1 for t in tasks if t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
                   and t.due_date and t.due_date < datetime.utcnow())
    open_risks = [r for r in risks if not r.resolved]
    critical_risks = [r for r in open_risks if r.severity == RiskSeverity.CRITICAL]

    delay_probability = min(0.15 + 0.12 * overdue + 0.08 * len(critical_risks), 0.98)
    budget_risk = min(0.1 + 0.05 * sum(1 for r in open_risks if r.category == RiskCategory.BUDGET), 0.95)
    bottleneck = min(0.1 + 0.15 * sum(1 for r in resources if r.utilization > 1.0), 0.95)

    if critical_risks or delay_probability > 0.7:
        status = HealthStatus.CRITICAL
    elif overdue > 0 or delay_probability > 0.45:
        status = HealthStatus.AT_RISK
    elif open_risks:
        status = HealthStatus.OFF_TRACK if delay_probability > 0.3 else HealthStatus.ON_TRACK
    else:
        status = HealthStatus.ON_TRACK

    schedule_variance = float(overdue) * 1.5

    summary = (
        f"{completed}/{total} tasks complete, {overdue} overdue, {len(open_risks)} open risk(s) "
        f"({len(critical_risks)} critical). Delay probability estimated at {int(delay_probability * 100)}%."
    )

    return ProjectHealth(
        project_id=project.id, status=status, schedule_variance_days=schedule_variance,
        tasks_total=total, tasks_completed=completed, tasks_overdue=overdue,
        open_risks=len(open_risks), critical_risks=len(critical_risks),
        delay_probability=round(delay_probability, 2), budget_risk_score=round(budget_risk, 2),
        resource_bottleneck_score=round(bottleneck, 2), summary=summary,
    )
