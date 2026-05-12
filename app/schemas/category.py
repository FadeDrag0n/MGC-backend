from __future__ import annotations
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name_ru: str
    name_uk: str
    name_en: str
    slug: str
    image: str | None = None
    is_active: bool = True
    sort_order: int = 0
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name_ru: str | None = None
    name_uk: str | None = None
    name_en: str | None = None
    slug: str | None = None
    image: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None
    parent_id: int | None = None


class CategoryResponse(CategoryBase):
    id: int
    children: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class CategoryShortResponse(BaseModel):
    id: int
    name_ru: str
    name_uk: str
    name_en: str
    slug: str
    image: str | None

    model_config = {"from_attributes": True}