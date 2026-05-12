from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.models.order import OrderStatus, PaymentStatus, PaymentMethod
from app.schemas.product import ProductShortResponse


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity_must_be_positive")
        return v


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    product_sku: str | None
    price: float
    quantity: float
    product: ProductShortResponse | None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    city: str
    address: str
    comment: str | None = None
    payment_method: PaymentMethod = PaymentMethod.CASH
    items: list[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        if not v:
            raise ValueError("order_must_have_items")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if not cleaned.isdigit():
            raise ValueError("phone_invalid_format")
        if len(cleaned) < 10 or len(cleaned) > 13:
            raise ValueError("phone_invalid_length")
        return v


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderPaymentUpdate(BaseModel):
    payment_status: PaymentStatus


class OrderResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    city: str
    address: str
    comment: str | None
    total_price: float
    delivery_price: float
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderShortResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    total_price: float
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime

    model_config = {"from_attributes": True}