from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password_too_short")
        if not any(c.isupper() for c in v):
            raise ValueError("password_no_uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("password_no_digit")
        return v


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    bio: str | None = None


class UserResponse(UserBase):
    id: int
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar: str | None
    bio: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserShortResponse(BaseModel):
    id: int
    username: str
    avatar: str | None

    model_config = {"from_attributes": True}