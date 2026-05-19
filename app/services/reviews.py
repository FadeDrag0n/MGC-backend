from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewModerationUpdate


async def get_product_reviews(
    db: AsyncSession,
    product_slug: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    product_result = await db.execute(select(Product).where(Product.slug == product_slug))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product_not_found")

    query = select(Review).where(
        Review.product_id == product.id,
        Review.is_approved == True
    )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.options(
        selectinload(Review.user)
    ).order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reviews = result.scalars().all()

    # средний рейтинг
    avg_result = await db.execute(
        select(func.avg(Review.rating)).where(
            Review.product_id == product.id,
            Review.is_approved == True
        )
    )
    avg_rating = avg_result.scalar()

    return {
        "items": reviews,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "avg_rating": round(float(avg_rating), 1) if avg_rating else None,
    }


async def create_review(
    db: AsyncSession,
    product_slug: str,
    data: ReviewCreate,
    user_id: int,
) -> Review:
    product_result = await db.execute(select(Product).where(Product.slug == product_slug))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product_not_found")

    # проверяем что юзер ещё не оставлял отзыв на этот товар
    existing = await db.execute(
        select(Review).where(
            Review.product_id == product.id,
            Review.user_id == user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="review_already_exists"
        )

    review = Review(
        product_id=product.id,
        user_id=user_id,
        rating=data.rating,
        comment=data.comment,
        is_approved=False,
    )
    db.add(review)
    await db.flush()

    result = await db.execute(
        select(Review)
        .where(Review.id == review.id)
        .options(selectinload(Review.user))
    )
    return result.scalar_one()


async def update_review(
    db: AsyncSession,
    review_id: int,
    data: ReviewUpdate,
    user_id: int,
) -> Review:
    result = await db.execute(
        select(Review).where(Review.id == review_id, Review.user_id == user_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review_not_found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)

    # после редактирования отзыв снова уходит на модерацию
    review.is_approved = False
    await db.flush()

    result = await db.execute(
        select(Review)
        .where(Review.id == review.id)
        .options(selectinload(Review.user))
    )
    return result.scalar_one()


async def delete_review(db: AsyncSession, review_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Review).where(Review.id == review_id, Review.user_id == user_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review_not_found")
    await db.delete(review)


async def moderate_review(
    db: AsyncSession,
    review_id: int,
    data: ReviewModerationUpdate,
) -> Review:
    result = await db.execute(
        select(Review).where(Review.id == review_id).options(selectinload(Review.user))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review_not_found")
    review.is_approved = data.is_approved
    return review