from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CollegeIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    department_name: str = Field(default="", max_length=255)
    academic_year_label: str = Field(default="", max_length=64)
    semester_label: str = Field(default="", max_length=64)
    timezone: str = Field(default="Asia/Kolkata", max_length=64)
    contact_email: EmailStr | None = None
    department_email: EmailStr | None = None


class CollegeUpdate(CollegeIn):
    pass


class CollegeOut(BaseModel):
    id: int
    name: str
    department_name: str
    academic_year_label: str
    semester_label: str
    timezone: str
    contact_email: str
    department_email: str
    setup_completed: bool
    setup_progress: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
