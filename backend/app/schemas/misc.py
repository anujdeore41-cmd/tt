from datetime import datetime
from pydantic import BaseModel, Field


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    related: dict
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationPreferenceIn(BaseModel):
    type: str
    enabled: bool


class NotificationPreferenceOut(BaseModel):
    id: int
    type: str
    enabled: bool

    model_config = {"from_attributes": True}


class EmailLogOut(BaseModel):
    id: int
    recipient: str
    subject: str
    body: str
    status: str
    error: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AttachmentOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    size_bytes: int
    absence_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SettingIn(BaseModel):
    value: dict


class SettingOut(BaseModel):
    key: str
    value: dict
    description: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class SearchResults(BaseModel):
    faculty: list[dict]
    subjects: list[dict]
    rooms: list[dict]
    laboratories: list[dict]
    divisions: list[dict]


class AuditLogOut(BaseModel):
    id: int
    user_label: str
    action: str
    entity_type: str
    entity_id: str
    previous_value: dict
    new_value: dict
    reason: str
    ip_address: str
    created_at: datetime

    model_config = {"from_attributes": True}
