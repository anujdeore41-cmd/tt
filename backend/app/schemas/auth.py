from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(default="", max_length=255)
    role: str = Field(default="FACULTY")  # ADMIN / FACULTY / ACADEMIC_MANAGEMENT

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        v = v.upper()
        if v not in {"ADMIN", "FACULTY", "ACADEMIC_MANAGEMENT"}:
            raise ValueError("role must be ADMIN, FACULTY or ACADEMIC_MANAGEMENT")
        return v


class LoginRequest(BaseModel):
    username: str  # username or email
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    roles: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
