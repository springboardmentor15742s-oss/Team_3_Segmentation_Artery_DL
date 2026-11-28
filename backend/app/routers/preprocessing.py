"""Basic, non-AI image normalization for inspection/preview; not a diagnostic pipeline."""
import secrets
import uuid
from pathlib import Path
from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AnalysisHistory, ImageRecord, MedicalCase, Notification, User
from app.routers.cases import get_authorized_case
from app.schemas import PreprocessOut

router = APIRouter(tags=["Image Preprocessing"])


def _normalize_array(array: np.ndarray) -> tuple[Image.Image, dict[str, Any]]:
    """Return an 8-bit grayscale preview slice and source-shape metadata."""
    source_shape = [int(dimension) for dimension in array.shape]
    if array.size == 0:
        raise ValueError("The image contains no pixel data.")
    if array.size > 100_000_000:
        raise ValueError("The decoded image is too large to preprocess safely (over 100 million pixels/voxels).")

    # For 3D/4D volumes, create a clearly labelled central-slice preview only.
    slice_description = "entire 2D image"
    data = np.asarray(array)
    if data.ndim >= 4:
        data = data[..., data.shape[-1] // 2]
        slice_description = f"central frame in last dimension; shape={source_shape}"
    if data.ndim == 3:
        if data.shape[-1] in (3, 4):  # conventional RGB/RGBA raster array
            image = Image.fromarray(data.astype(np.uint8)).convert("L")
            return image, {"source_shape": source_shape, "preview_slice": "RGB/RGBA converted to grayscale"}
        # Otherwise treat first dimension as frames/volume and select its centre.
        data = data[data.shape[0] // 2]
        slice_description = f"central slice on first dimension; source shape={source_shape}"
    if data.ndim != 2:
        raise ValueError(f"Could not convert the decoded image to a 2D preview (shape={source_shape}).")

    data = data.astype(np.float64, copy=False)
    finite = np.isfinite(data)
    if not finite.any():
        raise ValueError("The image has no finite pixel values.")
    values = data[finite]
    low, high = np.percentile(values, (1, 99))
    if high <= low:
        low, high = float(values.min()), float(values.max())
    if high <= low:
        normalized = np.zeros(data.shape, dtype=np.uint8)
    else:
        cleaned = np.nan_to_num(data, nan=low, posinf=high, neginf=low)
        normalized = np.clip((cleaned - low) * (255.0 / (high - low)), 0, 255).astype(np.uint8)
    return Image.fromarray(normalized), {"source_shape": source_shape, "preview_slice": slice_description, "intensity_window_percentiles": [1, 99]}


def _load_source(path: Path, extension: str) -> tuple[Image.Image, dict[str, Any]]:
    if extension in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        try:
            with Image.open(path) as source:
                source.seek(0)
                image = ImageOps.exif_transpose(source).convert("L")
                meta = {"source_dimensions": [int(image.width), int(image.height)], "preview_slice": "first frame if source is multi-frame"}
                return image, meta
        except Exception as exc:
            raise ValueError("The uploaded raster image is invalid or cannot be decoded.") from exc

    if extension == ".dcm":
        try:
            import pydicom
            dataset = pydicom.dcmread(str(path), stop_before_pixels=True)
            rows = int(getattr(dataset, "Rows", 0))
            columns = int(getattr(dataset, "Columns", 0))
            frames = int(getattr(dataset, "NumberOfFrames", 1))
            samples = int(getattr(dataset, "SamplesPerPixel", 1))
            if rows <= 0 or columns <= 0 or rows * columns * max(frames, 1) * max(samples, 1) > 100_000_000:
                raise ValueError("DICOM dimensions are invalid or too large to preprocess safely.")
            dataset = pydicom.dcmread(str(path))
            pixels = dataset.pixel_array
            if int(getattr(dataset, "SamplesPerPixel", 1)) > 1 and pixels.ndim == 3 and pixels.shape[-1] in (3, 4):
                image = Image.fromarray(pixels.astype(np.uint8)).convert("L")
                return image, {"source_shape": list(pixels.shape), "preview_slice": "colour DICOM converted to grayscale"}
            slope = float(getattr(dataset, "RescaleSlope", 1.0))
            intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
            return _normalize_array(np.asarray(pixels, dtype=np.float64) * slope + intercept)
        except ImportError as exc:
            raise RuntimeError("DICOM support requires pydicom. Install the backend requirements.") from exc
        except Exception as exc:
            raise ValueError("The DICOM file could not be decoded. The file may be invalid or need an additional pixel decoder.") from exc

    if extension in {".nii", ".nii.gz"}:
        try:
            import nibabel as nib
            volume = nib.load(str(path))
            source_shape = [int(size) for size in volume.shape]
            if len(source_shape) < 2 or int(np.prod(source_shape)) > 100_000_000:
                raise ValueError("NIfTI dimensions are invalid or too large to preprocess safely.")
            array = np.asanyarray(volume.dataobj)
            if array.ndim >= 3:
                # Use a middle slice of the Z axis; for 4D files select the middle time/frame first.
                frame_note = ""
                if array.ndim >= 4:
                    frame_index = array.shape[-1] // 2
                    array = array[..., frame_index]
                    frame_note = f"; central frame {frame_index} from last dimension"
                z_index = array.shape[2] // 2
                array = array[:, :, z_index]
                preview_note = f"central Z slice {z_index} from source shape={source_shape}{frame_note}"
            else:
                preview_note = f"2D source image shape={source_shape}"
            image, meta = _normalize_array(array)
            meta["source_shape"] = source_shape
            meta["preview_slice"] = preview_note
            return image, meta
        except ImportError as exc:
            raise RuntimeError("NIfTI support requires nibabel. Install the backend requirements.") from exc
        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("The NIfTI file could not be decoded.") from exc

    raise ValueError("Unsupported file extension for preprocessing.")


@router.post("/cases/{case_id}/images/{image_id}/preprocess", response_model=PreprocessOut)
def preprocess_image(
    case_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    denoise: Annotated[bool, Query()] = True,
    enhance_contrast: Annotated[bool, Query()] = True,
    max_dimension: Annotated[int, Query(ge=64, le=2048)] = 1024,
):
    """Create a normalized PNG preview. This is conventional image processing, not AI inference."""
    case: MedicalCase = get_authorized_case(case_id, user, db)
    record = db.scalar(select(ImageRecord).where(ImageRecord.image_id == image_id, ImageRecord.case_id == case.case_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Image not found for this case.")

    upload_root = settings.upload_path.resolve()
    source_path = (upload_root / record.file_reference).resolve()
    if not source_path.is_relative_to(upload_root) or not source_path.is_file():
        raise HTTPException(status_code=404, detail="Stored source image was not found.")

    extension = ".nii.gz" if record.original_filename.lower().endswith(".nii.gz") else Path(record.original_filename).suffix.lower()
    try:
        image, metadata = _load_source(source_path, extension)
        original_width, original_height = image.size
        applied_operations = ["grayscale conversion", "1st–99th percentile intensity normalization"]
        if denoise:
            image = image.filter(ImageFilter.MedianFilter(size=3))
            applied_operations.append("3x3 median-filter denoising")
        if enhance_contrast:
            image = ImageEnhance.Contrast(image).enhance(1.25)
            applied_operations.append("contrast enhancement (factor 1.25)")
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        applied_operations.append(f"resize to fit {max_dimension}x{max_dimension} (aspect ratio preserved)")
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail="The file could not be preprocessed. Check the uploaded file and server logs.") from exc

    processed_folder = upload_root / str(case.case_id) / "processed"
    processed_folder.mkdir(parents=True, exist_ok=True)
    output_name = f"{record.image_id}-{secrets.token_hex(8)}.png"
    output_path = processed_folder / output_name
    relative_reference = str(output_path.relative_to(upload_root)).replace("\\", "/")
    try:
        image.save(output_path, format="PNG", optimize=True)
        metadata.update({
            "method": "basic_non_ai_preprocessing",
            "output_dimensions": [int(image.width), int(image.height)],
            "source_dimensions_before_resize": [int(original_width), int(original_height)],
            "operations": applied_operations,
            "denoise_enabled": denoise,
            "contrast_enhancement_enabled": enhance_contrast,
            "max_dimension": max_dimension,
            "warning": "Preview/preprocessing output only. Not validated for clinical use and not an artery segmentation or stenosis result.",
        })
        old_reference = record.preprocessed_reference
        record.preprocessed_reference = relative_reference
        record.preprocessing_metadata = metadata
        db.add(AnalysisHistory(case_id=case.case_id, action="Image preprocessing", status="Completed", message=f"Created normalized PNG preview for {record.original_filename[:150]}. No AI inference was run."))
        db.add(Notification(user_id=case.owner_user_id, case_id=case.case_id, alert_type="preprocessing_complete", message=f"A basic preprocessed preview is ready for '{record.original_filename[:150]}'. This is not an AI result.", severity="info"))
        record_audit(db, user_id=user.user_id, action="image_preprocessed", resource_type="image", resource_id=str(record.image_id), details={"case_id": str(case.case_id), "operations": applied_operations})
        db.commit()
        db.refresh(record)
        if old_reference:
            old_path = (upload_root / old_reference).resolve()
            if old_path.is_relative_to(upload_root) and old_path != output_path:
                old_path.unlink(missing_ok=True)
    except Exception as exc:
        db.rollback()
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Preprocessed preview could not be saved. Check server logs.") from exc

    return PreprocessOut(
        case_id=case.case_id,
        image_id=record.image_id,
        download_url=f"/cases/{case.case_id}/images/{record.image_id}/preprocessed-file",
        metadata=metadata,
        message="Basic preprocessing finished. This preview is not an AI or diagnostic result.",
    )


@router.get("/cases/{case_id}/images/{image_id}/preprocessed-file")
def download_preprocessed_image(
    case_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    case = get_authorized_case(case_id, user, db)
    record = db.scalar(select(ImageRecord).where(ImageRecord.image_id == image_id, ImageRecord.case_id == case.case_id))
    if record is None or not record.preprocessed_reference:
        raise HTTPException(status_code=404, detail="No preprocessed preview exists for this image yet.")
    root = settings.upload_path.resolve()
    path = (root / record.preprocessed_reference).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(status_code=404, detail="Stored preprocessed preview was not found.")
    record_audit(db, user_id=user.user_id, action="preprocessed_image_downloaded", resource_type="image", resource_id=str(record.image_id))
    db.commit()
    return FileResponse(path, filename=f"{Path(record.original_filename).stem}_preprocessed.png", media_type="image/png")
