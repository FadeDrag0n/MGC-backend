from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Мультиязычность
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_uk: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)

    content_ru: Mapped[str | None] = mapped_column(Text)
    content_uk: Mapped[str | None] = mapped_column(Text)
    content_en: Mapped[str | None] = mapped_column(Text)

    excerpt_ru: Mapped[str | None] = mapped_column(String(500))
    excerpt_uk: Mapped[str | None] = mapped_column(String(500))
    excerpt_en: Mapped[str | None] = mapped_column(String(500))

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(500))

    # Статусы
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    views: Mapped[int] = mapped_column(Integer, default=0)

    # Временные метки
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Связи
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship()