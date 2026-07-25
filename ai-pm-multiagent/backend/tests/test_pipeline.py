"""
End-to-end smoke test of the full agentic pipeline in mock mode:
brief ingestion -> Atlas plans & executes -> Sentinel monitors -> approval flow.
Run: pytest -q  (from backend/)
"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

SAMPLE_BRIEF = """
Project Brief: Customer Loyalty Mobile App

We need to build a customer loyalty mobile app with an evolving feature set.
The team will work in an iterative, sprint-based fashion given fast-moving
market requirements and an MVP-first approach.

Key features:
- User registration and login
- Points earning engine tied to purchases
- Rewards catalog and redemption flow
- Push notification service
- Admin analytics dashboard

Third-party integration required with an existing payment gateway.
"""


@pytest.mark.asyncio
async def test_full_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/projects/ingest", json={
            "project_name": "Customer Loyalty Mobile App",
            "raw_text": SAMPLE_BRIEF,
        })
        assert resp.status_code == 200
        project = resp.json()
        assert project["methodology"] in ("agile_scrum", "hybrid")
        project_id = project["id"]

        tasks_resp = await client.get(f"/projects/{project_id}/tasks")
        assert tasks_resp.status_code == 200
        tasks = tasks_resp.json()
        assert len(tasks) > 0
        assert all(t["planner_task_id"] for t in tasks)

        dashboard_resp = await client.get(f"/dashboard/{project_id}")
        assert dashboard_resp.status_code == 200
        dashboard = dashboard_resp.json()
        assert dashboard["task_summary"]["total"] == len(tasks)

        sentinel_resp = await client.post(f"/agents/sentinel/monitor/{project_id}")
        assert sentinel_resp.status_code == 200

        notif_resp = await client.get(f"/projects/{project_id}/notifications")
        assert notif_resp.status_code == 200
        assert len(notif_resp.json()) > 0
