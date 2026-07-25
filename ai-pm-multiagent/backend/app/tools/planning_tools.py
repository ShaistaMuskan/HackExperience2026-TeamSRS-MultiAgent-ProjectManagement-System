"""
Tool: WBS generation, dependency detection, duration estimation, critical path.

These are deterministic/heuristic "planning" tools Atlas calls after it has
chosen a methodology. They are intentionally rule-based (not LLM calls) so
the planning output is reproducible and auditable - a common pattern in
production agentic systems: let the LLM *decide which tool to call and with
what arguments*, but keep the actual computation in tested, deterministic code.
"""
from __future__ import annotations
import re
from datetime import datetime, timedelta
from typing import Any

from app.models import (
    Project, ProjectPhase, PhaseType, Epic, Task, TaskStatus, Priority,
    Milestone, Dependency, DependencyType, Sprint, MethodologyType,
)
from app.core.logging import get_logger

logger = get_logger("tools.planning")

# Generic SDLC-style phase template, reused/relabelled per methodology.
_PHASE_TEMPLATE: list[tuple[str, PhaseType, list[str]]] = [
    ("Initiation", PhaseType.INITIATION, ["Stakeholder kickoff", "Charter & scope sign-off", "Team onboarding"]),
    ("Planning & Design", PhaseType.PLANNING, ["Requirements analysis", "Solution architecture", "UX/UI design", "Risk register baseline"]),
    ("Execution", PhaseType.EXECUTION, []),  # populated from brief-derived features
    ("Monitoring & QA", PhaseType.MONITORING, ["Integration testing", "UAT", "Performance & security testing"]),
    ("Closure", PhaseType.CLOSURE, ["Deployment / go-live", "Documentation handover", "Post-implementation review"]),
]

_FEATURE_LINE_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.{4,120})$", re.MULTILINE)


def _extract_feature_lines(brief_text: str) -> list[str]:
    matches = [m.strip(" .") for m in _FEATURE_LINE_RE.findall(brief_text)]
    # de-duplicate while preserving order
    seen: set[str] = set()
    out = []
    for m in matches:
        key = m.lower()
        if key not in seen and len(m.split()) <= 20:
            seen.add(key)
            out.append(m)
    return out[:25]


def generate_wbs(
    project: Project, brief_text: str, methodology: MethodologyType, start_date: datetime | None = None,
) -> tuple[list[ProjectPhase], list[Epic], list[Task], list[Milestone]]:
    start_date = start_date or datetime.utcnow()
    phases: list[ProjectPhase] = []
    epics: list[Epic] = []
    tasks: list[Task] = []
    milestones: list[Milestone] = []

    feature_lines = _extract_feature_lines(brief_text)
    cursor = start_date
    wbs_phase_counter = 0

    for phase_name, phase_type, default_tasks in _PHASE_TEMPLATE:
        wbs_phase_counter += 1
        phase = ProjectPhase(name=phase_name, phase_type=phase_type, start_date=cursor)
        phase_task_titles = list(default_tasks)

        if phase_type == PhaseType.EXECUTION:
            phase_task_titles = feature_lines if feature_lines else [
                "Core module development", "API layer implementation", "Frontend implementation", "Data model implementation",
            ]
            epic = Epic(project_id=project.id, title="Core Delivery Epic", phase_id=phase.id,
                         description="Auto-generated epic grouping execution-phase feature work.")
            epics.append(epic)

        wbs_task_counter = 0
        phase_task_ids: list[str] = []
        for title in phase_task_titles:
            wbs_task_counter += 1
            est_hours = estimate_duration(title)
            due = cursor + timedelta(hours=est_hours)
            task = Task(
                project_id=project.id,
                epic_id=epics[-1].id if (phase_type == PhaseType.EXECUTION and epics) else None,
                title=title[:200],
                status=TaskStatus.NOT_STARTED,
                priority=_infer_priority(title),
                estimated_hours=est_hours,
                start_date=cursor,
                due_date=due,
                wbs_code=f"{wbs_phase_counter}.{wbs_task_counter}",
            )
            tasks.append(task)
            phase_task_ids.append(task.id)
            cursor = due

        phase.end_date = cursor
        phases.append(phase)
        milestones.append(Milestone(
            project_id=project.id, name=f"{phase_name} complete", due_date=cursor,
            is_deliverable=phase_type in (PhaseType.EXECUTION, PhaseType.CLOSURE),
            dependent_task_ids=phase_task_ids,
        ))

    return phases, epics, tasks, milestones


def _infer_priority(title: str) -> Priority:
    t = title.lower()
    if any(k in t for k in ["security", "compliance", "go-live", "deployment", "critical", "charter"]):
        return Priority.CRITICAL
    if any(k in t for k in ["design", "architecture", "requirements", "testing", "uat"]):
        return Priority.HIGH
    if any(k in t for k in ["documentation", "review", "handover"]):
        return Priority.LOW
    return Priority.MEDIUM


def estimate_duration(task_title: str) -> float:
    """Heuristic effort estimate in hours, based on task-type keywords."""
    t = task_title.lower()
    if any(k in t for k in ["architecture", "design", "integration", "security"]):
        return 24.0
    if any(k in t for k in ["development", "implementation", "module", "api", "frontend", "build"]):
        return 32.0
    if any(k in t for k in ["testing", "uat", "qa"]):
        return 16.0
    if any(k in t for k in ["kickoff", "onboarding", "review", "sign-off", "handover"]):
        return 4.0
    return 12.0


def detect_dependencies(tasks: list[Task]) -> list[Dependency]:
    """Heuristic: sequential finish-to-start dependency chain within each phase/epic grouping,
    ordered by wbs_code. In production, an LLM or graph-based analysis over the brief's stated
    prerequisites could refine this."""
    deps: list[Dependency] = []
    ordered = sorted(tasks, key=lambda t: t.wbs_code or "")
    for prev, curr in zip(ordered, ordered[1:]):
        # only chain within the same phase (first wbs segment matches)
        prev_phase = (prev.wbs_code or "0").split(".")[0]
        curr_phase = (curr.wbs_code or "0").split(".")[0]
        if prev_phase == curr_phase:
            deps.append(Dependency(
                project_id=curr.project_id, predecessor_task_id=prev.id,
                successor_task_id=curr.id, dependency_type=DependencyType.FINISH_TO_START,
            ))
            curr.dependency_ids.append(prev.id)
    return deps


def calculate_critical_path(tasks: list[Task], dependencies: list[Dependency]) -> list[str]:
    """Longest-path-by-duration walk through the dependency DAG (simplified CPM)."""
    duration_by_id = {t.id: (t.estimated_hours or 1.0) for t in tasks}
    successors: dict[str, list[str]] = {}
    predecessors: dict[str, list[str]] = {}
    for d in dependencies:
        successors.setdefault(d.predecessor_task_id, []).append(d.successor_task_id)
        predecessors.setdefault(d.successor_task_id, []).append(d.predecessor_task_id)

    memo: dict[str, float] = {}

    def longest_from(task_id: str) -> float:
        if task_id in memo:
            return memo[task_id]
        children = successors.get(task_id, [])
        best = max((longest_from(c) for c in children), default=0.0)
        memo[task_id] = duration_by_id.get(task_id, 1.0) + best
        return memo[task_id]

    roots = [t.id for t in tasks if t.id not in predecessors]
    if not roots:
        roots = [t.id for t in tasks]
    best_root = max(roots, key=longest_from, default=None)
    if not best_root:
        return []

    path = [best_root]
    current = best_root
    while successors.get(current):
        current = max(successors[current], key=longest_from)
        path.append(current)
    return path


def generate_sprint_plan(project: Project, tasks: list[Task], sprint_length_days: int = 14) -> list[Sprint]:
    """For Agile/Hybrid methodologies: bucket execution tasks into sprints by estimated hours (assume 60 story hrs/sprint capacity)."""
    execution_tasks = [t for t in tasks if t.epic_id]
    sprints: list[Sprint] = []
    capacity_hours = 60.0
    sprint_num = 1
    bucket: list[Task] = []
    bucket_hours = 0.0
    start = min((t.start_date for t in execution_tasks if t.start_date), default=datetime.utcnow())

    def flush():
        nonlocal sprint_num, bucket, bucket_hours, start
        if not bucket:
            return
        end = start + timedelta(days=sprint_length_days)
        sprint = Sprint(
            project_id=project.id, name=f"Sprint {sprint_num}", sprint_number=sprint_num,
            start_date=start, end_date=end, task_ids=[t.id for t in bucket],
            committed_points=len(bucket),
        )
        for t in bucket:
            t.sprint_id = sprint.id
        sprints.append(sprint)
        sprint_num += 1
        start = end
        bucket = []
        bucket_hours = 0.0

    for t in execution_tasks:
        if bucket_hours + (t.estimated_hours or 0) > capacity_hours and bucket:
            flush()
        bucket.append(t)
        bucket_hours += t.estimated_hours or 0
    flush()
    return sprints
