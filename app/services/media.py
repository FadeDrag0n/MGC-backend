from __future__ import annotations
import uuid
import aiofiles
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def save_image(file: UploadFile, folder: str) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_image_type"
        )

    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_too_large"
        )

    upload_dir = Path(settings.MEDIA_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = upload_dir / filename

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    if folder == "avatars":
        img = Image.open(filepath)
        img.thumbnail((300, 300))
        img.save(filepath)

    return f"/{settings.MEDIA_DIR}/{folder}/{filename}"


def delete_image(image_url: str) -> None:
    if not image_url:
        return
    path = Path(image_url.lstrip("/"))
    if path.exists():
        path.unlink()