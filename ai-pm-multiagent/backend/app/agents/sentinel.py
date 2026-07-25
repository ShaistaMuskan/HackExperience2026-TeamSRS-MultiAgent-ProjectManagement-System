"""
Sentinel - Monitoring & Risk Agent.

Runs continuously (background asyncio task started in main.py's lifespan,
polling every `settings.sentinel_poll_interval_seconds`) rather than waiting
for a user request. Each pass: Observe -> Reason (detect) -> Predict -> Mitigate.
"""
from __future__ import annotations
import asyncio
from datetime import datetime

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.db import get_repository
from app.models import Risk, RiskSeverity, ApprovalActionType
from app.tools import risk_tools, status_tools, teams_tools


class SentinelAgent(BaseAgent):
    agent_id = "sentinel"

    def __init__(self) -> None:
        super().__init__()
        self.repo = get_repository()
        self._running = False

    # ------------------------------------------------------------------
    async def monitor_project(self, project_id: str) -> dict:
        project = self.repo.get_project(project_id)
        if not project:
            raise KeyError(f"Unknown project {project_id}")

        tasks = self.repo.list_tasks(project_id)
        dependencies = self.repo.list_dependencies(project_id)
        resources = self.repo.list_resources()
        existing_risks = self.repo.list_risks(project_id)

        # OBSERVE + REASON: detect
        new_risks: list[Risk] = []
        new_risks += risk_tools.detect_late_tasks(tasks)
        new_risks += risk_tools.detect_dependency_violations(tasks, dependencies)
        for r in risk_tools.detect_resource_conflicts(resources):
            r.project_id = project_id
            new_risks.append(r)

        # de-dupe against existing open risks by title
        existing_titles = {r.title for r in existing_risks if not r.resolved}
        fresh_risks = [r for r in new_risks if r.title not in existing_titles]
        self.repo.save_risks(fresh_risks)
        all_risks = existing_risks + fresh_risks

        # PREDICT: recompute health
        health = risk_tools.calculate_project_risk(project, tasks, all_risks, resources)
        await status_tools.update_project_status(project, health)
        self.repo.save_project(project)

        # MITIGATE: for high/critical severity risks, generate a recommendation
        # and (per the Human Approval Agent workflow) request approval before acting.
        mitigations = []
        for risk in fresh_risks:
            if risk.severity in (RiskSeverity.HIGH, RiskSeverity.CRITICAL):
                suggestion = risk_tools.suggest_mitigation(risk, resources, tasks)
                risk.mitigation_plan = suggestion
                risk.requires_approval = True
                self.repo.save_risk(risk)
                # If there's a clean, single-task reassignment candidate, hand it
                # along structured (not just as text) so the Orchestrator can route
                # this straight to a REASSIGN_RESOURCE approval - one human click
                # then auto-executes the reassignment, rather than only recording
                # a decision that still needs a manual follow-up call.
                reassignment_candidate = risk_tools.find_reassignment_candidate(risk, resources, tasks)
                mitigations.append({"risk_id": risk.id, "suggestion": suggestion})
                await self.emit("sentinel.risk.detected", project_id, {
                    "risk_id": risk.id, "title": risk.title, "severity": risk.severity,
                    "mitigation_suggestion": suggestion,
                    "reassignment_candidate": reassignment_candidate,
                })

        if fresh_risks:
            channel_id = project.teams_channel_id or "channel_default"
            await teams_tools.send_teams_message(
                project_id=project_id, channel_id=channel_id,
                message=f"🛰️ Sentinel detected {len(fresh_risks)} new risk(s). Project health is now **{health.status}**.",
                sent_by_agent=self.agent_id,
            )

        self.remember(project_id, "observation", {
            "new_risks": len(fresh_risks), "health_status": health.status, "delay_probability": health.delay_probability,
        })
        await self.emit("sentinel.health.updated", project_id, {"health_status": health.status})

        return {"health": health, "new_risks": fresh_risks, "mitigations": mitigations}

    # ------------------------------------------------------------------
    # Continuous background monitoring loop
    # ------------------------------------------------------------------
    async def run_forever(self) -> None:
        settings = get_settings()
        self._running = True
        self.logger.info(f"Sentinel monitoring loop started (interval={settings.sentinel_poll_interval_seconds}s)")
        while self._running:
            for project in self.repo.list_projects():
                try:
                    await self.monitor_project(project.id)
                except Exception as exc:  # fault tolerance: one project's failure shouldn't kill the loop
                    self.logger.exception(f"Sentinel monitoring pass failed for project {project.id}: {exc}")
            await asyncio.sleep(settings.sentinel_poll_interval_seconds)

    def stop(self) -> None:
        self._running = False
