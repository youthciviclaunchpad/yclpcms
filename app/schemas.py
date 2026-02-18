from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Role(str, Enum):
    ADMIN = "admin"
    PROGRAM_MANAGER = "program_manager"
    FINANCE_MEAL = "finance_meal"
    TRAINER_FACILITATOR = "trainer_facilitator"
    PARTNER_VIEWER = "partner_viewer"
    YOUTH_PARTICIPANT = "youth_participant"


class ProgramStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class WorkflowState(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


class ApplicationState(str, Enum):
    SUBMITTED = "submitted"
    SHORTLISTED = "shortlisted"
    SELECTED = "selected"
    WAITLIST = "waitlist"
    REJECTED = "rejected"


class Program(BaseModel):
    id: int
    edition_name: str = Field(description="YCLP edition e.g., Bardibas Feb 2026")
    municipality: str
    start_date: date
    end_date: date
    status: ProgramStatus = ProgramStatus.DRAFT
    workflow_state: WorkflowState = WorkflowState.DRAFT


class ProgramCreate(BaseModel):
    edition_name: str
    municipality: str
    start_date: date
    end_date: date


class Initiative(BaseModel):
    id: int
    program_id: int
    name: str = Field(description="Post-bootcamp municipal implementation")
    municipality: str
    status: WorkflowState = WorkflowState.DRAFT


class Cohort(BaseModel):
    id: int
    program_id: int
    school: str
    ward: str
    cohort_name: str


class Session(BaseModel):
    id: int
    cohort_id: int
    title: str
    scheduled_at: datetime
    facilitator: str


class Application(BaseModel):
    id: int
    program_id: int
    full_name: str
    school: str
    grade: str
    phone: str
    status: ApplicationState = ApplicationState.SUBMITTED


class AttendanceRecord(BaseModel):
    id: int
    session_id: int
    participant_id: int
    present: bool
    final_day_confirmed: bool = False
    photo_video_consent: bool


class Participant(BaseModel):
    id: int
    program_id: int
    full_name: str
    school: str
    grade: str
    contact: str
    team: Optional[str] = None
    awards: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class ProjectSubmission(BaseModel):
    id: int
    participant_id: int
    title: str
    summary: str
    submitted_at: datetime


class Certificate(BaseModel):
    id: int
    participant_id: int
    certificate_type: str
    template_locked: bool = True
    workflow_state: WorkflowState = WorkflowState.DRAFT


class SurveyMetric(BaseModel):
    civic_confidence: float
    design_thinking_skill: float
    community_engagement_hours: float
    outputs_delivered: float


class ImpactRecord(BaseModel):
    id: int
    participant_id: int
    pre: SurveyMetric
    post: SurveyMetric


class BudgetLine(BaseModel):
    id: int
    program_id: int
    category: str
    allocated_amount: float


class Expense(BaseModel):
    id: int
    budget_line_id: int
    amount: float
    description: str
    bill_url: Optional[str] = None


class SponsorContribution(BaseModel):
    id: int
    program_id: int
    sponsor_name: str
    amount: float


class FundReleaseRequest(BaseModel):
    id: int
    program_id: int
    amount: float
    reason: str
    approved: bool = False


class ActivityItem(BaseModel):
    id: int
    program_id: int
    item_type: str
    message: str
    created_at: datetime


class BrandAsset(BaseModel):
    id: int
    asset_type: str
    name: str
    value: str
    locked: bool = True


class ContentItem(BaseModel):
    id: int
    section: str
    title: str
    body: str
    workflow_state: WorkflowState = WorkflowState.DRAFT
    style_guardrail_check: bool = True
