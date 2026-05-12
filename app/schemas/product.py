from __future__ import annotations
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.category import CategoryShortResponse


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    is_main: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name_ru: str
    name_uk: str
    name_en: str
    description_ru: str | None = None
    description_uk: str | None = None
    description_en: str | None = None
    slug: str
    price: float
    old_price: float | None = None
    stock: int = 0
    sku: str | None = None
    weight: float | None = None
    attributes: dict | None = None
    is_active: bool = True
    is_featured: bool = False
    category_id: int


class ProductCreate(ProductBase):
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price_must_be_positive")
        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v: int) -> int:
        if v < 0:
            raise ValueError("stock_cannot_be_negative")
        return v


class ProductUpdate(BaseModel):
    name_ru: str | None = None
    name_uk: str | None = None
    name_en: str | None = None
    description_ru: str | None = None
    description_uk: str | None = None
    description_en: str | None = None
    slug: str | None = None
    price: float | None = None
    old_price: float | None = None
    stock: int | None = None
    sku: str | None = None
    weight: float | None = None
    attributes: dict | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    category_id: int | None = None


class ProductResponse(ProductBase):
    id: int
    images: list[ProductImageResponse] = []
    category: CategoryShortResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductShortResponse(BaseModel):
    id: int
    name_ru: str
    name_uk: str
    name_en: str
    slug: str
    price: float
    old_price: float | None
    stock: int
    is_active: bool
    is_featured: bool
    images: list[ProductImageResponse] = []
    category: CategoryShortResponse

    model_config = {"from_attributes": True}