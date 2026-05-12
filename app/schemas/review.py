from __future__ import annotations
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.user import UserShortResponse


class ReviewBase(BaseModel):
    rating: int
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("rating_must_be_between_1_and_5")
        return v


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None


class ReviewModerationUpdate(BaseModel):
    is_approved: bool


class ReviewResponse(ReviewBase):
    id: int
    is_approved: bool
    user: UserShortResponse
    product_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewShortResponse(BaseModel):
    id: int
    rating: int
    comment: str | None
    user: UserShortResponse
    created_at: datetime

    model_config = {"from_attributes": True}