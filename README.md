# AI-Powered Multi-Agent Project Management System

# HackExperience 2026 - Track 2C - Workflow Automation - AI For Living
## Team SRS - Sakthi, Rhithika, Shaista

An autonomous multi-agent platform (not a chatbot) that plans, executes, and monitors software projects through four collaborating AI agents — **Atlas** (planning), **Sentinel** (continuous monitoring & risk), a **Workflow Orchestrator** (event routing), and a **Human Approval Agent** (approval gate) — invoking Microsoft Planner, Teams, SharePoint, and Outlook via Microsoft Graph, with reasoning and RAG powered by Azure AI Foundry and Azure AI Search.

Runs out of the box with **zero Azure/Microsoft 365 credentials** (mock integration mode). See `docs/architecture/azure-foundry-m365-integration-guide.md` for the exact steps to connect the real tenant.

## Quick start

```bash
# Backend
cd backend
python -m venv .venv && source 
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
# -> http://localhost:8000/docs

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# -> http://localhost:5173
```

Or with Docker:
```bash
docker compose up --build
```

Try it:
```bash
curl -X POST http://localhost:8000/projects/ingest \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Customer Loyalty App", "raw_text": "Iterative sprint-based MVP with evolving requirements..."}'
```

Watch the logs: Atlas selects a methodology, builds a WBS, creates Planner tasks and a Teams channel, then Sentinel automatically starts monitoring the new project.

## Example Prompt
Project Name: E-Commerce Website
Project Description: Project Objective

Develop a responsive e-commerce web application for small businesses.

Business Requirements

Customers should be able to:
- Register and login
- Browse products
- Add products to a shopping cart
- Checkout securely
- Track orders

Administrators should be able to:
- Manage products
- Manage inventory
- View sales reports
- Process refunds

Project Constraints

- Budget: SGD 120,000
- Timeline: 4 months
- Team: 5 Developers, 2 Designers, 1 QA Engineer

Requirements are expected to evolve during development due to stakeholder feedback.

Weekly sprint reviews are required.

The platform must support at least 20,000 concurrent users.

PCI-DSS compliant payment gateway is required.

High availability is mandatory.

- **`docs/SRS_AI_PM_MultiAgent.docx`** — full Software Requirements Specification: architecture, agent design, data models, 
## Repository layout

```
backend/app/
├── agents/          Atlas, Sentinel, Orchestrator, Human Approval
├── tools/           Planner/Teams/SharePoint/Outlook/RAG/planning/risk tool functions
├── integrations/    interfaces.py (ports) + mock/ (default) + azure/ (real, production)
├── models/          Pydantic domain models
├── db/              In-memory repository (MVP) + SQLAlchemy production schema
├── orchestration/   Async event bus
├── memory/          Per-agent, per-project memory store
├── knowledge_base/  Seed RAG documents (methodology guides, SOPs, historical projects)
├── core/            config.py (mock/real client factory), security.py (RBAC), logging.py
└── api/             FastAPI routes

frontend/src/        React + TypeScript + Tailwind dashboard
```

## Key design decision: mock-first, one flag from production

Every enterprise integration (Planner, Teams, Outlook, SharePoint, Azure AI Search, Azure OpenAI/Foundry, Blob Storage, Key Vault) is defined as an abstract interface in `backend/app/integrations/interfaces.py`, with a working in-memory mock implementation and a real Azure/Graph implementation. Set `USE_MOCK_INTEGRATIONS=false` and supply credentials (see the integration guide) to go live — no agent, tool, or API code changes required.

## Testing

```bash
cd backend && pytest -q
```

Runs a full end-to-end smoke test: brief ingestion → Atlas plans and executes (Planner + Teams + SharePoint tool calls) → Sentinel monitoring pass → dashboard aggregation.
