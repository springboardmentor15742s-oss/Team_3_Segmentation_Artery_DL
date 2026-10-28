import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="researcher", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cases: Mapped[list["MedicalCase"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PatientRecord(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    display_code: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(30), nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_factors: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cases: Mapped[list["MedicalCase"]] = relationship(back_populates="patient")


class MedicalCase(Base):
    __tablename__ = "cases"

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.patient_id", ondelete="SET NULL"), index=True, nullable=True)
    case_name: Mapped[str] = mapped_column(String(150), nullable=False)
    imaging_modality: Mapped[str] = mapped_column(String(50), default="CCTA", nullable=False)
    anatomical_region: Mapped[str] = mapped_column(String(100), default="Coronary arteries", nullable=False)
    scan_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_status: Mapped[str] = mapped_column(String(30), default="Pending", index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner: Mapped[User] = relationship(back_populates="cases")
    patient: Mapped[PatientRecord | None] = relationship(back_populates="cases")
    images: Mapped[list["ImageRecord"]] = relationship(back_populates="case", cascade="all, delete-orphan", passive_deletes=True)
    results: Mapped[list["AnalysisResult"]] = relationship(back_populates="case", cascade="all, delete-orphan", passive_deletes=True)
    history: Mapped[list["AnalysisHistory"]] = relationship(back_populates="case", cascade="all, delete-orphan", passive_deletes=True)


class ImageRecord(Base):
    __tablename__ = "images"

    image_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_reference: Mapped[str] = mapped_column(Text, nullable=False)
    file_format: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    image_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    preprocessed_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    preprocessing_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case: Mapped[MedicalCase] = relationship(back_populates="images")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    result_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    segmentation_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    stenosis_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_narrowing: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case: Mapped[MedicalCase] = relationship(back_populates="results")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    history_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case: Mapped[MedicalCase] = relationship(back_populates="history")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    outcome: Mapped[str] = mapped_column(String(30), default="success", nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    case_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True, nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    task: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    framework: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="planned", nullable=False)
    performance_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("model_name", "version", name="uq_model_registry_name_version"),)


class ReportRecord(Base):
    __tablename__ = "report_records"

    report_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True, nullable=False)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    file_reference: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
