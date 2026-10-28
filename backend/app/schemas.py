import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)

class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class CaseCreate(BaseModel):
    case_name: str = Field(min_length=1, max_length=150)
    imaging_modality: str = Field(default="CCTA", max_length=50)
    anatomical_region: str = Field(default="Coronary arteries", max_length=100)
    scan_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)
    patient_id: uuid.UUID | None = None

class CaseUpdate(BaseModel):
    case_name: str | None = Field(default=None, min_length=1, max_length=150)
    imaging_modality: str | None = Field(default=None, max_length=50)
    anatomical_region: str | None = Field(default=None, max_length=100)
    scan_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)
    patient_id: uuid.UUID | None = None

class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    case_id: uuid.UUID
    owner_user_id: uuid.UUID
    patient_id: uuid.UUID | None = None
    case_name: str
    imaging_modality: str
    anatomical_region: str
    scan_date: date | None
    notes: str | None = None
    case_status: str
    created_at: datetime
    updated_at: datetime

class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    image_id: uuid.UUID
    case_id: uuid.UUID
    original_filename: str
    file_format: str
    file_size: int
    content_type: str | None
    image_metadata: dict[str, Any] | None = None
    preprocessed_reference: str | None = Field(default=None, exclude=True)
    preprocessing_metadata: dict[str, Any] | None = None
    uploaded_at: datetime

    @computed_field
    @property
    def preprocessed_available(self) -> bool:
        return bool(self.preprocessed_reference)


class PreprocessOut(BaseModel):
    case_id: uuid.UUID
    image_id: uuid.UUID
    preprocessed_available: bool = True
    output_format: str = "png"
    download_url: str
    metadata: dict[str, Any]
    message: str

class AnalysisResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    result_id: uuid.UUID
    case_id: uuid.UUID
    model_version: str | None
    segmentation_file: str | None
    stenosis_file: str | None
    estimated_narrowing: Decimal | None
    confidence_score: Decimal | None
    created_at: datetime

class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    history_id: uuid.UUID
    case_id: uuid.UUID
    action: str
    status: str
    message: str | None
    created_at: datetime

class PatientCreate(BaseModel):
    display_code: str = Field(min_length=1, max_length=80)
    age: int | None = Field(default=None, ge=0, le=120)
    sex: str | None = Field(default=None, max_length=30)
    medical_history: str | None = Field(default=None, max_length=5000)
    risk_factors: str | None = Field(default=None, max_length=5000)
    clinical_notes: str | None = Field(default=None, max_length=5000)

class PatientUpdate(BaseModel):
    display_code: str | None = Field(default=None, min_length=1, max_length=80)
    age: int | None = Field(default=None, ge=0, le=120)
    sex: str | None = Field(default=None, max_length=30)
    medical_history: str | None = Field(default=None, max_length=5000)
    risk_factors: str | None = Field(default=None, max_length=5000)
    clinical_notes: str | None = Field(default=None, max_length=5000)

class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_id: uuid.UUID
    owner_user_id: uuid.UUID
    display_code: str
    age: int | None
    sex: str | None
    medical_history: str | None
    risk_factors: str | None
    clinical_notes: str | None
    created_at: datetime

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    notification_id: uuid.UUID
    case_id: uuid.UUID | None
    alert_type: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

class ModelRegistryCreate(BaseModel):
    model_name: str = Field(min_length=1, max_length=150)
    version: str = Field(min_length=1, max_length=50)
    task: Literal["segmentation", "stenosis_detection", "centerline", "other"]
    description: str | None = Field(default=None, max_length=5000)
    framework: str | None = Field(default=None, max_length=80)
    model_reference: str | None = Field(default=None, max_length=1000)
    status: Literal["planned", "available", "deployed", "retired"] = "planned"
    performance_metadata: dict[str, Any] | None = None

class ModelRegistryUpdate(BaseModel):
    model_name: str | None = Field(default=None, min_length=1, max_length=150)
    version: str | None = Field(default=None, min_length=1, max_length=50)
    task: Literal["segmentation", "stenosis_detection", "centerline", "other"] | None = None
    description: str | None = Field(default=None, max_length=5000)
    framework: str | None = Field(default=None, max_length=80)
    model_reference: str | None = Field(default=None, max_length=1000)
    status: Literal["planned", "available", "deployed", "retired"] | None = None
    performance_metadata: dict[str, Any] | None = None

class ModelRegistryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model_id: uuid.UUID
    model_name: str
    version: str
    task: str
    description: str | None
    framework: str | None
    model_reference: str | None
    status: str
    performance_metadata: dict[str, Any] | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

class DashboardSummary(BaseModel):
    total_cases: int
    pending_cases: int
    processing_cases: int
    completed_cases: int
    failed_cases: int
    images_uploaded: int
    stored_result_records: int
    unread_notifications: int
    recent_cases: list[CaseOut]

class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    audit_id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    outcome: str
    details: dict[str, Any] | None
    created_at: datetime

class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    report_id: uuid.UUID
    case_id: uuid.UUID
    file_format: str
    created_at: datetime

class ResultsCompareOut(BaseModel):
    case_id: uuid.UUID
    baseline: dict[str, Any]
    comparison: dict[str, Any]
    changes: dict[str, Any]
