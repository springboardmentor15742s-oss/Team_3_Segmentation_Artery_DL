import secrets
import uuid
from pathlib import Path
from typing import Annotated

import numpy as np
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
    AnalysisResult,
    ImageRecord,
    MedicalCase,
    Notification,
    User,
)
from app.routers.cases import get_authorized_case
from app.schemas import ImageOut, AnalysisResultOut


router = APIRouter(tags=["Medical Images"])

ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".tif", ".tiff",
    ".dcm", ".nii", ".nii.gz",
}

CHUNK_SIZE = 1024 * 1024

# --------------------------------------------------
# RESEARCH SEVERITY ESTIMATION
# --------------------------------------------------

def estimate_stenosis_severity(mask_image: Image.Image) -> tuple[str, float]:
    """
    Research/project severity estimate based on predicted stenosis-mask
    coverage. This is NOT a clinical stenosis measurement.

    Thresholds are intentionally simple project heuristics:
      < 1%  -> Mild
      1-3%  -> Moderate
      > 3%  -> Severe
    """
    mask = np.asarray(mask_image.convert("L")) > 0
    total_pixels = mask.size
    affected_pixels = int(mask.sum())

    if total_pixels == 0:
        return "Mild", 0.0

    coverage_percent = (affected_pixels / total_pixels) * 100.0

    if coverage_percent < 1.0:
        severity = "Mild"
    elif coverage_percent <= 3.0:
        severity = "Moderate"
    else:
        severity = "Severe"

    return severity, round(coverage_percent, 2)


IMAGE_UPLOAD_ROLES = {
    "clinician",
    "researcher",
    "administrator",
}


def require_image_upload_permission(user: User) -> None:
    if user.role not in IMAGE_UPLOAD_ROLES:
        raise HTTPException(
            status_code=403,
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
    if extension in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        try:
            with Image.open(path) as image:
                width, height = image.size

                if (
                    width <= 0
                    or height <= 0
                    or width * height > 100_000_000
                ):
                    raise ValueError("Invalid or oversized image dimensions.")

                metadata = {
                    "width": int(width),
                    "height": int(height),
                    "mode": image.mode,
                    "detected_format": image.format,
                }

                image.verify()

            return metadata

        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("Invalid raster image.") from exc

    if extension == ".dcm":
        try:
            import pydicom

            dataset = pydicom.dcmread(str(path))

            if (
                not hasattr(dataset, "Rows")
                or not hasattr(dataset, "Columns")
                or "PixelData" not in dataset
            ):
                raise ValueError("DICOM file is missing image data.")

            rows = int(dataset.Rows)
            columns = int(dataset.Columns)

            if (
                rows <= 0
                or columns <= 0
                or rows * columns > 100_000_000
            ):
                raise ValueError("Invalid DICOM dimensions.")

            return {
                "rows": rows,
                "columns": columns,
                "modality": str(getattr(dataset, "Modality", ""))[:20],
                "pixel_spacing": (
                    [float(x) for x in dataset.PixelSpacing[:2]]
                    if hasattr(dataset, "PixelSpacing")
                    else None
                ),
            }

        except ImportError as exc:
            raise RuntimeError("Install pydicom to validate DICOM files.") from exc
        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("Invalid DICOM file.") from exc

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
                raise ValueError("Invalid NIfTI dimensions.")

            return {
                "shape": shape,
                "spatial_units": str(image.header.get_xyzt_units()[0]),
            }

        except ImportError as exc:
            raise RuntimeError("Install nibabel to validate NIfTI files.") from exc
        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("Invalid NIfTI file.") from exc

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
    case = get_authorized_case(case_id, user, db)
    require_image_upload_permission(user)

    original_name = Path(file.filename or "uploaded_image").name
    extension = get_extension(original_name)

    if extension not in ALLOWED_EXTENSIONS:
        message = f"Unsupported file type: {extension}"

        record_upload_failure(db, user, case, message)

        raise HTTPException(status_code=415, detail=message)

    upload_root = settings.upload_path
    case_folder = upload_root / str(case.case_id)
    case_folder.mkdir(parents=True, exist_ok=True)

    stored_name = f"{secrets.token_hex(16)}{extension}"
    destination = case_folder / stored_name
    relative_reference = f"{case.case_id}/{stored_name}"

    total_size = 0
    limit = settings.max_upload_size_mb * 1024 * 1024

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > limit:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the upload size limit.",
                    )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        try:
            safe_metadata = validate_file_readable(destination, extension)
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

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
                message=f"Uploaded {original_name[:200]} ({total_size} bytes).",
            )
        )

        db.add(
            Notification(
                user_id=case.owner_user_id,
                case_id=case.case_id,
                alert_type="image_uploaded",
                message=f"Image '{original_name[:180]}' was uploaded.",
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
        destination.unlink(missing_ok=True)

        if exc.status_code in (400, 413, 422, 501):
            try:
                record_upload_failure(db, user, case, str(exc.detail))
            except Exception:
                db.rollback()

        raise

    except (OSError, SQLAlchemyError) as exc:
        db.rollback()
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="The image could not be stored. Check server logs.",
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
    get_authorized_case(case_id, user, db)

    statement = (
        select(ImageRecord)
        .where(ImageRecord.case_id == case_id)
        .order_by(ImageRecord.uploaded_at.desc())
    )

    return list(db.scalars(statement).all())


@router.get("/cases/{case_id}/images/{image_id}/file")
def download_case_image(
    case_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    get_authorized_case(case_id, user, db)

    image = db.scalar(
        select(ImageRecord).where(
            ImageRecord.image_id == image_id,
            ImageRecord.case_id == case_id,
        )
    )

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found.")

    root = settings.upload_path.resolve()
    path = (root / image.file_reference).resolve()

    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(status_code=404, detail="Stored image file not found.")

    record_audit(
        db,
        user_id=user.user_id,
        action="image_downloaded",
        resource_type="image",
        resource_id=str(image.image_id),
        details={"case_id": str(case_id)},
    )

    db.commit()

    return FileResponse(
        path,
        filename=image.original_filename,
        media_type=image.content_type or "application/octet-stream",
    )


# --------------------------------------------------
# AI STENOSIS INFERENCE ENDPOINT
# --------------------------------------------------

@router.post(
    "/cases/{case_id}/images/{image_id}/analyze",
    response_model=AnalysisResultOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_stenosis_image(
    case_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    from app.stenosis_inference import predict_stenosis

    case = get_authorized_case(case_id, user, db)

    image = db.scalar(
        select(ImageRecord).where(
            ImageRecord.image_id == image_id,
            ImageRecord.case_id == case_id,
        )
    )

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found.")

    if image.file_format.lower() not in {
        "png", "jpg", "jpeg", "tif", "tiff"
    }:
        raise HTTPException(
            status_code=415,
            detail="Only PNG, JPG and TIFF images are supported for inference.",
        )

    root = settings.upload_path.resolve()
    source_path = (root / image.file_reference).resolve()

    if not source_path.is_relative_to(root) or not source_path.is_file():
        raise HTTPException(status_code=404, detail="Original image not found.")

    output_path = None

    try:
        prediction = predict_stenosis(source_path)

        if isinstance(prediction, Image.Image):
            mask_image = prediction.convert("L")
        else:
            mask_array = np.asarray(prediction)
            mask_image = Image.fromarray(
                (mask_array > 0).astype("uint8") * 255
            ).convert("L")

        output_folder = root / str(case_id) / "results"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_name = f"stenosis_{secrets.token_hex(12)}.png"
        output_path = output_folder / output_name
        mask_image.save(output_path)

        relative_path = f"{case_id}/results/{output_name}"

        severity, mask_coverage = estimate_stenosis_severity(mask_image)

        result = AnalysisResult(
            case_id=case_id,
            model_version="stenosis-unet-1.0",
            stenosis_file=relative_path,
            segmentation_file=None,
            estimated_narrowing=mask_coverage,
            confidence_score=None,
            severity=severity,
        )

        db.add(result)

        # Update the case only after inference has succeeded.
        case.case_status = "Completed"

        db.add(
            AnalysisHistory(
                case_id=case_id,
                action="AI stenosis segmentation",
                status="Completed",
                message=(
                    "Research U-Net generated a stenosis-region mask. "
                    f"Research severity estimate: {severity}. "
                    f"Predicted-mask coverage: {mask_coverage:.2f}%. "
                    "This is not a clinically validated severity measurement."
                ),
            )
        )

        record_audit(
            db,
            user_id=user.user_id,
            action="stenosis_analysis_completed",
            resource_type="image",
            resource_id=str(image_id),
            details={"case_id": str(case_id)},
        )

        db.commit()
        db.refresh(result)

        return result

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        if output_path is not None:
            output_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Stenosis inference failed: {str(exc)}",
        ) from exc


@router.get("/cases/{case_id}/results/{result_id}/severity")
def get_stenosis_severity(
    case_id: uuid.UUID,
    result_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Return the research severity estimate for a saved stenosis prediction."""
    get_authorized_case(case_id, user, db)

    result = db.scalar(
        select(AnalysisResult).where(
            AnalysisResult.result_id == result_id,
            AnalysisResult.case_id == case_id,
        )
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found.")

    if not result.stenosis_file:
        raise HTTPException(
            status_code=404,
            detail="No stenosis prediction is stored for this result.",
        )

    root = settings.upload_path.resolve()
    mask_path = (root / result.stenosis_file).resolve()

    if not mask_path.is_relative_to(root) or not mask_path.is_file():
        raise HTTPException(status_code=404, detail="Stenosis prediction file not found.")

    try:
        with Image.open(mask_path) as mask_image:
            severity, mask_coverage = estimate_stenosis_severity(mask_image)

        return {
            "result_id": str(result.result_id),
            "severity": severity,
            "mask_coverage_percent": mask_coverage,
            "note": (
                "Research/project estimate based on predicted-mask coverage; "
                "not a clinically validated stenosis measurement."
            ),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Severity estimation failed: {str(exc)}",
        ) from exc
