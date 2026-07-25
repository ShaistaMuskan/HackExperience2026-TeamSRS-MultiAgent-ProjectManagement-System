"""
Production database schema (SQLAlchemy 2.0 declarative), targeting either
Azure Database for PostgreSQL or Azure Cosmos DB (via its Postgres-compatible
API / SQLAlchemy dialect). This is the schema the SRS "Database Schema"
section documents.

NOT wired into the runtime in the hackathon MVP - app/db/repository.py's
in-memory store is used instead so the demo needs zero infrastructure.
Post-hackathon: implement a `SqlRepository(Repository)` backed by these
tables and swap it in via app/core/config.py.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProjectORM(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    brief_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    methodology: Mapped[str | None] = mapped_column(String(50), nullable=True)
    methodology_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sponsor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_manager: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    target_end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    health: Mapped[str] = mapped_column(String(20), default="on_track")
    planner_plan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    teams_channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sharepoint_folder_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["TaskORM"]] = relationship(back_populates="project")
    risks: Mapped[list["RiskORM"]] = relationship(back_populates="project")


class ProjectPhaseORM(Base):
    __tablename__ = "project_phases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    phase_type: Mapped[str] = mapped_column(String(30))
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")


class EpicORM(Base):
    __tablename__ = "epics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    phase_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class TaskORM(Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    epic_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("epics.id"), nullable=True)
    parent_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    wbs_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    planner_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sprint_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project: Mapped["ProjectORM"] = relationship(back_populates="tasks")


class DependencyORM(Base):
    __tablename__ = "dependencies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    predecessor_task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"))
    successor_task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"))
    dependency_type: Mapped[str] = mapped_column(String(30), default="finish_to_start")
    lag_days: Mapped[float] = mapped_column(Float, default=0)
    is_violated: Mapped[bool] = mapped_column(Boolean, default=False)


class MilestoneORM(Base):
    __tablename__ = "milestones"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    due_date: Mapped[datetime] = mapped_column(DateTime)
    is_deliverable: Mapped[bool] = mapped_column(Boolean, default=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    on_critical_path: Mapped[bool] = mapped_column(Boolean, default=False)


class SprintORM(Base):
    __tablename__ = "sprints"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(100))
    sprint_number: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    goal: Mapped[str] = mapped_column(Text, default="")
    committed_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_points: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RiskORM(Base):
    __tablename__ = "risks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(20))
    probability: Mapped[float] = mapped_column(Float)
    impact_score: Mapped[float] = mapped_column(Float)
    detected_by: Mapped[str] = mapped_column(String(50), default="sentinel")
    mitigation_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["ProjectORM"] = relationship(back_populates="risks")


class ResourceORM(Base):
    __tablename__ = "resources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(100))
    weekly_capacity_hours: Mapped[float] = mapped_column(Float, default=40)
    allocated_hours: Mapped[float] = mapped_column(Float, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


class ApprovalRequestORM(Base):
    __tablename__ = "approval_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    requested_by_agent: Mapped[str] = mapped_column(String(50))
    action_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    teams_card_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class NotificationORM(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    channel: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    sent_by_agent: Mapped[str] = mapped_column(String(50))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)


class AgentMemoryORM(Base):
    """One row per (agent_id, project_id); `content` holds the serialized AgentMemory JSON."""
    __tablename__ = "agent_memory"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(50))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    content: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
