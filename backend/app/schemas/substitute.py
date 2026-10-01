from datetime import datetime
from pydantic import BaseModel, Field


class SubstituteCreate(BaseModel):
    affected_lecture_id: int
    substitute_faculty_id: int
    notes: str = Field(default="", max_length=2000)
    assignment_instructions: str = Field(default="", max_length=2000)


class SubstituteOut(BaseModel):
    id: int
    absence_id: int | None
    affected_lecture_id: int | None
    original_entry_id: int | None
    absent_faculty_id: int
    substitute_faculty_id: int | None
    substitute_date: datetime
    time_slot_id: int | None
    academic_year_id: int | None
    division_id: int | None
    subject_id: int | None
    room_id: int | None
    laboratory_id: int | None
    batch_id: int | None
    notes: str
    assignment_instructions: str
    status: str
    created_at: datetime
    responded_at: datetime | None
    # display
    absent_faculty_name: str | None = None
    substitute_faculty_name: str | None = None
    subject_name: str | None = None
    division_name: str | None = None
    academic_year_name: str | None = None
    room_number: str | None = None
    slot_start: datetime | None = None
    slot_end: datetime | None = None

    model_config = {"from_attributes": True}


class SubstituteRespond(BaseModel):
    response: str  # ACCEPTED / DECLINED
    comment: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def validate(self):
        if self.response not in {"ACCEPTED", "DECLINED"}:
            raise ValueError("response must be ACCEPTED or DECLINED")
        return self
