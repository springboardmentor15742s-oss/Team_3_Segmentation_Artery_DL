
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import ModelRegistry, User
from app.schemas import (
    ModelRegistryCreate,
    ModelRegistryOut,
    ModelRegistryUpdate,
)


router = APIRouter(
    prefix="/models",
    tags=["Model Registry Metadata"],
)


# Only ML Engineers and Administrators can manage model metadata.
MODEL_MANAGER_ROLES = (
    "administrator",
    "ml_engineer",
)


@router.get(
    "",
    response_model=list[ModelRegistryOut],
)
def list_models(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    List registered model metadata.

    All authenticated roles can view the model registry.
    """

    statement = (
        select(ModelRegistry)
        .order_by(
            ModelRegistry.updated_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


@router.post(
    "",
    response_model=ModelRegistryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_model(
    data: ModelRegistryCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[
        User,
        Depends(
            require_roles(*MODEL_MANAGER_ROLES)
        ),
    ],
):
    """
    Register a model.

    Only ML Engineers and Administrators can create model records.
    """

    model = ModelRegistry(
        **data.model_dump(),
        created_by=user.user_id,
    )

    db.add(model)

    try:
        db.flush()

        record_audit(
            db,
            user_id=user.user_id,
            action="model_registry_created",
            resource_type="model",
            resource_id=str(model.model_id),
        )

        db.commit()
        db.refresh(model)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A model with this name and version "
                "already exists."
            ),
        ) from exc

    return model


@router.patch(
    "/{model_id}",
    response_model=ModelRegistryOut,
)
def update_model(
    model_id: uuid.UUID,
    data: ModelRegistryUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[
        User,
        Depends(
            require_roles(*MODEL_MANAGER_ROLES)
        ),
    ],
):
    """
    Update model metadata.

    Only ML Engineers and Administrators can update model records.
    """

    model = db.get(
        ModelRegistry,
        model_id,
    )

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model record not found.",
        )

    changes = data.model_dump(
        exclude_unset=True
    )

    for key, value in changes.items():
        setattr(
            model,
            key,
            value,
        )

    record_audit(
        db,
        user_id=user.user_id,
        action="model_registry_updated",
        resource_type="model",
        resource_id=str(model.model_id),
        details={
            "fields": sorted(changes.keys())
        },
    )

    try:
        db.commit()
        db.refresh(model)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A model with this name and version "
                "already exists."
            ),
        ) from exc

    return model


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_model(
    model_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[
        User,
        Depends(
            require_roles(*MODEL_MANAGER_ROLES)
        ),
    ],
):
    """
    Delete model metadata.

    Only ML Engineers and Administrators can delete model records.
    """

    model = db.get(
        ModelRegistry,
        model_id,
    )

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model record not found.",
        )

    record_audit(
        db,
        user_id=user.user_id,
        action="model_registry_deleted",
        resource_type="model",
        resource_id=str(model.model_id),
    )

    db.delete(model)
    db.commit()

    return None
