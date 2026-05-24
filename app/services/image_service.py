from pathlib import Path
from PIL import Image
import aiofiles
import uuid

from fastapi import UploadFile

from app.config import settings
from app.exceptions import ValidationException

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

MAX_FILE_SIZE = 5 * 1024 * 1024

MAX_IMAGE_SIZE = (1200, 1200)


class ImageService:

    def validate_image(self, file: UploadFile) -> None:
        ext = Path(file.filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(detail="Недопустимый формат файла")

        file.file.seek(0, 2)

        size = file.file.tell()

        file.file.seek(0)

        if size > MAX_FILE_SIZE:
            raise ValidationException(detail="Файл слишком большой")

    async def save_image(
        self,
        file: UploadFile,
        subdirectory: str,
    ) -> str:

        upload_dir = Path(settings.MEDIA_ROOT) / subdirectory

        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        ext = Path(file.filename).suffix.lower()

        filename = f"{uuid.uuid4()}{ext}"

        filepath = upload_dir / filename

        async with aiofiles.open(filepath, "wb") as f:
            content = await file.read()
            await f.write(content)

        img = Image.open(filepath)

        if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
            img.thumbnail(MAX_IMAGE_SIZE)

        img.save(
            filepath,
            optimize=True,
            quality=85,
        )

        return f"{subdirectory}/{filename}"
