"""
FastAPI entrypoint for the AI-Powered Multi-Agent Project Management System.

Starts Sentinel's continuous background monitoring loop on app startup and
wires the Workflow Orchestrator's event subscriptions - after this module
loads, the agents are "alive": Atlas can plan+execute a project the moment a
brief is ingested, and Sentinel begins observing it without further user input.
"""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger
from app.agents import get_orchestrator, get_sentinel
from app.api import routes_projects, routes_approvals, routes_agents, routes_dashboard, routes_system

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    get_orchestrator()  # instantiates + wires event subscriptions (Atlas/Sentinel/HumanApproval routing)
    sentinel = get_sentinel()
    task = asyncio.create_task(sentinel.run_forever())
    logger.info(f"{settings.app_name} started | mock_integrations={settings.use_mock_integrations}")
    yield
    sentinel.stop()
    task.cancel()
    logger.info("Shutdown complete")


app = FastAPI(
    title="AI-Powered Multi-Agent Project Management System",
    description="Atlas (planning) + Sentinel (monitoring) + Orchestrator + Human Approval agents "
                "over Microsoft Planner/Teams/SharePoint via Azure AI Foundry.",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_projects.router)
app.include_router(routes_approvals.router)
app.include_router(routes_agents.router)
app.include_router(routes_dashboard.router)
app.include_router(routes_system.router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.app_name, "mock_integrations": settings.use_mock_integrations}
