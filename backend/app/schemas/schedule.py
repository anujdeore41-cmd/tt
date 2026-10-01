from datetime import datetime, time
from pydantic import BaseModel, Field, model_validator


class WorkingDayOut(BaseModel):
    id: int
    day_of_week: str
    day_number: int
    is_working: bool
    sequence: int

    model_config = {"from_attributes": True}


class WorkingDaysUpdate(BaseModel):
    """Update which of the 7 days are working days."""
    working_days: list[str] = Field(min_length=1, max_length=7)  # e.g. ["MON","TUE",...]

    @model_validator(mode="after")
    def validate(self):
        valid = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}
        cleaned = [d.upper() for d in self.working_days]
        if any(d not in valid for d in cleaned):
            raise ValueError("working_days must contain valid day codes MON..SUN")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("duplicate days are not allowed")
        self.working_days = cleaned
        return self


class BreakIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    duration_minutes: int = Field(ge=1, le=240)
    after_lectures: int = Field(ge=1, le=20)
    sequence: int = Field(default=0)
    break_kind: str = Field(default="BREAK")  # BREAK / LUNCH

    @model_validator(mode="after")
    def validate(self):
        if self.break_kind not in {"BREAK", "LUNCH"}:
            raise ValueError("break_kind must be BREAK or LUNCH")
        return self


class BreakUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    duration_minutes: int | None = Field(default=None, ge=1, le=240)
    after_lectures: int | None = Field(default=None, ge=1, le=20)
    break_kind: str | None = None


class BreakOut(BaseModel):
    id: int
    name: str
    duration_minutes: int
    after_lectures: int
    sequence: int
    break_kind: str

    model_config = {"from_attributes": True}


class TimeSlotOut(BaseModel):
    id: int
    start_time: time
    end_time: time
    sequence: int
    slot_type: str
    is_teaching_period: bool
    break_id: int | None
    label: str

    model_config = {"from_attributes": True}


class ScheduleConfigurationIn(BaseModel):
    working_days_count: int = Field(ge=1, le=7)
    college_start_time: time
    college_end_time: time
    lecture_duration_minutes: int = Field(ge=15, le=180)
    lecture_duration_custom: bool = False
    default_practical_duration_minutes: int | None = Field(default=None, ge=30, le=300)
    max_lectures_per_day_per_division: int = Field(default=8, ge=1, le=16)
    same_faculty_division_day_penalty: int = Field(default=100, ge=0, le=10000)
    same_subject_division_day_penalty: int = Field(default=60, ge=0, le=10000)
    gap_penalty: int = Field(default=30, ge=0, le=10000)
    consecutive_lecture_penalty: int = Field(default=40, ge=0, le=10000)
    workload_balance_penalty: int = Field(default=50, ge=0, le=10000)
    query_window_minutes: int = Field(default=60, ge=5, le=1440)
    notification_lead_minutes: int = Field(default=0, ge=0, le=1440)

    @model_validator(mode="after")
    def validate(self):
        if self.college_end_time <= self.college_start_time:
            raise ValueError("college_end_time must be after college_start_time")
        return self


class ScheduleConfigurationUpdate(BaseModel):
    working_days_count: int | None = Field(default=None, ge=1, le=7)
    college_start_time: time | None = None
    college_end_time: time | None = None
    lecture_duration_minutes: int | None = Field(default=None, ge=15, le=180)
    lecture_duration_custom: bool | None = None
    default_practical_duration_minutes: int | None = Field(default=None, ge=30, le=300)
    max_lectures_per_day_per_division: int | None = Field(default=None, ge=1, le=16)
    same_faculty_division_day_penalty: int | None = Field(default=None, ge=0, le=10000)
    same_subject_division_day_penalty: int | None = Field(default=None, ge=0, le=10000)
    gap_penalty: int | None = Field(default=None, ge=0, le=10000)
    consecutive_lecture_penalty: int | None = Field(default=None, ge=0, le=10000)
    workload_balance_penalty: int | None = Field(default=None, ge=0, le=10000)
    query_window_minutes: int | None = Field(default=None, ge=5, le=1440)
    notification_lead_minutes: int | None = Field(default=None, ge=0, le=1440)


class ScheduleConfigurationOut(ScheduleConfigurationIn):
    id: int
    breaks: list[BreakOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleBreaksIn(BaseModel):
    breaks: list[BreakIn] = Field(max_length=6)


class SchedulePreviewSlot(BaseModel):
    start_time: time
    end_time: time
    slot_type: str
    is_teaching_period: bool
    label: str
    sequence: int


class SchedulePreviewOut(BaseModel):
    slots: list[SchedulePreviewSlot]
    teaching_periods: int
    total_break_minutes: int
    fits_in_college_hours: bool


class ValidationIssue(BaseModel):
    code: str
    severity: str  # ERROR / WARNING
    message: str
    fix_hint: str = ""


class ValidationOut(BaseModel):
    valid: bool
    issues: list[ValidationIssue]
