from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Optional
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import settings
from fastapi import HTTPException, UploadFile, status

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MIME_TO_FORMAT = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}
ALLOWED_PIL_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
CHUNK_SIZE = 1024 * 1024
MAX_IMAGE_SIZE = settings.max_image_size_bytes


class SavedImage:
    def __init__(self, filename: str, path: Path, thumbnail_path: Path, image_hash: str):
        self.filename = filename
        self.path = path
        self.thumbnail_path = thumbnail_path
        self.image_hash = image_hash

    def __iter__(self):
        return iter((self.filename, self.path))

    def __getitem__(self, index):
        return (self.filename, self.path, self.thumbnail_path, self.image_hash)[index]

    def __len__(self):
        return 4


def get_thumbnail_filename(filename: str) -> str:
    return f"thumb_{filename}"


def ensure_upload_dir(upload_dir: Path) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def count_user_uploads(upload_dir: Path) -> int:
    if not upload_dir.exists():
        return 0
    return sum(1 for f in upload_dir.iterdir() if f.is_file() and not f.name.startswith("thumb_"))


def delete_image_files(upload_dir: Path, filename: str) -> None:
    main_file = resolve_image(upload_dir, filename)
    if main_file is not None and main_file.is_file():
        main_file.unlink(missing_ok=True)
    thumb_filename = get_thumbnail_filename(filename)
    thumb_file = resolve_image(upload_dir, thumb_filename)
    if thumb_file is not None and thumb_file.is_file():
        thumb_file.unlink(missing_ok=True)


def validate_image_content(content: bytes, declared_content_type: Optional[str] = None) -> tuple[str, str]:
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size must not exceed 5 MB",
        )

    expected_ext = ALLOWED_IMAGE_TYPES.get(declared_content_type or "")
    if expected_ext is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    try:
        with Image.open(io.BytesIO(content)) as img:
            fmt = (img.format or "").upper()
            if fmt not in ALLOWED_PIL_FORMATS:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported image format: {fmt}",
                )
            expected_format = MIME_TO_FORMAT.get(declared_content_type or "")
            if expected_format and fmt != expected_format:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image content ({fmt}) does not match declared MIME type ({declared_content_type})",
                )
            img.verify()
    except (UnidentifiedImageError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image content: file is not a valid image",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image content or corrupted file",
        ) from exc

    return fmt, expected_ext


def validate_image(upload: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(upload.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported",
        )
    return extension


def save_image(
    upload: UploadFile,
    upload_dir: Path,
    max_dimension: Optional[int] = None,
    thumbnail_dimension: Optional[int] = None,
) -> SavedImage:
    target_dir = ensure_upload_dir(upload_dir)
    chunks = []
    total_size = 0

    try:
        while chunk := upload.file.read(CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Image size must not exceed 5 MB",
                )
            chunks.append(chunk)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read upload stream",
        ) from error

    content = b"".join(chunks)
    img_format, extension = validate_image_content(content, upload.content_type)
    image_hash = hashlib.sha256(content).hexdigest()

    max_dim = max_dimension or settings.max_image_dimension
    thumb_dim = thumbnail_dimension or settings.thumbnail_dimension

    stem = uuid4().hex
    filename = f"{stem}{extension}"
    target = target_dir / filename
    thumb_filename = get_thumbnail_filename(filename)
    thumb_target = target_dir / thumb_filename

    try:
        img = Image.open(io.BytesIO(content))
        img = ImageOps.exif_transpose(img)

        # Handle color modes for JPEG
        if img_format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize if dimensions exceed max_dim
        if img.width > max_dim or img.height > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        save_kwargs = {}
        if img_format == "JPEG":
            save_kwargs = {"quality": 85, "optimize": True}
        elif img_format == "PNG":
            save_kwargs = {"optimize": True}
        elif img_format == "WEBP":
            save_kwargs = {"quality": 85}

        img.save(target, format=img_format, **save_kwargs)

        # Generate thumbnail
        thumb_img = img.copy()
        thumb_img.thumbnail((thumb_dim, thumb_dim), Image.Resampling.LANCZOS)
        thumb_img.save(thumb_target, format=img_format, **save_kwargs)

    except HTTPException:
        target.unlink(missing_ok=True)
        thumb_target.unlink(missing_ok=True)
        raise
    except OSError as error:
        target.unlink(missing_ok=True)
        thumb_target.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save image",
        ) from error

    return SavedImage(filename, target, thumb_target, image_hash)


def resolve_image(upload_dir: Path, filename: str) -> Path | None:
    candidate = (upload_dir / filename).resolve()
    root = upload_dir.resolve()
    if candidate.parent != root or not candidate.is_file():
        return None
    return candidate
