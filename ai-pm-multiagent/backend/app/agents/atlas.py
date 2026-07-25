"""
Atlas - Project Intelligence Agent.

Observe (read brief + retrieve knowledge) -> Reason (classify, choose
methodology) -> Plan (WBS/phases/epics/tasks/milestones/dependencies/sprints/
critical path) -> Act (Planner + Teams + SharePoint tool calls).

Atlas does not just return JSON - `run_full_pipeline` performs the enterprise
tool calls itself and only stops to emit events / request approval where the
spec calls for it.
"""
from __future__ import annotations
from datetime import datetime

from app.agents.base import BaseAgent
from app.core.config import get_llm_client
from app.db import get_repository
from app.models import (
    Project, ProjectBrief, MethodologyType, Task, TaskStatus,
)
from app.tools import planner_tools, teams_tools, sharepoint_outlook_tools, rag_tools, planning_tools, risk_tools


class AtlasAgent(BaseAgent):
    agent_id = "atlas"

    def __init__(self) -> None:
        super().__init__()
        self.repo = get_repository()
        self.llm = get_llm_client()
        self.register_tool("create_planner_task", planner_tools.create_planner_task)
        self.register_tool("update_planner_task", planner_tools.update_planner_task)
        self.register_tool("create_bucket", planner_tools.create_bucket)
        self.register_tool("send_teams_message", teams_tools.send_teams_message)
        self.register_tool("create_channel", teams_tools.create_channel)
        self.register_tool("schedule_meeting", teams_tools.schedule_meeting)
        self.register_tool("upload_document", sharepoint_outlook_tools.upload_document)
        self.register_tool("retrieve_rag_documents", rag_tools.retrieve_rag_documents)
        self.register_tool("generate_wbs", planning_tools.generate_wbs)
        self.register_tool("detect_dependencies", planning_tools.detect_dependencies)
        self.register_tool("estimate_duration", planning_tools.estimate_duration)

    # ------------------------------------------------------------------
    # OBSERVE
    # ------------------------------------------------------------------
    async def observe(self, brief: ProjectBrief) -> list[dict]:
        self.logger.info(f"[OBSERVE] reading brief '{brief.source_filename}'")
        knowledge = await rag_tools.retrieve_rag_documents(query=brief.raw_text[:500], top_k=5)
        self.remember(brief.id, "observation", {"brief_id": brief.id, "knowledge_doc_ids": [d["id"] for d in knowledge]})
        return knowledge

    # ------------------------------------------------------------------
    # REASON
    # ------------------------------------------------------------------
    async def reason(self, brief: ProjectBrief) -> tuple[MethodologyType, str, float]:
        methodology_resp = await self.llm.chat(
            system_prompt="TASK: methodology_selection\nYou are Atlas, an expert PMO agent. Select the best-fit "
                          "methodology (agile_scrum, kanban, waterfall, prince2, hybrid) for the given brief. "
                          "Respond with ONLY a JSON object, no markdown fences, matching exactly this shape: "
                          '{"methodology": "agile_scrum|kanban|waterfall|prince2|hybrid", '
                          '"rationale": "<one or two sentences>", "confidence": <float 0-1>}',
            messages=[{"role": "user", "content": brief.raw_text}],
        )
        complexity_resp = await self.llm.chat(
            system_prompt="TASK: complexity_scoring\nScore project complexity 0-1 based on the brief. "
                          "Respond with ONLY a JSON object, no markdown fences, matching exactly this shape: "
                          '{"complexity_score": <float 0-1>, "signals": {"integration_terms_found": <int>, "word_count": <int>}}',
            messages=[{"role": "user", "content": brief.raw_text}],
        )
        import json
        methodology_data = json.loads(methodology_resp["content"])
        complexity_data = json.loads(complexity_resp["content"])
        methodology = MethodologyType(methodology_data["methodology"])
        rationale = methodology_data["rationale"]
        complexity = complexity_data["complexity_score"]
        self.logger.info(f"[REASON] methodology={methodology} complexity={complexity} rationale={rationale}")
        return methodology, rationale, complexity

    # ------------------------------------------------------------------
    # PLAN
    # ------------------------------------------------------------------
    def plan(self, project: Project, brief: ProjectBrief):
        phases, epics, tasks, milestones = planning_tools.generate_wbs(
            project, brief.raw_text, project.methodology, start_date=datetime.utcnow(),
        )
        dependencies = planning_tools.detect_dependencies(tasks)
        sprints = []
        if project.methodology in (MethodologyType.AGILE_SCRUM, MethodologyType.HYBRID):
            sprints = planning_tools.generate_sprint_plan(project, tasks)
        critical_path = planning_tools.calculate_critical_path(tasks, dependencies)
        for t in tasks:
            if t.id in critical_path:
                t.tags.append("critical_path")
        project.phases = phases
        return {
            "epics": epics, "tasks": tasks, "milestones": milestones,
            "dependencies": dependencies, "sprints": sprints, "critical_path": critical_path,
        }

    # ------------------------------------------------------------------
    # ACT (enterprise tool calls)
    # ------------------------------------------------------------------
    async def act(self, project: Project, plan_output: dict):
        tasks: list[Task] = plan_output["tasks"]

        # 1. SharePoint project folder
        folder = await sharepoint_outlook_tools.create_sharepoint_project_folder(project.name)
        project.sharepoint_folder_url = folder["url"]

        # 2. Teams channel + kickoff notification
        channel = await teams_tools.create_channel(team_id="team_default", name=project.name[:50])
        project.teams_channel_id = channel["id"]
        await teams_tools.send_teams_message(
            project_id=project.id, channel_id=channel["id"],
            message=(f"🧭 Atlas has planned **{project.name}** using **{project.methodology}**. "
                     f"{len(tasks)} tasks across {len(project.phases)} phases created in Planner."),
            sent_by_agent=self.agent_id,
        )

        # 3. Planner plan + buckets (one per phase) + tasks
        planner_plan = await planner_tools.create_plan(project.id, title=project.name)
        project.planner_plan_id = planner_plan.id
        bucket_by_phase: dict[str, str] = {}
        for phase in project.phases:
            bucket = await planner_tools.create_bucket(planner_plan.id, phase.name)
            bucket_by_phase[phase.name] = bucket.id
            planner_plan.buckets.append(bucket)
        self.repo.save_planner_plan(planner_plan)

        resources = self.repo.list_resources()
        for i, task in enumerate(tasks):
            phase_name = self._phase_for_task(project, task)
            bucket_id = bucket_by_phase.get(phase_name, next(iter(bucket_by_phase.values())))
            assignee = resources[i % len(resources)] if resources else None
            if assignee:
                planner_tools.assign_task(task, assignee)
            planner_task = await planner_tools.create_planner_task(
                planner_plan.id, bucket_id, task, assignees=[assignee] if assignee else [],
            )
            task.planner_task_id = planner_task.id
            self.repo.save_task(task)

        self.repo.save_milestones(plan_output["milestones"])
        self.repo.save_sprints(plan_output["sprints"])
        self.repo.save_dependencies(plan_output["dependencies"])
        self.repo.save_project(project)

        await self.emit("atlas.plan.created", project.id, {
            "task_count": len(tasks), "methodology": project.methodology,
            "sprint_count": len(plan_output["sprints"]),
        })
        self.remember(project.id, "decision", {
            "action": "plan_created", "methodology": project.methodology, "task_count": len(tasks),
        })
        return project

    @staticmethod
    def _phase_for_task(project: Project, task: Task) -> str:
        if not task.wbs_code:
            return project.phases[0].name if project.phases else ""
        idx = int(task.wbs_code.split(".")[0]) - 1
        if 0 <= idx < len(project.phases):
            return project.phases[idx].name
        return project.phases[0].name if project.phases else ""

    # ------------------------------------------------------------------
    # FULL PIPELINE - the single entrypoint the API calls
    # ------------------------------------------------------------------
    async def run_full_pipeline(self, brief: ProjectBrief, project_name: str) -> Project:
        self.repo.save_brief(brief)
        await self.observe(brief)
        methodology, rationale, complexity = await self.reason(brief)

        project = Project(
            name=project_name, description=brief.raw_text[:500], brief_id=brief.id,
            methodology=methodology, methodology_rationale=rationale, complexity_score=complexity,
            start_date=datetime.utcnow(),
        )
        self.repo.save_project(project)

        plan_output = self.plan(project, brief)

        # seed baseline risk register from detected dependency risk & resourcing
        baseline_risks = risk_tools.detect_dependency_violations(plan_output["tasks"], plan_output["dependencies"])
        self.repo.save_risks(baseline_risks)

        project = await self.act(project, plan_output)
        return project
