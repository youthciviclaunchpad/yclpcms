from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from app import schemas


class InMemoryStore:
    def __init__(self) -> None:
        self._ids = defaultdict(int)
        self.programs: dict[int, schemas.Program] = {}
        self.initiatives: dict[int, schemas.Initiative] = {}
        self.cohorts: dict[int, schemas.Cohort] = {}
        self.sessions: dict[int, schemas.Session] = {}
        self.applications: dict[int, schemas.Application] = {}
        self.participants: dict[int, schemas.Participant] = {}
        self.attendance: dict[int, schemas.AttendanceRecord] = {}
        self.projects: dict[int, schemas.ProjectSubmission] = {}
        self.certificates: dict[int, schemas.Certificate] = {}
        self.impacts: dict[int, schemas.ImpactRecord] = {}
        self.budget_lines: dict[int, schemas.BudgetLine] = {}
        self.expenses: dict[int, schemas.Expense] = {}
        self.sponsor_contributions: dict[int, schemas.SponsorContribution] = {}
        self.fund_requests: dict[int, schemas.FundReleaseRequest] = {}
        self.activity_feed: dict[int, schemas.ActivityItem] = {}
        self.brand_assets: dict[int, schemas.BrandAsset] = {}
        self.content: dict[int, schemas.ContentItem] = {}

    def next_id(self, bucket: str) -> int:
        self._ids[bucket] += 1
        return self._ids[bucket]

    def add_program(self, payload: schemas.ProgramCreate) -> schemas.Program:
        program = schemas.Program(id=self.next_id("programs"), **payload.model_dump())
        self.programs[program.id] = program
        return program

    def add_activity(self, program_id: int, item_type: str, message: str) -> schemas.ActivityItem:
        activity = schemas.ActivityItem(
            id=self.next_id("activity"),
            program_id=program_id,
            item_type=item_type,
            message=message,
            created_at=datetime.utcnow(),
        )
        self.activity_feed[activity.id] = activity
        return activity

    def search(self, *, program_id: int | None = None, school: str | None = None, ward: str | None = None) -> dict[str, list[Any]]:
        cohorts = list(self.cohorts.values())
        participants = list(self.participants.values())
        applications = list(self.applications.values())

        if program_id is not None:
            cohorts = [c for c in cohorts if c.program_id == program_id]
            participants = [p for p in participants if p.program_id == program_id]
            applications = [a for a in applications if a.program_id == program_id]

        if school:
            cohorts = [c for c in cohorts if school.lower() in c.school.lower()]
            participants = [p for p in participants if school.lower() in p.school.lower()]
            applications = [a for a in applications if school.lower() in a.school.lower()]

        if ward:
            cohorts = [c for c in cohorts if ward.lower() in c.ward.lower()]

        return {
            "cohorts": cohorts,
            "participants": participants,
            "applications": applications,
        }


store = InMemoryStore()
