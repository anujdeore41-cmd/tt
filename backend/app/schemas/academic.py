from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator


# ---------- Academic years ----------
class AcademicYearIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    start_date: date | None = None
    end_date: date | None = None
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def dates_valid(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        if self.status not in {"ACTIVE", "INACTIVE", "ARCHIVED"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ARCHIVED")
        return self


class AcademicYearUpdate(AcademicYearIn):
    pass


class AcademicYearOut(BaseModel):
    id: int
    name: str
    start_date: date | None
    end_date: date | None
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Semesters ----------
class SemesterIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    number: int = Field(default=1, ge=1, le=12)
    status: str = Field(default="ACTIVE")


class SemesterOut(BaseModel):
    id: int
    academic_year_id: int
    name: str
    number: int
    status: str

    model_config = {"from_attributes": True}


# ---------- Divisions ----------
class DivisionIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    capacity: int | None = Field(default=None, ge=1)
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def status_valid(self):
        if self.status not in {"ACTIVE", "INACTIVE", "ARCHIVED"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ARCHIVED")
        return self


class DivisionUpdate(DivisionIn):
    pass


class DivisionOut(BaseModel):
    id: int
    academic_year_id: int
    name: str
    capacity: int | None
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
