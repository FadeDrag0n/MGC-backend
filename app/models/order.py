from sqlalchemy import String, Text, Integer, ForeignKey, Numeric, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SAEnum
from app.database import Base
import enum


class OrderStatus(enum.Enum):
    PENDING = "pending"         # ожидает подтверждения
    CONFIRMED = "confirmed"     # подтверждён
    PROCESSING = "processing"   # в обработке
    SHIPPED = "shipped"         # отправлен
    DELIVERED = "delivered"     # доставлен
    CANCELLED = "cancelled"     # отменён


class PaymentStatus(enum.Enum):
    UNPAID = "unpaid"       # не оплачен
    PAID = "paid"           # оплачен
    REFUNDED = "refunded"   # возврат


class PaymentMethod(enum.Enum):
    CASH = "cash"               # наличные при получении
    CARD = "card"               # карта при получении
    ONLINE = "online"           # онлайн оплата


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Данные доставки
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    # Суммы
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    # Статусы
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.UNPAID)
    payment_method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), default=PaymentMethod.CASH)

    # Временные метки
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User | None"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Сохраняем данные товара на момент заказа
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_sku: Mapped[str | None] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Связи
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["Order"] = relationship(back_populates="items")
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    product: Mapped["Product | None"] = relationship(back_populates="order_items")