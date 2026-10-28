
import secrets
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from PIL import Image
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    AnalysisHistory,
    ImageRecord,
    MedicalCase,
    Notification,
    User,
)
from app.routers.cases import get_authorized_case
from app.schemas import ImageOut


router = APIRouter(tags=["Medical Images"])

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".dcm",
    ".nii",
    ".nii.gz",
}

CHUNK_SIZE = 1024 * 1024

# Roles allowed to upload medical images.
IMAGE_UPLOAD_ROLES = {
    "clinician",
    "researcher",
    "administrator",
}


def require_image_upload_permission(user: User) -> None:
    if user.role not in IMAGE_UPLOAD_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role does not have permission to upload medical images.",
        )


def record_upload_failure(
    db: Session,
    user: User,
    case: MedicalCase,
    message: str,
    alert_type: str = "upload_failed",
) -> None:
    db.add(
        Notification(
            user_id=case.owner_user_id,
            case_id=case.case_id,
            alert_type=alert_type,
            message=message[:1000],
            severity="warning",
        )
    )

    record_audit(
        db,
        user_id=user.user_id,
        action=alert_type,
        resource_type="case",
        resource_id=str(case.case_id),
        outcome="failed",
        details={"message": message[:500]},
    )

    db.commit()


def get_extension(filename: str) -> str:
    lower = filename.lower()

    if lower.endswith(".nii.gz"):
        return ".nii.gz"

    return Path(lower).suffix


def validate_file_readable(path: Path, extension: str) -> dict:
    """Check file structure and store only non-identifying technical metadata."""

    # Raster image validation
    if extension in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        try:
            with Image.open(path) as image:
                width, height = image.size

                if (
                    width <= 0
                    or height <= 0
                    or width * height > 100_000_000
                ):
                    raise ValueError(
                        "Image dimensions are invalid or too large "
                        "to process safely."
                    )

                image_format = image.format
                mode = image.mode

                image.verify()

            return {
                "width": int(width),
                "height": int(height),
                "mode": mode,
                "detected_format": image_format,
            }

        except Exception as exc:
            if isinstance(exc, ValueError):
                raise

            raise ValueError(
                "The uploaded image is not a valid readable raster file."
            ) from exc

    # DICOM validation
    if extension == ".dcm":
        try:
            import pydicom

            dataset = pydicom.dcmread(str(path))

            if (
                not hasattr(dataset, "Rows")
                or not hasattr(dataset, "Columns")
                or "PixelData" not in dataset
            ):
                raise ValueError(
                    "The DICOM file is missing required image pixel "
                    "data or dimensions."
                )

            rows = int(dataset.Rows)
            columns = int(dataset.Columns)

            if (
                rows <= 0
                or columns <= 0
                or rows * columns > 100_000_000
            ):
                raise ValueError(
                    "DICOM image dimensions are invalid or too large "
                    "to process safely."
                )

            # Store technical fields only.
            # Do not persist PatientName or other identifiers.
            return {
                "rows": rows,
                "columns": columns,
                "modality": str(
                    getattr(dataset, "Modality", "")
                )[:20],
                "pixel_spacing": (
                    [
                        float(x)
                        for x in dataset.PixelSpacing[:2]
                    ]
                    if hasattr(dataset, "PixelSpacing")
                    else None
                ),
            }

        except ImportError as exc:
            raise RuntimeError(
                "DICOM upload validation requires pydicom. "
                "Install the backend requirements."
            ) from exc

        except Exception as exc:
            if isinstance(exc, ValueError):
                raise

            raise ValueError(
                "The uploaded DICOM file is not readable or is "
                "missing required image data."
            ) from exc

    # NIfTI validation
    if extension in {".nii", ".nii.gz"}:
        try:
            import math
            import nibabel as nib

            image = nib.load(str(path))
            shape = [int(size) for size in image.shape]

            if (
                len(shape) < 2
                or any(size <= 0 for size in shape)
                or math.prod(shape) > 100_000_000
            ):
                raise ValueError(
                    "NIfTI image dimensions are invalid or too large "
                    "to process safely."
                )

            return {
                "shape": shape,
                "spatial_units": str(
                    image.header.get_xyzt_units()[0]
                ),
            }

        except ImportError as exc:
            raise RuntimeError(
                "NIfTI upload validation requires nibabel. "
                "Install the backend requirements."
            ) from exc

        except Exception as exc:
            if isinstance(exc, ValueError):
                raise

            raise ValueError(
                "The uploaded NIfTI file is not readable."
            ) from exc

    raise ValueError("Unsupported file extension.")


@router.post(
    "/cases/{case_id}/upload",
    response_model=ImageOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    case_id: uuid.UUID,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    # First verify that the user can access this case.
    case = get_authorized_case(case_id, user, db)

    # Then verify that their role permits image uploads.
    require_image_upload_permission(user)

    original_name = Path(
        file.filename or "uploaded_image"
    ).name

    extension = get_extension(original_name)

    if extension not in ALLOWED_EXTENSIONS:
        message = (
            f"Unsupported file type for '{original_name[:180]}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

        record_upload_failure(
            db,
            user,
            case,
            message,
        )

        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=message,
        )

    upload_root = settings.upload_path
    case_folder = upload_root / str(case.case_id)

    case_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_name = f"{secrets.token_hex(16)}{extension}"

    destination = case_folder / stored_name

    relative_reference = (
        f"{case.case_id}/{stored_name}"
    )

    total_size = 0

    limit = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > limit:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"File exceeds the "
                            f"{settings.max_upload_size_mb} MB "
                            f"upload limit."
                        ),
                    )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        try:
            safe_metadata = validate_file_readable(
                destination,
                extension,
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=str(exc),
            ) from exc

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        record = ImageRecord(
            case_id=case.case_id,
            original_filename=original_name[:255],
            file_reference=relative_reference,
            file_format=extension.lstrip("."),
            file_size=total_size,
            content_type=file.content_type,
            image_metadata=safe_metadata,
        )

        db.add(record)

        db.add(
            AnalysisHistory(
                case_id=case.case_id,
                action="Image uploaded",
                status=case.case_status,
                message=(
                    f"Uploaded {original_name[:200]} "
                    f"({total_size} bytes)."
                ),
            )
        )

        db.add(
            Notification(
                user_id=case.owner_user_id,
                case_id=case.case_id,
                alert_type="image_uploaded",
                message=(
                    f"Image '{original_name[:180]}' was uploaded "
                    f"to case '{case.case_name}'."
                ),
                severity="info",
            )
        )

        record_audit(
            db,
            user_id=user.user_id,
            action="image_uploaded",
            resource_type="image",
            resource_id=str(record.image_id),
            details={
                "case_id": str(case.case_id),
                "file_size": total_size,
                "format": extension.lstrip("."),
            },
        )

        db.commit()
        db.refresh(record)

        return record

    except HTTPException as exc:
        db.rollback()

        destination.unlink(
            missing_ok=True
        )

        if exc.status_code in (
            400,
            413,
            422,
            501,
        ):
            try:
                record_upload_failure(
                    db,
                    user,
                    case,
                    str(exc.detail),
                )

            except Exception:
                db.rollback()

        raise

    except (OSError, SQLAlchemyError) as exc:
        db.rollback()

        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The image could not be stored. "
                "Check server logs."
            ),
        ) from exc

    finally:
        await file.close()


@router.get(
    "/cases/{case_id}/images",
    response_model=list[ImageOut],
)
def list_case_images(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    get_authorized_case(
        case_id,
        user,
        db,
    )

    statement = (
        select(ImageRecord)
        .where(ImageRecord.case_id == case_id)
        .order_by(ImageRecord.uploaded_at.desc())
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/cases/{case_id}/images/{image_id}/file",
)
def download_case_image(
    case_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    get_authorized_case(
        case_id,
        user,
        db,
    )

    image = db.scalar(
        select(ImageRecord).where(
            ImageRecord.image_id == image_id,
            ImageRecord.case_id == case_id,
        )
    )

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )

    root = settings.upload_path.resolve()

    path = (
        root / image.file_reference
    ).resolve()

    # Prevent path traversal and verify that the file exists.
    if (
        not path.is_relative_to(root)
        or not path.is_file()
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored image file was not found.",
        )

    record_audit(
        db,
        user_id=user.user_id,
        action="image_downloaded",
        resource_type="image",
        resource_id=str(image.image_id),
        details={
            "case_id": str(case_id),
        },
    )

    db.commit()

    return FileResponse(
        path,
        filename=image.original_filename,
        media_type=(
            image.content_type
            or "application/octet-stream"
        ),
    )
