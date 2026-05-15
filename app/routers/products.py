from __future__ import annotations
from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductShortResponse
from app.services.products import (
    get_products,
    get_product_by_slug,
    create_product,
    update_product,
    delete_product,
    add_product_image,
    delete_product_image,
)
from app.services.media import save_image, delete_image
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["Products"])


class ProductListResponse(BaseModel):
    items: list[ProductShortResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = {"from_attributes": True}


@router.get("/", response_model=ProductListResponse)
async def get_product_list(
    category_slug: str | None = Query(None),
    is_featured: bool | None = Query(None),
    search: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    in_stock: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_products(
        db, category_slug, is_featured, search,
        min_price, max_price, in_stock, page, page_size
    )


@router.get("/{slug}", response_model=ProductResponse)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    return await get_product_by_slug(db, slug)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_admin)])
async def create_new_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, data)


@router.patch("/{slug}", response_model=ProductResponse,
              dependencies=[Depends(get_current_admin)])
async def update_existing_product(slug: str, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await update_product(db, slug, data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)])
async def delete_existing_product(slug: str, db: AsyncSession = Depends(get_db)):
    await delete_product(db, slug)


@router.post("/{slug}/images", response_model=ProductResponse,
             dependencies=[Depends(get_current_admin)])
async def upload_product_image(
    slug: str,
    is_main: bool = False,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    image_url = await save_image(file, "products")
    return await add_product_image(db, slug, image_url, is_main)


@router.delete("/{slug}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)])
async def remove_product_image(slug: str, image_id: int, db: AsyncSession = Depends(get_db)):
    await delete_product_image(db, slug, image_id)