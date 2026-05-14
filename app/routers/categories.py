from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.categories import (
    get_all_categories,
    get_category_by_slug,
    create_category,
    update_category,
    delete_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await get_all_categories(db)


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    return await get_category_by_slug(db, slug)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_admin)])
async def create_new_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await create_category(db, data)


@router.patch("/{slug}", response_model=CategoryResponse,
              dependencies=[Depends(get_current_admin)])
async def update_existing_category(slug: str, data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    return await update_category(db, slug, data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)])
async def delete_existing_category(slug: str, db: AsyncSession = Depends(get_db)):
    await delete_category(db, slug)