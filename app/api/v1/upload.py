import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from PIL import Image
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_SIZE = (1200, 1200)


def validate_image(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
        )


async def save_image(file: UploadFile, subdirectory: str = "posts") -> str:
    upload_dir = Path(settings.MEDIA_ROOT) / subdirectory
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    filepath = upload_dir / filename
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    img = Image.open(filepath)
    if ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb_img

    if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
    
    img.save(filepath, optimize=True, quality=85)
    
    return f"{subdirectory}/{filename}"


@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    validate_image(file)
    
    try:
        image_path = await save_image(file)
        return {
            "filename": file.filename,
            "path": image_path,
            "url": f"/media/{image_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )


@router.delete("/upload/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_path: str,
    current_user: User = Depends(get_current_user),
):
    full_path = Path(settings.MEDIA_ROOT) / image_path

    try:
        full_path.resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый путь к файлу"
        )
    
    if full_path.exists():
        os.remove(full_path)
    
    return None