from datetime import datetime, time
from pydantic import BaseModel, Field, EmailStr, model_validator

DAYS = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}


class FacultyIn(BaseModel):
    faculty_code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(default="", max_length=32)
    department: str = Field(default="", max_length=128)
    designation_id: int | None = None
    max_weekly_hours: int = Field(default=20, ge=1, le=60)
    min_weekly_hours: int = Field(default=0, ge=0, le=40)
    preferred_working_hours: str = Field(default="", max_length=64)
    can_take_theory: bool = True
    can_take_practical: bool = False
    substitute_eligible: bool = True
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def validate(self):
        if self.status not in {"ACTIVE", "INACTIVE", "ON_LEAVE"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ON_LEAVE")
        if self.min_weekly_hours > self.max_weekly_hours:
            raise ValueError("min_weekly_hours cannot exceed max_weekly_hours")
        return self


class FacultyUpdate(BaseModel):
    faculty_code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    department: str | None = Field(default=None, max_length=128)
    designation_id: int | None = None
    max_weekly_hours: int | None = Field(default=None, ge=1, le=60)
    min_weekly_hours: int | None = Field(default=None, ge=0, le=40)
    preferred_working_hours: str | None = Field(default=None, max_length=64)
    can_take_theory: bool | None = None
    can_take_practical: bool | None = None
    substitute_eligible: bool | None = None
    status: str | None = None


class FacultyOut(BaseModel):
    id: int
    faculty_code: str
    name: str
    email: str
    phone: str
    department: str
    designation_id: int | None
    max_weekly_hours: int
    min_weekly_hours: int
    preferred_working_hours: str
    can_take_theory: bool
    can_take_practical: bool
    substitute_eligible: bool
    status: str
    is_demo: bool
    user_id: int | None
    subject_ids: list[int] = []
    designation_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Designations ----------
class DesignationIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=255)


class DesignationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class DesignationOut(BaseModel):
    id: int
    name: str
    description: str
    is_demo: bool

    model_config = {"from_attributes": True}


# ---------- Availability ----------
class AvailabilityWindow(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time
    is_available: bool = True

    @model_validator(mode="after")
    def validate(self):
        if self.day_of_week not in DAYS:
            raise ValueError(f"day_of_week must be one of {sorted(DAYS)}")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AvailabilityBulkIn(BaseModel):
    """Faculty × Day × Time Slot grid save: list of availability windows."""
    windows: list[AvailabilityWindow] = Field(min_length=1, max_length=400)


class AvailabilityOut(BaseModel):
    id: int
    faculty_id: int
    day_of_week: str
    start_time: time
    end_time: time
    is_available: bool

    model_config = {"from_attributes": True}
