from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from fastapi import HTTPException, UploadFile, status

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
CHUNK_SIZE = 1024 * 1024
MAX_IMAGE_SIZE = settings.max_image_size_bytes


def ensure_upload_dir(upload_dir: Path) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_image(upload: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(upload.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported",
        )
    return extension


def save_image(upload: UploadFile, upload_dir: Path) -> tuple[str, Path]:
    extension = validate_image(upload)
    target_dir = ensure_upload_dir(upload_dir)
    filename = f"{uuid4().hex}{extension}"
    target = target_dir / filename
    total_size = 0

    try:
        with target.open("wb") as destination:
            while chunk := upload.file.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > MAX_IMAGE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Image size must not exceed 5 MB",
                    )
                destination.write(chunk)
    except HTTPException:
        target.unlink(missing_ok=True)
        raise
    except OSError as error:
        target.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save image",
        ) from error

    return filename, target


def resolve_image(upload_dir: Path, filename: str) -> Path | None:
    candidate = (upload_dir / filename).resolve()
    root = upload_dir.resolve()
    if candidate.parent != root or not candidate.is_file():
        return None
    return candidate
