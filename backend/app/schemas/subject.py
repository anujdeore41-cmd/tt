from datetime import datetime
from pydantic import BaseModel, Field, model_validator

SUBJECT_TYPES = {"THEORY", "PRACTICAL", "TUTORIAL", "SEMINAR", "PROJECT", "OTHER"}


class SubjectIn(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    subject_type: str = Field(default="THEORY")
    credits: int = Field(default=1, ge=1, le=10)
    weekly_required_sessions: int = Field(default=1, ge=1, le=30)
    practical_duration_minutes: int | None = Field(default=None, ge=30, le=300)
    practical_batches_count: int | None = Field(default=None, ge=1, le=10)
    preferred_room_id: int | None = None
    preferred_laboratory_id: int | None = None
    academic_year_id: int
    division_ids: list[int] = Field(default_factory=list)
    faculty_ids: list[int] = Field(default_factory=list)
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def validate_types(self):
        if self.subject_type not in SUBJECT_TYPES:
            raise ValueError(f"subject_type must be one of {sorted(SUBJECT_TYPES)}")
        if self.status not in {"ACTIVE", "INACTIVE", "ARCHIVED"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ARCHIVED")
        if self.subject_type == "PRACTICAL" and self.practical_batches_count:
            if not self.division_ids:
                raise ValueError("practical subjects need at least one division")
        return self


class SubjectUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject_type: str | None = None
    credits: int | None = Field(default=None, ge=1, le=10)
    weekly_required_sessions: int | None = Field(default=None, ge=1, le=30)
    practical_duration_minutes: int | None = Field(default=None, ge=30, le=300)
    practical_batches_count: int | None = Field(default=None, ge=1, le=10)
    preferred_room_id: int | None = None
    preferred_laboratory_id: int | None = None
    academic_year_id: int | None = None
    division_ids: list[int] | None = None
    faculty_ids: list[int] | None = None
    status: str | None = None


class SubjectOut(BaseModel):
    id: int
    code: str
    name: str
    subject_type: str
    credits: int
    weekly_required_sessions: int
    practical_duration_minutes: int | None
    practical_batches_count: int | None
    preferred_room_id: int | None
    preferred_laboratory_id: int | None
    academic_year_id: int
    status: str
    is_demo: bool
    division_ids: list[int] = []
    faculty_ids: list[int] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Credit rules ----------
class CreditRuleIn(BaseModel):
    credits: int = Field(ge=1, le=10)
    weekly_hours: int = Field(ge=1, le=20)
    label: str = Field(default="", max_length=128)


class CreditRuleUpdate(BaseModel):
    weekly_hours: int | None = Field(default=None, ge=1, le=20)
    label: str | None = Field(default=None, max_length=128)


class CreditRuleOut(BaseModel):
    id: int
    credits: int
    weekly_hours: int
    label: str

    model_config = {"from_attributes": True}


# ---------- Practical batches ----------
class BatchIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    capacity: int = Field(default=30, ge=1)
    faculty_id: int | None = None
    laboratory_id: int | None = None
    status: str = Field(default="ACTIVE")


class BatchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    capacity: int | None = Field(default=None, ge=1)
    faculty_id: int | None = None
    laboratory_id: int | None = None
    status: str | None = None


class BatchOut(BaseModel):
    id: int
    division_id: int
    name: str
    capacity: int
    faculty_id: int | None
    laboratory_id: int | None
    status: str
    is_demo: bool
    division_name: str | None = None

    model_config = {"from_attributes": True}
