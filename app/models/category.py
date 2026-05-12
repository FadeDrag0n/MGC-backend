from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_uk: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    image: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")

    # relations
    products: Mapped[list["Product"]] = relationship(back_populates="category")