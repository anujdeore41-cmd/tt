from datetime import datetime, time
from pydantic import BaseModel, Field, model_validator


class GenerateRequest(BaseModel):
    academic_year_id: int | None = None  # None = all years
    reason: str = Field(default="", max_length=255)


class VersionOut(BaseModel):
    id: int
    version_number: int
    academic_year_id: int | None
    status: str
    created_by: int | None
    generation_job_id: int | None
    published_at: datetime | None
    last_updated_at: datetime | None
    reason: str
    stats: dict
    query_deadline: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntryOut(BaseModel):
    id: int
    timetable_version_id: int
    day_of_week: str
    time_slot_id: int
    academic_year_id: int
    division_id: int
    subject_id: int | None
    faculty_id: int | None
    room_id: int | None
    laboratory_id: int | None
    batch_id: int | None
    session_type: str
    is_substitute_override: bool
    effective_date: datetime | None
    recurring_entry_id: int | None
    notes: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntryDetail(EntryOut):
    subject_name: str | None = None
    subject_code: str | None = None
    faculty_name: str | None = None
    division_name: str | None = None
    academic_year_name: str | None = None
    room_number: str | None = None
    lab_number: str | None = None
    batch_name: str | None = None
    slot_start: time | None = None
    slot_end: time | None = None
    slot_label: str | None = None


class ModifyEntryRequest(BaseModel):
    faculty_id: int | None = None
    room_id: int | None = None
    laboratory_id: int | None = None
    time_slot_id: int | None = None
    subject_id: int | None = None
    division_id: int | None = None
    batch_id: int | None = None
    reason: str = Field(default="", max_length=255)
    auto_resolve: bool = False  # try smart local rescheduling when the direct change conflicts


class ConflictOut(BaseModel):
    id: int
    timetable_version_id: int | None
    conflict_type: str
    severity: str
    description: str
    day_of_week: str | None
    time_slot_id: int | None
    faculty_id: int | None
    room_id: int | None
    laboratory_id: int | None
    division_id: int | None
    subject_id: int | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobOut(BaseModel):
    id: int
    academic_year_id: int | None
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    required_sessions: int
    scheduled_sessions: int
    unscheduled_sessions: int
    result: dict
    error: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangeOut(BaseModel):
    id: int
    timetable_version_id: int
    timetable_entry_id: int
    changes: dict
    reason: str
    change_kind: str
    created_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PublishRequest(BaseModel):
    reason: str = Field(default="", max_length=255)


class TimetableQueryIn(BaseModel):
    timetable_entry_id: int | None = None
    query_type: str = Field(default="OTHER")
    message: str = Field(min_length=3, max_length=1000)

    @model_validator(mode="after")
    def validate(self):
        allowed = {"WRONG_FACULTY", "WRONG_ROOM", "TIMING_ISSUE", "SUBJECT_ISSUE", "AVAILABILITY_ISSUE", "OTHER"}
        if self.query_type not in allowed:
            raise ValueError(f"query_type must be one of {sorted(allowed)}")
        return self


class TimetableQueryOut(BaseModel):
    id: int
    faculty_id: int
    timetable_version_id: int
    timetable_entry_id: int | None
    query_type: str
    message: str
    status: str
    resolution_note: str
    created_at: datetime
    resolved_at: datetime | None
    faculty_name: str | None = None

    model_config = {"from_attributes": True}


class QueryResolveRequest(BaseModel):
    status: str = Field(default="RESOLVED")  # RESOLVED / REJECTED
    resolution_note: str = Field(default="", max_length=1000)
