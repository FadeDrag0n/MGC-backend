from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_all_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .where(Category.parent_id == None)
        .options(selectinload(Category.children))
        .order_by(Category.sort_order)
    )
    return result.scalars().all()


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category:
    result = await db.execute(
        select(Category)
        .where(Category.slug == slug)
        .options(selectinload(Category.children))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category_not_found"
        )
    return category


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    existing = await db.execute(select(Category).where(Category.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="slug_already_exists"
        )
    category = Category(**data.model_dump())
    db.add(category)
    await db.flush()
    return category


async def update_category(db: AsyncSession, slug: str, data: CategoryUpdate) -> Category:
    category = await get_category_by_slug(db, slug)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    return category


async def delete_category(db: AsyncSession, slug: str) -> None:
    category = await get_category_by_slug(db, slug)
    await db.delete(category)