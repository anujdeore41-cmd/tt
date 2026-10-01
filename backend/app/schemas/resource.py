from datetime import datetime, time
from pydantic import BaseModel, Field, model_validator

ROOM_TYPES = {"CLASSROOM", "SMART_CLASSROOM", "SEMINAR_HALL", "TUTORIAL_ROOM", "OTHER"}


class RoomIn(BaseModel):
    room_number: str = Field(min_length=1, max_length=32)
    room_name: str = Field(default="", max_length=128)
    building: str = Field(default="", max_length=64)
    floor: str = Field(default="", max_length=32)
    capacity: int = Field(default=60, ge=1, le=2000)
    room_type: str = Field(default="CLASSROOM")
    equipment: str = Field(default="", max_length=255)
    is_available: bool = True
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def validate(self):
        if self.room_type not in ROOM_TYPES:
            raise ValueError(f"room_type must be one of {sorted(ROOM_TYPES)}")
        if self.status not in {"ACTIVE", "INACTIVE", "ARCHIVED"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ARCHIVED")
        return self


class RoomUpdate(BaseModel):
    room_number: str | None = Field(default=None, min_length=1, max_length=32)
    room_name: str | None = Field(default=None, max_length=128)
    building: str | None = Field(default=None, max_length=64)
    floor: str | None = Field(default=None, max_length=32)
    capacity: int | None = Field(default=None, ge=1, le=2000)
    room_type: str | None = None
    equipment: str | None = Field(default=None, max_length=255)
    is_available: bool | None = None
    status: str | None = None


class RoomOut(BaseModel):
    id: int
    room_number: str
    room_name: str
    building: str
    floor: str
    capacity: int
    room_type: str
    equipment: str
    is_available: bool
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LaboratoryIn(BaseModel):
    lab_number: str = Field(min_length=1, max_length=32)
    lab_name: str = Field(default="", max_length=128)
    building: str = Field(default="", max_length=64)
    floor: str = Field(default="", max_length=32)
    capacity: int = Field(default=30, ge=1, le=2000)
    equipment: str = Field(default="", max_length=255)
    software: str = Field(default="", max_length=255)
    is_available: bool = True
    status: str = Field(default="ACTIVE")

    @model_validator(mode="after")
    def validate(self):
        if self.status not in {"ACTIVE", "INACTIVE", "ARCHIVED"}:
            raise ValueError("status must be ACTIVE, INACTIVE or ARCHIVED")
        return self


class LaboratoryUpdate(BaseModel):
    lab_number: str | None = Field(default=None, min_length=1, max_length=32)
    lab_name: str | None = Field(default=None, max_length=128)
    building: str | None = Field(default=None, max_length=64)
    floor: str | None = Field(default=None, max_length=32)
    capacity: int | None = Field(default=None, ge=1, le=2000)
    equipment: str | None = Field(default=None, max_length=255)
    software: str | None = Field(default=None, max_length=255)
    is_available: bool | None = None
    status: str | None = None


class LaboratoryOut(BaseModel):
    id: int
    lab_number: str
    lab_name: str
    building: str
    floor: str
    capacity: int
    equipment: str
    software: str
    is_available: bool
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
