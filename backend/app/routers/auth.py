import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.audit import record_audit
from app.config import settings
from app.database import get_db
from app.dependencies import bearer_scheme, get_current_user
from app.models import User, UserSession
from app.schemas import PasswordChange, TokenOut, UserLogin, UserOut, UserProfileUpdate, UserRegister
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(data: UserRegister, db: Annotated[Session, Depends(get_db)]):
    normalized_email = str(data.email).lower().strip()
    if db.scalar(select(User).where(User.email == normalized_email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(full_name=data.full_name.strip(), email=normalized_email, password_hash=hash_password(data.password), role="researcher", is_active=True)
    db.add(user)
    try:
        db.flush()
        record_audit(db, user_id=user.user_id, action="user_registered", resource_type="user", resource_id=str(user.user_id))
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    return user


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Annotated[Session, Depends(get_db)]):
    normalized_email = str(data.email).lower().strip()
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is None or not verify_password(data.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Incorrect email or password.", headers={"WWW-Authenticate": "Bearer"})
    jti = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    session = UserSession(user_id=user.user_id, jti=jti, expires_at=expires_at)
    db.add(session)
    record_audit(db, user_id=user.user_id, action="user_login", resource_type="user", resource_id=str(user.user_id), details={"client": "api"})
    db.commit()
    token, expires_in = create_access_token(str(user.user_id), user.role, jti)
    return TokenOut(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserOut)
def get_my_profile(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.patch("/me", response_model=UserOut)
def update_my_profile(data: UserProfileUpdate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    user.full_name = data.full_name.strip()
    record_audit(db, user_id=user.user_id, action="profile_updated", resource_type="user", resource_id=str(user.user_id))
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(data: PasswordChange, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is not correct.")
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="Choose a new password different from the current password.")
    user.password_hash = hash_password(data.new_password)
    now = datetime.now(timezone.utc)
    # Revoke every active session, including the token used for this request. Sign in again afterwards.
    active_sessions = db.scalars(select(UserSession).where(UserSession.user_id == user.user_id, UserSession.revoked_at.is_(None))).all()
    for session in active_sessions:
        session.revoked_at = now
    record_audit(db, user_id=user.user_id, action="password_changed", resource_type="user", resource_id=str(user.user_id))
    db.commit()
    return None


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    import jwt

    payload = jwt.decode(
        credentials.credentials,
        settings.secret_key,
        algorithms=["HS256"],
    )

    jti = payload.get("jti")

    session = db.scalar(
        select(UserSession).where(
            UserSession.user_id == user.user_id,
            UserSession.jti == jti,
        )
    )

    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)

    record_audit(
        db,
        user_id=user.user_id,
        action="user_logout",
        resource_type="user",
        resource_id=str(user.user_id),
    )

    db.commit()

    return None
