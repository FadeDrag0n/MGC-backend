from __future__ import annotations
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.dependencies.auth import get_current_active_user, get_current_admin
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewShortResponse, ReviewModerationUpdate
from app.services.reviews import (
    get_product_reviews,
    create_review,
    update_review,
    delete_review,
    moderate_review,
)

router = APIRouter(tags=["Reviews"])


class ReviewListResponse(BaseModel):
    items: list[ReviewShortResponse]
    total: int
    page: int
    page_size: int
    pages: int
    avg_rating: float | None

    model_config = {"from_attributes": True}


@router.get("/products/{slug}/reviews", response_model=ReviewListResponse)
async def get_reviews(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await get_product_reviews(db, slug, page, page_size)


@router.post("/products/{slug}/reviews", response_model=ReviewResponse,
             status_code=status.HTTP_201_CREATED)
async def add_review(
    slug: str,
    data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_review(db, slug, data, current_user.id)


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def edit_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_review(db, review_id, data, current_user.id)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_review(db, review_id, current_user.id)


@router.patch("/reviews/{review_id}/moderate", response_model=ReviewResponse,
              dependencies=[Depends(get_current_admin)])
async def moderate_existing_review(
    review_id: int,
    data: ReviewModerationUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await moderate_review(db, review_id, data)