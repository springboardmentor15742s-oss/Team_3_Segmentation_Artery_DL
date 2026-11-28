import csv
import html
import io
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
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
    ReportRecord,
    User,
)
from app.routers.cases import get_authorized_case
from app.schemas import ReportOut


router = APIRouter(prefix="/reports", tags=["Reports & Exports"])


def _case_payload(case: MedicalCase, db: Session) -> dict:
    images = list(
        db.scalars(
            select(ImageRecord)
            .where(ImageRecord.case_id == case.case_id)
            .order_by(ImageRecord.uploaded_at.desc())
        ).all()
    )
    results = list(
        db.scalars(
            select(AnalysisResult)
            .where(AnalysisResult.case_id == case.case_id)
            .order_by(AnalysisResult.created_at.desc())
        ).all()
    )
    history = list(
        db.scalars(
            select(AnalysisHistory)
            .where(AnalysisHistory.case_id == case.case_id)
            .order_by(AnalysisHistory.created_at.desc())
        ).all()
    )

    analysis_results = []
    for result in results:
        analysis_results.append(
            {
                "result_id": str(result.result_id),
                "model_version": result.model_version,
                "estimated_narrowing": (
                    float(result.estimated_narrowing)
                    if result.estimated_narrowing is not None
                    else None
                ),
                "severity": getattr(result, "severity", None),
                "confidence_score": (
                    float(result.confidence_score)
                    if result.confidence_score is not None
                    else None
                ),
                "segmentation_output_available": bool(result.segmentation_file),
                "stenosis_output_available": bool(result.stenosis_file),
                "created_at": (
                    result.created_at.isoformat() if result.created_at else None
                ),
            }
        )

    has_saved_results = bool(analysis_results)
    return {
        "report_info": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_scope": (
                "Stored case metadata and previously saved research inference "
                "results. This export endpoint does not run AI inference."
                if has_saved_results
                else "Stored case metadata only. No saved AI inference results "
                "are available for this case."
            ),
        },
        "case": {
            "case_id": str(case.case_id),
            "case_name": case.case_name,
            "imaging_modality": case.imaging_modality,
            "anatomical_region": case.anatomical_region,
            "scan_date": case.scan_date.isoformat() if case.scan_date else None,
            "notes": case.notes,
            "case_status": case.case_status,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        },
        "images": [
            {
                "image_id": str(image.image_id),
                "filename": image.original_filename,
                "format": image.file_format,
                "size_bytes": image.file_size,
                "content_type": image.content_type,
                "uploaded_at": (
                    image.uploaded_at.isoformat() if image.uploaded_at else None
                ),
            }
            for image in images
        ],
        "analysis_results": analysis_results,
        "history": [
            {
                "action": entry.action,
                "status": entry.status,
                "message": entry.message,
                "created_at": (
                    entry.created_at.isoformat() if entry.created_at else None
                ),
            }
            for entry in history
        ],
    }


def _safe_csv_value(value):
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def _make_csv(payload: dict) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["section", "field", "value"])

    for key, value in payload["report_info"].items():
        writer.writerow(
            ["report_info", _safe_csv_value(key), _safe_csv_value(value)]
        )

    for key, value in payload["case"].items():
        writer.writerow(["case", _safe_csv_value(key), _safe_csv_value(value)])

    for index, image in enumerate(payload["images"], start=1):
        for key, value in image.items():
            writer.writerow(
                [f"image_{index}", _safe_csv_value(key), _safe_csv_value(value)]
            )

    for index, result in enumerate(payload["analysis_results"], start=1):
        for key, value in result.items():
            writer.writerow(
                [f"result_{index}", _safe_csv_value(key), _safe_csv_value(value)]
            )

    for index, entry in enumerate(payload["history"], start=1):
        for key, value in entry.items():
            writer.writerow(
                [f"history_{index}", _safe_csv_value(key), _safe_csv_value(value)]
            )

    writer.writerow(
        [
            "notice",
            "research_use",
            "Saved model outputs are research results only, not a medical diagnosis "
            "or clinically validated stenosis measurement.",
        ]
    )
    return out.getvalue().encode("utf-8-sig")


def _make_pdf(payload: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("ArteryVision — Case Export", styles["Title"]),
        Spacer(1, 4 * mm),
    ]

    if payload["analysis_results"]:
        disclaimer = (
            "This report includes previously saved AI research outputs and case "
            "metadata. These outputs are experimental, are not a medical diagnosis, "
            "and must not be used as a clinically validated stenosis measurement."
        )
    else:
        disclaimer = (
            "This report contains stored case metadata only. No saved AI analysis "
            "results are available for this case. It is not a medical diagnosis."
        )

    story.append(Paragraph(html.escape(disclaimer), styles["BodyText"]))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Case Details", styles["Heading2"]))
    case_rows = [["Field", "Value"]]
    for key, value in payload["case"].items():
        case_rows.append(
            [
                html.escape(key.replace("_", " ").title()),
                html.escape(str(value if value is not None else "—")),
            ]
        )

    case_table = Table(case_rows, colWidths=[48 * mm, 118 * mm], repeatRows=1)
    case_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#152744")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(case_table)
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Uploaded Images", styles["Heading2"]))
    if payload["images"]:
        image_rows = [["Filename", "Format", "Size (bytes)", "Uploaded"]]
        image_rows.extend(
            [
                [
                    html.escape(str(image["filename"] or "—")),
                    html.escape(str(image["format"] or "—")),
                    str(image["size_bytes"] if image["size_bytes"] is not None else "—"),
                    html.escape(str(image["uploaded_at"] or "—")),
                ]
                for image in payload["images"]
            ]
        )
        image_table = Table(
            image_rows,
            colWidths=[58 * mm, 24 * mm, 26 * mm, 58 * mm],
            repeatRows=1,
        )
        image_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(image_table)
    else:
        story.append(
            Paragraph("No images are attached to this case.", styles["BodyText"])
        )

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Saved AI Research Results", styles["Heading2"]))

    if payload["analysis_results"]:
        for index, result in enumerate(payload["analysis_results"], start=1):
            story.append(
                Paragraph(f"Analysis Result {index}", styles["Heading3"])
            )
            result_rows = [
                ["Field", "Saved Value"],
                ["Model version", html.escape(str(result["model_version"] or "—"))],
                [
                    "Estimated narrowing",
                    (
                        f'{result["estimated_narrowing"]}%'
                        if result["estimated_narrowing"] is not None
                        else "Not recorded"
                    ),
                ],
                [
                    "Research severity estimate",
                    html.escape(str(result["severity"] or "Not recorded")),
                ],
                [
                    "Confidence score",
                    (
                        str(result["confidence_score"])
                        if result["confidence_score"] is not None
                        else "Not recorded"
                    ),
                ],
                [
                    "Segmentation output available",
                    "Yes" if result["segmentation_output_available"] else "No",
                ],
                [
                    "Stenosis prediction output available",
                    "Yes" if result["stenosis_output_available"] else "No",
                ],
                [
                    "Created at",
                    html.escape(str(result["created_at"] or "—")),
                ],
            ]
            result_table = Table(
                result_rows, colWidths=[65 * mm, 101 * mm], repeatRows=1
            )
            result_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#152744")),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(result_table)
            story.append(Spacer(1, 3 * mm))
    else:
        story.append(
            Paragraph(
                "No saved analysis result records are available for this case.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Activity History", styles["Heading2"]))
    if payload["history"]:
        for entry in payload["history"][:50]:
            line = (
                f'{entry.get("created_at") or "—"} — {entry.get("action") or "—"} '
                f'[{entry.get("status") or "—"}] — {entry.get("message") or ""}'
            )
            story.append(Paragraph(html.escape(line), styles["BodyText"]))
            story.append(Spacer(1, 1.5 * mm))
    else:
        story.append(
            Paragraph("No history entries are available.", styles["BodyText"])
        )

    doc.build(story)
    return buffer.getvalue()


@router.post("/cases/{case_id}/export", response_model=ReportOut)
def create_case_report(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    format: str = Query(default="pdf", pattern="^(pdf|json|csv)$"),
):
    case = get_authorized_case(case_id, user, db)
    payload = _case_payload(case, db)

    if format == "json":
        content = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    elif format == "csv":
        content = _make_csv(payload)
    else:
        content = _make_pdf(payload)

    report_id = uuid.uuid4()
    report_root = settings.report_path.resolve()
    case_folder = report_root / str(case.case_id)
    case_folder.mkdir(parents=True, exist_ok=True)

    filename = f"report_{report_id}.{format}"
    destination = case_folder / filename
    destination.write_bytes(content)

    record = ReportRecord(
        report_id=report_id,
        case_id=case.case_id,
        owner_user_id=case.owner_user_id,
        file_format=format,
        file_reference=str(destination.relative_to(report_root)),
    )
    db.add(record)
    record_audit(
        db,
        user_id=user.user_id,
        action="case_report_generated",
        resource_type="report",
        resource_id=str(report_id),
        details={"format": format, "case_id": str(case.case_id)},
    )
    db.commit()
    db.refresh(record)
    return record


@router.get("/cases/{case_id}", response_model=list[ReportOut])
def list_case_reports(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    get_authorized_case(case_id, user, db)
    stmt = (
        select(ReportRecord)
        .where(ReportRecord.case_id == case_id)
        .order_by(ReportRecord.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.get("/{report_id}/download")
def download_report(
    report_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    record = db.scalar(
        select(ReportRecord).where(ReportRecord.report_id == report_id)
    )

    if not record:
        raise HTTPException(status_code=404, detail="Report not found.")

    # Enforce the same case-access rules as other report endpoints.
    get_authorized_case(record.case_id, user, db)

    root = settings.report_path.resolve()
    path = (root / record.file_reference).resolve()

    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored report file was not found.",
        )

    return FileResponse(
        path,
        filename=(
            f"arteryvision_case_report_{record.case_id}.{record.file_format}"
        ),
    )
