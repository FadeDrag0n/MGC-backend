from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


async def get_category_or_404(db: AsyncSession, category_id: int) -> Category:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_not_found"
        )
    return category


async def get_products(
    db: AsyncSession,
    category_slug: str | None = None,
    is_featured: bool | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = select(Product).where(Product.is_active == True)

    if category_slug:
        cat_result = await db.execute(select(Category).where(Category.slug == category_slug))
        category = cat_result.scalar_one_or_none()
        if category:
            query = query.where(Product.category_id == category.id)

    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)

    if search:
        query = query.where(
            Product.name_ru.ilike(f"%{search}%") |
            Product.name_uk.ilike(f"%{search}%") |
            Product.name_en.ilike(f"%{search}%")
        )

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if in_stock:
        query = query.where(Product.stock > 0)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.options(
        selectinload(Product.images),
        selectinload(Product.category),
    ).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


async def get_product_by_slug(db: AsyncSession, slug: str) -> Product:
    result = await db.execute(
        select(Product)
        .where(Product.slug == slug)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
            selectinload(Product.reviews),
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product_not_found"
        )
    return product


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    existing = await db.execute(select(Product).where(Product.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="slug_already_exists"
        )

    await get_category_or_404(db, data.category_id)

    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()

    result = await db.execute(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    return result.scalar_one()


async def update_product(db: AsyncSession, slug: str, data: ProductUpdate) -> Product:
    product = await get_product_by_slug(db, slug)

    if data.category_id is not None:
        await get_category_or_404(db, data.category_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.flush()

    result = await db.execute(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    return result.scalar_one()


async def delete_product(db: AsyncSession, slug: str) -> None:
    product = await get_product_by_slug(db, slug)
    await db.delete(product)


async def add_product_image(db: AsyncSession, slug: str, image_url: str, is_main: bool = False) -> Product:
    product = await get_product_by_slug(db, slug)

    if is_main:
        result = await db.execute(
            select(ProductImage).where(
                ProductImage.product_id == product.id,
                ProductImage.is_main == True
            )
        )
        old_main = result.scalar_one_or_none()
        if old_main:
            old_main.is_main = False

    image = ProductImage(
        product_id=product.id,
        image_url=image_url,
        is_main=is_main,
    )
    db.add(image)
    await db.flush()

    result = await db.execute(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    return result.scalar_one()


async def delete_product_image(db: AsyncSession, slug: str, image_id: int) -> None:
    product = await get_product_by_slug(db, slug)
    result = await db.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id == product.id
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="image_not_found"
        )
    await db.delete(image)