from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserShortResponse


class ArticleBase(BaseModel):
    title_ru: str
    title_uk: str
    title_en: str
    content_ru: str | None = None
    content_uk: str | None = None
    content_en: str | None = None
    excerpt_ru: str | None = None
    excerpt_uk: str | None = None
    excerpt_en: str | None = None
    slug: str
    cover_image: str | None = None
    is_published: bool = False


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title_ru: str | None = None
    title_uk: str | None = None
    title_en: str | None = None
    content_ru: str | None = None
    content_uk: str | None = None
    content_en: str | None = None
    excerpt_ru: str | None = None
    excerpt_uk: str | None = None
    excerpt_en: str | None = None
    slug: str | None = None
    cover_image: str | None = None
    is_published: bool | None = None


class ArticleResponse(ArticleBase):
    id: int
    views: int
    author: UserShortResponse
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None

    model_config = {"from_attributes": True}


class ArticleShortResponse(BaseModel):
    id: int
    title_ru: str
    title_uk: str
    title_en: str
    slug: str
    excerpt_ru: str | None
    excerpt_uk: str | None
    excerpt_en: str | None
    cover_image: str | None
    views: int
    is_published: bool
    author: UserShortResponse
    published_at: datetime | None

    model_config = {"from_attributes": True}