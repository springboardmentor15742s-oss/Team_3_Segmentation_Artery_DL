"""End-to-end smoke tests. Uses an isolated temporary SQLite database, never the developer's PostgreSQL DB."""
import os
import tempfile
from pathlib import Path
from decimal import Decimal

ROOT = Path(tempfile.gettempdir()) / f"arteryvision-tests-{os.getpid()}"
ROOT.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{ROOT / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(ROOT / "uploads")
os.environ["REPORT_DIR"] = str(ROOT / "reports")
os.environ["SECRET_KEY"] = "test-only-secret-key-that-is-long-enough-for-tests"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402
from app.main import app  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import AnalysisResult, User  # noqa: E402


def test_non_ai_workflow_end_to_end():
    db_path = ROOT / "test.db"
    if db_path.exists():
        db_path.unlink()
    # Reset side-effect folders for repeatable tests.
    for folder in (ROOT / "uploads", ROOT / "reports"):
        if folder.exists():
            for path in sorted(folder.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink(missing_ok=True)
                elif path.is_dir():
                    path.rmdir()
            folder.rmdir()

    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        register = client.post("/auth/register", json={
            "full_name": "Test Researcher", "email": "researcher@example.com", "password": "StrongPass123"
        })
        assert register.status_code == 201, register.text

        login = client.post("/auth/login", json={"email": "researcher@example.com", "password": "StrongPass123"})
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.get("/auth/me", headers=headers).status_code == 200

        profile = client.patch("/auth/me", headers=headers, json={"full_name": "Updated Researcher"})
        assert profile.status_code == 200 and profile.json()["full_name"] == "Updated Researcher"

        patient = client.post("/patients", headers=headers, json={"display_code": "DEID-001", "age": 25})
        assert patient.status_code == 201, patient.text
        patient_id = patient.json()["patient_id"]

        case = client.post("/cases", headers=headers, json={
            "case_name": "CCTA non-AI test", "imaging_modality": "CCTA",
            "anatomical_region": "Coronary arteries", "notes": "Test notes", "patient_id": patient_id,
        })
        assert case.status_code == 201, case.text
        case_id = case.json()["case_id"]
        assert client.get("/cases", headers=headers).status_code == 200
        assert client.get(f"/cases/{case_id}/history", headers=headers).status_code == 200

        # An extension error should create a durable notification without saving the file.
        bad_upload = client.post(f"/cases/{case_id}/upload", headers=headers, files={"file": ("bad.exe", b"test", "application/octet-stream")})
        assert bad_upload.status_code == 415
        notifications = client.get("/notifications", headers=headers)
        assert notifications.status_code == 200
        assert any(n["alert_type"] == "upload_failed" for n in notifications.json())

        # Supported extension upload is stored with metadata (this test intentionally uses a tiny fixture, not a medical scan).
        from io import BytesIO
        from PIL import Image as PILImage
        demo_jpeg = BytesIO()
        PILImage.new("RGB", (16, 12), color=(120, 100, 80)).save(demo_jpeg, format="JPEG")
        upload = client.post(f"/cases/{case_id}/upload", headers=headers, files={"file": ("demo.jpg", demo_jpeg.getvalue(), "image/jpeg")})
        assert upload.status_code == 201, upload.text
        image_id = upload.json()["image_id"]
        assert upload.json()["preprocessed_available"] is False
        assert upload.json()["image_metadata"]["width"] == 16
        invalid_raster = client.post(f"/cases/{case_id}/upload", headers=headers, files={"file": ("broken.jpg", b"not-a-real-jpeg", "image/jpeg")})
        assert invalid_raster.status_code == 422
        assert client.get(f"/cases/{case_id}/images", headers=headers).status_code == 200
        assert client.get(f"/cases/{case_id}/images/{image_id}/file", headers=headers).status_code == 200

        # Run the conventional (non-AI) preprocessing path against a valid raster image.
        raster = BytesIO()
        PILImage.new("L", (32, 24), color=120).save(raster, format="PNG")
        raster.seek(0)
        valid_upload = client.post(f"/cases/{case_id}/upload", headers=headers, files={"file": ("valid-demo.png", raster.getvalue(), "image/png")})
        assert valid_upload.status_code == 201, valid_upload.text
        valid_image_id = valid_upload.json()["image_id"]
        processed = client.post(f"/cases/{case_id}/images/{valid_image_id}/preprocess", headers=headers)
        assert processed.status_code == 200, processed.text
        assert processed.json()["preprocessed_available"] is True
        processed_file = client.get(f"/cases/{case_id}/images/{valid_image_id}/preprocessed-file", headers=headers)
        assert processed_file.status_code == 200 and processed_file.content.startswith(b"\x89PNG\r\n\x1a\n")

        # Create two saved result metadata records directly, as a trusted processing service would in a later phase.
        with SessionLocal() as db:
            db.add_all([
                AnalysisResult(case_id=__import__("uuid").UUID(case_id), model_version="baseline-0.1", estimated_narrowing=Decimal("20.0"), confidence_score=Decimal("0.7000")),
                AnalysisResult(case_id=__import__("uuid").UUID(case_id), model_version="baseline-0.2", estimated_narrowing=Decimal("25.0"), confidence_score=Decimal("0.8000")),
            ])
            db.commit()
            ids = [str(row.result_id) for row in db.scalars(select(AnalysisResult).where(AnalysisResult.case_id == __import__("uuid").UUID(case_id)).order_by(AnalysisResult.created_at, AnalysisResult.model_version)).all()]
        assert len(ids) == 2
        compared = client.get(f"/cases/{case_id}/results/compare", params={"baseline_id": ids[0], "comparison_id": ids[1]}, headers=headers)
        assert compared.status_code == 200, compared.text
        assert compared.json()["changes"]["estimated_narrowing_delta"] == 5.0

        summary = client.get("/dashboard/summary", headers=headers)
        assert summary.status_code == 200 and summary.json()["total_cases"] == 1
        assert summary.json()["images_uploaded"] == 2
        assert client.get("/models", headers=headers).status_code == 200
        assert client.post("/models", headers=headers, json={"model_name":"No permission", "version":"1", "task":"segmentation"}).status_code == 403

        for report_format in ("pdf", "json", "csv"):
            record = client.post(f"/reports/cases/{case_id}/export?format={report_format}", headers=headers)
            assert record.status_code == 200, (report_format, record.text)
            downloaded = client.get(f"/reports/{record.json()['report_id']}/download", headers=headers)
            assert downloaded.status_code == 200 and len(downloaded.content) > 30

        # Users cannot access another researcher's case.
        client.post("/auth/register", json={"full_name":"Second Researcher", "email":"second@example.com", "password":"StrongPass123"})
        second_login = client.post("/auth/login", json={"email":"second@example.com", "password":"StrongPass123"})
        second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
        assert client.get(f"/cases/{case_id}", headers=second_headers).status_code == 404

        # Logout revokes the current server-side session.
        assert client.post("/auth/logout", headers=headers).status_code == 204
        assert client.get("/auth/me", headers=headers).status_code == 401
