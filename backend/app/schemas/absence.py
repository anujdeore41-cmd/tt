from datetime import datetime, time
from pydantic import BaseModel, Field, field_validator

ABSENCE_REASONS = {"SICK_LEAVE", "PERSONAL", "OFFICIAL_DUTY", "OTHER"}


class AbsenceIn(BaseModel):
    faculty_id: int | None = None  # required for admins creating on behalf; defaults to self for faculty
    absence_date: str = Field(min_length=8, max_length=10)  # YYYY-MM-DD
    reason: str = Field(default="OTHER")
    message: str = Field(default="", max_length=2000)
    attachment_ids: list[int] = Field(default_factory=list)

    @field_validator("absence_date")
    @classmethod
    def date_valid(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("absence_date must be YYYY-MM-DD")
        return v

    @field_validator("reason")
    @classmethod
    def reason_valid(cls, v: str) -> str:
        if v not in ABSENCE_REASONS:
            raise ValueError(f"reason must be one of {sorted(ABSENCE_REASONS)}")
        return v


class AbsenceOut(BaseModel):
    id: int
    faculty_id: int
    absence_date: datetime
    reason: str
    message: str
    status: str
    created_at: datetime
    faculty_name: str | None = None
    affected_lectures: list[dict] = []

    model_config = {"from_attributes": True}


class AffectedLectureOut(BaseModel):
    id: int
    absence_id: int
    timetable_entry_id: int
    time_slot_id: int | None
    day_of_week: str | None
    division_id: int | None
    subject_id: int | None
    room_id: int | None
    laboratory_id: int | None
    batch_id: int | None
    session_type: str
    # joined display fields
    subject_name: str | None = None
    faculty_name: str | None = None
    division_name: str | None = None
    academic_year_name: str | None = None
    room_number: str | None = None
    lab_number: str | None = None
    batch_name: str | None = None
    slot_start: time | None = None
    slot_end: time | None = None

    model_config = {"from_attributes": True}


class SubstituteCandidate(BaseModel):
    faculty_id: int
    name: str
    designation: str | None = None
    department: str = ""
    eligible: bool
    weekly_workload_hours: float
    max_weekly_hours: int
    has_free_slot: bool
    teaches_subject: bool
    score: float
    reasons: list[str] = []
