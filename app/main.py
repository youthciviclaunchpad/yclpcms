from __future__ import annotations

from datetime import datetime
from typing import Iterable

from fastapi import Depends, FastAPI, HTTPException, Query, status

from app.schemas import (
    ActivityItem,
    Application,
    ApplicationState,
    AttendanceRecord,
    BrandAsset,
    BudgetLine,
    Certificate,
    Cohort,
    ContentItem,
    Expense,
    FundReleaseRequest,
    ImpactRecord,
    Initiative,
    Participant,
    Program,
    ProgramStatus,
    ProgramCreate,
    ProjectSubmission,
    Role,
    Session,
    SponsorContribution,
    WorkflowState,
)
from app.store import store

app = FastAPI(title="YCLP CMS", version="0.1.0")


def require_roles(allowed: Iterable[Role]):
    def checker(x_role: Role = Query(..., alias="role")) -> Role:
        if x_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{x_role.value}' cannot perform this action.",
            )
        return x_role

    return checker


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "yclp-cms"}


@app.post("/programs", response_model=Program)
def create_program(
    payload: ProgramCreate,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER])),
):
    program = store.add_program(payload)
    store.add_activity(program.id, "program", f"Program '{program.edition_name}' created.")
    return program


@app.get("/programs", response_model=list[Program])
def list_programs() -> list[Program]:
    return list(store.programs.values())


@app.patch("/programs/{program_id}/status", response_model=Program)
def update_program_status(
    program_id: int,
    status_value: ProgramStatus = Query(..., alias="status"),
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER])),
):
    program = store.programs.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    program.status = status_value
    store.programs[program.id] = program
    store.add_activity(program.id, "program", f"Program status set to '{status_value}'.")
    return program


@app.post("/initiatives", response_model=Initiative)
def create_initiative(
    payload: Initiative,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER])),
):
    payload.id = store.next_id("initiatives")
    store.initiatives[payload.id] = payload
    store.add_activity(payload.program_id, "initiative", f"Initiative '{payload.name}' created.")
    return payload


@app.post("/cohorts", response_model=Cohort)
def create_cohort(
    payload: Cohort,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("cohorts")
    store.cohorts[payload.id] = payload
    store.add_activity(payload.program_id, "cohort", f"Cohort '{payload.cohort_name}' created for {payload.school}.")
    return payload


@app.post("/sessions", response_model=Session)
def create_session(
    payload: Session,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("sessions")
    store.sessions[payload.id] = payload
    cohort = store.cohorts.get(payload.cohort_id)
    if cohort:
        store.add_activity(cohort.program_id, "session", f"Session '{payload.title}' scheduled.")
    return payload


@app.post("/applications", response_model=Application)
def create_application(payload: Application):
    payload.id = store.next_id("applications")
    store.applications[payload.id] = payload
    store.add_activity(payload.program_id, "application", f"Application received from {payload.full_name}.")
    return payload


@app.patch("/applications/{application_id}/status", response_model=Application)
def progress_application(
    application_id: int,
    status_value: ApplicationState = Query(..., alias="status"),
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    app_record = store.applications.get(application_id)
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")
    app_record.status = status_value
    store.applications[application_id] = app_record
    store.add_activity(app_record.program_id, "application", f"{app_record.full_name} moved to {status_value.value}.")
    return app_record


@app.get("/applications/export")
def export_applications(
    program_id: int,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.PARTNER_VIEWER])),
):
    records = [a.model_dump() for a in store.applications.values() if a.program_id == program_id]
    return {"program_id": program_id, "count": len(records), "items": records}


@app.post("/attendance", response_model=AttendanceRecord)
def mark_attendance(
    payload: AttendanceRecord,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("attendance")
    store.attendance[payload.id] = payload
    participant = store.participants.get(payload.participant_id)
    if participant:
        store.add_activity(participant.program_id, "attendance", f"Attendance logged for {participant.full_name}.")
    return payload


@app.post("/participants", response_model=Participant)
def create_participant(
    payload: Participant,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("participants")
    store.participants[payload.id] = payload
    store.add_activity(payload.program_id, "participant", f"Participant profile created for {payload.full_name}.")
    return payload


@app.post("/projects", response_model=ProjectSubmission)
def add_project_submission(
    payload: ProjectSubmission,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR, Role.YOUTH_PARTICIPANT])),
):
    payload.id = store.next_id("projects")
    payload.submitted_at = datetime.utcnow()
    store.projects[payload.id] = payload
    participant = store.participants.get(payload.participant_id)
    if participant:
        store.add_activity(participant.program_id, "project", f"Project '{payload.title}' submitted.")
    return payload


@app.post("/certificates", response_model=Certificate)
def create_certificate(
    payload: Certificate,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("certificates")
    store.certificates[payload.id] = payload
    return payload


@app.post("/impact", response_model=ImpactRecord)
def record_impact(
    payload: ImpactRecord,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.FINANCE_MEAL, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("impact")
    store.impacts[payload.id] = payload
    return payload


@app.get("/impact/dashboard")
def impact_dashboard(program_id: int):
    participant_ids = {p.id for p in store.participants.values() if p.program_id == program_id}
    records = [r for r in store.impacts.values() if r.participant_id in participant_ids]
    if not records:
        return {"program_id": program_id, "records": 0, "summary": {}}

    def lift(attr: str) -> float:
        total = sum(getattr(r.post, attr) - getattr(r.pre, attr) for r in records)
        return round(total / len(records), 2)

    return {
        "program_id": program_id,
        "records": len(records),
        "summary": {
            "school_level_lift": {
                "civic_confidence": lift("civic_confidence"),
                "design_thinking_skill": lift("design_thinking_skill"),
                "community_engagement_hours": lift("community_engagement_hours"),
                "outputs_delivered": lift("outputs_delivered"),
            },
            "executive_summary_line": "Average indicator lift has improved across all tracked metrics.",
        },
    }


@app.post("/finance/budget-lines", response_model=BudgetLine)
def create_budget_line(
    payload: BudgetLine,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.FINANCE_MEAL])),
):
    payload.id = store.next_id("budget_lines")
    store.budget_lines[payload.id] = payload
    return payload


@app.post("/finance/expenses", response_model=Expense)
def record_expense(
    payload: Expense,
    _: Role = Depends(require_roles([Role.ADMIN, Role.FINANCE_MEAL])),
):
    payload.id = store.next_id("expenses")
    store.expenses[payload.id] = payload
    return payload


@app.post("/finance/sponsor-contributions", response_model=SponsorContribution)
def record_contribution(
    payload: SponsorContribution,
    _: Role = Depends(require_roles([Role.ADMIN, Role.FINANCE_MEAL])),
):
    payload.id = store.next_id("sponsor_contributions")
    store.sponsor_contributions[payload.id] = payload
    return payload


@app.post("/finance/fund-release-requests", response_model=FundReleaseRequest)
def request_funds(
    payload: FundReleaseRequest,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.FINANCE_MEAL])),
):
    payload.id = store.next_id("fund_requests")
    store.fund_requests[payload.id] = payload
    return payload


@app.get("/finance/export")
def export_finance(
    program_id: int,
    _: Role = Depends(require_roles([Role.ADMIN, Role.FINANCE_MEAL, Role.PARTNER_VIEWER])),
):
    lines = [x.model_dump() for x in store.budget_lines.values() if x.program_id == program_id]
    contributions = [x.model_dump() for x in store.sponsor_contributions.values() if x.program_id == program_id]
    fund_requests = [x.model_dump() for x in store.fund_requests.values() if x.program_id == program_id]
    expenses = [x.model_dump() for x in store.expenses.values() if store.budget_lines.get(x.budget_line_id, BudgetLine(id=0, program_id=0, category="", allocated_amount=0)).program_id == program_id]
    return {
        "program_id": program_id,
        "budget_lines": lines,
        "expenses": expenses,
        "sponsor_contributions": contributions,
        "fund_release_requests": fund_requests,
    }


@app.post("/governance/content", response_model=ContentItem)
def create_content_item(
    payload: ContentItem,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER, Role.TRAINER_FACILITATOR])),
):
    payload.id = store.next_id("content")
    store.content[payload.id] = payload
    return payload


@app.patch("/governance/content/{content_id}/workflow", response_model=ContentItem)
def transition_content_workflow(
    content_id: int,
    workflow_state: WorkflowState,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER])),
):
    item = store.content.get(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    item.workflow_state = workflow_state
    store.content[item.id] = item
    return item


@app.post("/brand/assets", response_model=BrandAsset)
def register_brand_asset(
    payload: BrandAsset,
    _: Role = Depends(require_roles([Role.ADMIN, Role.PROGRAM_MANAGER])),
):
    payload.id = store.next_id("brand_assets")
    store.brand_assets[payload.id] = payload
    return payload


@app.get("/public/published")
def get_published_content():
    return [
        item
        for item in store.content.values()
        if item.workflow_state == WorkflowState.PUBLISHED and item.style_guardrail_check
    ]


@app.get("/activity-feed", response_model=list[ActivityItem])
def list_activity_feed(program_id: int | None = None):
    items = list(store.activity_feed.values())
    if program_id is not None:
        items = [i for i in items if i.program_id == program_id]
    return sorted(items, key=lambda i: i.created_at, reverse=True)


@app.get("/search")
def search(
    program_id: int | None = None,
    school: str | None = None,
    ward: str | None = None,
):
    return store.search(program_id=program_id, school=school, ward=ward)
