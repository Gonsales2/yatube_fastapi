import os
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from PIL import Image
import aiofiles

from app.api.deps import get_current_user
from app.models.user import User
from app.config import settings
from app.exceptions import ValidationError

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_SIZE = (1200, 1200)


def validate_image(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            field="file",
            message=f"Недопустимый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationError(
            field="file",
            message=f"Файл слишком большой. Максимум: {MAX_FILE_SIZE // (1024*1024)}MB",
        )


async def save_image(file: UploadFile, subdirectory: str = "posts") -> str:
    upload_dir = Path(settings.MEDIA_ROOT) / subdirectory
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    filepath = upload_dir / filename

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    img = Image.open(filepath)
    if ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "P"):
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = rgb_img

    if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)

    save_kwargs = {"optimize": True, "quality": 85}
    if ext == ".png":
        save_kwargs.pop("quality", None)
    img.save(filepath, **save_kwargs)

    return f"{subdirectory}/{filename}"


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Загрузить одно изображение"
)
async def upload_single(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    validate_image(file)
    path = await save_image(file, "uploads")
    return {
        "filename": file.filename,
        "path": path,
        "url": f"/media/{path}",
    }


@router.post(
    "/multiple/",
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить несколько изображений",
)
async def upload_multiple(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    if not files:
        raise ValidationError(field="files", message="Не выбрано ни одного файла")
    if len(files) > 10:
        raise ValidationError(field="files", message="Максимум 10 файлов за раз")

    results = []
    for file in files:
        validate_image(file)
        path = await save_image(file, "uploads")
        results.append(
            {
                "filename": file.filename,
                "path": path,
                "url": f"/media/{path}",
            }
        )
    return results
