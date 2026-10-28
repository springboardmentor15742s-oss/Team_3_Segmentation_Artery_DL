
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import AnalysisResult, User
from app.routers.cases import get_authorized_case
from app.schemas import AnalysisResultOut, ResultsCompareOut


router = APIRouter(
    prefix="/cases",
    tags=["Analysis Results"],
)


@router.get(
    "/{case_id}/results",
    response_model=list[AnalysisResultOut],
)
def list_case_results(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    List stored analysis results for a case the user is authorized to access.

    This endpoint does not run model inference.
    Results remain empty until a trusted processing workflow stores them.
    """

    get_authorized_case(
        case_id,
        user,
        db,
    )

    statement = (
        select(AnalysisResult)
        .where(
            AnalysisResult.case_id == case_id
        )
        .order_by(
            AnalysisResult.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/{case_id}/results/compare",
    response_model=ResultsCompareOut,
)
def compare_case_results(
    case_id: uuid.UUID,
    baseline_id: uuid.UUID,
    comparison_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Compare two stored result records belonging to the same authorized case.

    This endpoint does not run model inference.
    """

    get_authorized_case(
        case_id,
        user,
        db,
    )

    if baseline_id == comparison_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose two different result records.",
        )

    statement = select(AnalysisResult).where(
        AnalysisResult.case_id == case_id,
        AnalysisResult.result_id.in_(
            [baseline_id, comparison_id]
        ),
    )

    records = list(
        db.scalars(statement).all()
    )

    by_id = {
        record.result_id: record
        for record in records
    }

    baseline = by_id.get(baseline_id)
    comparison = by_id.get(comparison_id)

    if baseline is None or comparison is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Both result records must exist "
                "and belong to this case."
            ),
        )

    def snapshot(item: AnalysisResult) -> dict:
        return {
            "result_id": str(item.result_id),
            "model_version": item.model_version,
            "estimated_narrowing": (
                float(item.estimated_narrowing)
                if item.estimated_narrowing is not None
                else None
            ),
            "confidence_score": (
                float(item.confidence_score)
                if item.confidence_score is not None
                else None
            ),
            "segmentation_output_available": bool(
                item.segmentation_file
            ),
            "stenosis_output_available": bool(
                item.stenosis_file
            ),
            "created_at": (
                item.created_at.isoformat()
                if item.created_at
                else None
            ),
        }

    baseline_snapshot = snapshot(baseline)
    comparison_snapshot = snapshot(comparison)

    def delta(field: str):
        baseline_value = baseline_snapshot[field]
        comparison_value = comparison_snapshot[field]

        if (
            baseline_value is not None
            and comparison_value is not None
        ):
            return round(
                comparison_value - baseline_value,
                4,
            )

        return None

    return ResultsCompareOut(
        case_id=case_id,
        baseline=baseline_snapshot,
        comparison=comparison_snapshot,
        changes={
            "estimated_narrowing_delta": delta(
                "estimated_narrowing"
            ),
            "confidence_score_delta": delta(
                "confidence_score"
            ),
            "model_version_changed": (
                baseline_snapshot["model_version"]
                != comparison_snapshot["model_version"]
            ),
            "segmentation_output_availability_changed": (
                baseline_snapshot[
                    "segmentation_output_available"
                ]
                != comparison_snapshot[
                    "segmentation_output_available"
                ]
            ),
            "stenosis_output_availability_changed": (
                baseline_snapshot[
                    "stenosis_output_available"
                ]
                != comparison_snapshot[
                    "stenosis_output_available"
                ]
            ),
        },
    )
