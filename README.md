# YCLP CMS (Youth Civic Launchpad)

A focused FastAPI CMS backend for Youth Civic Launchpad operations.

## What is implemented

- **Role-based access control** with these roles: Admin, Program Manager, Finance/MEAL, Trainer/Facilitator, Partner Viewer, Youth Participant.
- **Program + cohort operations** where programs are YCLP editions (e.g., *Bardibas Feb 2026*) and initiatives represent post-bootcamp municipal implementations.
- **Applications workflow** with status transitions: Submitted → Shortlisted → Selected → Waitlist → Rejected.
- **Attendance + consent tracking** including final-day confirmation and photo/video consent logs.
- **Participant profiles** with team assignments, project submissions, awards/achievements, and certificate records.
- **Impact module** capturing pre/post metrics: civic confidence, design-thinking skill, community engagement hours, outputs delivered.
- **Governance workflow** draft → review → approved → published for content publishing.
- **Finance module** budget lines, expenses + bill upload URL, sponsor contributions, fund release requests, and export endpoint.
- **Data visualization-ready API** with indicator lift + executive summary line via `/impact/dashboard`.
- **Activity feed** for milestones, deadlines, and updates.
- **Search + filters** by program, school, ward.
- **Brand governance and public publishing** via brand assets, guardrails, and published-only endpoint.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs at: `http://127.0.0.1:8000/docs`

## API notes

- Pass role in query param for protected endpoints, e.g. `?role=admin`.
- Workflow enums are strict values, see schemas in `app/schemas.py`.

## Suggested next steps

1. Replace in-memory store with PostgreSQL + SQLAlchemy.
2. Move role info from query params to JWT auth.
3. Add file storage integration for bill uploads and certificate artifacts.
4. Add front-end admin portal for cohorts, dashboards, and content approvals.
